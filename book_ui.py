# Book UI - Display educational knowledge cards
# Press B to open the knowledge book during gameplay

import pygame
from settings import *
from knowledge_book import KNOWLEDGE_CARDS, KNOWLEDGE_CATEGORIES, QUICK_TIPS
from knowledge_base import ACHIEVEMENT_DEFINITIONS
from timer import Timer

class KnowledgeBookUI:
    """
    Interactive knowledge book UI for learning sustainable farming practices.
    Press B to open, Escape to close, arrows to navigate.
    """
    
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font('./font/LycheeSoda.ttf', 28)
        self.title_font = pygame.font.Font('./font/LycheeSoda.ttf', 36)
        self.small_font = pygame.font.Font('./font/LycheeSoda.ttf', 18)
        
        # Book state
        self.is_open = False
        self.current_page = 0
        self.is_open = False
        self.current_page = 0
        self.cards = list(KNOWLEDGE_CARDS.keys())
        self.learning_system = None
        
        # Tabs
        self.tabs = ["Guide", "Achievements"]
        self.active_tab = 0 # 0: Guide, 1: Achievements
        
        # Navigation timer
        self.timer = Timer(200)
        
        # Cooldown to prevent immediate close after open
        self.open_time = 0
        
        # Book dimensions (taller to fit more content)
        self.book_width = 800
        self.book_height = 650
        self.book_x = (SCREEN_WIDTH - self.book_width) // 2
        self.book_y = (SCREEN_HEIGHT - self.book_height) // 2
    
    def toggle(self):
        """Open or close the book"""
        self.is_open = not self.is_open
        if self.is_open:
            self.open_time = pygame.time.get_ticks()
    
    def update(self):
        """Handle input when book is open"""
        if not self.is_open:
            return
        
        keys = pygame.key.get_pressed()
        self.timer.update()
        current_time = pygame.time.get_ticks()
        
        # Don't allow close for 500ms after opening (prevents double-toggle)
        if current_time - self.open_time < 500:
            return
        
        # Only Escape closes (B is handled by Level to toggle)
        if keys[pygame.K_ESCAPE]:
            if not self.timer.active:
                self.timer.activate()
                self.is_open = False
        
        if not self.timer.active:
            # Page Navigation
            if keys[pygame.K_LEFT]:
                self.current_page = max(0, self.current_page - 1)
                self.timer.activate()
            
            if keys[pygame.K_RIGHT]:
                self.current_page = min(len(self.cards) - 1, self.current_page + 1)
                self.timer.activate()

            # Tab Navigation (1, 2)
            if keys[pygame.K_1]:
                self.active_tab = 0
                self.current_page = 0
                self.timer.activate()
            if keys[pygame.K_2]:
                self.active_tab = 1
                self.timer.activate()
    
    def display(self):
        """Render the knowledge book"""
        if not self.is_open:
            return
        
        # Dim background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.display_surface.blit(overlay, (0, 0))
        
        # Book background
        book_rect = pygame.Rect(self.book_x, self.book_y, self.book_width, self.book_height)
        pygame.draw.rect(self.display_surface, (45, 35, 25), book_rect, 0, 10)
        pygame.draw.rect(self.display_surface, (139, 90, 43), book_rect, 4, 10)
        
        # Book title and Tabs
        title_text = "📖 Sustainable Guide" if self.active_tab == 0 else "🏆 Achievements"
        title = self.title_font.render(title_text, False, (255, 230, 180))
        title_rect = title.get_rect(midtop=(SCREEN_WIDTH // 2, self.book_y + 15))
        self.display_surface.blit(title, title_rect)

        # Tab Hints
        tab_hint = self.small_font.render("Tabs: [1] Guide   [2] Achievements", False, (200, 200, 200))
        tab_rect = tab_hint.get_rect(midtop=(SCREEN_WIDTH // 2, self.book_y + 55))
        self.display_surface.blit(tab_hint, tab_rect)
        
        # Content
        if self.active_tab == 0:
            self._render_guide_content()
        else:
            self._render_achievements_content()

    def _render_guide_content(self):
        if self.cards:
            card_key = self.cards[self.current_page]
            card = KNOWLEDGE_CARDS[card_key]
            self._render_card(card)
        
        # Page indicator
        page_text = self.small_font.render(
            f"Page {self.current_page + 1}/{len(self.cards)}", 
            False, 
            (200, 200, 200)
        )
        page_rect = page_text.get_rect(midbottom=(SCREEN_WIDTH // 2, self.book_y + self.book_height - 15))
        self.display_surface.blit(page_text, page_rect)

    def _render_achievements_content(self):
        start_y = self.book_y + 120
        padding = 15
        
        # Get unlocked set
        unlocked_ids = set()
        if self.learning_system:
            unlocked_ids = self.learning_system.achievements

        # Pagination for achievements
        achievements_list = list(ACHIEVEMENT_DEFINITIONS.items())
        items_per_page = 6  # Max achievements that fit on one page
        total_pages = max(1, (len(achievements_list) + items_per_page - 1) // items_per_page)
        current_ach_page = min(self.current_page, total_pages - 1)
        
        start_idx = current_ach_page * items_per_page
        end_idx = min(start_idx + items_per_page, len(achievements_list))
        
        # Count unlocked
        unlocked_count = len(unlocked_ids)
        total_count = len(achievements_list)
        
        # Progress header
        progress_text = self.small_font.render(
            f"Progress: {unlocked_count}/{total_count} achievements unlocked",
            False, (255, 215, 0)
        )
        progress_rect = progress_text.get_rect(midtop=(SCREEN_WIDTH // 2, self.book_y + 95))
        self.display_surface.blit(progress_text, progress_rect)

        # Render list (paginated)
        for display_idx, (ach_id, data) in enumerate(achievements_list[start_idx:end_idx]):
            is_unlocked = ach_id in unlocked_ids
            
            # Colors
            color = (50, 168, 82) if is_unlocked else (100, 100, 100)  # Green vs Gray
            text_color = (255, 255, 255) if is_unlocked else (150, 150, 150)
            
            # Entry Background
            entry_rect = pygame.Rect(self.book_x + 40, start_y + (display_idx * 80), self.book_width - 80, 70)
            pygame.draw.rect(self.display_surface, (60, 50, 40), entry_rect, 0, 5)
            pygame.draw.rect(self.display_surface, color, entry_rect, 2, 5)
            
            # Icon/Status
            status = "🔓" if is_unlocked else "🔒"
            status_surf = self.font.render(status, False, text_color)
            self.display_surface.blit(status_surf, (entry_rect.left + 15, entry_rect.centery - 15))
            
            # Name - always show the name for discoverability
            name_surf = self.font.render(data['name'], False, text_color)
            self.display_surface.blit(name_surf, (entry_rect.left + 60, entry_rect.top + 10))
            
            # Description - show condition hint if locked, full description if unlocked
            desc_text = data['description'] if is_unlocked else data['condition']
            desc_surf = self.small_font.render(desc_text, False, (200, 200, 200) if is_unlocked else (120, 120, 120))
            self.display_surface.blit(desc_surf, (entry_rect.left + 60, entry_rect.bottom - 25))
            
            # Points
            pts_surf = self.small_font.render(f"+{data['points']} pts", False, (255, 215, 0) if is_unlocked else (100, 100, 100))
            pts_rect = pts_surf.get_rect(midright=(entry_rect.right - 15, entry_rect.centery))
            self.display_surface.blit(pts_surf, pts_rect)
        
        # Page indicator if multiple pages
        if total_pages > 1:
            page_text = self.small_font.render(
                f"◀ Page {current_ach_page + 1}/{total_pages} ▶  (Arrow keys to navigate, ESC to close)",
                False, (200, 200, 200)
            )
        else:
            page_text = self.small_font.render(
                "ESC to close",
                False, (200, 200, 200)
            )
        page_rect = page_text.get_rect(midbottom=(SCREEN_WIDTH // 2, self.book_y + self.book_height - 15))
        self.display_surface.blit(page_text, page_rect)
    
    def _render_card(self, card):
        """Render a single knowledge card"""
        content_x = self.book_x + 30
        content_y = self.book_y + 85
        max_width = self.book_width - 60
        max_content_y = self.book_y + self.book_height - 80  # Leave room for page nav
        
        # Card title
        title = self.font.render(card["title"], False, (255, 220, 100))
        self.display_surface.blit(title, (content_x, content_y))
        content_y += 35
        
        # Category badge
        category = card.get("category", "General")
        cat_data = KNOWLEDGE_CATEGORIES.get(category, {"icon": "📚", "color": (200, 200, 200)})
        cat_text = self.small_font.render(f"{cat_data['icon']} {category}", False, cat_data['color'])
        self.display_surface.blit(cat_text, (content_x, content_y))
        content_y += 25
        
        # Summary
        summary = self.small_font.render(card["summary"], False, (255, 255, 255))
        self.display_surface.blit(summary, (content_x, content_y))
        content_y += 30
        
        # Divider
        pygame.draw.line(self.display_surface, (100, 80, 60),
            (content_x, content_y), (content_x + max_width, content_y), 2)
        content_y += 10
        
        # Why it matters (wrapped text) - show all lines that fit
        why_text = card.get("why_it_matters", "").strip()
        lines = why_text.split('\n')
        line_height = 18
        
        for line in lines:
            if content_y + line_height > max_content_y - 50:  # Leave room for effect box
                break
            if line.strip():
                text_surf = self.small_font.render(line.strip(), False, (220, 220, 220))
                self.display_surface.blit(text_surf, (content_x, content_y))
            content_y += line_height
        
        # Game effect box - positioned at fixed location near bottom
        effect_y = self.book_y + self.book_height - 75
        effect_text = card.get("game_effect", "")
        if effect_text:
            effect_rect = pygame.Rect(content_x - 5, effect_y, max_width + 10, 28)
            pygame.draw.rect(self.display_surface, (60, 50, 40), effect_rect, 0, 5)
            pygame.draw.rect(self.display_surface, (100, 200, 100), effect_rect, 2, 5)
            
            effect_surf = self.small_font.render(f"🎮 {effect_text}", False, (150, 255, 150))
            self.display_surface.blit(effect_surf, (content_x, effect_y + 5))


# Singleton instance
knowledge_book_ui = None

def get_knowledge_book():
    global knowledge_book_ui
    if knowledge_book_ui is None:
        knowledge_book_ui = KnowledgeBookUI()
    return knowledge_book_ui
