import pygame
from settings import *
from pytmx.util_pygame import load_pygame
from support import *
from random import choice
from knowledge_base import CROP_DATA, SOIL_IMPACTS, INITIAL_SOIL_HEALTH, MIN_SOIL_HEALTH, MAX_SOIL_HEALTH

class SoilTile(pygame.sprite.Sprite):
	def __init__(self, pos, surf, groups):
		super().__init__(groups)
		self.image = surf
		self.rect = self.image.get_rect(topleft = pos)
		self.z = LAYERS['soil']

class WaterTile(pygame.sprite.Sprite):
	def __init__(self, pos, surf, groups):
		super().__init__(groups)
		self.image = surf
		self.rect = self.image.get_rect(topleft = pos)
		self.z = LAYERS['soil water']

class DripEmitter(pygame.sprite.Sprite):
	"""Drip irrigation emitter placed on soil tiles"""
	def __init__(self, pos, surf, groups):
		super().__init__(groups)
		self.image = surf
		self.rect = self.image.get_rect(topleft = pos)
		self.z = LAYERS['ground plant']  # Same layer as plants so it overlays nicely

class Plant(pygame.sprite.Sprite):
	def __init__(self, plant_type, groups, soil, check_watered):
		super().__init__(groups)
		
		# setup
		self.soil = soil
		self.check_watered = check_watered
		
		# Growth attributes
		self.plant_type = plant_type
		self.frames = import_folder(f'./graphics/fruit/{plant_type}')
		self.age = 0
		self.max_age = len(self.frames) - 1
		self.grow_speed = GROW_SPEED[plant_type]
		self.harvestable = False
		self.unwatered_days = 0

		# sprite setup
		self.image = self.frames[self.age]
		self.y_offset = -16 if plant_type == 'corn' else -8
		self.rect = self.image.get_rect(midbottom = soil.rect.midbottom + pygame.math.Vector2(0,self.y_offset))
		self.z = LAYERS['ground plant']

	def grow(self):
		if self.check_watered(self.rect.center):
			self.age += self.grow_speed

			if int(self.age) > 0:
				self.z = LAYERS['main']
				self.hitbox = self.rect.copy().inflate(-26,-self.rect.height * 0.4)

			if self.age >= self.max_age:
				self.age = self.max_age
				self.harvestable = True

			self.image = self.frames[int(self.age)]
			self.rect = self.image.get_rect(midbottom = self.soil.rect.midbottom + pygame.math.Vector2(0,self.y_offset))

