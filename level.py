import pygame 
from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic, Water, WildFlower, Tree, Interaction, Particle
from pytmx.util_pygame import load_pygame
from support import *
from transition import Transition
from soil import SoilLayer
from sky import Rain, Sky
from random import randint
from menu import Menu
from learning_system import LearningSystem
from book_ui import get_knowledge_book
from settings_menu import get_settings_menu
from save_manager import SaveManager

class Level:
	def __init__(self):

		# get the display surface
		self.display_surface = pygame.display.get_surface()
        
		# Reset flag
		self.reset_pending = False

		# sprite groups
		self.all_sprites = CameraGroup()
		self.collision_sprites = pygame.sprite.Group()
		self.tree_sprites = pygame.sprite.Group()
		self.interaction_sprites = pygame.sprite.Group()

		self.soil_layer = SoilLayer(self.all_sprites, self.collision_sprites)
		self.setup()
		self.overlay = Overlay(self.player)
		self.transition = Transition(self.reset, self.player)

		# LEARNING SYSTEM - Initialize and connect
		self.learning_system = LearningSystem()
		self.soil_layer.learning_system = self.learning_system
		self.overlay.learning_system = self.learning_system
		self.overlay.soil_layer = self.soil_layer
		self.overlay.interaction_sprites = self.interaction_sprites
		self.player.learning_system = self.learning_system
		
		# Day summary state
		self.showing_summary = False
		self.day_summary_text = ""

		# sky
		self.rain = Rain(self.all_sprites)
		self.raining = randint(0,10) > 7
		self.soil_layer.raining = self.raining
		self.sky = Sky()
		
		# Sync weather with learning system
		self._sync_weather()
		if self.raining:
			self.soil_layer.water_all()

		# UI - Singleton setup
		self.menu = Menu(self.player, self.toggle_shop)
		self.settings_menu = get_settings_menu(self)
		self.settings_menu.level = self # Ensure singleton points to THIS level instance
		self.shop_active = False
		
		# Knowledge book
		self.knowledge_book = get_knowledge_book()
		self.book_toggle_timer = pygame.time.get_ticks()

		# music
		self.success = pygame.mixer.Sound('./audio/success.wav')
		self.success.set_volume(0.3)
		self.music = pygame.mixer.Sound('./audio/music.mp3')
		self.music.set_volume(0.3)  # Initial volume
		self.music.play(loops = -1)
		
		# Settings menu (created after music so it can control volume)
		self.settings_menu = get_settings_menu(self)
		self.settings_toggle_timer = pygame.time.get_ticks()

		# SAVE SYSTEM
		self.save_manager = SaveManager()
		try:
			# Pass tree sprites to load their state
			self.save_manager.load_game(self.player, self.soil_layer, self.learning_system, self.tree_sprites)
			
			# Re-sync weather and water after load (in case save was rainy)
			self._sync_weather()
			if self.raining:
				self.soil_layer.water_all()
		except Exception as e:
			print(f"Failed to load save: {e}")
	
	def _sync_weather(self):
		"""Sync game weather with learning system weather queue"""
		weather = self.learning_system.get_current_weather()
		self.raining = weather == 'rain'
		self.soil_layer.raining = self.raining

	def setup(self):
		tmx_data = load_pygame('./data/map.tmx')

		# house 
		for layer in ['HouseFloor', 'HouseFurnitureBottom']:
			for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
				Generic((x * TILE_SIZE,y * TILE_SIZE), surf, self.all_sprites, LAYERS['house bottom'])

		for layer in ['HouseWalls', 'HouseFurnitureTop']:
			for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
				Generic((x * TILE_SIZE,y * TILE_SIZE), surf, self.all_sprites)

		# Fence
		for x, y, surf in tmx_data.get_layer_by_name('Fence').tiles():
			Generic((x * TILE_SIZE,y * TILE_SIZE), surf, [self.all_sprites, self.collision_sprites])

		# water 
		water_frames = import_folder('./graphics/water')
		for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
			Water((x * TILE_SIZE,y * TILE_SIZE), water_frames, self.all_sprites)

		# trees 
		for obj in tmx_data.get_layer_by_name('Trees'):
			Tree(
				pos = (obj.x, obj.y), 
				surf = obj.image, 
				groups = [self.all_sprites, self.collision_sprites, self.tree_sprites], 
				name = obj.name,
				player_add = self.player_add,
				all_sprites = self.all_sprites)

		# wildflowers 
		for obj in tmx_data.get_layer_by_name('Decoration'):
			WildFlower((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites])

		# collion tiles
		for x, y, surf in tmx_data.get_layer_by_name('Collision').tiles():
			Generic((x * TILE_SIZE, y * TILE_SIZE), pygame.Surface((TILE_SIZE, TILE_SIZE)), self.collision_sprites)

		# Player 
		for obj in tmx_data.get_layer_by_name('Player'):
			if obj.name == 'Start':
				self.player = Player(
					pos = (obj.x,obj.y), 
					group = self.all_sprites, 
					collision_sprites = self.collision_sprites,
					tree_sprites = self.tree_sprites,
					interaction = self.interaction_sprites,
					soil_layer = self.soil_layer,
					toggle_shop = self.toggle_shop)
			
			if obj.name == 'Bed':
				Interaction((obj.x,obj.y), (obj.width,obj.height), self.interaction_sprites, obj.name)

			if obj.name == 'Trader':
				Interaction((obj.x,obj.y), (obj.width,obj.height), self.interaction_sprites, obj.name)


		Generic(
			pos = (0,0),
			surf = pygame.image.load('./graphics/world/ground.png').convert_alpha(),
			groups = self.all_sprites,
			z = LAYERS['ground'])

	def player_add(self,item):

		self.player.item_inventory[item] += 1
		self.success.play()

	def toggle_shop(self):

		self.shop_active = not self.shop_active

	def reset(self):
		# LEARNING SYSTEM - End of day processing
		# Evaluate watering and reset water counts
		self.soil_layer.reset_daily_water_counts()
		
		# Check for achievements and skill unlocks
		stats = {
			'avg_soil_health': self.soil_layer.get_average_soil_health()
		}
		self.learning_system.check_achievements(stats)
		self.learning_system.check_skill_unlocks(stats)
		
		# Generate and store day summary
		self.day_summary_text = self.learning_system.get_daily_summary()
		
		# Advance to next day in learning system
		self.learning_system.advance_day()
		self.learning_system.clear_daily_log()
		
		# plants
		self.soil_layer.update_plants()

		# soil
		self.soil_layer.remove_water()
		
		# Sync weather from learning system queue
		self._sync_weather()
		if self.raining:
			self.soil_layer.water_all()
			# Collect rainwater into player's reserve
			self.player.collect_rainwater(5)
		
		# Auto-save after day transition (update trees first)
		# Regrow trees logic
		for tree in self.tree_sprites.sprites():
			if not tree.alive:
				tree.respawn_timer += 1
				if tree.respawn_timer >= 5:
					tree.respawn()

			# Clear old apples and spawn new ones (create_fruit checks alive status)
			for apple in tree.apple_sprites.sprites():
				apple.kill()
			tree.create_fruit()

		self.save_manager.save_game(self.player, self.soil_layer, self.learning_system, self.tree_sprites)

		# sky
		self.sky.start_color = [255,255,255]

	def plant_collision(self):
		if self.soil_layer.plant_sprites:
			for plant in self.soil_layer.plant_sprites.sprites():
				if plant.harvestable and plant.rect.colliderect(self.player.hitbox):
					# Calculate yield based on soil health
					yield_modifier = self.soil_layer.calculate_yield_modifier(plant.rect.center)
					
					# Add to inventory (base + modifier bonus)
					self.player_add(plant.plant_type)
					if yield_modifier >= 1.5:
						# Bonus harvest for healthy soil!
						self.player_add(plant.plant_type)
						self.learning_system.add_notification("🌾 Bonus harvest from healthy soil!")
					
					plant.kill()
					Particle(plant.rect.topleft, plant.image, self.all_sprites, z = LAYERS['main'])
					self.soil_layer.grid[plant.rect.centery // TILE_SIZE][plant.rect.centerx // TILE_SIZE].remove('P')

	def run(self,dt):
		
		# drawing logic
		self.display_surface.fill('black')
		self.all_sprites.custom_draw(self.player)
		
		# Handle keyboard input for book toggle (works in all states except sleeping)
		keys = pygame.key.get_pressed()
		current_time = pygame.time.get_ticks()
		
		# B key to toggle Knowledge Book
		if keys[pygame.K_b] and not self.player.sleep and not self.shop_active and not self.settings_menu.is_open:
			if current_time - self.book_toggle_timer > 400:
				self.knowledge_book.toggle()
				self.book_toggle_timer = current_time
		
		# P key to toggle Settings Menu
		if keys[pygame.K_p] and not self.player.sleep and not self.shop_active and not self.knowledge_book.is_open:
			if current_time - self.settings_toggle_timer > 400:
				self.settings_menu.toggle()
				self.settings_toggle_timer = current_time
		
		# Main game state updates
		if self.settings_menu.is_open:
			self.settings_menu.update()
		elif self.knowledge_book.is_open:
			# Book is open - update and display it
			self.knowledge_book.update()
			self.knowledge_book.display()
		elif self.shop_active:
			pass  # Menu updates handled below
		else:
			self.all_sprites.update(dt)
			self.plant_collision()

		# weather & overlay (drawn before menus so menus appear on top)
		self.overlay.display()
		if self.raining and not self.shop_active:
			self.rain.update()
		self.sky.display(dt)

		# Draw menus/book LAST so they appear on top of everything
		if self.settings_menu.is_open:
			self.settings_menu.display()
		elif self.knowledge_book.is_open:
			self.knowledge_book.display()
		elif self.shop_active:
			self.menu.update()

		# transition overlay
		if self.player.sleep:
			self.transition.play()

class CameraGroup(pygame.sprite.Group):
	def __init__(self):
		super().__init__()
		self.display_surface = pygame.display.get_surface()
		self.offset = pygame.math.Vector2()

	def custom_draw(self, player):
		self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
		self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2

		for layer in LAYERS.values():
			for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):
				if sprite.z == layer:
					offset_rect = sprite.rect.copy()
					offset_rect.center -= self.offset
					self.display_surface.blit(sprite.image, offset_rect)

					# # anaytics
					# if sprite == player:
					# 	pygame.draw.rect(self.display_surface,'red',offset_rect,5)
					# 	hitbox_rect = player.hitbox.copy()
					# 	hitbox_rect.center = offset_rect.center
					# 	pygame.draw.rect(self.display_surface,'green',hitbox_rect,5)
					# 	target_pos = offset_rect.center + PLAYER_TOOL_OFFSET[player.status.split('_')[0]]
					# 	pygame.draw.circle(self.display_surface,'blue',target_pos,5)