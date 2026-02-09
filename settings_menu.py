
import pygame
import os
from settings import *
from timer import Timer

class SettingsMenu:
    
    def __init__(self, level):
        self.display_surface = pygame.display.get_surface()
        self.level = level
        self.font = pygame.font.Font('./font/LycheeSoda.ttf', 24)
        self.title_font = pygame.font.Font('./font/LycheeSoda.ttf', 32)
        self.small_font = pygame.font.Font('./font/LycheeSoda.ttf', 18)
        
        self.is_open = False
        self.open_time = 0
        
        self.music_volume = 0
        self.sfx_volume = 0.2
        
        self.width = 600
        self.height = 480
        self.menu_x = (SCREEN_WIDTH - self.width) // 2
        self.menu_y = (SCREEN_HEIGHT - self.height) // 2
        
        self.tabs = ['AUDIO', 'CONTROLS', 'GAME']
        self.current_tab = 0
        
        self.audio_options = ['Music Volume', 'SFX Volume']
        self.selected = 0
        
        self.controls = [
            ('W/A/S/D', 'Move player'),
            ('Space', 'Use current tool'),
            ('Q', 'Switch tool'),
            ('E', 'Switch seed'),
            ('Left Ctrl', 'Plant seed'),
            ('F', 'Switch fertilizer'),
            ('R', 'Apply fertilizer'),
            ('G', 'Place drip irrigation'),
            ('X', 'Remove drip irrigation'),
            ('O', 'Switch irrigation mode'),
            ('I', 'Open Inventory'),
            ('T', 'Open Skill Tree'),
            ('B', 'Open Knowledge Book'),
            ('P', 'Open Settings'),
            ('Enter', 'Interact (shop/bed)'),
            ('Escape', 'Close menus'),
        ]
        self.controls_scroll = 0  # Scroll offset for controls
        self.max_visible_controls = 10  # Max controls visible at once
        
        self.timer = Timer(150)
    
    def toggle(self):
        self.is_open = not self.is_open
        if self.is_open:
            self.open_time = pygame.time.get_ticks()
    
    def update(self):
        if not self.is_open:
            return
        
        keys = pygame.key.get_pressed()
        self.timer.update()
        current_time = pygame.time.get_ticks()
        
        if current_time - self.open_time < 300:
            return
        
        if not self.timer.active:
            if keys[pygame.K_LEFT]:
                 self.current_tab = (self.current_tab - 1) % len(self.tabs)
                 self.selected = 0
                 self.timer.activate()
            if keys[pygame.K_RIGHT]:
                 self.current_tab = (self.current_tab + 1) % len(self.tabs)
                 self.selected = 0
                 self.timer.activate()
            
            if self.current_tab == 0:
                if keys[pygame.K_UP]:
                    self.selected = max(0, self.selected - 1)
                    self.timer.activate()
                if keys[pygame.K_DOWN]:
                    self.selected = min(len(self.audio_options) - 1, self.selected + 1)
                    self.timer.activate()
                
                if keys[pygame.K_a]:
                    self._adjust_setting(-0.1)
                    self.timer.activate()
                if keys[pygame.K_d]:
                    self._adjust_setting(0.1)
                    self.timer.activate()
            
            if self.current_tab == 1:
                if keys[pygame.K_UP]:
                    self.controls_scroll = max(0, self.controls_scroll - 1)
                    self.timer.activate()
                if keys[pygame.K_DOWN]:
                    max_scroll = max(0, len(self.controls) - self.max_visible_controls)
                    self.controls_scroll = min(max_scroll, self.controls_scroll + 1)
                    self.timer.activate()
            
            if self.current_tab == 2:
                 if keys[pygame.K_SPACE] or keys[pygame.K_RETURN]:
                     self.timer.activate()
                     self._reset_game()
            
            if keys[pygame.K_ESCAPE] or keys[pygame.K_p]:
                self.is_open = False
                self.timer.activate()
    
    def _adjust_setting(self, delta):
        option = self.audio_options[self.selected]
        if option == 'Music Volume':
            self.music_volume = max(0, min(1, self.music_volume + delta))
            self.level.music.set_volume(self.music_volume)
        elif option == 'SFX Volume':
            self.sfx_volume = max(0, min(1, self.sfx_volume + delta))
            self.level.success.set_volume(self.sfx_volume)
    
    def display(self):
        if not self.is_open:
            return
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.display_surface.blit(overlay, (0, 0))
        
        menu_rect = pygame.Rect(self.menu_x, self.menu_y, self.width, self.height)
        pygame.draw.rect(self.display_surface, (50, 45, 55), menu_rect, 0, 12)
        pygame.draw.rect(self.display_surface, (100, 100, 120), menu_rect, 3, 12)
        
        title = self.title_font.render("⚙️ Settings", False, (255, 255, 255))
        self.display_surface.blit(title, (self.menu_x + 20, self.menu_y + 15))
        
        self._draw_tabs()
        
        if self.current_tab == 0:
            self._draw_audio_tab()
        elif self.current_tab == 1:
            self._draw_controls_tab()
        else:
            self._draw_game_tab()
        
        if self.current_tab == 0:
            help_text = "A/D: Adjust Volume  |  ESC: Close"
        elif self.current_tab == 1:
            help_text = "Up/Down: Scroll  |  ESC: Close"
        elif self.current_tab == 2:
             help_text = "SPACE/ENTER: Select  |  ESC: Close"
        else:
            help_text = "ESC: Close"
        help_surf = self.small_font.render(help_text, False, (150, 150, 150))
        help_rect = help_surf.get_rect(midbottom=(SCREEN_WIDTH // 2, self.menu_y + self.height - 15))
        self.display_surface.blit(help_surf, help_rect)
    
    def _draw_tabs(self):
        tab_width = self.width // 3 - 15
        tab_y = self.menu_y + 55
        
        for i, tab in enumerate(self.tabs):
            tab_x = self.menu_x + 15 + i * (tab_width + 10)
            tab_rect = pygame.Rect(tab_x, tab_y, tab_width, 35)
            
            if i == self.current_tab:
                pygame.draw.rect(self.display_surface, (80, 120, 80), tab_rect, 0, 6)
                color = (255, 255, 255)
            else:
                pygame.draw.rect(self.display_surface, (60, 55, 65), tab_rect, 0, 6)
                color = (150, 150, 150)
            
            text = self.font.render(tab, False, color)
            text_rect = text.get_rect(center=tab_rect.center)
            self.display_surface.blit(text, text_rect)
    
    def _draw_audio_tab(self):
        y = self.menu_y + 110
        
        for i, option in enumerate(self.audio_options):
            is_selected = i == self.selected
            
            if is_selected:
                opt_rect = pygame.Rect(self.menu_x + 20, y - 5, self.width - 40, 45)
                pygame.draw.rect(self.display_surface, (70, 65, 80), opt_rect, 0, 6)
            
            color = (255, 220, 100) if is_selected else (200, 200, 200)
            text = self.font.render(option, False, color)
            self.display_surface.blit(text, (self.menu_x + 30, y + 5))
            
            value = self.music_volume if option == 'Music Volume' else self.sfx_volume
            self._draw_slider(y + 5, value, is_selected)
            
            y += 60
    
    def _draw_slider(self, y, value, is_selected):
        slider_x = self.menu_x + 250
        slider_width = 200
        slider_height = 14
        
        bg_rect = pygame.Rect(slider_x, y + 5, slider_width, slider_height)
        pygame.draw.rect(self.display_surface, (40, 40, 50), bg_rect, 0, 7)
        
        fill_width = int(slider_width * value)
        if fill_width > 0:
            fill_rect = pygame.Rect(slider_x, y + 5, fill_width, slider_height)
            color = (100, 200, 100) if is_selected else (80, 160, 80)
            pygame.draw.rect(self.display_surface, color, fill_rect, 0, 7)
        
        pygame.draw.rect(self.display_surface, (100, 100, 120), bg_rect, 2, 7)
        
        pct = self.font.render(f"{int(value * 100)}%", False, (200, 200, 200))
        self.display_surface.blit(pct, (slider_x + slider_width + 15, y))
    
    def _draw_controls_tab(self):
        y = self.menu_y + 105
        col1_x = self.menu_x + 30
        col2_x = self.menu_x + 180
        
        header1 = self.small_font.render("KEY", False, (255, 220, 100))
        header2 = self.small_font.render("ACTION", False, (255, 220, 100))
        self.display_surface.blit(header1, (col1_x, y))
        self.display_surface.blit(header2, (col2_x, y))
        y += 25
        
        pygame.draw.line(self.display_surface, (100, 100, 120),
            (col1_x, y), (self.menu_x + self.width - 30, y), 2)
        y += 10
        
        if self.controls_scroll > 0:
            arrow_up = self.small_font.render("^ More above", False, (150, 150, 150))
            self.display_surface.blit(arrow_up, (self.menu_x + self.width - 120, self.menu_y + 105))
        
        visible_controls = self.controls[self.controls_scroll:self.controls_scroll + self.max_visible_controls]
        for key, action in visible_controls:
            key_surf = self.small_font.render(key, False, (255, 255, 255))
            key_rect = pygame.Rect(col1_x - 5, y - 2, 130, 22)
            pygame.draw.rect(self.display_surface, (60, 55, 70), key_rect, 0, 4)
            self.display_surface.blit(key_surf, (col1_x, y))
            
            action_surf = self.small_font.render(action, False, (200, 200, 200))
            self.display_surface.blit(action_surf, (col2_x, y))
            
            y += 26
        
        if self.controls_scroll + self.max_visible_controls < len(self.controls):
            arrow_down = self.small_font.render("v More below", False, (150, 150, 150))
            self.display_surface.blit(arrow_down, (self.menu_x + self.width - 120, y - 10))

    def _draw_game_tab(self):
        y = self.menu_y + 150
        
        warning = self.font.render("WARNING: This cannot be undone!", False, (255, 100, 100))
        warning_rect = warning.get_rect(center=(self.menu_x + self.width // 2, y))
        self.display_surface.blit(warning, warning_rect)
        
        y += 60
        
        btn_rect = pygame.Rect(self.menu_x + self.width // 2 - 100, y, 200, 50)
        
        pygame.draw.rect(self.display_surface, (200, 80, 80), btn_rect, 0, 8)
        pygame.draw.rect(self.display_surface, (255, 255, 255), btn_rect, 2, 8)
        
        btn_text = self.font.render("Start New Game", False, (255, 255, 255))
        btn_text_rect = btn_text.get_rect(center=btn_rect.center)
        self.display_surface.blit(btn_text, btn_text_rect)

    def _reset_game(self):
        if os.path.exists('savegame.json'):
            try:
                os.remove('savegame.json')
                print("Save deleted.")
            except Exception as e:
                print(f"Error deleting save: {e}")
        
        self.level.reset_pending = True
        self.is_open = False


settings_menu = None

def get_settings_menu(level):
    global settings_menu
    if settings_menu is None:
        settings_menu = SettingsMenu(level)
    return settings_menu
