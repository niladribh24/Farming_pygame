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

class DripIrrigationSetup(pygame.sprite.Sprite):
	"""A 2x2 tile (128x128 pixel) drip irrigation system that auto-waters covered tiles"""
	def __init__(self, pos, groups):
		super().__init__(groups)
		# Load and scale image to 2x2 tiles (TILE_SIZE * 2 = 128 pixels)
		size = TILE_SIZE * 2  # 128 pixels for 2x2 tiles
		try:
			original = pygame.image.load('./graphics/objects/drip_irrigation.png').convert_alpha()
			self.image = pygame.transform.scale(original, (size, size))
		except:
			# Fallback if image not found
			self.image = pygame.Surface((size, size), pygame.SRCALPHA)
			pygame.draw.rect(self.image, (139, 90, 43), (0, 30, size, 8))
			pygame.draw.rect(self.image, (139, 90, 43), (0, 90, size, 8))
			pygame.draw.rect(self.image, (139, 90, 43), (30, 0, 8, size))
			pygame.draw.rect(self.image, (139, 90, 43), (90, 0, 8, size))
		
		self.rect = self.image.get_rect(topleft=pos)
		self.z = LAYERS['main']  # Above soil
		
		# Store grid position (top-left tile)
		self.grid_x = pos[0] // TILE_SIZE
		self.grid_y = pos[1] // TILE_SIZE
	
	def get_covered_tiles(self):
		"""Return list of (x, y) tile coordinates this setup covers"""
		return [
			(self.grid_x, self.grid_y),
			(self.grid_x + 1, self.grid_y),
			(self.grid_x, self.grid_y + 1),
			(self.grid_x + 1, self.grid_y + 1)
		]

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
		
		# Fertilizer tracking for double yield
		self.fertilized_days = 0  # Days fertilized during growth
		self.total_grow_days = 0  # Total days of growth

		# sprite setup
		self.image = self.frames[self.age]
		self.y_offset = -16 if plant_type == 'corn' else -8
		self.rect = self.image.get_rect(midbottom = soil.rect.midbottom + pygame.math.Vector2(0,self.y_offset))
		self.z = LAYERS['ground plant']

	def grow(self):
		if self.check_watered(self.rect.center):
			self.age += self.grow_speed
			self.total_grow_days += 1  # Track total days of growth

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
		self.drip_irrigation_sprites = pygame.sprite.Group()  # Drip irrigation setups

		# graphics
		self.soil_surfs = import_folder_dict('./graphics/soil/')
		self.water_surfs = import_folder('./graphics/soil_water')

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
		
		# 2D Array - Fertilized Today Grid (tracks if tile was fertilized this day)
		self.fertilized_today_grid = [[False for col in range(h_tiles)] for row in range(v_tiles)]
		
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
					# Set initial tile health to 10% when tilled
					self.soil_health_grid[y][x] = 10
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

	def _force_plant(self, soil_sprite, seed, age, harvestable, unwatered_days=0, fertilized_days=0, total_grow_days=0):
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
		plant.fertilized_days = fertilized_days
		plant.total_grow_days = total_grow_days
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
		# Kill all existing soil sprites (removes from ALL groups they're in)
		for sprite in self.soil_sprites.sprites():
			sprite.kill()
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
		x = pos[0] // TILE_SIZE
		y = pos[1] // TILE_SIZE
		if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
			return self.soil_health_grid[y][x]
		return INITIAL_SOIL_HEALTH
	
	def is_tile_tilled(self, pos):
		"""Check if tile at position is tilled (has 'X' in grid).
		Also untills tiles that have 0% health."""
		x = pos[0] // TILE_SIZE
		y = pos[1] // TILE_SIZE
		if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
			if 'X' in self.grid[y][x]:
				# Check if tile should be untilled due to 0% health
				if self.soil_health_grid[y][x] <= 0:
					self._untill_tile(x, y)
					self.create_soil_tiles()  # Update visuals immediately
					return False
				return True
		return False
	
	def calculate_yield_modifier(self, pos):
		"""Calculate yield modifier based on soil health at position"""
		health = self.get_tile_soil_health(pos)
		return health / 50.0  # 50 = 100% yield, 100 = 200%, 0 = 0%
	
	def reset_daily_water_counts(self):
		"""Reset water counts at end of day and evaluate watering.
		Also applies -5% tile health decay for unfertilized tiles."""
		tiles_to_untill = []
		
		for row_idx in range(self.grid_height):
			for col_idx in range(self.grid_width):
				water_count = self.water_count_grid[row_idx][col_idx]
				
				# Only evaluate tiles that were worked on (tilled)
				if 'X' in self.grid[row_idx][col_idx]:
					if water_count == 1 or water_count == 2:
						# Correct watering
						if self.learning_system:
							self.apply_soil_impact(col_idx, row_idx, 'correct_water')
					elif water_count == 0 and 'P' in self.grid[row_idx][col_idx]:
						# Under-watering (planted but not watered), UNLESS it's raining
						if self.learning_system and not self.raining:
							self.apply_soil_impact(col_idx, row_idx, 'under_water')
					
					# Daily tile health decay if NOT fertilized today
					if not self.fertilized_today_grid[row_idx][col_idx]:
						self.soil_health_grid[row_idx][col_idx] -= 5  # -5% daily decay
						
						# Check if tile should become untilled
						if self.soil_health_grid[row_idx][col_idx] <= 0:
							tiles_to_untill.append((col_idx, row_idx))
				
				# Reset water count
				self.water_count_grid[row_idx][col_idx] = 0
				
				# Reset fertilized today flag
				self.fertilized_today_grid[row_idx][col_idx] = False
		
		# Untill ALL depleted tiles (check every tilled tile, not just decayed)
		for row_idx in range(self.grid_height):
			for col_idx in range(self.grid_width):
				if 'X' in self.grid[row_idx][col_idx] and self.soil_health_grid[row_idx][col_idx] <= 0:
					tiles_to_untill.append((col_idx, row_idx))
		
		# Remove duplicates and untill
		tiles_untilled = set(tiles_to_untill)
		for x, y in tiles_untilled:
			self._untill_tile(x, y)
			if self.learning_system:
				self.learning_system.add_notification("⚠️ A tile was depleted and returned to grass.")
		
		# Recreate soil tiles ONCE after all untilling is done
		if tiles_untilled:
			self.create_soil_tiles()
	
	def apply_fertilizer(self, target_pos, fertilizer_type):
		"""
		Apply fertilizer to a soil tile.
		Right fertilizer: +10% tile health, score bonus
		Wrong fertilizer: -10% tile health
		Tracks fertilized_today for double yield calculation.
		Returns True if successful, False otherwise.
		"""
		from knowledge_base import FERTILIZER_DATA, CROP_DATA
		
		for soil_sprite in self.soil_sprites.sprites():
			if soil_sprite.rect.collidepoint(target_pos):
				x = soil_sprite.rect.x // TILE_SIZE
				y = soil_sprite.rect.y // TILE_SIZE
				
				# Get fertilizer data
				fert_data = FERTILIZER_DATA.get(fertilizer_type, {})
				score_effect = fert_data.get('score_effect', 0)
				
				# Check if right or wrong fertilizer for current crop
				current_crop = self.last_crop_grid[y][x]
				is_right_fertilizer = False
				
				if current_crop:
					# Get crop's best fertilizer list
					crop_data = CROP_DATA.get(current_crop, {})
					best_fertilizers = crop_data.get('best_fertilizer', [])
					is_right_fertilizer = fertilizer_type in best_fertilizers
				
				# Apply tile health change: +10% for right, -10% for wrong
				if is_right_fertilizer:
					health_change = 10
					msg = f"✔ Right fertilizer for {current_crop.capitalize()}! +10% tile health"
					bonus_score = 5
				elif current_crop:
					# Wrong fertilizer for the crop
					health_change = -10
					msg = f"✖ Wrong fertilizer for {current_crop.capitalize()}! -10% tile health"
					bonus_score = 0
				else:
					# No crop planted - fertilizer still adds health
					health_change = 10
					msg = f"Applied fertilizer (+10% tile health)"
					bonus_score = 0
				
				# Update tile health
				self.soil_health_grid[y][x] = max(MIN_SOIL_HEALTH,
					min(MAX_SOIL_HEALTH, self.soil_health_grid[y][x] + health_change))
				
				# Mark tile as fertilized today (for double yield and daily decay)
				self.fertilized_today_grid[y][x] = True
				
				# Check if tile should become untilled (0% health)
				if self.soil_health_grid[y][x] <= 0:
					self._untill_tile(x, y)
					if self.learning_system:
						self.learning_system.add_notification("⚠️ Tile depleted! Returned to grass.")
					return True
				
				# Update plant's fertilized_days counter
				if 'P' in self.grid[y][x]:
					for plant in self.plant_sprites.sprites():
						if plant.soil == soil_sprite:
							plant.fertilized_days += 1
							break
				
				# Log to learning system
				if self.learning_system:
					self.learning_system.add_notification(msg)
					self.learning_system.total_score += score_effect + bonus_score
				
				return True
		return False
	
	def _untill_tile(self, x, y):
		"""Convert a tilled tile back to untilled grass"""
		# Remove 'X' (tilled) marker
		if 'X' in self.grid[y][x]:
			self.grid[y][x].remove('X')
		
		# Remove 'W' (watered) marker
		if 'W' in self.grid[y][x]:
			self.grid[y][x].remove('W')
		
		# Remove 'P' (planted) marker and kill any plant
		if 'P' in self.grid[y][x]:
			self.grid[y][x].remove('P')
			# Kill plant on this tile
			for plant in self.plant_sprites.sprites():
				if plant.soil.rect.x // TILE_SIZE == x and plant.soil.rect.y // TILE_SIZE == y:
					plant.kill()
					break
		
		# Reset tile health to 0
		self.soil_health_grid[y][x] = 0
	
	def place_drip_irrigation(self, target_pos, player):
		"""Place a drip irrigation setup at the target position (2x2 tiles).
		Returns True if placed successfully, False otherwise."""
		# Get tile coordinates
		x = int(target_pos[0] // TILE_SIZE)
		y = int(target_pos[1] // TILE_SIZE)
		
		# Check if player has drip setups available
		if player.drip_irrigation_count <= 0:
			return False
		
		# Check if all 4 tiles are within bounds
		if x + 1 >= self.grid_width or y + 1 >= self.grid_height:
			if self.learning_system:
				self.learning_system.add_notification("Can't place here - out of bounds!")
			return False
		
		# Check if all 4 tiles are farmable (tillable land)
		tiles_to_check = [(x, y), (x+1, y), (x, y+1), (x+1, y+1)]
		for tx, ty in tiles_to_check:
			if 'F' not in self.grid[ty][tx]:
				if self.learning_system:
					self.learning_system.add_notification("Can only place on tillable farmland!")
				return False
		
		# Check if any of the 4 tiles already have drip irrigation
		for drip in self.drip_irrigation_sprites.sprites():
			for (dx, dy) in drip.get_covered_tiles():
				if (dx == x or dx == x + 1) and (dy == y or dy == y + 1):
					if self.learning_system:
						self.learning_system.add_notification("Drip irrigation already placed here!")
					return False  # Overlapping
		
		# Place the drip irrigation setup
		pixel_x = x * TILE_SIZE
		pixel_y = y * TILE_SIZE
		DripIrrigationSetup((pixel_x, pixel_y), [self.all_sprites, self.drip_irrigation_sprites])
		
		# Use one from inventory
		player.drip_irrigation_count -= 1
		
		if self.learning_system:
			self.learning_system.add_notification("Drip irrigation placed! Will auto-water 4 tiles daily.")
		
		return True
	
	def remove_drip_irrigation(self, target_pos, player):
		"""Remove a drip irrigation setup at the target position.
		Returns True if removed, False if none found."""
		x = int(target_pos[0] // TILE_SIZE)
		y = int(target_pos[1] // TILE_SIZE)
		
		for drip in self.drip_irrigation_sprites.sprites():
			if (drip.grid_x, drip.grid_y) == (x, y) or \
			   (drip.grid_x + 1, drip.grid_y) == (x, y) or \
			   (drip.grid_x, drip.grid_y + 1) == (x, y) or \
			   (drip.grid_x + 1, drip.grid_y + 1) == (x, y):
				drip.kill()
				player.drip_irrigation_count += 1  # Return to inventory
				if self.learning_system:
					self.learning_system.add_notification("Drip irrigation removed and returned to inventory.")
				return True
		return False
	
	def auto_water_drip_tiles(self):
		"""Water all tiles covered by drip irrigation systems (called on new day, unless raining)"""
		watered_count = 0
		for drip in self.drip_irrigation_sprites.sprites():
			for (x, y) in drip.get_covered_tiles():
				if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
					# Only water tilled tiles with plants or just tilled
					if 'X' in self.grid[y][x]:
						pixel_x = x * TILE_SIZE
						pixel_y = y * TILE_SIZE
						# Add water if not already watered
						if 'W' not in self.grid[y][x]:
							self.grid[y][x].append('W')
							WaterTile(
								(pixel_x, pixel_y),
								choice(self.water_surfs),
								[self.all_sprites, self.water_sprites]
							)
							watered_count += 1
		return watered_count