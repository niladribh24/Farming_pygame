import pygame
from settings import *
from support import *
from timer import Timer
from knowledge_base import FERTILIZER_DATA, IRRIGATION_DATA, INITIAL_WATER_RESERVE, MAX_WATER_RESERVE

class Player(pygame.sprite.Sprite):
	def __init__(self, pos, group, collision_sprites, tree_sprites, interaction, soil_layer, toggle_shop):
		super().__init__(group)

		self.import_assets()
		self.status = 'down_idle'
		self.frame_index = 0

		# general setup
		self.image = self.animations[self.status][self.frame_index]
		self.rect = self.image.get_rect(center = pos)
		self.z = LAYERS['main']

		# movement attributes
		self.direction = pygame.math.Vector2()
		self.pos = pygame.math.Vector2(self.rect.center)
		self.speed = 200

		# collision
		self.hitbox = self.rect.copy().inflate((-126,-70))
		self.collision_sprites = collision_sprites

		# timers 
		self.timers = {
			'tool use': Timer(350,self.use_tool),
			'tool switch': Timer(200),
			'seed use': Timer(350,self.use_seed),
			'seed switch': Timer(200),
			'fertilizer use': Timer(350, self.use_fertilizer),
			'fertilizer switch': Timer(200),
			'irrigation switch': Timer(200),
		}

		# tools 
		self.tools = ['hoe','axe','water']
		self.tool_index = 0
		self.selected_tool = self.tools[self.tool_index]

		# seeds (5 types)
		self.seeds = ['corn', 'tomato', 'wheat', 'carrot', 'potato']
		self.seed_index = 0
		self.selected_seed = self.seeds[self.seed_index]

		# inventory
		self.item_inventory = {
			'wood':   20,
			'apple':  20,
			'corn':   20,
			'tomato': 20,
			'wheat':  0,
			'carrot': 0,
			'potato': 0
		}
		self.seed_inventory = {
		'corn': 5,
		'tomato': 5,
		'wheat': 3,
		'carrot': 3,
		'potato': 2
		}
		# Fertilizer inventory - 8 types (5 organic, 3 chemical)
		self.fertilizer_inventory = {
			'compost': 3,
			'bone_meal': 2,
			'fish_emulsion': 1,
			'blood_meal': 1,
			'wood_ash': 2,
			'npk_10_10_10': 2,
			'npk_5_10_10': 1,
			'urea': 1
		}
		# Fertilizer selection (organic ones first)
		self.fertilizers = ['compost', 'bone_meal', 'fish_emulsion', 'blood_meal', 'wood_ash', 'npk_10_10_10', 'npk_5_10_10', 'urea']
		self.fertilizer_index = 0
		self.selected_fertilizer = self.fertilizers[self.fertilizer_index]
		
		# Irrigation system
		self.irrigation_modes = ['manual', 'efficient', 'drip']
		self.irrigation_index = 0
		self.selected_irrigation = self.irrigation_modes[self.irrigation_index]
		
		# Water reserve (for rainwater collection)
		self.water_reserve = INITIAL_WATER_RESERVE
		self.max_water_reserve = MAX_WATER_RESERVE
		
		self.money = 200

		# interaction
		self.tree_sprites = tree_sprites
		self.interaction = interaction
		self.sleep = False
		self.soil_layer = soil_layer
		self.toggle_shop = toggle_shop
		
		# Learning system reference (set by Level)
		self.learning_system = None
		
		# SKILL SYSTEM
		# Water skills: affects max_water_reserve
		self.water_skill_level = 1  # 1, 2, or 3
		self.water_skill_capacities = {1: 50, 2: 100, 3: 150}
		
		# Speed skills: affects movement speed
		self.speed_skill_level = 1  # 1, 2, or 3
		self.base_speed = 200  # Base speed at level 1
		self.speed_multipliers = {1: 1.0, 2: 1.1, 3: 1.2}  # 100%, 110%, 120%
		
		# Apply initial skill effects
		self._apply_skill_effects()

		# sound
		self.watering = pygame.mixer.Sound('./audio/water.mp3')
		self.watering.set_volume(0.2)

	def use_tool(self):
		if self.selected_tool == 'hoe':
			self.soil_layer.get_hit(self.target_pos)
		
		if self.selected_tool == 'axe':
			for tree in self.tree_sprites.sprites():
				if tree.rect.collidepoint(self.target_pos):
					tree.damage()
		
		if self.selected_tool == 'water':
			# Get water cost based on irrigation mode
			water_cost = IRRIGATION_DATA[self.selected_irrigation]['water_cost']
			
			# Check if player has enough water
			if self.water_reserve >= water_cost:
				self.water_reserve -= water_cost
				self.soil_layer.water(self.target_pos)
				self.watering.play()
			else:
				# Alert: no water
				if self.learning_system:
					self.learning_system.add_notification("No water!")

	def get_target_pos(self):

		self.target_pos = self.rect.center + PLAYER_TOOL_OFFSET[self.status.split('_')[0]]

	def use_seed(self):
		if self.seed_inventory[self.selected_seed] > 0:
			self.soil_layer.plant_seed(self.target_pos, self.selected_seed)
			self.seed_inventory[self.selected_seed] -= 1
		else:
			# Alert: no seeds
			if self.learning_system:
				self.learning_system.add_notification(f"No {self.selected_seed} seeds!")
	
	def use_fertilizer(self):
		"""Apply selected fertilizer to soil tile"""
		if self.fertilizer_inventory[self.selected_fertilizer] > 0:
			if self.soil_layer.apply_fertilizer(self.target_pos, self.selected_fertilizer):
				self.fertilizer_inventory[self.selected_fertilizer] -= 1
				
				# Track for achievements
				if self.learning_system and self.selected_fertilizer == 'organic':
					self.learning_system.organic_fertilizer_count += 1
		else:
			# Alert: no fertilizer
			if self.learning_system:
				fert_name = FERTILIZER_DATA[self.selected_fertilizer]['name']
				self.learning_system.add_notification(f"No {fert_name}!")
	
	def collect_rainwater(self, amount=5):
		"""Collect rainwater into reserve (called on rainy days)"""
		self.water_reserve = min(self.max_water_reserve, self.water_reserve + amount)
		if self.learning_system:
			self.learning_system.add_notification(f"💧 Collected rainwater (+{amount})")
	
	def get_unlocked_irrigation_modes(self):
		"""Get list of irrigation modes available based on skills"""
		unlocked = ['manual']  # Always available
		if self.learning_system:
			skills = self.learning_system.skill_tree.get_unlocked_skills()
			if 'Water Management' in skills:
				unlocked.append('efficient')
			if 'Drip Irrigation' in skills:
				unlocked.append('drip')
		return unlocked

	def import_assets(self):
		self.animations = {'up': [],'down': [],'left': [],'right': [],
						   'right_idle':[],'left_idle':[],'up_idle':[],'down_idle':[],
						   'right_hoe':[],'left_hoe':[],'up_hoe':[],'down_hoe':[],
						   'right_axe':[],'left_axe':[],'up_axe':[],'down_axe':[],
						   'right_water':[],'left_water':[],'up_water':[],'down_water':[]}

		for animation in self.animations.keys():
			full_path = './graphics/character/' + animation
			self.animations[animation] = import_folder(full_path)

	def animate(self,dt):
		self.frame_index += 4 * dt
		if self.frame_index >= len(self.animations[self.status]):
			self.frame_index = 0

		self.image = self.animations[self.status][int(self.frame_index)]

	def input(self):
		keys = pygame.key.get_pressed()

		if not self.timers['tool use'].active and not self.sleep:
			# directions (WASD)
			if keys[pygame.K_w]:
				self.direction.y = -1
				self.status = 'up'
			elif keys[pygame.K_s]:
				self.direction.y = 1
				self.status = 'down'
			else:
				self.direction.y = 0

			if keys[pygame.K_d]:
				self.direction.x = 1
				self.status = 'right'
			elif keys[pygame.K_a]:
				self.direction.x = -1
				self.status = 'left'
			else:
				self.direction.x = 0

			# tool use
			if keys[pygame.K_SPACE]:
				self.timers['tool use'].activate()
				self.direction = pygame.math.Vector2()
				self.frame_index = 0

			# change tool
			if keys[pygame.K_q] and not self.timers['tool switch'].active:
				self.timers['tool switch'].activate()
				self.tool_index += 1
				self.tool_index = self.tool_index if self.tool_index < len(self.tools) else 0
				self.selected_tool = self.tools[self.tool_index]

			# seed use
			if keys[pygame.K_LCTRL]:
				self.timers['seed use'].activate()
				self.direction = pygame.math.Vector2()
				self.frame_index = 0

			# change seed 
			if keys[pygame.K_e] and not self.timers['seed switch'].active:
				self.timers['seed switch'].activate()
				self.seed_index += 1
				self.seed_index = self.seed_index if self.seed_index < len(self.seeds) else 0
				self.selected_seed = self.seeds[self.seed_index]
			
			# FERTILIZER CONTROLS
			# F key = switch fertilizer type
			if keys[pygame.K_f] and not self.timers['fertilizer switch'].active:
				self.timers['fertilizer switch'].activate()
				self.fertilizer_index += 1
				self.fertilizer_index = self.fertilizer_index if self.fertilizer_index < len(self.fertilizers) else 0
				self.selected_fertilizer = self.fertilizers[self.fertilizer_index]
			
			# R key = apply fertilizer
			if keys[pygame.K_r] and not self.timers['fertilizer use'].active:
				self.timers['fertilizer use'].activate()
				self.direction = pygame.math.Vector2()
				self.frame_index = 0
			
			# IRRIGATION CONTROLS
			# O key = switch irrigation mode (only unlocked modes)
			if keys[pygame.K_o] and not self.timers['irrigation switch'].active:
				self.timers['irrigation switch'].activate()
				unlocked_modes = self.get_unlocked_irrigation_modes()
				if len(unlocked_modes) > 1:
					current_idx = unlocked_modes.index(self.selected_irrigation) if self.selected_irrigation in unlocked_modes else 0
					next_idx = (current_idx + 1) % len(unlocked_modes)
					self.selected_irrigation = unlocked_modes[next_idx]
					if self.learning_system:
						mode_name = IRRIGATION_DATA[self.selected_irrigation]['name']
						self.learning_system.add_notification(f"🚿 Switched to {mode_name}")

			if keys[pygame.K_RETURN]:
				collided_interaction_sprite = pygame.sprite.spritecollide(self,self.interaction,False)
				if collided_interaction_sprite:
					if collided_interaction_sprite[0].name == 'Trader':
						self.toggle_shop()
					else:
						self.status = 'left_idle'
						self.sleep = True
			
			# TEST KEYBINDS FOR SKILLS (temporary for testing)
			# 1, 2, 3 = Water skill levels
			if keys[pygame.K_1] and not self.timers['tool switch'].active:
				self.timers['tool switch'].activate()
				self.water_skill_level = 1
				self._apply_skill_effects()
				if self.learning_system:
					self.learning_system.add_notification(f"💧 Water Skill 1 (Capacity: 50)")
			if keys[pygame.K_2] and not self.timers['tool switch'].active:
				self.timers['tool switch'].activate()
				self.water_skill_level = 2
				self._apply_skill_effects()
				if self.learning_system:
					self.learning_system.add_notification(f"💧 Water Skill 2 (Capacity: 100)")
			if keys[pygame.K_3] and not self.timers['tool switch'].active:
				self.timers['tool switch'].activate()
				self.water_skill_level = 3
				self._apply_skill_effects()
				if self.learning_system:
					self.learning_system.add_notification(f"💧 Water Skill 3 (Capacity: 150)")
			
			# 4, 5, 6 = Speed skill levels
			if keys[pygame.K_4] and not self.timers['tool switch'].active:
				self.timers['tool switch'].activate()
				self.speed_skill_level = 1
				self._apply_skill_effects()
				if self.learning_system:
					self.learning_system.add_notification(f"🏃 Speed Skill 1 (100%)")
			if keys[pygame.K_5] and not self.timers['tool switch'].active:
				self.timers['tool switch'].activate()
				self.speed_skill_level = 2
				self._apply_skill_effects()
				if self.learning_system:
					self.learning_system.add_notification(f"🏃 Speed Skill 2 (110%)")
			if keys[pygame.K_6] and not self.timers['tool switch'].active:
				self.timers['tool switch'].activate()
				self.speed_skill_level = 3
				self._apply_skill_effects()
				if self.learning_system:
					self.learning_system.add_notification(f"🏃 Speed Skill 3 (120%)")
	
	def _apply_skill_effects(self):
		"""Apply skill effects to player stats"""
		# Water skill affects max water reserve
		self.max_water_reserve = self.water_skill_capacities[self.water_skill_level]
		# Clamp current reserve to new max
		if self.water_reserve > self.max_water_reserve:
			self.water_reserve = self.max_water_reserve
		
		# Speed skill affects movement speed
		self.speed = int(self.base_speed * self.speed_multipliers[self.speed_skill_level])

	def get_status(self):
		
		# idle
		if self.direction.magnitude() == 0:
			self.status = self.status.split('_')[0] + '_idle'

		# tool use
		if self.timers['tool use'].active:
			self.status = self.status.split('_')[0] + '_' + self.selected_tool

	def update_timers(self):
		for timer in self.timers.values():
			timer.update()

	def collision(self, direction):
		for sprite in self.collision_sprites.sprites():
			if hasattr(sprite, 'hitbox'):
				if sprite.hitbox.colliderect(self.hitbox):
					if direction == 'horizontal':
						if self.direction.x > 0: # moving right
							self.hitbox.right = sprite.hitbox.left
						if self.direction.x < 0: # moving left
							self.hitbox.left = sprite.hitbox.right
						self.rect.centerx = self.hitbox.centerx
						self.pos.x = self.hitbox.centerx

					if direction == 'vertical':
						if self.direction.y > 0: # moving down
							self.hitbox.bottom = sprite.hitbox.top
						if self.direction.y < 0: # moving up
							self.hitbox.top = sprite.hitbox.bottom
						self.rect.centery = self.hitbox.centery
						self.pos.y = self.hitbox.centery

	def move(self,dt):

		# normalizing a vector 
		if self.direction.magnitude() > 0:
			self.direction = self.direction.normalize()

		# horizontal movement
		self.pos.x += self.direction.x * self.speed * dt
		self.hitbox.centerx = round(self.pos.x)
		self.rect.centerx = self.hitbox.centerx
		self.collision('horizontal')

		# vertical movement
		self.pos.y += self.direction.y * self.speed * dt
		self.hitbox.centery = round(self.pos.y)
		self.rect.centery = self.hitbox.centery
		self.collision('vertical')

	def update(self, dt):
		self.input()
		self.get_status()
		self.update_timers()
		self.get_target_pos()

		self.move(dt)
		self.animate(dt)
