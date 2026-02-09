import pygame 
from settings import *
from support import import_folder
from sprites import Generic
from random import randint, choice

class Sky:
	def __init__(self):
		self.display_surface = pygame.display.get_surface()
		self.full_surf = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))
		self.day_color = [255,255,255]  # Bright day
		self.night_color = (38,101,189)  # Dark night
		self.current_color = [255,255,255]
		
		self.bright_day_duration = 90000   # Stay bright (1:30)
		self.sunset_duration = 30000       # Darken (0:30)
		self.dark_night_duration = 90000   # Stay dark (1:30)
		self.sunrise_duration = 30000      # Brighten (0:30)
		
		self.phase_start_time = pygame.time.get_ticks()
		self.current_phase = 'day'  # 'day', 'sunset', 'night', 'sunrise'
		self.night_complete = False
	
	def display(self, dt):
		current_time = pygame.time.get_ticks()
		elapsed = current_time - self.phase_start_time
		
		if self.current_phase == 'day':
			self.current_color = [255, 255, 255]
			if elapsed >= self.bright_day_duration:
				self.current_phase = 'sunset'
				self.phase_start_time = current_time
		
		elif self.current_phase == 'sunset':
			progress = min(1.0, elapsed / self.sunset_duration)
			for index, value in enumerate(self.night_color):
				self.current_color[index] = 255 - (255 - value) * progress
			if elapsed >= self.sunset_duration:
				self.current_phase = 'night'
				self.phase_start_time = current_time
		
		elif self.current_phase == 'night':
			for index, value in enumerate(self.night_color):
				self.current_color[index] = value
			if elapsed >= self.dark_night_duration:
				self.current_phase = 'sunrise'
				self.phase_start_time = current_time
		
		elif self.current_phase == 'sunrise':
			progress = min(1.0, elapsed / self.sunrise_duration)
			for index, value in enumerate(self.night_color):
				self.current_color[index] = value + (255 - value) * progress
			if elapsed >= self.sunrise_duration:
				self.current_phase = 'day'
				self.phase_start_time = current_time
				self.night_complete = True  # Signal new day
		
		self.full_surf.fill(self.current_color)
		self.display_surface.blit(self.full_surf, (0,0), special_flags = pygame.BLEND_RGBA_MULT)
	
	def reset_cycle(self):
		self.current_color = [255, 255, 255]
		self.phase_start_time = pygame.time.get_ticks()
		self.current_phase = 'day'
		self.night_complete = False

class Drop(Generic):
	def __init__(self, surf, pos, moving, groups, z):
		
		super().__init__(pos, surf, groups, z)
		self.lifetime = randint(400,500)
		self.start_time = pygame.time.get_ticks()

		self.moving = moving
		if self.moving:
			self.pos = pygame.math.Vector2(self.rect.topleft)
			self.direction = pygame.math.Vector2(-2,4)
			self.speed = randint(200,250)

	def update(self,dt):
		if self.moving:
			self.pos += self.direction * self.speed * dt
			self.rect.topleft = (round(self.pos.x), round(self.pos.y))

		if pygame.time.get_ticks() - self.start_time >= self.lifetime:
			self.kill()

class Rain:
	def __init__(self, all_sprites):
		self.all_sprites = all_sprites
		self.rain_drops = import_folder('./graphics/rain/drops/')
		self.rain_floor = import_folder('./graphics/rain/floor/')
		self.floor_w, self.floor_h =  pygame.image.load('./graphics/world/ground.png').get_size()

	def create_floor(self):
		Drop(
			surf = choice(self.rain_floor), 
			pos = (randint(0,self.floor_w),randint(0,self.floor_h)), 
			moving = False, 
			groups = self.all_sprites, 
			z = LAYERS['rain floor'])

	def create_drops(self):
		Drop(
			surf = choice(self.rain_drops), 
			pos = (randint(0,self.floor_w),randint(0,self.floor_h)), 
			moving = True, 
			groups = self.all_sprites, 
			z = LAYERS['rain drops'])

	def update(self):
		self.create_floor()
		self.create_drops()