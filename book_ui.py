
import pygame
from settings import *
from knowledge_book import KNOWLEDGE_CARDS, KNOWLEDGE_CATEGORIES, QUICK_TIPS
from knowledge_base import ACHIEVEMENT_DEFINITIONS, SKILL_DEFINITIONS
from timer import Timer

class KnowledgeBookUI:
    
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font('./font/LycheeSoda.ttf', 28)
        self.title_font = pygame.font.Font('./font/LycheeSoda.ttf', 36)
        self.small_font = pygame.font.Font('./font/LycheeSoda.ttf', 18)
        
        self.is_open = False
        self.current_page = 0
        self.cards = list(KNOWLEDGE_CARDS.keys())
        self.learning_system = None
        
        self.tabs = ["Guide"]
        self.active_tab = 0 # 0: Guide only
        
        self.timer = Timer(200)
        
        self.open_time = 0
        
        self.book_width = 800
        self.book_height = 650
        self.book_x = (SCREEN_WIDTH - self.book_width) // 2
        self.book_y = (SCREEN_HEIGHT - self.book_height) // 2
    
    def toggle(self):
        self.is_open = not self.is_open
        if self.is_open:
            self.open_time = pygame.time.get_ticks()
            self.cards = list(KNOWLEDGE_CARDS.keys())
    
    def update(self):
        if not self.is_open:
            return
        
        keys = pygame.key.get_pressed()
        self.timer.update()
        current_time = pygame.time.get_ticks()
        
        if current_time - self.open_time < 500:
            return
        
        if keys[pygame.K_ESCAPE]:
            if not self.timer.active:
                self.timer.activate()
                self.is_open = False
        
        if not self.timer.active:
            if keys[pygame.K_LEFT]:
                self.current_page = max(0, self.current_page - 1)
                self.timer.activate()
            
            if keys[pygame.K_RIGHT]:
                if self.active_tab == 0:
                    limit = len(self.cards) - 1
                elif self.active_tab == 1:
                    limit = 5 # roughly
                else:
                    limit = 0 # Skills fits on one page
                
                self.current_page = min(limit, self.current_page + 1)
                self.timer.activate()

    
    def display(self):
        if not self.is_open:
            return
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.display_surface.blit(overlay, (0, 0))
        
        book_rect = pygame.Rect(self.book_x, self.book_y, self.book_width, self.book_height)
        pygame.draw.rect(self.display_surface, (45, 35, 25), book_rect, 0, 10)
        pygame.draw.rect(self.display_surface, (139, 90, 43), book_rect, 4, 10)
        
        title = self.title_font.render("📖 Sustainable Farming Guide", False, (255, 230, 180))
        title_rect = title.get_rect(midtop=(SCREEN_WIDTH // 2, self.book_y + 15))
        self.display_surface.blit(title, title_rect)

        
        self._render_guide_content()

    def _render_guide_content(self):
        if self.cards:
            card_key = self.cards[self.current_page]
            card = KNOWLEDGE_CARDS[card_key]
            self._render_card(card)
        
        page_text = self.small_font.render(
            f"Page {self.current_page + 1}/{len(self.cards)}", 
            False, 
            (200, 200, 200)
        )
        page_rect = page_text.get_rect(midbottom=(SCREEN_WIDTH // 2, self.book_y + self.book_height - 15))
        self.display_surface.blit(page_text, page_rect)

    def _render_card(self, card):
        content_x = self.book_x + 30
        content_y = self.book_y + 85
        max_width = self.book_width - 60
        max_content_y = self.book_y + self.book_height - 80  # Leave room for page nav
        
        title = self.font.render(card["title"], False, (255, 220, 100))
        self.display_surface.blit(title, (content_x, content_y))
        content_y += 35
        
        category = card.get("category", "General")
        cat_data = KNOWLEDGE_CATEGORIES.get(category, {"icon": "📚", "color": (200, 200, 200)})
        cat_text = self.small_font.render(f"{cat_data['icon']} {category}", False, cat_data['color'])
        self.display_surface.blit(cat_text, (content_x, content_y))
        content_y += 25
        
        summary = self.small_font.render(card["summary"], False, (255, 255, 255))
        self.display_surface.blit(summary, (content_x, content_y))
        content_y += 30
        
        pygame.draw.line(self.display_surface, (100, 80, 60),
            (content_x, content_y), (content_x + max_width, content_y), 2)
        content_y += 10
        
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
        
        effect_y = self.book_y + self.book_height - 75
        effect_text = card.get("game_effect", "")
        if effect_text:
            effect_rect = pygame.Rect(content_x - 5, effect_y, max_width + 10, 28)
            pygame.draw.rect(self.display_surface, (60, 50, 40), effect_rect, 0, 5)
            pygame.draw.rect(self.display_surface, (100, 200, 100), effect_rect, 2, 5)
            
            effect_surf = self.small_font.render(f"🎮 {effect_text}", False, (150, 255, 150))
            self.display_surface.blit(effect_surf, (content_x, effect_y + 5))


knowledge_book_ui = None

def get_knowledge_book():
    global knowledge_book_ui
    if knowledge_book_ui is None:
        knowledge_book_ui = KnowledgeBookUI()
    return knowledge_book_ui
