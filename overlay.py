import pygame
import os
from settings import *
from knowledge_base import IRRIGATION_DATA


class Overlay:
	def __init__(self, player):

		# general setup
		self.display_surface = pygame.display.get_surface()
		self.player = player
		
		# Learning system reference (will be set by Level)
		self.learning_system = None
		self.soil_layer = None

		# imports 
		overlay_path = './graphics/overlay/'
		self.tools_surf = {tool: pygame.image.load(f'{overlay_path}{tool}.png').convert_alpha() for tool in player.tools}
		
		# Load seed images with fallbacks for missing files
		self.seeds_surf = {}
		for seed in player.seeds:
			img_path = f'{overlay_path}{seed}.png'
			if os.path.exists(img_path):
				self.seeds_surf[seed] = pygame.image.load(img_path).convert_alpha()
			else:
				# Create placeholder for missing seed images
				placeholder = pygame.Surface((64, 64), pygame.SRCALPHA)
				pygame.draw.circle(placeholder, (100, 200, 100), (32, 32), 28)
				font = pygame.font.Font(None, 24)
				text = font.render(seed[:3].upper(), True, (255, 255, 255))
				placeholder.blit(text, (32 - text.get_width()//2, 32 - text.get_height()//2))
				self.seeds_surf[seed] = placeholder
		
		# Font for learning system UI
		self.font = pygame.font.Font('./font/LycheeSoda.ttf', 24)
		self.small_font = pygame.font.Font('./font/LycheeSoda.ttf', 18)
		
		# Notification system
		self.notifications = []
		self.notification_timer = 0
		self.notification_duration = 3000  # 3 seconds

	def display(self):

		# tool
		tool_surf = self.tools_surf[self.player.selected_tool]
		tool_rect = tool_surf.get_rect(midbottom = OVERLAY_POSITIONS['tool'])
		self.display_surface.blit(tool_surf,tool_rect)

		# seeds
		seed_surf = self.seeds_surf[self.player.selected_seed]
		seed_rect = seed_surf.get_rect(midbottom = OVERLAY_POSITIONS['seed'])
		self.display_surface.blit(seed_surf,seed_rect)
		
		# Learning System UI
		self.display_soil_health()
		self.display_score()
		self.display_day()
		self.display_fertilizer()
		self.display_water_reserve()
		self.display_irrigation_mode()

		self.display_notifications()
		self.display_shop_prompt()
	
	def display_shop_prompt(self):
		"""Display welcome message when near shop"""
		# Find trader interaction
		if not hasattr(self, 'interaction_sprites'):
			return
			
		for interaction in self.interaction_sprites.sprites():
			if interaction.name == 'Trader':
				# Check distance
				dist = pygame.math.Vector2(interaction.rect.center) - pygame.math.Vector2(self.player.rect.center)
				if dist.magnitude() < 150:
					# Calculate camera offset (same as CameraGroup)
					offset_x = self.player.rect.centerx - SCREEN_WIDTH / 2
					offset_y = self.player.rect.centery - SCREEN_HEIGHT / 2
					
					# Convert world position to screen position
					screen_x = interaction.rect.centerx - offset_x
					screen_y = interaction.rect.top - offset_y
					
					# Dimensions
					rect_width = 280
					rect_height = 70
					rect_x = screen_x - rect_width // 2
					rect_y = screen_y - 90
					
					bg_color = 'White'
					border_color = 'Black'
					
					# Draw speech bubble tail (triangle pointing down)
					tail_points = [
						(screen_x - 10, rect_y + rect_height - 2),
						(screen_x + 10, rect_y + rect_height - 2),
						(screen_x, rect_y + rect_height + 15)
					]
					pygame.draw.polygon(self.display_surface, bg_color, tail_points)
					pygame.draw.polygon(self.display_surface, border_color, tail_points, 2)
					
					# Draw speech bubble body
					rect = pygame.Rect(rect_x, rect_y, rect_width, rect_height)
					pygame.draw.rect(self.display_surface, bg_color, rect, 0, 8)
					pygame.draw.rect(self.display_surface, border_color, rect, 2, 8)
					
					# Cover the line between box and tail
					cover_rect = pygame.Rect(screen_x - 8, rect_y + rect_height - 3, 16, 6)
					pygame.draw.rect(self.display_surface, bg_color, cover_rect)

					# Text Line 1 (Black)
					text_surf1 = self.font.render("Hi! Welcome to the shop!", False, 'Black')
					text_rect1 = text_surf1.get_rect(midtop=(rect.centerx, rect.top + 12))
					self.display_surface.blit(text_surf1, text_rect1)
					
					# Text Line 2 (Grey)
					text_surf2 = self.font.render("PRESS ENTER to trade", False, (100, 100, 100))
					text_rect2 = text_surf2.get_rect(midtop=(rect.centerx, rect.top + 38))
					self.display_surface.blit(text_surf2, text_rect2)
					
					return # Only one trader	
	def display_soil_health(self):
		"""Display tile health for the tile the player is standing on"""
		if not self.soil_layer:
			return
		
		# Get player's current position
		player_pos = self.player.rect.center
		
		# Check if player is on a tilled tile
		is_tilled = self.soil_layer.is_tile_tilled(player_pos)
		
		# Draw label
		label = self.font.render('Tile Health', False, 'White')
		label_rect = label.get_rect(topleft=SOIL_HEALTH_BAR_POS)
		self.display_surface.blit(label, label_rect)
		
		# Draw health bar background
		bar_x = SOIL_HEALTH_BAR_POS[0]
		bar_y = SOIL_HEALTH_BAR_POS[1] + 25
		bar_width = 200
		bar_height = 20
		
		# Background (dark)
		pygame.draw.rect(self.display_surface, (50, 50, 50), 
			(bar_x, bar_y, bar_width, bar_height), 0, 4)
		
		if is_tilled:
			# Get tile health
			health = self.soil_layer.get_tile_soil_health(player_pos)
			
			# Health fill (color changes based on health)
			health_percent = health / 100
			fill_width = int(bar_width * health_percent)
			
			# Color gradient: red (low) -> yellow (mid) -> green (high)
			if health < 30:
				color = (200, 50, 50)  # Red
			elif health < 60:
				color = (200, 200, 50)  # Yellow
			else:
				color = (50, 200, 50)  # Green
			
			if fill_width > 0:
				pygame.draw.rect(self.display_surface, color,
					(bar_x, bar_y, fill_width, bar_height), 0, 4)
			
			# Border
			pygame.draw.rect(self.display_surface, 'White',
				(bar_x, bar_y, bar_width, bar_height), 2, 4)
			
			# Health value text
			health_text = self.small_font.render(f'{int(health)}%', False, 'White')
			health_rect = health_text.get_rect(center=(bar_x + bar_width//2, bar_y + bar_height//2))
			self.display_surface.blit(health_text, health_rect)
		else:
			# Grass/untilled tile
			pygame.draw.rect(self.display_surface, (80, 120, 60),
				(bar_x, bar_y, bar_width, bar_height), 0, 4)
			pygame.draw.rect(self.display_surface, (100, 150, 80),
				(bar_x, bar_y, bar_width, bar_height), 2, 4)
			
			# Grass text
			grass_text = self.small_font.render('Grass', False, 'White')
			grass_rect = grass_text.get_rect(center=(bar_x + bar_width//2, bar_y + bar_height//2))
			self.display_surface.blit(grass_text, grass_rect)
	
	def display_score(self):
		"""Display current score"""
		if not self.learning_system:
			return
			
		score = self.learning_system.total_score
		score_text = self.font.render(f'Score: {score}', False, 'White')
		score_rect = score_text.get_rect(topright=(SCREEN_WIDTH - 20, 90))
		
		# Background
		bg_rect = score_rect.inflate(20, 10)
		pygame.draw.rect(self.display_surface, (0, 0, 0, 128), bg_rect, 0, 4)
		self.display_surface.blit(score_text, score_rect)
	
	def display_day(self):
		"""Display current day number"""
		if not self.learning_system:
			return
			
		day = self.learning_system.current_day
		weather = self.learning_system.get_current_weather()
		
		# Weather emoji
		weather_icons = {
			'rain': '🌧',
			'heatwave': '🔥',
			'drought': '☀',
			'normal': '⛅'
		}
		weather_icon = weather_icons.get(weather, '⛅')
		
		day_text = self.font.render(f'Day {day} {weather_icon}', False, 'White')
		day_rect = day_text.get_rect(topleft=DAY_DISPLAY_POS)
		
		# Background
		bg_rect = day_rect.inflate(20, 10)
		pygame.draw.rect(self.display_surface, (0, 0, 0, 128), bg_rect, 0, 4)
		self.display_surface.blit(day_text, day_rect)
	
	def display_fertilizer(self):
		"""Display selected fertilizer type"""
		# Position top-left below day
		fert_type = self.player.selected_fertilizer
		fert_count = self.player.fertilizer_inventory.get(fert_type, 0)
		
		# determine color based on type (just organic/chemical via simple check)
		# NO EXPLICIT LABELS
		# User requested uniform color
		
		# Icon based on type
		icon = '🌿' if fert_type in ['compost', 'bone_meal', 'fish_emulsion', 'blood_meal', 'wood_ash'] else '⚗️'
		color = (255, 255, 255) # White for all
		
		fert_text = self.small_font.render(f'{icon} {fert_type.title()}: {fert_count}', False, color)
		fert_rect = fert_text.get_rect(topleft=(20, 60))
		
		# Background
		bg_rect = fert_rect.inflate(10, 6)
			
		pygame.draw.rect(self.display_surface, (0, 0, 0, 150), bg_rect, 0, 4)
		self.display_surface.blit(fert_text, fert_rect)
	
	def display_water_reserve(self):
		"""Display water reserve amount"""
		reserve = self.player.water_reserve
		max_reserve = self.player.max_water_reserve
		
		# Position top-left below fertilizer
		reserve_text = self.small_font.render(f'💧 Water: {int(reserve)}/{max_reserve}', False, (100, 180, 255))
		reserve_rect = reserve_text.get_rect(topleft=(20, 95))
		
		# Background
		bg_rect = reserve_rect.inflate(10, 6)
		pygame.draw.rect(self.display_surface, (0, 0, 0, 150), bg_rect, 0, 4)
		self.display_surface.blit(reserve_text, reserve_rect)
	
	def display_irrigation_mode(self):
		"""Display current irrigation mode"""
		mode = self.player.selected_irrigation
		mode_data = IRRIGATION_DATA.get(mode, {})
		mode_name = mode_data.get('name', mode.title())
		
		# Check if mode is unlocked
		unlocked_modes = self.player.get_unlocked_irrigation_modes()
		is_unlocked = mode in unlocked_modes
		
		if is_unlocked:
			color = (100, 255, 200)
			text = f'🚿 {mode_name}'
		else:
			color = (150, 150, 150)
			text = f'🔒 {mode_name}'
		
		irr_text = self.small_font.render(text, False, color)
		irr_rect = irr_text.get_rect(topleft=(20, 130))
		
		# Background
		bg_rect = irr_rect.inflate(10, 6)
		pygame.draw.rect(self.display_surface, (0, 0, 0, 150), bg_rect, 0, 4)
		self.display_surface.blit(irr_text, irr_rect)
	
	def display_notifications(self):
		"""Display notification messages"""
		# Get new notifications from learning system
		if self.learning_system:
			new_notifs = self.learning_system.get_notifications()
			for notif in new_notifs:
				self.add_notification(notif)
		
		# Update and display notifications
		current_time = pygame.time.get_ticks()
		
		# Remove expired notifications
		self.notifications = [(msg, start_time) for msg, start_time in self.notifications 
			if current_time - start_time < self.notification_duration]
		
		# Display active notifications
		y_offset = 0
		for msg, start_time in self.notifications:
			# Calculate alpha based on time remaining
			time_left = self.notification_duration - (current_time - start_time)
			alpha = min(255, int(255 * (time_left / self.notification_duration)))
			
			# Determine color based on message type
			if '✔' in msg or '(+' in msg:
				color = (100, 255, 100)  # Green for positive
			elif '✖' in msg or '(-' in msg:
				color = (255, 100, 100)  # Red for negative
			elif '🏆' in msg or '🔓' in msg:
				color = (255, 215, 0)  # Gold for achievements/unlocks
			else:
				color = (255, 255, 255)  # White default
			
			notif_text = self.small_font.render(msg, False, color)
			notif_rect = notif_text.get_rect(center=(NOTIFICATION_POS[0], NOTIFICATION_POS[1] + y_offset))
			
			# Background with transparency
			bg_rect = notif_rect.inflate(20, 10)
			bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
			bg_surface.fill((0, 0, 0, int(alpha * 0.7)))
			self.display_surface.blit(bg_surface, bg_rect)
			
			self.display_surface.blit(notif_text, notif_rect)
			y_offset += 30
	
	def add_notification(self, message):
		"""Add a notification to display"""
		current_time = pygame.time.get_ticks()
		self.notifications.append((message, current_time))
		
		# Limit number of visible notifications
		if len(self.notifications) > 5:
			self.notifications.pop(0)