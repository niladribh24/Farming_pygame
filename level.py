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
from knowledge_base import MAX_WATER_RESERVE
from book_ui import get_knowledge_book
from settings_menu import get_settings_menu
from equipment import PlacedWaterTank
from save_manager import SaveManager
from inventory import get_inventory
from skill_tree import get_skill_tree

class Level:
	def __init__(self):

		self.display_surface = pygame.display.get_surface()
        
		self.reset_pending = False

		self.all_sprites = CameraGroup()
		self.collision_sprites = pygame.sprite.Group()
		self.tree_sprites = pygame.sprite.Group()
		self.interaction_sprites = pygame.sprite.Group()
		self.water_tank_sprites = pygame.sprite.Group()  # FEATURE: Placed water tanks

		self.soil_layer = SoilLayer(self.all_sprites, self.collision_sprites)
		self.setup()
		self.overlay = Overlay(self.player)
		self.transition = Transition(self.reset, self.player)

		self.learning_system = LearningSystem()
		self.soil_layer.learning_system = self.learning_system
		self.overlay.learning_system = self.learning_system
		self.overlay.soil_layer = self.soil_layer
		self.overlay.interaction_sprites = self.interaction_sprites
		self.player.learning_system = self.learning_system
		
		self.player.place_tank_callback = self.place_water_tank
		
		self.showing_summary = False
		self.day_summary_text = ""

		self.rain = Rain(self.all_sprites)
		self.raining = randint(0,10) > 7
		self.soil_layer.raining = self.raining
		self.sky = Sky()
		
		self._sync_weather()
		if self.raining:
			self.soil_layer.water_all()

		self.menu = Menu(self.player, self.toggle_shop)
		self.settings_menu = get_settings_menu(self)
		self.settings_menu.level = self # Ensure singleton points to THIS level instance
		self.shop_active = False
		
		self.knowledge_book = get_knowledge_book()
		
		self.inventory = get_inventory(self.player)
		self.inventory_toggle_timer = pygame.time.get_ticks()
		self.book_toggle_timer = pygame.time.get_ticks()
		
		self.skill_tree = get_skill_tree(self.player)
		self.skill_tree.learning_system = self.learning_system
		
		self.drip_removal_pending = False
		self.drip_removal_target = None
		self.skill_tree_toggle_timer = pygame.time.get_ticks()

		self.success = pygame.mixer.Sound('./audio/success.wav')
		self.success.set_volume(0.3)
		self.music = pygame.mixer.Sound('./audio/music.mp3')
		self.music.set_volume(0)  # Initial volume (muted by default)
		self.music.play(loops = -1)
		
		self.settings_menu = get_settings_menu(self)
		self.settings_toggle_timer = pygame.time.get_ticks()

		self.save_manager = SaveManager()
		try:
			self.save_manager.load_game(self.player, self.soil_layer, self.learning_system, self.tree_sprites, water_tanks=self.water_tank_sprites)
			
			self._sync_weather()
			if self.raining:
				self.soil_layer.water_all()
		except Exception as e:
			print(f"Failed to load save: {e}")
	
	def _sync_weather(self):
		weather = self.learning_system.get_current_weather()
		self.raining = weather == 'rain'
		self.soil_layer.raining = self.raining

	def setup(self):
		tmx_data = load_pygame('./data/map.tmx')

		for layer in ['HouseFloor', 'HouseFurnitureBottom']:
			for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
				Generic((x * TILE_SIZE,y * TILE_SIZE), surf, self.all_sprites, LAYERS['house bottom'])

		for layer in ['HouseWalls', 'HouseFurnitureTop']:
			for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
				Generic((x * TILE_SIZE,y * TILE_SIZE), surf, self.all_sprites)

		for x, y, surf in tmx_data.get_layer_by_name('Fence').tiles():
			Generic((x * TILE_SIZE,y * TILE_SIZE), surf, [self.all_sprites, self.collision_sprites])

		water_frames = import_folder('./graphics/water')
		for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
			Water((x * TILE_SIZE,y * TILE_SIZE), water_frames, self.all_sprites)

		for obj in tmx_data.get_layer_by_name('Trees'):
			Tree(
				pos = (obj.x, obj.y), 
				surf = obj.image, 
				groups = [self.all_sprites, self.collision_sprites, self.tree_sprites], 
				name = obj.name,
				player_add = self.player_add,
				all_sprites = self.all_sprites)

		for obj in tmx_data.get_layer_by_name('Decoration'):
			WildFlower((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites])

		for x, y, surf in tmx_data.get_layer_by_name('Collision').tiles():
			Generic((x * TILE_SIZE, y * TILE_SIZE), pygame.Surface((TILE_SIZE, TILE_SIZE)), self.collision_sprites)

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
	
	def place_water_tank(self, pos):
		x = (int(pos[0]) // TILE_SIZE) * TILE_SIZE
		y = (int(pos[1]) // TILE_SIZE) * TILE_SIZE
		
		PlacedWaterTank(
			pos=(x, y),
			groups=[self.all_sprites, self.water_tank_sprites],
			collision_groups=[self.collision_sprites]
		)
		
		self.player.water_tank_bonus = getattr(self.player, 'water_tank_bonus', 0) + 20
		
		self.player.apply_skill_effects()
		self.learning_system.add_notification(f"💧 Water capacity +20! (Max: {self.player.max_water_reserve})")

	def reset(self):
		self.soil_layer.reset_daily_water_counts()
		
		stats = {
			'avg_soil_health': self.soil_layer.get_average_soil_health()
		}
		self.learning_system.check_achievements(stats)
		self.learning_system.check_skill_unlocks(stats)
		
		self.day_summary_text = self.learning_system.get_daily_summary()
		
		self.learning_system.advance_day()
		self.learning_system.clear_daily_log()
		
		self.soil_layer.update_plants()

		self.soil_layer.remove_water()
		
		self._sync_weather()
		if self.raining:
			self.soil_layer.water_all()
			self.player.collect_rainwater(5)
			tank_bonus = len(self.water_tank_sprites.sprites()) * 15
			if tank_bonus > 0:
				self.player.rain_tank.collect_rain(tank_bonus)
				self.learning_system.add_notification(f"💧 Tanks collected +{tank_bonus} water!")
		else:
			drip_watered = self.soil_layer.auto_water_drip_tiles()
			if drip_watered > 0:
				self.learning_system.add_notification(f"Drip irrigation watered {drip_watered} tiles automatically!")
		
		for tree in self.tree_sprites.sprites():
			if not tree.alive:
				tree.respawn_timer += 1
				if tree.respawn_timer >= 5:
					tree.respawn()

			for apple in tree.apple_sprites.sprites():
				apple.kill()
			tree.create_fruit()

		self.save_manager.save_game(self.player, self.soil_layer, self.learning_system, self.tree_sprites, water_tanks=self.water_tank_sprites)
		
		self.sky.reset_cycle()

	def save(self):
		self.save_manager.save_game(self.player, self.soil_layer, self.learning_system, self.tree_sprites, water_tanks=self.water_tank_sprites)

		self.sky.reset_cycle()

	def plant_collision(self):
		if self.soil_layer.plant_sprites:
			for plant in self.soil_layer.plant_sprites.sprites():
				if plant.harvestable and plant.rect.colliderect(self.player.hitbox):
					tile_health = self.soil_layer.get_tile_soil_health(plant.rect.center)
					
					if tile_health >= 100:
						health_multiplier = 4
					elif tile_health >= 50:
						health_multiplier = 2
					else:
						health_multiplier = 1
					
					fertilizer_multiplier = 1
					if plant.total_grow_days > 0:
						fertilized_ratio = plant.fertilized_days / plant.total_grow_days
						if fertilized_ratio >= 0.5:  # 50% or more days fertilized
							fertilizer_multiplier = 2
					
					total_yield = health_multiplier * fertilizer_multiplier
					
					for _ in range(total_yield):
						self.player_add(plant.plant_type)
					
					if total_yield >= 8:
						self.learning_system.add_notification(f"x{total_yield} MEGA harvest! (100% health + fertilized) +20pts")
						self.learning_system.add_score(20, "mega_harvest")
					elif total_yield >= 4:
						self.learning_system.add_notification(f"x{total_yield} harvest! (great soil + fertilizer) +8pts")
						self.learning_system.add_score(8, "great_harvest")
					elif total_yield >= 2:
						self.learning_system.add_notification(f"x{total_yield} harvest from healthy soil! +3pts")
						self.learning_system.add_score(3, "good_harvest")
					else:
						self.learning_system.add_score(1, "harvest")
					
					plant.kill()
					Particle(plant.rect.topleft, plant.image, self.all_sprites, z = LAYERS['main'])
					self.soil_layer.grid[plant.rect.centery // TILE_SIZE][plant.rect.centerx // TILE_SIZE].remove('P')

	def run(self, dt, events=None):
		if events is None:
			events = []
		
		self.display_surface.fill('black')
		self.all_sprites.custom_draw(self.player)
		
		keys = pygame.key.get_pressed()
		current_time = pygame.time.get_ticks()
		
		if keys[pygame.K_b] and not self.player.sleep and not self.shop_active and not self.settings_menu.is_open and not self.inventory.is_open:
			if current_time - self.book_toggle_timer > 400:
				self.knowledge_book.toggle()
				self.book_toggle_timer = current_time
		
		if keys[pygame.K_i] and not self.player.sleep and not self.shop_active and not self.settings_menu.is_open and not self.knowledge_book.is_open:
			if not (self.inventory.is_open and self.inventory.search_active):
				if current_time - self.inventory_toggle_timer > 400:
					self.inventory.toggle()
					self.inventory_toggle_timer = current_time
		
		if keys[pygame.K_p] and not self.player.sleep and not self.shop_active and not self.knowledge_book.is_open and not self.inventory.is_open and not self.skill_tree.is_open:
			if current_time - self.settings_toggle_timer > 400:
				self.settings_menu.toggle()
				self.settings_toggle_timer = current_time
		
		if keys[pygame.K_t] and not self.player.sleep and not self.shop_active and not self.knowledge_book.is_open and not self.inventory.is_open and not self.settings_menu.is_open:
			if current_time - self.skill_tree_toggle_timer > 400:
				self.skill_tree.toggle()
				self.skill_tree_toggle_timer = current_time
		
		if keys[pygame.K_x] and not self.player.sleep and not self.shop_active:
			if current_time - self.skill_tree_toggle_timer > 400:  # Reuse timer
				self.skill_tree_toggle_timer = current_time
				if self.drip_removal_pending:
					if self.drip_removal_target:
						self.soil_layer.remove_drip_irrigation(self.drip_removal_target, self.player)
					self.drip_removal_pending = False
					self.drip_removal_target = None
				else:
					target_pos = self.player.rect.center
					for drip in self.soil_layer.drip_irrigation_sprites.sprites():
						if drip.rect.collidepoint(target_pos):
							self.drip_removal_pending = True
							self.drip_removal_target = target_pos
							self.learning_system.add_notification("Remove drip irrigation? Press X again to confirm, ESC to cancel.")
							break
		
		if keys[pygame.K_ESCAPE] and self.drip_removal_pending:
			self.drip_removal_pending = False
			self.drip_removal_target = None
			self.learning_system.add_notification("Removal cancelled.")
		
		if self.settings_menu.is_open:
			self.settings_menu.update()
		elif self.skill_tree.is_open:
			self.skill_tree.update()
		elif self.inventory.is_open:
			for event in events:
				self.inventory.handle_text_input(event)
			self.inventory.update()
		elif self.knowledge_book.is_open:
			self.knowledge_book.update()
			self.knowledge_book.display()
		elif self.shop_active:
			pass  # Menu updates handled below
		else:
			self.all_sprites.update(dt)
			self.plant_collision()

		self.overlay.display()
		if self.raining and not self.shop_active:
			self.rain.update()
		self.sky.display(dt)
		
		if self.sky.night_complete:
			self.sky.night_complete = False
			self.reset()
			self.sky.reset_cycle()

		if self.settings_menu.is_open:
			self.settings_menu.display()
		elif self.skill_tree.is_open:
			self.skill_tree.display()
		elif self.inventory.is_open:
			self.inventory.display()
		elif self.knowledge_book.is_open:
			self.knowledge_book.display()
		elif self.shop_active:
			self.menu.update()

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