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
	def __init__(self, pos, groups):
		super().__init__(groups)
		size = TILE_SIZE * 2  # 128 pixels for 2x2 tiles
		try:
			original = pygame.image.load('./graphics/objects/drip_irrigation.png').convert_alpha()
			self.image = pygame.transform.scale(original, (size, size))
		except:
			self.image = pygame.Surface((size, size), pygame.SRCALPHA)
			pygame.draw.rect(self.image, (139, 90, 43), (0, 30, size, 8))
			pygame.draw.rect(self.image, (139, 90, 43), (0, 90, size, 8))
			pygame.draw.rect(self.image, (139, 90, 43), (30, 0, 8, size))
			pygame.draw.rect(self.image, (139, 90, 43), (90, 0, 8, size))
		
		self.rect = self.image.get_rect(topleft=pos)
		self.z = LAYERS['main']  # Above soil
		
		self.grid_x = pos[0] // TILE_SIZE
		self.grid_y = pos[1] // TILE_SIZE
	
	def get_covered_tiles(self):
		return [
			(self.grid_x, self.grid_y),
			(self.grid_x + 1, self.grid_y),
			(self.grid_x, self.grid_y + 1),
			(self.grid_x + 1, self.grid_y + 1)
		]

class Plant(pygame.sprite.Sprite):
	def __init__(self, plant_type, groups, soil, check_watered):
		super().__init__(groups)
		
		self.soil = soil
		self.check_watered = check_watered
		
		self.plant_type = plant_type
		self.frames = import_folder(f'./graphics/fruit/{plant_type}')
		self.age = 0
		self.max_age = len(self.frames) - 1
		self.grow_speed = GROW_SPEED[plant_type]
		self.harvestable = False
		self.unwatered_days = 0
		
		self.fertilized_days = 0  # Days fertilized during growth
		self.total_grow_days = 0  # Total days of growth

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

		self.all_sprites = all_sprites
		self.collision_sprites = collision_sprites
		self.soil_sprites = pygame.sprite.Group()
		self.water_sprites = pygame.sprite.Group()
		self.plant_sprites = pygame.sprite.Group()
		self.drip_irrigation_sprites = pygame.sprite.Group()  # Drip irrigation setups

		self.soil_surfs = import_folder_dict('./graphics/soil/')
		self.water_surfs = import_folder('./graphics/soil_water')
		
		drip_size = TILE_SIZE * 2
		
		self.drip_surf = pygame.Surface((drip_size, drip_size), pygame.SRCALPHA)
		self.drip_surf.fill((0,0,0,0)) # Explicitly clear to transparent
		
		color = (80, 80, 80) # Dark gray pipe
		width = 6
		pygame.draw.rect(self.drip_surf, color, (10, 10, drip_size-20, drip_size-20), width, 5)
		
		pygame.draw.line(self.drip_surf, color, (drip_size//2, 10), (drip_size//2, drip_size-10), width)
		pygame.draw.line(self.drip_surf, color, (10, drip_size//2), (drip_size-10, drip_size//2), width)
		
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
		
		self.learning_system = None

		self.hoe_sound = pygame.mixer.Sound('./audio/hoe.wav')
		self.hoe_sound.set_volume(0.1)

		self.plant_sound = pygame.mixer.Sound('./audio/plant.wav') 
		self.plant_sound.set_volume(0.2)

	def create_soil_grid(self):
		ground = pygame.image.load('./graphics/world/ground.png')
		h_tiles, v_tiles = ground.get_width() // TILE_SIZE, ground.get_height() // TILE_SIZE
		
		self.grid_width = h_tiles
		self.grid_height = v_tiles
		
		self.grid = [[[] for col in range(h_tiles)] for row in range(v_tiles)]
		
		self.soil_health_grid = [[INITIAL_SOIL_HEALTH for col in range(h_tiles)] for row in range(v_tiles)]
		
		self.water_count_grid = [[0 for col in range(h_tiles)] for row in range(v_tiles)]
		
		self.last_crop_grid = [[None for col in range(h_tiles)] for row in range(v_tiles)]
		
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
				
				self.water_count_grid[y][x] += 1
				
				if self.learning_system and self.water_count_grid[y][x] > 2:
					self.apply_soil_impact(x, y, 'over_water')
					self.learning_system.overwatered_today = True
				elif self.learning_system and self.water_count_grid[y][x] == 1:
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
		
		if self.learning_system:
			self.learning_system.watered_today = True

	def remove_water(self):

		for sprite in self.water_sprites.sprites():
			sprite.kill()

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
					last_crop = self.last_crop_grid[y][x]
					if self.learning_system:
						if last_crop and last_crop == seed:
							self.apply_soil_impact(x, y, 'monocrop')
						elif last_crop and last_crop != seed:
							self.apply_soil_impact(x, y, 'rotation')
							self.learning_system.rotation_count += 1
					
					self.last_crop_grid[y][x] = seed
					
					self.grid[y][x].append('P')
					Plant(seed, [self.all_sprites, self.plant_sprites, self.collision_sprites], soil_sprite, self.check_watered)

	def _force_plant(self, soil_sprite, seed, age, harvestable, unwatered_days=0, fertilized_days=0, total_grow_days=0):
		x = soil_sprite.rect.x // TILE_SIZE
		y = soil_sprite.rect.y // TILE_SIZE
		
		if 'P' not in self.grid[y][x]:
			self.grid[y][x].append('P')
		
		plant = Plant(seed, [self.all_sprites, self.plant_sprites, self.collision_sprites], soil_sprite, self.check_watered)
		plant.age = age
		plant.harvestable = harvestable
		
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
			is_watered = self.check_watered(plant.rect.center)
			
			if is_watered:
				plant.unwatered_days = 0
				plant.grow()
			else:
				plant.unwatered_days += 1
				if plant.unwatered_days >= 2:
					x = plant.rect.centerx // TILE_SIZE
					y = plant.rect.centery // TILE_SIZE
					if 'P' in self.grid[y][x]:
						self.grid[y][x].remove('P')
					
					plant.kill()

	def create_soil_tiles(self):
		for sprite in self.soil_sprites.sprites():
			sprite.kill()
		self.soil_sprites.empty()
		for index_row, row in enumerate(self.grid):
			for index_col, cell in enumerate(row):
				if 'X' in cell:
					
					t = 'X' in self.grid[index_row - 1][index_col]
					b = 'X' in self.grid[index_row + 1][index_col]
					r = 'X' in row[index_col + 1]
					l = 'X' in row[index_col - 1]

					tile_type = 'o'

					if all((t,r,b,l)): tile_type = 'x'

					if l and not any((t,r,b)): tile_type = 'r'
					if r and not any((t,l,b)): tile_type = 'l'
					if r and l and not any((t,b)): tile_type = 'lr'

					if t and not any((r,l,b)): tile_type = 'b'
					if b and not any((r,l,t)): tile_type = 't'
					if b and t and not any((r,l)): tile_type = 'tb'

					if l and b and not any((t,r)): tile_type = 'tr'
					if r and b and not any((t,l)): tile_type = 'tl'
					if l and t and not any((b,r)): tile_type = 'br'
					if r and t and not any((b,l)): tile_type = 'bl'

					if all((t,b,r)) and not l: tile_type = 'tbr'
					if all((t,b,l)) and not r: tile_type = 'tbl'
					if all((l,r,t)) and not b: tile_type = 'lrb'
					if all((l,r,b)) and not t: tile_type = 'lrt'

					SoilTile(
						pos = (index_col * TILE_SIZE,index_row * TILE_SIZE), 
						surf = self.soil_surfs[tile_type], 
						groups = [self.all_sprites, self.soil_sprites])

	
	def apply_soil_impact(self, x, y, impact_type):
		impact = SOIL_IMPACTS.get(impact_type, {})
		soil_change = impact.get('soil', 0)
		
		self.soil_health_grid[y][x] = max(MIN_SOIL_HEALTH, 
			min(MAX_SOIL_HEALTH, self.soil_health_grid[y][x] + soil_change))
		
		if self.learning_system:
			self.learning_system.log_action(impact_type)
	
	def get_average_soil_health(self):
		total_health = 0
		tile_count = 0
		for row_idx, row in enumerate(self.grid):
			for col_idx, cell in enumerate(row):
				if 'F' in cell:  # Only count farmable tiles
					total_health += self.soil_health_grid[row_idx][col_idx]
					tile_count += 1
		return total_health / tile_count if tile_count > 0 else INITIAL_SOIL_HEALTH
	
	def get_tile_soil_health(self, pos):
		x = int(pos[0] // TILE_SIZE)
		y = int(pos[1] // TILE_SIZE)
		if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
			return self.soil_health_grid[y][x]
		return INITIAL_SOIL_HEALTH
	
	def is_tile_tilled(self, pos):
		x = pos[0] // TILE_SIZE
		y = pos[1] // TILE_SIZE
		if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
			if 'X' in self.grid[y][x]:
				if self.soil_health_grid[y][x] <= 0:
					self._untill_tile(x, y)
					self.create_soil_tiles()  # Update visuals immediately
					return False
				return True
		return False
	

	def calculate_yield_modifier(self, pos):
		health = self.get_tile_soil_health(pos)
		return health / 50.0  # 50 = 100% yield, 100 = 200%, 0 = 0%
	
	def reset_daily_water_counts(self):
		tiles_to_untill = []
		
		for row_idx in range(self.grid_height):
			for col_idx in range(self.grid_width):
				water_count = self.water_count_grid[row_idx][col_idx]
				
				if 'X' in self.grid[row_idx][col_idx]:
					if water_count == 1 or water_count == 2:
						if self.learning_system:
							self.apply_soil_impact(col_idx, row_idx, 'correct_water')
					elif water_count == 0 and 'P' in self.grid[row_idx][col_idx]:
						is_drip_covered = False
						for drip in self.drip_irrigation_sprites.sprites():
							if (col_idx, row_idx) in drip.get_covered_tiles():
								is_drip_covered = True
								break
						
						if self.learning_system and not self.raining and not is_drip_covered:
							self.apply_soil_impact(col_idx, row_idx, 'under_water')
					
					if not self.fertilized_today_grid[row_idx][col_idx]:
						self.soil_health_grid[row_idx][col_idx] -= 5  # -5% daily decay
						
						if self.soil_health_grid[row_idx][col_idx] <= 0:
							tiles_to_untill.append((col_idx, row_idx))
				
				self.water_count_grid[row_idx][col_idx] = 0
				
				self.fertilized_today_grid[row_idx][col_idx] = False
		
		for row_idx in range(self.grid_height):
			for col_idx in range(self.grid_width):
				if 'X' in self.grid[row_idx][col_idx] and self.soil_health_grid[row_idx][col_idx] <= 0:
					tiles_to_untill.append((col_idx, row_idx))
		
		tiles_untilled = set(tiles_to_untill)
		for x, y in tiles_untilled:
			self._untill_tile(x, y)
			if self.learning_system:
				self.learning_system.add_notification("⚠️ A tile was depleted and returned to grass.")
		
		if tiles_untilled:
			self.create_soil_tiles()
	
	def apply_fertilizer(self, target_pos, fertilizer_type):
		from knowledge_base import FERTILIZER_DATA, CROP_DATA
		
		for soil_sprite in self.soil_sprites.sprites():
			if soil_sprite.rect.collidepoint(target_pos):
				x = soil_sprite.rect.x // TILE_SIZE
				y = soil_sprite.rect.y // TILE_SIZE
				
				fert_data = FERTILIZER_DATA.get(fertilizer_type, {})
				score_effect = fert_data.get('score_effect', 0)
				
				current_crop = self.last_crop_grid[y][x]
				is_right_fertilizer = False
				
				if current_crop:
					crop_data = CROP_DATA.get(current_crop, {})
					best_fertilizers = crop_data.get('best_fertilizer', [])
					is_right_fertilizer = fertilizer_type in best_fertilizers
				
				if is_right_fertilizer:
					health_change = 10
					msg = f"✔ Right fertilizer for {current_crop.capitalize()}! +10% tile health"
					bonus_score = 5
				elif current_crop:
					health_change = -10
					msg = f"✖ Wrong fertilizer for {current_crop.capitalize()}! -10% tile health"
					bonus_score = 0
				else:
					health_change = 10
					msg = f"Applied fertilizer (+10% tile health)"
					bonus_score = 0
				
				self.soil_health_grid[y][x] = max(MIN_SOIL_HEALTH,
					min(MAX_SOIL_HEALTH, self.soil_health_grid[y][x] + health_change))
				
				self.fertilized_today_grid[y][x] = True
				
				if self.soil_health_grid[y][x] <= 0:
					self._untill_tile(x, y)
					if self.learning_system:
						self.learning_system.add_notification("⚠️ Tile depleted! Returned to grass.")
					return True
				
				if 'P' in self.grid[y][x]:
					for plant in self.plant_sprites.sprites():
						if plant.soil == soil_sprite:
							plant.fertilized_days += 1
							break
				
				if self.learning_system:
					self.learning_system.add_notification(msg)
					self.learning_system.total_score += score_effect + bonus_score
				
				return True
		return False
	
	def _untill_tile(self, x, y):
		if 'X' in self.grid[y][x]:
			self.grid[y][x].remove('X')
		
		if 'W' in self.grid[y][x]:
			self.grid[y][x].remove('W')
		
		if 'P' in self.grid[y][x]:
			self.grid[y][x].remove('P')
			for plant in self.plant_sprites.sprites():
				if plant.soil.rect.x // TILE_SIZE == x and plant.soil.rect.y // TILE_SIZE == y:
					plant.kill()
					break
		
		self.soil_health_grid[y][x] = 0
	
	def place_drip_irrigation(self, target_pos, player):
		x = int(target_pos[0] // TILE_SIZE)
		y = int(target_pos[1] // TILE_SIZE)
		
		if player.drip_irrigation_count <= 0:
			return False
		
		if x + 1 >= self.grid_width or y + 1 >= self.grid_height:
			if self.learning_system:
				self.learning_system.add_notification("Can't place here - out of bounds!")
			return False
		
		tiles_to_check = [(x, y), (x+1, y), (x, y+1), (x+1, y+1)]
		for tx, ty in tiles_to_check:
			if 'F' not in self.grid[ty][tx]:
				if self.learning_system:
					self.learning_system.add_notification("Can only place on tillable farmland!")
				return False
		
		for drip in self.drip_irrigation_sprites.sprites():
			for (dx, dy) in drip.get_covered_tiles():
				if (dx == x or dx == x + 1) and (dy == y or dy == y + 1):
					if self.learning_system:
						self.learning_system.add_notification("Drip irrigation already placed here!")
					return False  # Overlapping
		
		pixel_x = x * TILE_SIZE
		pixel_y = y * TILE_SIZE
		DripIrrigationSetup((pixel_x, pixel_y), [self.all_sprites, self.drip_irrigation_sprites])
		
		player.drip_irrigation_count -= 1
		
		if self.learning_system:
			self.learning_system.add_notification("Drip irrigation placed! Will auto-water 4 tiles daily.")
		
		return True
	
	def remove_drip_irrigation(self, target_pos, player):
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
		watered_count = 0
		for drip in self.drip_irrigation_sprites.sprites():
			for (x, y) in drip.get_covered_tiles():
				if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
					if 'X' in self.grid[y][x]:
						pixel_x = x * TILE_SIZE
						pixel_y = y * TILE_SIZE
						if 'W' not in self.grid[y][x]:
							self.grid[y][x].append('W')
							WaterTile(
								(pixel_x, pixel_y),
								choice(self.water_surfs),
								[self.all_sprites, self.water_sprites]
							)
							watered_count += 1
		return watered_count