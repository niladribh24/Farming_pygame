
import pygame
from settings import *
from knowledge_base import FERTILIZER_DATA

class Inventory:
    def __init__(self, player):
        self.player = player
        self.display_surface = pygame.display.get_surface()
        self.is_open = False
        
        self.font_path = './font/LycheeSoda.ttf'
        self.title_font = pygame.font.Font(self.font_path, 32)
        self.item_font = pygame.font.Font(self.font_path, 20)
        self.quantity_font = pygame.font.Font(self.font_path, 16)
        
        self.cols = 8
        self.rows = 4
        self.slot_size = 64
        self.slot_padding = 6
        self.grid_padding = 20
        
        self.inv_width = (self.slot_size + self.slot_padding) * self.cols + self.grid_padding * 2
        self.inv_height = (self.slot_size + self.slot_padding) * self.rows + 210  # Extra for tabs, search, item info, and help
        
        self.rect = pygame.Rect(
            (SCREEN_WIDTH - self.inv_width) // 2,
            (SCREEN_HEIGHT - self.inv_height) // 2,
            self.inv_width,
            self.inv_height
        )
        
        self.categories = ['Seeds', 'Harvest', 'Fertilizers', 'Supplies']
        self.current_category = 0
        
        self.selected_slot = 0
        
        self.input_timer = pygame.time.get_ticks()
        self.input_cooldown = 150
        
        self.bg_color = (29, 29, 29)           # Dark gray background
        self.border_color = (60, 60, 60)       # Lighter gray border
        self.slot_color = (55, 55, 55)         # Slot background
        self.slot_border = (80, 80, 80)        # Slot border
        self.slot_hover = (100, 100, 100)      # Hover highlight
        self.tab_active = (60, 140, 60)        # Green for active tab
        self.tab_inactive = (45, 45, 45)       # Dark for inactive tab
        self.text_color = (255, 255, 255)      # White text
        self.quantity_bg = (30, 30, 30)        # Quantity badge background
        self.search_bg = (40, 40, 40)          # Search bar background
        self.search_active_bg = (50, 60, 50)   # Search bar when active
        
        self.search_text = ""
        self.search_active = False
        self.item_hash_map = {}  # Hash map for O(1) item lookup
        
        self.item_icons = {}
        self._load_icons()
    
    def _load_icons(self):
        overlay_path = './graphics/overlay/'
        icon_names = ['corn', 'tomato', 'wheat', 'carrot', 'potato', 'axe', 'hoe', 'water']
        
        for name in icon_names:
            try:
                icon = pygame.image.load(f'{overlay_path}{name}.png').convert_alpha()
                icon = pygame.transform.scale(icon, (48, 48))
                self.item_icons[name] = icon
            except:
                pass  # Icon not found, will show text instead
        
        self._create_placeholder_icons()
        self._create_drip_irrigation_icon()
    
    def _create_placeholder_icons(self):
        self._create_wood_icon()
        self._create_apple_icon()
        
        fertilizer_styles = {
            'compost': ((101, 67, 33), 'C'),      # Dark brown - organic
            'bone_meal': ((245, 245, 220), 'B'),  # Beige
            'fish_emulsion': ((70, 130, 180), 'F'),  # Steel blue
            'blood_meal': ((139, 0, 0), 'Bl'),    # Dark red
            'wood_ash': ((169, 169, 169), 'W'),   # Gray
            'npk_10_10_10': ((50, 205, 50), 'N'),  # Lime green - chemical
            'npk_5_10_10': ((34, 139, 34), 'N2'),  # Forest green
            'urea': ((255, 255, 100), 'U'),        # Yellow
        }
        
        for name, (color, label) in fertilizer_styles.items():
            if name not in self.item_icons:
                surf = pygame.Surface((48, 48), pygame.SRCALPHA)
                pygame.draw.rect(surf, color, (8, 12, 32, 28), border_radius=4)
                pygame.draw.rect(surf, (255, 255, 255), (8, 12, 32, 28), 2, border_radius=4)
                font = pygame.font.Font(self.font_path, 14)
                text = font.render(label, True, (0, 0, 0) if sum(color) > 400 else (255, 255, 255))
                text_rect = text.get_rect(center=(24, 26))
                surf.blit(text, text_rect)
                self.item_icons[name] = surf
    
    def _create_wood_icon(self):
        surf = pygame.Surface((48, 48), pygame.SRCALPHA)
        pygame.draw.rect(surf, (139, 90, 43), (8, 14, 32, 20), border_radius=3)
        pygame.draw.rect(surf, (101, 67, 33), (8, 14, 32, 20), 2, border_radius=3)
        pygame.draw.line(surf, (101, 67, 33), (12, 18), (12, 30), 2)
        pygame.draw.line(surf, (101, 67, 33), (24, 18), (24, 30), 2)
        pygame.draw.line(surf, (101, 67, 33), (36, 18), (36, 30), 2)
        self.item_icons['wood'] = surf
    
    def _create_apple_icon(self):
        surf = pygame.Surface((48, 48), pygame.SRCALPHA)
        pygame.draw.circle(surf, (220, 50, 50), (24, 28), 14)
        pygame.draw.circle(surf, (180, 30, 30), (24, 28), 14, 2)
        pygame.draw.line(surf, (101, 67, 33), (24, 14), (24, 8), 3)
        pygame.draw.ellipse(surf, (50, 180, 50), (26, 6, 10, 6))
        self.item_icons['apple'] = surf
    
    def _create_drip_irrigation_icon(self):
        surf = pygame.Surface((48, 48), pygame.SRCALPHA)
        pygame.draw.rect(surf, (100, 100, 100), (4, 20, 40, 6), border_radius=2)
        pygame.draw.rect(surf, (80, 80, 80), (10, 24, 4, 12))
        pygame.draw.rect(surf, (80, 80, 80), (22, 24, 4, 12))
        pygame.draw.rect(surf, (80, 80, 80), (34, 24, 4, 12))
        pygame.draw.circle(surf, (100, 180, 255), (12, 42), 4)
        pygame.draw.circle(surf, (100, 180, 255), (24, 42), 4)
        pygame.draw.circle(surf, (100, 180, 255), (36, 42), 4)
        self.item_icons['drip_irrigation'] = surf
    
    def toggle(self):
        self.is_open = not self.is_open
        if self.is_open:
            self.selected_slot = 0
            self.current_category = 0
            self.search_text = ""
            self.search_active = False
            self.input_timer = pygame.time.get_ticks()
            self._build_item_hash_map()
    
    def _build_item_hash_map(self):
        self.item_hash_map = {}
        
        for seed, qty in self.player.seed_inventory.items():
            if qty > 0:
                key = seed.lower()
                self.item_hash_map[key] = {'name': seed, 'quantity': qty, 'type': 'seed', 'category': 0}
        
        harvest_names = ['corn', 'tomato', 'wheat', 'carrot', 'potato', 'apple']
        for item_name in harvest_names:
            if item_name in self.player.item_inventory and self.player.item_inventory[item_name] > 0:
                key = item_name.lower()
                self.item_hash_map[key] = {'name': item_name, 'quantity': self.player.item_inventory[item_name], 'type': 'harvest', 'category': 1}
        
        for fert, qty in self.player.fertilizer_inventory.items():
            if qty > 0:
                key = fert.lower()
                self.item_hash_map[key] = {'name': fert, 'quantity': qty, 'type': 'fertilizer', 'category': 2}
        
        if 'wood' in self.player.item_inventory and self.player.item_inventory['wood'] > 0:
            self.item_hash_map['wood'] = {'name': 'wood', 'quantity': self.player.item_inventory['wood'], 'type': 'supply', 'category': 3}
        
        drip_count = getattr(self.player, 'drip_irrigation_count', 0)
        drip_unlocked = getattr(self.player, 'drip_irrigation_unlocked', False)
        
        if drip_count > 0 or drip_unlocked:
            self.item_hash_map['drip_irrigation'] = {'name': 'drip_irrigation', 'quantity': drip_count, 'type': 'supply', 'category': 3}
            self.item_hash_map['drip'] = {'name': 'drip_irrigation', 'quantity': drip_count, 'type': 'supply', 'category': 3}
    
    def search_items(self, query):
        query = query.lower().strip()
        if not query:
            return []
        
        results = []
        
        if query in self.item_hash_map:
            results.append(self.item_hash_map[query])
        
        for key, item in self.item_hash_map.items():
            if key.startswith(query) and item not in results:
                results.append(item)
        
        return results
    
    def get_category_items(self):
        if self.search_active:
            if self.search_text:
                return self.search_items(self.search_text)
            else:
                return []  # Empty while waiting for input
        
        items = []
        
        if self.current_category == 0:  # Seeds
            for seed, qty in self.player.seed_inventory.items():
                if qty > 0:
                    items.append({'name': seed, 'quantity': qty, 'type': 'seed'})
                
        elif self.current_category == 1:  # Harvest (Crops + Apples)
            harvest_names = ['corn', 'tomato', 'wheat', 'carrot', 'potato', 'apple']
            for item_name in harvest_names:
                if item_name in self.player.item_inventory and self.player.item_inventory[item_name] > 0:
                    items.append({'name': item_name, 'quantity': self.player.item_inventory[item_name], 'type': 'harvest'})
                    
        elif self.current_category == 2:  # Fertilizers
            for fert, qty in self.player.fertilizer_inventory.items():
                if qty > 0:
                    items.append({'name': fert, 'quantity': qty, 'type': 'fertilizer'})
        
        elif self.current_category == 3:  # Supplies (Wood + Drip Irrigation)
            if 'wood' in self.player.item_inventory and self.player.item_inventory['wood'] > 0:
                items.append({'name': 'wood', 'quantity': self.player.item_inventory['wood'], 'type': 'supply'})
            drip_count = getattr(self.player, 'drip_irrigation_count', 0)
            drip_unlocked = getattr(self.player, 'drip_irrigation_unlocked', False)
            
            if drip_count > 0 or drip_unlocked:
                items.append({'name': 'drip_irrigation', 'quantity': drip_count, 'type': 'supply'})
        
        return items
    
    def handle_text_input(self, event):
        if event.type == pygame.KEYDOWN and self.search_active:
            if event.key == pygame.K_BACKSPACE:
                self.search_text = self.search_text[:-1]
            elif event.key == pygame.K_RETURN:
                self.search_active = False
            elif event.key == pygame.K_ESCAPE:
                self.search_text = ""
                self.search_active = False
            elif event.unicode.isalnum() or event.unicode == '_':
                self.search_text += event.unicode.lower()
    
    def input(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.input_timer < self.input_cooldown:
            return
            
        keys = pygame.key.get_pressed()
        items = self.get_category_items()
        num_items = len(items)
        
        if not self.search_active and (keys[pygame.K_i] or keys[pygame.K_ESCAPE]):
            self.is_open = False
            self.input_timer = current_time
            return
        
        if keys[pygame.K_s] and not self.search_active:
            self.search_active = True
            self.search_text = ""
            self.input_timer = current_time
            return
        
        if keys[pygame.K_TAB]:
            self.current_category = (self.current_category + 1) % len(self.categories)
            self.selected_slot = 0
            self.input_timer = current_time
            return
        
        if keys[pygame.K_q]:
            self.current_category = (self.current_category - 1) % len(self.categories)
            self.selected_slot = 0
            self.input_timer = current_time
            return
        
        if num_items > 0:
            if keys[pygame.K_RIGHT]:
                self.selected_slot = (self.selected_slot + 1) % num_items
                self.input_timer = current_time
            elif keys[pygame.K_LEFT]:
                self.selected_slot = (self.selected_slot - 1) % num_items
                self.input_timer = current_time
            elif keys[pygame.K_DOWN]:
                new_slot = self.selected_slot + self.cols
                if new_slot < num_items:
                    self.selected_slot = new_slot
                self.input_timer = current_time
            elif keys[pygame.K_UP]:
                new_slot = self.selected_slot - self.cols
                if new_slot >= 0:
                    self.selected_slot = new_slot
                self.input_timer = current_time
    
    def draw_background(self):
        pygame.draw.rect(self.display_surface, self.bg_color, self.rect, border_radius=8)
        pygame.draw.rect(self.display_surface, self.border_color, self.rect, 3, border_radius=8)
        
        title = self.title_font.render("INVENTORY", True, self.text_color)
        title_rect = title.get_rect(midtop=(SCREEN_WIDTH // 2, self.rect.top + 10))
        self.display_surface.blit(title, title_rect)
    
    def draw_tabs(self):
        tab_y = self.rect.top + 82  # Moved down to make room for search bar
        tab_width = (self.inv_width - 40) // len(self.categories)
        tab_height = 32
        
        for i, category in enumerate(self.categories):
            tab_x = self.rect.left + 20 + i * tab_width
            tab_rect = pygame.Rect(tab_x, tab_y, tab_width - 4, tab_height)
            
            if i == self.current_category:
                color = self.tab_active
            else:
                color = self.tab_inactive
            
            pygame.draw.rect(self.display_surface, color, tab_rect, border_radius=4)
            pygame.draw.rect(self.display_surface, self.border_color, tab_rect, 2, border_radius=4)
            
            text = self.item_font.render(category, True, self.text_color)
            text_rect = text.get_rect(center=tab_rect.center)
            self.display_surface.blit(text, text_rect)
    
    def draw_slots(self):
        items = self.get_category_items()
        grid_start_x = self.rect.left + self.grid_padding
        grid_start_y = self.rect.top + 125  # Adjusted for search bar
        
        for row in range(self.rows):
            for col in range(self.cols):
                slot_index = row * self.cols + col
                slot_x = grid_start_x + col * (self.slot_size + self.slot_padding)
                slot_y = grid_start_y + row * (self.slot_size + self.slot_padding)
                slot_rect = pygame.Rect(slot_x, slot_y, self.slot_size, self.slot_size)
                
                if slot_index == self.selected_slot and slot_index < len(items):
                    pygame.draw.rect(self.display_surface, self.slot_hover, slot_rect, border_radius=4)
                else:
                    pygame.draw.rect(self.display_surface, self.slot_color, slot_rect, border_radius=4)
                
                pygame.draw.rect(self.display_surface, self.slot_border, slot_rect, 2, border_radius=4)
                
                if slot_index < len(items):
                    item = items[slot_index]
                    self._draw_item(slot_rect, item)
    
    def _draw_item(self, slot_rect, item):
        name = item['name']
        quantity = item['quantity']
        
        if name in self.item_icons:
            icon = self.item_icons[name]
            icon_rect = icon.get_rect(center=slot_rect.center)
            self.display_surface.blit(icon, icon_rect)
        else:
            abbrev = name[:3].upper()
            text = self.item_font.render(abbrev, True, self.text_color)
            text_rect = text.get_rect(center=slot_rect.center)
            self.display_surface.blit(text, text_rect)
        
        if quantity > 0:
            qty_text = self.quantity_font.render(f"x{quantity}", True, self.text_color)
            qty_rect = qty_text.get_rect(bottomright=(slot_rect.right - 4, slot_rect.bottom - 2))
            
            badge_rect = qty_rect.inflate(6, 2)
            pygame.draw.rect(self.display_surface, self.quantity_bg, badge_rect, border_radius=3)
            self.display_surface.blit(qty_text, qty_rect)
    
    def draw_help(self):
        help_y = self.rect.bottom - 15
        if self.search_active:
            help_text = "Type to search  |  ESC: Cancel  |  ENTER: Done"
        else:
            help_text = "S: Search  |  TAB/Q: Tabs  |  I/ESC: Close"
        text = self.item_font.render(help_text, True, (180, 180, 180))
        text_rect = text.get_rect(midbottom=(SCREEN_WIDTH // 2, help_y))
        self.display_surface.blit(text, text_rect)
    
    def draw_item_info(self):
        items = self.get_category_items()
        if self.selected_slot < len(items):
            item = items[self.selected_slot]
            name = item['name'].replace('_', ' ').title()
            
            if item['type'] == 'fertilizer' and item['name'] in FERTILIZER_DATA:
                name = FERTILIZER_DATA[item['name']]['name']
            
            info_y = self.rect.bottom - 40
            info_text = f"Selected: {name}"
            text = self.item_font.render(info_text, True, (200, 200, 100))
            text_rect = text.get_rect(midbottom=(SCREEN_WIDTH // 2, info_y))
            self.display_surface.blit(text, text_rect)
    
    def draw_search_bar(self):
        bar_width = self.inv_width - 40
        bar_height = 28
        bar_x = self.rect.left + 20
        bar_y = self.rect.top + 48
        bar_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        
        bg_color = self.search_active_bg if self.search_active else self.search_bg
        pygame.draw.rect(self.display_surface, bg_color, bar_rect, border_radius=4)
        pygame.draw.rect(self.display_surface, self.border_color, bar_rect, 2, border_radius=4)
        
        if self.search_text:
            display_text = self.search_text
        elif self.search_active:
            display_text = "Type to search..."
        else:
            display_text = "Press S to search"
        
        text_color = self.text_color if self.search_text else (120, 120, 120)
        text = self.item_font.render(display_text, True, text_color)
        text_rect = text.get_rect(midleft=(bar_x + 10, bar_rect.centery))
        self.display_surface.blit(text, text_rect)
        
        if self.search_active and (pygame.time.get_ticks() // 500) % 2 == 0:
            cursor_x = text_rect.right + 2
            pygame.draw.line(self.display_surface, self.text_color, 
                           (cursor_x, bar_rect.top + 5), (cursor_x, bar_rect.bottom - 5), 2)
    
    def draw_item_info(self):
        items = self.get_category_items()
        if self.selected_slot < len(items):
            item = items[self.selected_slot]
            name = item['name'].replace('_', ' ').title()
            
            if item['type'] == 'fertilizer' and item['name'] in FERTILIZER_DATA:
                name = FERTILIZER_DATA[item['name']]['name']
            
            info_y = self.rect.bottom - 55
            info_text = f"Selected: {name}"
            text = self.item_font.render(info_text, True, (200, 200, 100))
            text_rect = text.get_rect(midbottom=(SCREEN_WIDTH // 2, info_y))
            self.display_surface.blit(text, text_rect)
    
    def display(self):
        if not self.is_open:
            return
            
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.display_surface.blit(overlay, (0, 0))
        
        self.draw_background()
        self.draw_search_bar()
        self.draw_tabs()
        self.draw_slots()
        self.draw_item_info()
        self.draw_help()
    
    def update(self):
        if not self.is_open:
            return
        
        self.input()
        self.display()


_inventory_instance = None

def get_inventory(player=None):
    global _inventory_instance
    if _inventory_instance is None and player is not None:
        _inventory_instance = Inventory(player)
    return _inventory_instance