class SoilLayer:
	def __init__(self, all_sprites, collision_sprites):

		# sprite groups
		self.all_sprites = all_sprites
		self.collision_sprites = collision_sprites
		self.soil_sprites = pygame.sprite.Group()
		self.water_sprites = pygame.sprite.Group()
		self.plant_sprites = pygame.sprite.Group()
		self.drip_sprites = pygame.sprite.Group()  # FEATURE: Drip Emitters

		# graphics
		self.soil_surfs = import_folder_dict('./graphics/soil/')
		self.water_surfs = import_folder('./graphics/soil_water')
		
		# Drip emitter image - 2x2 tiles (Procedural Generation)
		# Drip size: 2x2 tiles = 128x128 pixels
		drip_size = TILE_SIZE * 2
		
		# Create surface with alpha channel and fill with transparent
		self.drip_surf = pygame.Surface((drip_size, drip_size), pygame.SRCALPHA)
		self.drip_surf.fill((0,0,0,0)) # Explicitly clear to transparent
		
		# Draw Pipe Grid Visual
		# Outer frame (pipes)
		color = (80, 80, 80) # Dark gray pipe
		width = 6
		pygame.draw.rect(self.drip_surf, color, (10, 10, drip_size-20, drip_size-20), width, 5)
		
		# Inner cross pipes
		pygame.draw.line(self.drip_surf, color, (drip_size//2, 10), (drip_size//2, drip_size-10), width)
		pygame.draw.line(self.drip_surf, color, (10, drip_size//2), (drip_size-10, drip_size//2), width)
		
		# Emitter nodes (blue dots)
		emitter_color = (100, 200, 255)
		centers = [
			(drip_size//4 + 2, drip_size//4 + 2),
			(drip_size*3//4 - 2, drip_size//4 + 2),
			(drip_size//4 + 2, drip_size*3//4 - 2),
			(drip_size*3//4 - 2, drip_size*3//4 - 2)
		]
		for center in centers:
			pygame.draw.circle(self.drip_surf, emitter_color, center, 6)
			pygame.draw.circle(self.drip_surf, (50, 50, 50), center, 6, 1)

		self.create_soil_grid()
		self.create_hit_rects()
		
		# Learning system reference (will be set by Level)
		self.learning_system = None

		# sounds
		self.hoe_sound = pygame.mixer.Sound('./audio/hoe.wav')
		self.hoe_sound.set_volume(0.1)

		self.plant_sound = pygame.mixer.Sound('./audio/plant.wav') 
		self.plant_sound.set_volume(0.2)

	def create_soil_grid(self):
		ground = pygame.image.load('./graphics/world/ground.png')
		h_tiles, v_tiles = ground.get_width() // TILE_SIZE, ground.get_height() // TILE_SIZE
		
		# Store dimensions for other grids
		self.grid_width = h_tiles
		self.grid_height = v_tiles
		
		# Original grid for tile states
		self.grid = [[[] for col in range(h_tiles)] for row in range(v_tiles)]
		
		# DATA STRUCTURE: 2D ARRAY - Soil Health Grid
		# Tracks soil health (0-100) per tile for consequence-based gameplay
		self.soil_health_grid = [[INITIAL_SOIL_HEALTH for col in range(h_tiles)] for row in range(v_tiles)]
		
		# 2D Array - Water Count Grid (for over-watering detection)
		self.water_count_grid = [[0 for col in range(h_tiles)] for row in range(v_tiles)]
		
		# 2D Array - Last Crop Grid (for monocropping detection)
		self.last_crop_grid = [[None for col in range(h_tiles)] for row in range(v_tiles)]
		
		# 2D Array - Drip Emitter Grid (tracks placed emitters)
		self.drip_emitter_grid = [[False for col in range(h_tiles)] for row in range(v_tiles)]
		
		for x, y, _ in load_pygame('./data/map.tmx').get_layer_by_name('Farmable').tiles():
			self.grid[y][x].append('F')

	def create_hit_rects(self):
		self.hit_rects = []
		for index_row, row in enumerate(self.grid):
			for index_col, cell in enumerate(row):
				if 'F' in cell:
					x = index_col * TILE_SIZE
					y = index_row * TILE_SIZE
					rect = pygame.Rect(x,y,TILE_SIZE, TILE_SIZE)
					self.hit_rects.append(rect)

	def get_hit(self, point):
		for rect in self.hit_rects:
			if rect.collidepoint(point):
				self.hoe_sound.play()

				x = rect.x // TILE_SIZE
				y = rect.y // TILE_SIZE

				if 'F' in self.grid[y][x]:
					self.grid[y][x].append('X')
					self.create_soil_tiles()
					if self.raining:
						self.water_all()

	def water(self, target_pos):
		for soil_sprite in self.soil_sprites.sprites():
			if soil_sprite.rect.collidepoint(target_pos):

				x = soil_sprite.rect.x // TILE_SIZE
				y = soil_sprite.rect.y // TILE_SIZE
				self.grid[y][x].append('W')
				
				# Track water count for this tile (for over-watering detection)
				self.water_count_grid[y][x] += 1
				
				# Check for over-watering consequence
				if self.learning_system and self.water_count_grid[y][x] > 2:
					self.apply_soil_impact(x, y, 'over_water')
					self.learning_system.overwatered_today = True
				elif self.learning_system and self.water_count_grid[y][x] == 1:
					# First water of the day - could be correct watering
					pass  # Evaluation happens at end of day

				pos = soil_sprite.rect.topleft
				surf = choice(self.water_surfs)
				WaterTile(pos, surf, [self.all_sprites, self.water_sprites])
				
				if self.learning_system:
					self.learning_system.watered_today = True

	def water_all(self):
		for index_row, row in enumerate(self.grid):
			for index_col, cell in enumerate(row):
				if 'X' in cell and 'W' not in cell:
					cell.append('W')
					x = index_col * TILE_SIZE
					y = index_row * TILE_SIZE
					WaterTile((x,y), choice(self.water_surfs), [self.all_sprites, self.water_sprites])
		
		# Rain counts as watering
		if self.learning_system:
			self.learning_system.watered_today = True

	def remove_water(self):

		# destroy all water sprites
		for sprite in self.water_sprites.sprites():
			sprite.kill()

		# clean up the grid
		for row in self.grid:
			for cell in row:
				if 'W' in cell:
					cell.remove('W')

	def check_watered(self, pos):
		x = pos[0] // TILE_SIZE
		y = pos[1] // TILE_SIZE
		cell = self.grid[y][x]
		is_watered = 'W' in cell
		return is_watered

	def plant_seed(self, target_pos, seed):
		for soil_sprite in self.soil_sprites.sprites():
			if soil_sprite.rect.collidepoint(target_pos):
				self.plant_sound.play()

				x = soil_sprite.rect.x // TILE_SIZE
				y = soil_sprite.rect.y // TILE_SIZE

				if 'P' not in self.grid[y][x]:
					# Check for monocropping (same crop planted repeatedly)
					last_crop = self.last_crop_grid[y][x]
					if self.learning_system:
						if last_crop and last_crop == seed:
							# Monocropping penalty
							self.apply_soil_impact(x, y, 'monocrop')
						elif last_crop and last_crop != seed:
							# Crop rotation bonus
							self.apply_soil_impact(x, y, 'rotation')
							self.learning_system.rotation_count += 1
					
					# Update last crop for this tile
					self.last_crop_grid[y][x] = seed
					
					self.grid[y][x].append('P')
					Plant(seed, [self.all_sprites, self.plant_sprites, self.collision_sprites], soil_sprite, self.check_watered)

	def _force_plant(self, soil_sprite, seed, age, harvestable, unwatered_days=0):
		"""Force create a plant at specific stage (for loading saves)"""
		x = soil_sprite.rect.x // TILE_SIZE
		y = soil_sprite.rect.y // TILE_SIZE
		
		# Ensure P flag is present
		if 'P' not in self.grid[y][x]:
			self.grid[y][x].append('P')
		
		# Create plant
		plant = Plant(seed, [self.all_sprites, self.plant_sprites, self.collision_sprites], soil_sprite, self.check_watered)
		plant.age = age
		plant.harvestable = harvestable
		
		# Update visual state based on age
		plant.image = plant.frames[int(plant.age)]
		plant.rect = plant.image.get_rect(midbottom = soil_sprite.rect.midbottom + pygame.math.Vector2(0, plant.y_offset))
		
		if int(plant.age) > 0:
			plant.z = LAYERS['main']
			plant.hitbox = plant.rect.copy().inflate(-26,-plant.rect.height * 0.4)
		
		plant.unwatered_days = unwatered_days
		return plant

	def update_plants(self):
		for plant in self.plant_sprites.sprites():
			# Check watering status before growing
			is_watered = self.check_watered(plant.rect.center)
			
			if is_watered:
				plant.unwatered_days = 0
				plant.grow()
			else:
				plant.unwatered_days += 1
				# Crop death logic (2 days without water)
				if plant.unwatered_days >= 2:
					# Clean up grid
					x = plant.rect.centerx // TILE_SIZE
					y = plant.rect.centery // TILE_SIZE
					if 'P' in self.grid[y][x]:
						self.grid[y][x].remove('P')
					
					# Kill plant
					plant.kill()

	def create_soil_tiles(self):
		self.soil_sprites.empty()
		for index_row, row in enumerate(self.grid):
			for index_col, cell in enumerate(row):
				if 'X' in cell:
					
					# tile options 
					t = 'X' in self.grid[index_row - 1][index_col]
					b = 'X' in self.grid[index_row + 1][index_col]
					r = 'X' in row[index_col + 1]
					l = 'X' in row[index_col - 1]

					tile_type = 'o'

					# all sides
					if all((t,r,b,l)): tile_type = 'x'

					# horizontal tiles only
					if l and not any((t,r,b)): tile_type = 'r'
					if r and not any((t,l,b)): tile_type = 'l'
					if r and l and not any((t,b)): tile_type = 'lr'

					# vertical only 
					if t and not any((r,l,b)): tile_type = 'b'
					if b and not any((r,l,t)): tile_type = 't'
					if b and t and not any((r,l)): tile_type = 'tb'

					# corners 
					if l and b and not any((t,r)): tile_type = 'tr'
					if r and b and not any((t,l)): tile_type = 'tl'
					if l and t and not any((b,r)): tile_type = 'br'
					if r and t and not any((b,l)): tile_type = 'bl'

					# T shapes
					if all((t,b,r)) and not l: tile_type = 'tbr'
					if all((t,b,l)) and not r: tile_type = 'tbl'
					if all((l,r,t)) and not b: tile_type = 'lrb'
					if all((l,r,b)) and not t: tile_type = 'lrt'

					SoilTile(
						pos = (index_col * TILE_SIZE,index_row * TILE_SIZE), 
						surf = self.soil_surfs[tile_type], 
						groups = [self.all_sprites, self.soil_sprites])

	# =========================================================================
	# LEARNING SYSTEM HELPER METHODS
	# =========================================================================
	
	def apply_soil_impact(self, x, y, impact_type):
		"""Apply soil health change and log to learning system"""
		impact = SOIL_IMPACTS.get(impact_type, {})
		soil_change = impact.get('soil', 0)
		
		# Update soil health (clamped to 0-100)
		self.soil_health_grid[y][x] = max(MIN_SOIL_HEALTH, 
			min(MAX_SOIL_HEALTH, self.soil_health_grid[y][x] + soil_change))
		
		# Log to learning system
		if self.learning_system:
			self.learning_system.log_action(impact_type)
	
	def get_average_soil_health(self):
		"""Calculate average soil health across all farmable tiles"""
		total_health = 0
		tile_count = 0
		for row_idx, row in enumerate(self.grid):
			for col_idx, cell in enumerate(row):
				if 'F' in cell:  # Only count farmable tiles
					total_health += self.soil_health_grid[row_idx][col_idx]
					tile_count += 1
		return total_health / tile_count if tile_count > 0 else INITIAL_SOIL_HEALTH
	
	def get_tile_soil_health(self, pos):
		"""Get soil health at a specific position"""
		x = int(pos[0] // TILE_SIZE)
		y = int(pos[1] // TILE_SIZE)
		if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
			return self.soil_health_grid[y][x]
		return INITIAL_SOIL_HEALTH
	
	def place_drip_emitter(self, target_pos):
		"""Place a drip emitter covering 2x2 soil tiles"""
		for soil_sprite in self.soil_sprites.sprites():
			if soil_sprite.rect.collidepoint(target_pos):
				x = soil_sprite.rect.x // TILE_SIZE
				y = soil_sprite.rect.y // TILE_SIZE
				
				# Check bounds for 2x2 area
				if x + 1 >= self.grid_width or y + 1 >= self.grid_height:
					return False
				
				# Check if all 4 tiles are farmable soil ('F')
				if ('F' not in self.grid[y][x] or 
					'F' not in self.grid[y][x+1] or 
					'F' not in self.grid[y+1][x] or 
					'F' not in self.grid[y+1][x+1]):
					return False
				
				# Check if area is clear of existing emitters
				if (self.drip_emitter_grid[y][x] or 
					self.drip_emitter_grid[y][x+1] or 
					self.drip_emitter_grid[y+1][x] or 
					self.drip_emitter_grid[y+1][x+1]):
					return False
				
				# Place emitter
				self.drip_emitter_grid[y][x] = True
				self.drip_emitter_grid[y][x+1] = True
				self.drip_emitter_grid[y+1][x] = True
				self.drip_emitter_grid[y+1][x+1] = True
				
				DripEmitter(
					pos=(soil_sprite.rect.x, soil_sprite.rect.y),
					surf=self.drip_surf,
					groups=[self.all_sprites, self.drip_sprites]
				)
				return True
		return False
	
	def has_drip_emitter(self, pos):
		"""Check if tile has a drip emitter"""
		x = int(pos[0] // TILE_SIZE)
		y = int(pos[1] // TILE_SIZE)
		if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
			return self.drip_emitter_grid[y][x]
		return False
	
	def calculate_yield_modifier(self, pos):
		"""Calculate yield modifier based on soil health at position"""
		health = self.get_tile_soil_health(pos)
		return health / 50.0  # 50 = 100% yield, 100 = 200%, 0 = 0%
	
	def reset_daily_water_counts(self):
		"""Reset water counts at end of day and evaluate watering"""
		for row_idx in range(self.grid_height):
			for col_idx in range(self.grid_width):
				water_count = self.water_count_grid[row_idx][col_idx]
				
				# Only evaluate tiles that were worked on
				if 'X' in self.grid[row_idx][col_idx]:
					if water_count == 1 or water_count == 2:
						# Correct watering
						if self.learning_system:
							self.apply_soil_impact(col_idx, row_idx, 'correct_water')
					elif water_count == 0 and 'P' in self.grid[row_idx][col_idx]:
						# Under-watering (planted but not watered), UNLESS it's raining
						if self.learning_system and not self.raining:
							self.apply_soil_impact(col_idx, row_idx, 'under_water')
				
				# Reset water count
				self.water_count_grid[row_idx][col_idx] = 0
	
	def apply_fertilizer(self, target_pos, fertilizer_type):
		"""
		Apply fertilizer to a soil tile.
		Returns True if successful, False otherwise.
		"""
		from knowledge_base import FERTILIZER_DATA
		
		for soil_sprite in self.soil_sprites.sprites():
			if soil_sprite.rect.collidepoint(target_pos):
				x = soil_sprite.rect.x // TILE_SIZE
				y = soil_sprite.rect.y // TILE_SIZE
				
				# Get fertilizer effects
				fert_data = FERTILIZER_DATA.get(fertilizer_type, {})
				soil_effect = fert_data.get('soil_effect', 0)
				score_effect = fert_data.get('score_effect', 0)
				
				# Apply soil health change
				self.soil_health_grid[y][x] = max(MIN_SOIL_HEALTH,
					min(MAX_SOIL_HEALTH, self.soil_health_grid[y][x] + soil_effect))
				
				# Log to learning system
				if self.learning_system:
					bonus_score = 0
					bonus_msg = ""
					
					# Check for Plant and Bonus
					if 'P' in self.grid[y][x]:
						current_crop = self.last_crop_grid[y][x]
						best_for = fert_data.get('best_for', [])
						if current_crop in best_for:
							bonus_score = 5
							bonus_msg = f" Perfect for {current_crop.capitalize()}! (+{bonus_score})"
					
					if fertilizer_type == 'organic':
						self.learning_system.log_action('organic_fert', f'+{soil_effect} soil')
						self.learning_system.add_notification(f"🌿 Organic fertilizer applied{bonus_msg}")
					else:
						self.learning_system.log_action('chemical_fert', f'{soil_effect} soil')
						self.learning_system.add_notification(f"⚗️ Chemical fertilizer applied{bonus_msg}")
					
					self.learning_system.total_score += score_effect + bonus_score
				
				return True
		return False