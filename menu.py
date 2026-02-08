# Improved Shop Menu with Tabs
# Visual tabbed interface for Buy/Sell with nice styling

import pygame
from settings import *
from timer import Timer
from knowledge_base import CROP_DATA, FERTILIZER_DATA, EQUIPMENT_DATA
from quiz_system import QUIZZES, has_badge, get_shop_discount, earned_badges

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
        self.tabs = ['SELL', 'SEEDS', 'FERT', 'EQUIP', 'QUIZ']
        self.current_tab = 0
        self.tab_width = self.width // 5
        
        # Build item lists per tab
        self._build_item_lists()
        
        # Selection
        self.index = 0
        self.timer = Timer(150)
        
        # Quiz State
        self.quiz_active = False
        self.current_quiz_id = None
        self.quiz_questions = []
        self.quiz_question_index = 0
        self.quiz_score = 0
        self.quiz_selected_option = 0
        self.quiz_feedback = ""
        self.quiz_feedback_timer = 0
        self.quiz_complete = False
        
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
            'quiz_gold': (255, 223, 0),
        }
        
        # Shop notifications (displayed on top of menu)
        self.notifications = []
        self.notification_duration = 2000  # 2 seconds

    def _build_item_lists(self):
        """Build item lists for each tab"""
        self.tab_items = {
            0: [('sell', item) for item in self.player.item_inventory.keys()],  # SELL
            1: [('buy_seed', seed) for seed in self.player.seed_inventory.keys()],  # SEEDS
            2: [('buy_fert', fert) for fert in self.player.fertilizer_inventory.keys()],  # FERTILIZERS
            3: [('buy_equip', equip) for equip in EQUIPMENT_DATA.keys()],  # EQUIPMENT
            4: [('take_quiz', q_id) for q_id in QUIZZES.keys()] # QUIZ
        }

    def display_money(self):
        # ... existing display_money code ...
        money_text = self.title_font.render(f'${self.player.money}', False, self.colors['price'])
        money_rect = money_text.get_rect(midbottom=(SCREEN_WIDTH // 2, self.menu_y + self.height - 80))
        
        # Money background
        bg_rect = money_rect.inflate(30, 15)
        pygame.draw.rect(self.display_surface, (30, 80, 30), bg_rect, 0, 8)
        pygame.draw.rect(self.display_surface, self.colors['price'], bg_rect, 2, 8)
        self.display_surface.blit(money_text, money_rect)
        
        # Show Discount if applicable
        discount = get_shop_discount()
        if discount < 1.0:
            off_pct = int((1.0 - discount) * 100)
            disc_text = self.small_font.render(f'-{off_pct}% Badge Discount Active!', False, self.colors['quiz_gold'])
            disc_rect = disc_text.get_rect(midtop=(money_rect.centerx, money_rect.bottom + 5))
            self.display_surface.blit(disc_text, disc_rect)

    def draw_tabs(self):
        # ... existing draw_tabs ...
        # Hide tabs during quiz
        if self.quiz_active:
            title_text = self.font.render("Sustainability Quiz", False, self.colors['text'])
            title_rect = title_text.get_rect(center=(self.menu_x + self.width//2, self.menu_y + 25))
            self.display_surface.blit(title_text, title_rect)
            return

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
        # ... existing draw_items ...
        if self.quiz_active:
            self.draw_quiz()
            return

        items = self.tab_items.get(self.current_tab, [])
        
        # Content area
        content_y = self.menu_y + 55
        content_height = self.height - 120
        item_height = 65 # Increased height specifically for better layout
        max_items = content_height // item_height
        
        # Scrolling
        start_idx = max(0, self.index - max_items + 1) if self.index >= max_items else 0
        
        if not items:
            empty_text = self.font.render("No items available", False, (150,150,150))
            self.display_surface.blit(empty_text, (self.menu_x + 60, content_y + 40))
        
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
            
            # Item Name
            name_color = self.colors['text']
            name_str = name
            
            if action == 'take_quiz':
                quiz = QUIZZES[item]
                if has_badge(quiz['badge']):
                    name_str = f"✓ {name} (DONE)"
                    name_color = self.colors['quiz_gold']
            
            name_text = self.font.render(name_str, False, name_color)
            self.display_surface.blit(name_text, (item_rect.x + 15, item_rect.y + 10))
            
            # Subtext (Amount or Badge)
            if action == 'take_quiz':
                quiz = QUIZZES[item]
                badge_text = self.small_font.render(f"Badge: {quiz['badge']}", False, (180, 180, 180))
                self.display_surface.blit(badge_text, (item_rect.x + 15, item_rect.y + 35))
                
                # Play button at far right
                price_text = self.font.render("PLAY", False, self.colors['buy'])
                self.display_surface.blit(price_text, (item_rect.right - 70, item_rect.centery - price_text.get_height()//2))

            else:
                # Normal Items
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
                self.display_surface.blit(price_text, (item_rect.right - 60, item_rect.centery - price_text.get_height()//2))

    def draw_quiz(self):
        """Draw the active quiz question and options"""
        # If complete, show result
        if self.quiz_complete:
            self._draw_quiz_result()
            return
            
        # Display feedback if timer is active
        if pygame.time.get_ticks() < self.quiz_feedback_timer:
            feedback_surf = self.title_font.render(self.quiz_feedback, False, self.colors['quiz_gold'])
            f_rect = feedback_surf.get_rect(center=(self.menu_x + self.width//2, self.menu_y + self.height//2))
            
            bg_rect = f_rect.inflate(40, 40)
            pygame.draw.rect(self.display_surface, (0,0,0), bg_rect)
            pygame.draw.rect(self.display_surface, self.colors['quiz_gold'], bg_rect, 3)
            self.display_surface.blit(feedback_surf, f_rect)
            return

        # Get current question
        if self.quiz_question_index < len(self.quiz_questions):
            q_data = self.quiz_questions[self.quiz_question_index]
            
            # Progress Header
            prog_text = self.small_font.render(f"Question {self.quiz_question_index + 1}/{len(self.quiz_questions)}", False, (200,200,200))
            self.display_surface.blit(prog_text, (self.menu_x + 30, self.menu_y + 80))

            # Question text (wrapping)
            question_words = q_data['q'].split(' ')
            lines = []
            current_line = ""
            for word in question_words:
                test_line = current_line + " " + word if current_line else word
                if self.font.size(test_line)[0] < self.width - 60:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            lines.append(current_line)
            
            y_offset = self.menu_y + 110
            for line in lines:
                q_surf = self.font.render(line, False, self.colors['text'])
                q_rect = q_surf.get_rect(center=(self.menu_x + self.width//2, y_offset))
                self.display_surface.blit(q_surf, q_rect)
                y_offset += 30
                
            # Draw Options
            y_offset += 30
            for idx, option in enumerate(q_data['options']):
                opt_rect = pygame.Rect(self.menu_x + 50, y_offset, self.width - 100, 45)
                
                if idx == self.quiz_selected_option:
                    pygame.draw.rect(self.display_surface, self.colors['item_hover'], opt_rect, 0, 5)
                    pygame.draw.rect(self.display_surface, self.colors['quiz_gold'], opt_rect, 2, 5)
                else:
                    pygame.draw.rect(self.display_surface, self.colors['item_bg'], opt_rect, 0, 5)
                    
                opt_text = self.small_font.render(option, False, self.colors['text'])
                self.display_surface.blit(opt_text, (opt_rect.x + 15, opt_rect.centery - opt_text.get_height()//2))
                
                y_offset += 55

    def _draw_quiz_result(self):
        """Draw final score and badge award"""
        total = len(self.quiz_questions)
        score = self.quiz_score
        
        # Result Text
        res_text = self.title_font.render(f"Quiz Complete!", False, self.colors['text'])
        res_rect = res_text.get_rect(midtop=(self.menu_x + self.width//2, self.menu_y + 100))
        self.display_surface.blit(res_text, res_rect)
        
        score_color = (100, 255, 100) if score == total else (255, 100, 100)
        score_text = self.title_font.render(f"Score: {score}/{total}", False, score_color)
        score_rect = score_text.get_rect(midtop=(self.menu_x + self.width//2, self.menu_y + 160))
        self.display_surface.blit(score_text, score_rect)
        
        msg_y = self.menu_y + 240
        
        if score == total:
             msg = "Perfect! Badge Earned!"
             badge = QUIZZES[self.current_quiz_id]['badge']
             badge_surf = self.font.render(f"🏆 {badge}", False, self.colors['quiz_gold'])
             badge_rect = badge_surf.get_rect(center=(self.menu_x + self.width//2, msg_y + 50))
             self.display_surface.blit(badge_surf, badge_rect)
        else:
             msg = "Get all questions right to earn the badge!"
             
        msg_text = self.small_font.render(msg, False, (200, 200, 200))
        msg_rect = msg_text.get_rect(center=(self.menu_x + self.width//2, msg_y))
        self.display_surface.blit(msg_text, msg_rect)
        
        # Continue prompt
        cont_text = self.small_font.render("Press SPACE to return", False, (150, 150, 150))
        cont_rect = cont_text.get_rect(midbottom=(self.menu_x + self.width//2, self.menu_y + self.height - 40))
        self.display_surface.blit(cont_text, cont_rect)

    def _get_item_details(self, action, item):
        # ... existing _get_item_details ...
        discount = get_shop_discount()
        
        if action == 'sell':
            name = item.title()
            amount = self.player.item_inventory[item]
            price = SALE_PRICES.get(item, 5)
        elif action == 'buy_seed':
            name = f"{item.title()} Seeds"
            amount = self.player.seed_inventory[item]
            base_price = CROP_DATA.get(item, {}).get('seed_price', 5)
            price = max(1, int(base_price * discount))
        elif action == 'buy_fert':
            name = FERTILIZER_DATA.get(item, {}).get('name', item)
            amount = self.player.fertilizer_inventory[item]
            base_price = FERTILIZER_DATA.get(item, {}).get('cost', 10)
            price = max(1, int(base_price * discount))
        elif action == 'buy_water':
            name = "Water Supply (+10)"
            amount = int(self.player.water_reserve)
            base_price = 5
            price = max(1, int(base_price * discount))
        elif action == 'buy_equip':
            equip_data = EQUIPMENT_DATA.get(item, {})
            name = equip_data.get('name', item.title())
            amount = self.player.equipment_inventory.get(item, 0)
            base_price = equip_data.get('cost', 25)
            price = max(1, int(base_price * discount))
        elif action == 'take_quiz':
             name = QUIZZES[item]['title'] # Use proper title
             amount = 0
             price = 0
        else:
             name = str(item)
             amount = 0
             price = 0
        
        return name, amount, price

    def update(self):
        self.input()
        
        # Draw background
        pygame.draw.rect(self.display_surface, self.colors['bg'], (self.menu_x, self.menu_y, self.width, self.height), 0, 15)
        pygame.draw.rect(self.display_surface, (100, 100, 120), (self.menu_x, self.menu_y, self.width, self.height), 4, 15)
        
        self.draw_tabs()
        self.draw_items()
        self.display_money()

    def input(self):
        keys = pygame.key.get_pressed()
        self.timer.update()

        if keys[pygame.K_ESCAPE]:
            if self.quiz_active:
                self.quiz_active = False # Back to list
                self.timer.activate()
            else:
                self.toggle_menu()

        if not self.timer.active:
            # Quiz Mode Input
            if self.quiz_active:
                if self.quiz_complete:
                    if keys[pygame.K_SPACE] or keys[pygame.K_RETURN]:
                        self.quiz_active = False
                        self.timer.activate()
                    return

                # Don't accept input during feedback timer
                if pygame.time.get_ticks() < self.quiz_feedback_timer:
                    # Check if timer just expired to advance question
                    return 
                elif self.quiz_feedback != "":
                    # Timer expired, advance question
                    self.quiz_feedback = ""
                    self.quiz_question_index += 1
                    self.quiz_selected_option = 0
                    
                    if self.quiz_question_index >= len(self.quiz_questions):
                        self.quiz_complete = True
                        # Award Badge if perfect score
                        if self.quiz_score == len(self.quiz_questions):
                            badge = QUIZZES[self.current_quiz_id]['badge']
                            earned_badges.add(badge)
                    return

                # Question Input
                q_data = self.quiz_questions[self.quiz_question_index]
                if keys[pygame.K_UP]:
                    self.quiz_selected_option = max(0, self.quiz_selected_option - 1)
                    self.timer.activate()
                if keys[pygame.K_DOWN]:
                    self.quiz_selected_option = min(len(q_data['options']) - 1, self.quiz_selected_option + 1)
                    self.timer.activate()
                if keys[pygame.K_SPACE]:
                    self.timer.activate()
                    # Check Answer
                    selected_text = q_data['options'][self.quiz_selected_option]
                    correct_text = q_data['a']
                    
                    if selected_text == correct_text:
                        self.quiz_score += 1
                        self.quiz_feedback = "Correct!"
                    else:
                        self.quiz_feedback = f"Incorrect!"
                    
                    self.quiz_feedback_timer = pygame.time.get_ticks() + 1000
            
            else:
                # Normal Menu Input
                if keys[pygame.K_RIGHT]:
                    self.current_tab = (self.current_tab + 1) % 5
                    self.index = 0
                    self.timer.activate()
                if keys[pygame.K_LEFT]:
                    self.current_tab = (self.current_tab - 1) % 5
                    self.index = 0
                    self.timer.activate()
                    
                if keys[pygame.K_UP]:
                    self.index = max(0, self.index - 1)
                    self.timer.activate()
                if keys[pygame.K_DOWN]:
                    items_len = len(self.tab_items.get(self.current_tab, []))
                    self.index = min(items_len - 1, self.index + 1)
                    self.timer.activate()
                    
                if keys[pygame.K_SPACE] or keys[pygame.K_RETURN]:
                    self.timer.activate()
                    
                    items = self.tab_items.get(self.current_tab, [])
                    if items:
                         action, item = items[self.index]
                         
                         if action == 'take_quiz':
                             self.current_quiz_id = item
                             self.quiz_questions = QUIZZES[item]['questions']
                             self.quiz_active = True
                             self.quiz_question_index = 0
                             self.quiz_score = 0
                             self.quiz_selected_option = 0
                             self.quiz_complete = False
                             self.quiz_feedback = ""
                         
                         elif action == 'buy_seed':
                            price = self._get_item_details(action, item)[2]
                            if self.player.money >= price:
                                self.player.seed_inventory[item] += 1
                                self.player.money -= price
                                
                         elif action == 'buy_fert':
                            price = self._get_item_details(action, item)[2]
                            if self.player.money >= price:
                                self.player.fertilizer_inventory[item] += 1
                                self.player.money -= price
                                
                         elif action == 'buy_water':
                            price = self._get_item_details(action, item)[2]
                            if self.player.money >= price:
                                self.player.water_reserve += 10
                                self.player.money -= price

                         elif action == 'buy_equip':
                            price = self._get_item_details(action, item)[2]
                            equip_data = EQUIPMENT_DATA.get(item, {})
                            unlock_skill = equip_data.get('unlock_skill')
                            
                            # Check skill requirement
                            can_buy = True
                            if unlock_skill and self.player.learning_system:
                                skills = self.player.learning_system.skill_tree.get_unlocked_skills()
                                if unlock_skill not in skills:
                                    can_buy = False
                                    self.notifications.append((f"🔒 Requires {unlock_skill} skill!", pygame.time.get_ticks()))
                            
                            if can_buy and self.player.money >= price:
                                self.player.equipment_inventory[item] = self.player.equipment_inventory.get(item, 0) + 1
                                self.player.money -= price
                                self.notifications.append((f"✓ Bought {equip_data.get('name', item)}!", pygame.time.get_ticks()))
                            elif can_buy:
                                self.notifications.append(("Not enough money!", pygame.time.get_ticks()))
                         elif action == 'sell':
                            price = self._get_item_details(action, item)[2]
                            if self.player.item_inventory[item] > 0:
                                self.player.item_inventory[item] -= 1
                                self.player.money += price
                                if self.player.item_inventory[item] == 0:
                                    self._build_item_lists()
                                    self.index = max(0, self.index - 1)