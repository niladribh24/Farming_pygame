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
		self.display_trader_hint()
		self.display_notifications()
	
	def display_trader_hint(self):
		"""Show speech bubble when player is near trader"""
		if not hasattr(self, 'interaction_sprites') or not self.interaction_sprites:
			return
		
		# Check if player is near trader
		for sprite in self.interaction_sprites.sprites():
			if hasattr(sprite, 'name') and sprite.name == 'Trader':
				# Calculate distance to player
				player_pos = self.player.rect.center
				trader_pos = sprite.rect.center
				distance = ((player_pos[0] - trader_pos[0])**2 + (player_pos[1] - trader_pos[1])**2)**0.5
				
				if distance < 100:  # Within 100 pixels
					# Calculate screen position relative to player (camera center)
					offset_x = self.player.rect.centerx - SCREEN_WIDTH / 2
					offset_y = self.player.rect.centery - SCREEN_HEIGHT / 2
					
					screen_x = sprite.rect.centerx - offset_x - 100  # -100 to center bubble (width 200)
					screen_y = sprite.rect.top - offset_y - 70      # Above head
					
					self._draw_speech_bubble(
						"Hi! Welcome to the shop!",
						"Press ENTER to trade",
						screen_x,
						screen_y
					)
					break
	
	def _draw_speech_bubble(self, line1, line2, x, y):
		"""Draw a speech bubble at screen position"""
		# x, y are already converted to screen coordinates
		
		bubble_width = 200
		bubble_height = 50
		
		# Bubble background
		bubble_rect = pygame.Rect(x, y, bubble_width, bubble_height)
		pygame.draw.rect(self.display_surface, (255, 255, 255), bubble_rect, 0, 8)
		pygame.draw.rect(self.display_surface, (80, 80, 80), bubble_rect, 2, 8)
		
		# Bubble tail
		pygame.draw.polygon(self.display_surface, (255, 255, 255), [
			(x + bubble_width//2 - 10, y + bubble_height),
			(x + bubble_width//2 + 10, y + bubble_height),
			(x + bubble_width//2, y + bubble_height + 12)
		])
		
		# Text
		font = self.small_font
		text1 = font.render(line1, False, (50, 50, 50))
		text2 = font.render(line2, False, (100, 100, 100))
		self.display_surface.blit(text1, (x + 10, y + 8))
		self.display_surface.blit(text2, (x + 10, y + 28))
	
	def display_soil_health(self):
		"""Display soil health bar in top-right corner"""
		if not self.soil_layer:
			return
			
		# Get average soil health
		health = self.soil_layer.get_average_soil_health()
		
		# Draw label
		label = self.font.render('Soil Health', False, 'White')
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
	
	def display_score(self):
		"""Display current score"""
		if not self.learning_system:
			return
			
		score = self.learning_system.total_score
		score_text = self.font.render(f'Score: {score}', False, 'White')
		score_rect = score_text.get_rect(topleft=SCORE_DISPLAY_POS)
		
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
		
		# Icon based on type
		icon = '🌿' if fert_type == 'organic' else '⚗️'
		color = (100, 200, 100) if fert_type == 'organic' else (200, 100, 100)
		
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
			if '✔' in msg or '+' in msg:
				color = (100, 255, 100)  # Green for positive
			elif '✖' in msg or '-' in msg:
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
	
	def show_day_summary(self, summary_text):
		"""Display end-of-day summary panel"""
		# Semi-transparent overlay
		overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
		overlay.fill((0, 0, 0, 200))
		self.display_surface.blit(overlay, (0, 0))
		
		# Summary panel
		panel_width = 500
		panel_height = 400
		panel_x = (SCREEN_WIDTH - panel_width) // 2
		panel_y = (SCREEN_HEIGHT - panel_height) // 2
		
		# Panel background
		pygame.draw.rect(self.display_surface, (40, 40, 60),
			(panel_x, panel_y, panel_width, panel_height), 0, 10)
		pygame.draw.rect(self.display_surface, (100, 100, 140),
			(panel_x, panel_y, panel_width, panel_height), 3, 10)
		
		# Render summary text
		lines = summary_text.split('\n')
		y = panel_y + 20
		for line in lines:
			if '═' in line:
				# Divider line
				pygame.draw.line(self.display_surface, (100, 100, 140),
					(panel_x + 20, y + 10), (panel_x + panel_width - 20, y + 10), 2)
				y += 25
			else:
				text_surf = self.small_font.render(line, False, 'White')
				text_rect = text_surf.get_rect(midleft=(panel_x + 30, y + 10))
				self.display_surface.blit(text_surf, text_rect)
				y += 25
		
		# Continue instruction
		continue_text = self.font.render('Press SPACE to continue...', False, (200, 200, 200))
		continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, panel_y + panel_height - 30))
		self.display_surface.blit(continue_text, continue_rect)