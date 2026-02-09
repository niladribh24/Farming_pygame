import pygame
from settings import *
from support import *
from timer import Timer
from knowledge_base import FERTILIZER_DATA, IRRIGATION_DATA, INITIAL_WATER_RESERVE, MAX_WATER_RESERVE
from rainwater import RainTank

class Player(pygame.sprite.Sprite):
	def __init__(self, pos, group, collision_sprites, tree_sprites, interaction, soil_layer, toggle_shop):
		super().__init__(group)

		self.import_assets()
		self.status = 'down_idle'
		self.frame_index = 0

		self.image = self.animations[self.status][self.frame_index]
		self.rect = self.image.get_rect(center = pos)
		self.z = LAYERS['main']

		self.direction = pygame.math.Vector2()
		self.pos = pygame.math.Vector2(self.rect.center)
		self.base_speed = 200
		self.speed = self.base_speed

		self.hitbox = self.rect.copy().inflate((-126,-70))
		self.collision_sprites = collision_sprites

		self.timers = {
			'tool use': Timer(350,self.use_tool),
			'tool switch': Timer(200),
			'seed use': Timer(350,self.use_seed),
			'seed switch': Timer(200),
			'fertilizer use': Timer(350, self.use_fertilizer),
			'fertilizer switch': Timer(200),
			'irrigation switch': Timer(200),
			'equipment place': Timer(350, self.place_equipment),
			'equipment switch': Timer(200),
			'drip_place': Timer(350),  # Drip irrigation placement cooldown
		}

		self.tools = ['hoe','axe','water']
		self.tool_index = 0
		self.selected_tool = self.tools[self.tool_index]

		self.seeds = ['corn', 'tomato', 'wheat', 'carrot', 'potato']
		self.seed_index = 0
		self.selected_seed = self.seeds[self.seed_index]

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
		self.fertilizers = ['compost', 'bone_meal', 'fish_emulsion', 'blood_meal', 'wood_ash', 'npk_10_10_10', 'npk_5_10_10', 'urea']
		self.fertilizer_index = 0
		self.selected_fertilizer = self.fertilizers[self.fertilizer_index]
		
		self.irrigation_modes = ['manual', 'efficient', 'drip']
		self.irrigation_index = 0
		self.selected_irrigation = self.irrigation_modes[self.irrigation_index]
		
		self.water_reserve = INITIAL_WATER_RESERVE
		self.base_max_water_reserve = MAX_WATER_RESERVE

		self.max_water_reserve = self.base_max_water_reserve
		self.water_tank_bonus = 0 # Updates from placed water tanks
		
		self.rain_tank = RainTank(capacity=100)
		
		self.equipment_inventory = {
			'drip_emitter': 0,
			'water_tank': 0
		}
		self.equipment_types = ['drip_emitter', 'water_tank']
		self.equipment_index = 0
		self.selected_equipment = self.equipment_types[self.equipment_index]
		
		self.drip_irrigation_count = 0
		
		self.money = 200

		self.tree_sprites = tree_sprites
		self.interaction = interaction
		self.sleep = False
		self.soil_layer = soil_layer
		self.toggle_shop = toggle_shop
		
		self.learning_system = None
		
		self.fatigue = 0 # 0 = rested, >0 = tired
		
		self.water_skill_level = 0  # 0 = not unlocked, 1-3 = unlocked levels
		self.water_skill_capacities = {0: 50, 1: 100, 2: 150, 3: 200}
		
		self.speed_skill_level = 0  # 0 = not unlocked, 1-3 = unlocked levels
		self.base_speed = 200  # Base speed at level 0
		self.speed_multipliers = {0: 1.0, 1: 1.1, 2: 1.2, 3: 1.3}  # 100%, 110%, 120%, 130%
		
		self.drip_irrigation_unlocked = False
		
		if hasattr(self, 'apply_skill_effects'):
			self.apply_skill_effects()

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
			water_cost = IRRIGATION_DATA[self.selected_irrigation]['water_cost']
			
			used_rain_tank = False
			if self.rain_tank.use_water(water_cost):
				used_rain_tank = True
				if self.learning_system:
					pass
			
			if used_rain_tank or self.water_reserve >= water_cost:
				if not used_rain_tank:
					self.water_reserve -= water_cost
				
				self.soil_layer.water(self.target_pos)
				self.watering.play()
				
				if self.learning_system and used_rain_tank:
					pass
			else:
				if self.learning_system:
					self.learning_system.add_notification("No water!")

	def get_target_pos(self):

		self.target_pos = self.rect.center + PLAYER_TOOL_OFFSET[self.status.split('_')[0]]

	def use_seed(self):
		if self.seed_inventory[self.selected_seed] > 0:
			self.soil_layer.plant_seed(self.target_pos, self.selected_seed)
			self.seed_inventory[self.selected_seed] -= 1
		else:
			if self.learning_system:
				self.learning_system.add_notification(f"No {self.selected_seed} seeds!")
	
	def use_fertilizer(self):
		if self.fertilizer_inventory[self.selected_fertilizer] > 0:
			if self.soil_layer.apply_fertilizer(self.target_pos, self.selected_fertilizer):
				self.fertilizer_inventory[self.selected_fertilizer] -= 1
				
				if self.learning_system and self.selected_fertilizer in ['compost', 'bone_meal', 'fish_emulsion', 'blood_meal', 'wood_ash']:
					self.learning_system.organic_fertilizer_count += 1
		else:
			if self.learning_system:
				fert_name = FERTILIZER_DATA[self.selected_fertilizer]['name']
				self.learning_system.add_notification(f"No {fert_name}!")
	
	def place_equipment(self):
		from knowledge_base import EQUIPMENT_DATA
		
		equip_type = self.selected_equipment
		if self.equipment_inventory.get(equip_type, 0) <= 0:
			if self.learning_system:
				equip_name = EQUIPMENT_DATA[equip_type]['name']
				self.learning_system.add_notification(f"No {equip_name} in inventory!")
			return
		
		equip_data = EQUIPMENT_DATA[equip_type]
		
		if equip_type == 'drip_emitter':
			if self.soil_layer.place_drip_irrigation(self.target_pos, self):
				self.equipment_inventory[equip_type] -= 1
				if self.learning_system:
					self.learning_system.add_notification("🌊 Drip emitter placed!")
			else:
				if self.learning_system:
					self.learning_system.add_notification("Can only place on tilled soil!")
		
		elif equip_type == 'water_tank':
			if hasattr(self, 'place_tank_callback') and self.place_tank_callback:
				self.place_tank_callback(self.target_pos)
				self.equipment_inventory[equip_type] -= 1
				if self.learning_system:
					self.learning_system.add_notification("💧 Water tank placed!")
	
	def collect_rainwater(self, amount=5):
		collected = self.rain_tank.collect_rain(amount * 2) # Tank collects more efficiently
		
		self.water_reserve = min(self.max_water_reserve, self.water_reserve + amount)
		
		if self.learning_system:
			self.learning_system.add_notification(f"💧 Rain Tank filled: {int(self.rain_tank.get_fill_percentage()*100)}%")
	
	def get_unlocked_irrigation_modes(self):
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

	def apply_skill_effects(self):
		base_capacity = self.water_skill_capacities.get(self.water_skill_level, 50)
		tank_bonus = getattr(self, 'water_tank_bonus', 0)
		self.max_water_reserve = base_capacity + tank_bonus
		
		if self.water_reserve > self.max_water_reserve:
			self.water_reserve = self.max_water_reserve
		
		multiplier = self.speed_multipliers.get(self.speed_skill_level, 1.0)
		self.speed = int(self.base_speed * multiplier)
			
		if hasattr(self, 'fatigue') and self.fatigue > 0:
			self.speed *= 0.8 # Sluggish

	def input(self):
		keys = pygame.key.get_pressed()

		if not self.timers['tool use'].active and not self.sleep:
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

			if keys[pygame.K_SPACE]:
				self.timers['tool use'].activate()
				self.direction = pygame.math.Vector2()
				self.frame_index = 0

			if keys[pygame.K_q] and not self.timers['tool switch'].active:
				self.timers['tool switch'].activate()
				self.tool_index += 1
				self.tool_index = self.tool_index if self.tool_index < len(self.tools) else 0
				self.selected_tool = self.tools[self.tool_index]

			if keys[pygame.K_LCTRL]:
				self.timers['seed use'].activate()
				self.direction = pygame.math.Vector2()
				self.frame_index = 0

			if keys[pygame.K_e] and not self.timers['seed switch'].active:
				self.timers['seed switch'].activate()
				self.seed_index += 1
				self.seed_index = self.seed_index if self.seed_index < len(self.seeds) else 0
				self.selected_seed = self.seeds[self.seed_index]
			
			if keys[pygame.K_f] and not self.timers['fertilizer switch'].active:
				self.timers['fertilizer switch'].activate()
				self.fertilizer_index += 1
				self.fertilizer_index = self.fertilizer_index if self.fertilizer_index < len(self.fertilizers) else 0
				self.selected_fertilizer = self.fertilizers[self.fertilizer_index]
			
			if keys[pygame.K_r] and not self.timers['fertilizer use'].active:
				self.timers['fertilizer use'].activate()
				self.direction = pygame.math.Vector2()
				self.frame_index = 0
			
			if keys[pygame.K_g] and not self.timers['drip_place'].active:
				self.timers['drip_place'].activate()  # Prevent spam
				if self.drip_irrigation_count > 0:
					target_pos = self.rect.center + PLAYER_TOOL_OFFSET[self.status.split('_')[0]]
					self.soil_layer.place_drip_irrigation(target_pos, self)
				elif self.learning_system:
					self.learning_system.add_notification("No drip irrigation setups! Buy from shop.")
			
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
	


	def get_status(self):
		
		if self.direction.magnitude() == 0:
			self.status = self.status.split('_')[0] + '_idle'

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

		if self.direction.magnitude() > 0:
			self.direction = self.direction.normalize()

		self.pos.x += self.direction.x * self.speed * dt
		self.hitbox.centerx = round(self.pos.x)
		self.rect.centerx = self.hitbox.centerx
		self.collision('horizontal')

		self.pos.y += self.direction.y * self.speed * dt
		self.hitbox.centery = round(self.pos.y)
		self.rect.centery = self.hitbox.centery
		self.collision('vertical')

	def update(self, dt):
		self.input()
		self.get_status()
		self.update_timers()
		self.get_target_pos()
		self.apply_skill_effects()
		self.move(dt)
		self.animate(dt)
