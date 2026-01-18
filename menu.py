# Improved Shop Menu with Tabs
# Visual tabbed interface for Buy/Sell with nice styling

import pygame
from settings import *
from timer import Timer
from knowledge_base import CROP_DATA, FERTILIZER_DATA

class Menu:
    def __init__(self, player, toggle_menu):
        # general setup
        self.player = player
        self.toggle_menu = toggle_menu
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font('./font/LycheeSoda.ttf', 28)
        self.small_font = pygame.font.Font('./font/LycheeSoda.ttf', 20)
        self.title_font = pygame.font.Font('./font/LycheeSoda.ttf', 36)

        # Menu dimensions
        self.width = 550
        self.height = 550
        self.menu_x = (SCREEN_WIDTH - self.width) // 2
        self.menu_y = (SCREEN_HEIGHT - self.height) // 2
        
        # Tabs
        self.tabs = ['SELL', 'SEEDS', 'FERTILIZERS']
        self.current_tab = 0
        self.tab_width = self.width // 3
        
        # Build item lists per tab
        self._build_item_lists()
        
        # Selection
        self.index = 0
        self.timer = Timer(150)
        
        # Colors
        self.colors = {
            'bg': (40, 35, 45),
            'tab_active': (80, 140, 80),
            'tab_inactive': (60, 55, 65),
            'item_bg': (55, 50, 60),
            'item_hover': (75, 70, 80),
            'text': (255, 255, 255),
            'price': (255, 215, 100),
            'sell': (255, 150, 150),
            'buy': (150, 255, 150),
        }

    def _build_item_lists(self):
        """Build item lists for each tab"""
        self.tab_items = {
            0: [('sell', item) for item in self.player.item_inventory.keys()],  # SELL
            1: [('buy_seed', seed) for seed in self.player.seed_inventory.keys()],  # SEEDS
            2: [('buy_fert', fert) for fert in self.player.fertilizer_inventory.keys()]  # FERTILIZERS
        }

    def display_money(self):
        money_text = self.title_font.render(f'${self.player.money}', False, self.colors['price'])
        money_rect = money_text.get_rect(midbottom=(SCREEN_WIDTH // 2, self.menu_y + self.height - 80))
        
        # Money background
        bg_rect = money_rect.inflate(30, 15)
        pygame.draw.rect(self.display_surface, (30, 80, 30), bg_rect, 0, 8)
        pygame.draw.rect(self.display_surface, self.colors['price'], bg_rect, 2, 8)
        self.display_surface.blit(money_text, money_rect)

    def draw_tabs(self):
        """Draw the tab buttons at top of menu"""
        for i, tab_name in enumerate(self.tabs):
            tab_x = self.menu_x + i * self.tab_width
            tab_rect = pygame.Rect(tab_x, self.menu_y, self.tab_width, 45)
            
            # Active vs inactive
            if i == self.current_tab:
                color = self.colors['tab_active']
                text_color = (255, 255, 255)
            else:
                color = self.colors['tab_inactive']
                text_color = (180, 180, 180)
            
            pygame.draw.rect(self.display_surface, color, tab_rect, 0, 8)
            
            # Tab text
            tab_text = self.font.render(tab_name, False, text_color)
            tab_text_rect = tab_text.get_rect(center=tab_rect.center)
            self.display_surface.blit(tab_text, tab_text_rect)

    def draw_items(self):
        """Draw items in current tab"""
        items = self.tab_items.get(self.current_tab, [])
        
        # Content area
        content_y = self.menu_y + 55
        content_height = self.height - 120
        item_height = 50
        max_items = content_height // item_height
        
        # Scrolling
        start_idx = max(0, self.index - max_items + 1) if self.index >= max_items else 0
        
        for idx, (action, item) in enumerate(items[start_idx:start_idx + max_items]):
            actual_idx = start_idx + idx
            item_y = content_y + idx * item_height
            item_rect = pygame.Rect(self.menu_x + 10, item_y, self.width - 20, item_height - 5)
            
            # Background (highlighted if selected)
            if actual_idx == self.index:
                pygame.draw.rect(self.display_surface, self.colors['item_hover'], item_rect, 0, 6)
                pygame.draw.rect(self.display_surface, self.colors['price'], item_rect, 3, 6)
            else:
                pygame.draw.rect(self.display_surface, self.colors['item_bg'], item_rect, 0, 6)
            
            # Get item details
            name, amount, price = self._get_item_details(action, item)
            
            # Item name
            name_text = self.font.render(name, False, self.colors['text'])
            self.display_surface.blit(name_text, (item_rect.x + 15, item_rect.centery - name_text.get_height()//2))
            
            # Amount
            amount_text = self.small_font.render(f'x{amount}', False, (200, 200, 200))
            self.display_surface.blit(amount_text, (item_rect.right - 120, item_rect.centery - amount_text.get_height()//2))
            
            # Price
            if action == 'sell':
                price_color = self.colors['sell']
                price_str = f'+${price}'
            else:
                price_color = self.colors['buy']
                price_str = f'-${price}'
            
            price_text = self.font.render(price_str, False, price_color)
            self.display_surface.blit(price_text, (item_rect.right - 70, item_rect.centery - price_text.get_height()//2))

    def _get_item_details(self, action, item):
        """Get name, amount, price for an item"""
        if action == 'sell':
            name = item.title()
            amount = self.player.item_inventory[item]
            price = SALE_PRICES.get(item, 5)
        elif action == 'buy_seed':
            name = f"{item.title()} Seeds"
            amount = self.player.seed_inventory[item]
            price = CROP_DATA.get(item, {}).get('seed_price', 5)
        else:  # buy_fert
            name = FERTILIZER_DATA.get(item, {}).get('name', item)
            amount = self.player.fertilizer_inventory[item]
            price = FERTILIZER_DATA.get(item, {}).get('cost', 10)
        
        return name, amount, price

    def input(self):
        keys = pygame.key.get_pressed()
        self.timer.update()

        if keys[pygame.K_ESCAPE]:
            self.toggle_menu()

        if not self.timer.active:
            items = self.tab_items.get(self.current_tab, [])
            
            # Navigate items
            if keys[pygame.K_UP]:
                self.index = max(0, self.index - 1)
                self.timer.activate()

            if keys[pygame.K_DOWN]:
                self.index = min(len(items) - 1, self.index + 1)
                self.timer.activate()

            # Switch tabs with LEFT/RIGHT
            if keys[pygame.K_LEFT]:
                self.current_tab = (self.current_tab - 1) % len(self.tabs)
                self.index = 0
                self.timer.activate()

            if keys[pygame.K_RIGHT]:
                self.current_tab = (self.current_tab + 1) % len(self.tabs)
                self.index = 0
                self.timer.activate()

            # Action with SPACE
            if keys[pygame.K_SPACE] and items:
                self.timer.activate()
                action, item = items[self.index]
                self._do_transaction(action, item)

    def _do_transaction(self, action, item):
        """Execute a buy or sell transaction"""
        if action == 'sell':
            if self.player.item_inventory[item] > 0:
                self.player.item_inventory[item] -= 1
                self.player.money += SALE_PRICES.get(item, 5)
        
        elif action == 'buy_seed':
            price = CROP_DATA.get(item, {}).get('seed_price', 5)
            if self.player.money >= price:
                self.player.seed_inventory[item] += 1
                self.player.money -= price
        
        elif action == 'buy_fert':
            price = FERTILIZER_DATA.get(item, {}).get('cost', 10)
            if self.player.money >= price:
                self.player.fertilizer_inventory[item] += 1
                self.player.money -= price

    def draw_help(self):
        """Draw help text at bottom"""
        help_text = "← → Tabs  |  ↑ ↓ Select  |  SPACE Buy/Sell  |  ESC Close"
        help_surf = self.small_font.render(help_text, False, (150, 150, 150))
        help_rect = help_surf.get_rect(midbottom=(SCREEN_WIDTH // 2, self.menu_y + self.height - 20))
        self.display_surface.blit(help_surf, help_rect)

    def draw_shopkeeper(self):
        """Draw shopkeeper character with speech bubble"""
        # Shopkeeper position (left of menu)
        keeper_x = self.menu_x - 100
        keeper_y = self.menu_y + 30
        
        # Draw simple shopkeeper (circle head + body)
        pygame.draw.circle(self.display_surface, (220, 180, 140), (keeper_x, keeper_y), 30)  # Head
        pygame.draw.circle(self.display_surface, (60, 60, 60), (keeper_x - 8, keeper_y - 5), 5)  # Left eye
        pygame.draw.circle(self.display_surface, (60, 60, 60), (keeper_x + 8, keeper_y - 5), 5)  # Right eye
        pygame.draw.arc(self.display_surface, (60, 60, 60), (keeper_x - 12, keeper_y, 24, 15), 3.14, 0, 3)  # Smile
        pygame.draw.rect(self.display_surface, (100, 60, 40), (keeper_x - 25, keeper_y + 30, 50, 60), 0, 5)  # Body
        
        # Speech bubble
        bubble_x = keeper_x + 50
        bubble_y = keeper_y - 60
        bubble_width = 220
        bubble_height = 50
        
        # Bubble background
        bubble_rect = pygame.Rect(bubble_x, bubble_y, bubble_width, bubble_height)
        pygame.draw.rect(self.display_surface, (255, 255, 255), bubble_rect, 0, 10)
        pygame.draw.rect(self.display_surface, (100, 100, 100), bubble_rect, 2, 10)
        
        # Bubble tail (triangle pointing to shopkeeper)
        pygame.draw.polygon(self.display_surface, (255, 255, 255), [
            (bubble_x + 10, bubble_y + bubble_height),
            (bubble_x + 30, bubble_y + bubble_height),
            (bubble_x - 10, bubble_y + bubble_height + 15)
        ])
        pygame.draw.polygon(self.display_surface, (100, 100, 100), [
            (bubble_x + 10, bubble_y + bubble_height),
            (bubble_x + 30, bubble_y + bubble_height),
            (bubble_x - 10, bubble_y + bubble_height + 15)
        ], 2)
        
        # Speech text
        speech = self.font.render("Hi! Welcome to", False, (60, 60, 60))
        speech2 = self.font.render("the shop!", False, (60, 60, 60))
        self.display_surface.blit(speech, (bubble_x + 15, bubble_y + 5))
        self.display_surface.blit(speech2, (bubble_x + 15, bubble_y + 25))

    def update(self):
        self.input()
        
        # Draw dimmed background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.display_surface.blit(overlay, (0, 0))
        
        # Main menu background
        menu_rect = pygame.Rect(self.menu_x, self.menu_y, self.width, self.height)
        pygame.draw.rect(self.display_surface, self.colors['bg'], menu_rect, 0, 12)
        pygame.draw.rect(self.display_surface, (100, 100, 120), menu_rect, 3, 12)
        
        # Draw components
        self.draw_tabs()
        self.draw_items()
        self.draw_help()
        self.display_money()