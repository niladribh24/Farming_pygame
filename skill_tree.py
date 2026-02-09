# Skill Tree UI - Quiz system for unlocking skills
# Press T to open the skill book during gameplay

import pygame
from settings import *
from timer import Timer

# ==============================================================================
# QUIZ DATA - Questions about sustainable agriculture (3 questions per level)
# ==============================================================================

SKILL_QUIZZES = {
    "water_mastery": {
        "name": "Water Conservation Quiz",
        "description": "Learn about drip irrigation and water efficiency",
        "skill_type": "water",  # Unlocks water skills
        "skill_rewards": ["Water 1 (100 capacity)", "Water 2 (150 capacity)", "Water 3 (200 capacity)"],
        "levels": {
            1: {
                "questions": [
                    {
                        "question": "In drip irrigation, water falls directly near the:",
                        "options": ["A) Leaves", "B) Roots", "C) Fence", "D) Path"],
                        "correct": "B"
                    },
                    {
                        "question": "Compared to flood irrigation, drip irrigation uses:",
                        "options": ["A) More water", "B) Same water", "C) Less water", "D) Rainwater"],
                        "correct": "C"
                    },
                    {
                        "question": "Drip irrigation helps keep the field free from excess:",
                        "options": ["A) Sunlight", "B) Mud", "C) Weeds", "D) Seeds"],
                        "correct": "C"
                    }
                ],
                "reward": "Water Skill 1 (100 capacity)"
            },
            2: {
                "questions": [
                    {
                        "question": "The small holes in drip pipes that release water are called:",
                        "options": ["A) Taps", "B) Emitters", "C) Motors", "D) Tanks"],
                        "correct": "B"
                    },
                    {
                        "question": "Drip irrigation is most useful during:",
                        "options": ["A) Heavy rain", "B) Floods", "C) Drought", "D) Storms"],
                        "correct": "C"
                    },
                    {
                        "question": "By giving water slowly and daily, drip irrigation helps prevent:",
                        "options": ["A) Waterlogging", "B) Sunburn", "C) Wind", "D) Shade"],
                        "correct": "A"
                    }
                ],
                "reward": "Water Skill 2 (150 capacity)"
            },
            3: {
                "questions": [
                    {
                        "question": "Drip irrigation reduces water waste by delivering water:",
                        "options": ["A) To the air", "B) Directly to soil near roots", "C) On leaves", "D) On fences"],
                        "correct": "B"
                    },
                    {
                        "question": "What is the main advantage of drip irrigation?",
                        "options": ["A) Uses more water", "B) Faster flooding", "C) Water efficiency", "D) Cheaper pipes"],
                        "correct": "C"
                    },
                    {
                        "question": "Drip systems help farmers save on:",
                        "options": ["A) Sunlight", "B) Seeds", "C) Water bills", "D) Fencing"],
                        "correct": "C"
                    }
                ],
                "reward": "Water Skill 3 (200 capacity)"
            }
        }
    },
    "speed_mastery": {
        "name": "Soil Health Quiz", 
        "description": "Master sustainable soil practices",
        "skill_type": "speed",  # Unlocks speed skills
        "skill_rewards": ["Speed 1 (110%)", "Speed 2 (120%)", "Speed 3 (130%)"],
        "levels": {
            1: {
                "questions": [
                    {
                        "question": "Dark-colored soil usually means it has more:",
                        "options": ["A) Sand", "B) Stones", "C) Organic matter", "D) Plastic"],
                        "correct": "C"
                    },
                    {
                        "question": "Adding compost to soil mainly improves:",
                        "options": ["A) Color only", "B) Soil fertility", "C) Fence height", "D) Water color"],
                        "correct": "B"
                    },
                    {
                        "question": "Cracked and hard soil is a sign of low:",
                        "options": ["A) Moisture", "B) Sunlight", "C) Wind", "D) Seeds"],
                        "correct": "A"
                    }
                ],
                "reward": "Speed Skill 1 (110%)"
            },
            2: {
                "questions": [
                    {
                        "question": "Earthworms in soil are a sign of good:",
                        "options": ["A) Pollution", "B) Soil health", "C) Pests", "D) Salinity"],
                        "correct": "B"
                    },
                    {
                        "question": "Growing different crops each season helps improve:",
                        "options": ["A) Soil nutrients", "B) Plastic waste", "C) Heat", "D) Dust"],
                        "correct": "A"
                    },
                    {
                        "question": "White crust on soil surface may indicate high:",
                        "options": ["A) Fertility", "B) Salinity", "C) Shade", "D) Rainfall"],
                        "correct": "B"
                    }
                ],
                "reward": "Speed Skill 2 (120%)"
            },
            3: {
                "questions": [
                    {
                        "question": "Healthy soil contains many beneficial:",
                        "options": ["A) Chemicals", "B) Plastics", "C) Microorganisms", "D) Metals"],
                        "correct": "C"
                    },
                    {
                        "question": "Mulching helps soil by:",
                        "options": ["A) Adding plastic", "B) Retaining moisture", "C) Increasing heat", "D) Removing nutrients"],
                        "correct": "B"
                    },
                    {
                        "question": "Leaving land fallow allows soil to:",
                        "options": ["A) Lose nutrients", "B) Recover naturally", "C) Become toxic", "D) Dry completely"],
                        "correct": "B"
                    }
                ],
                "reward": "Speed Skill 3 (130%)"
            }
        }
    },
    "drip_irrigation": {
        "name": "Drip Irrigation Quiz",
        "description": "Unlock the drip irrigation block",
        "skill_type": "drip",  # Unlocks drip irrigation item
        "skill_rewards": ["Drip Irrigation Block"],
        "levels": {
            1: {
                "questions": [
                    {
                        "question": "Drip irrigation systems deliver water through:",
                        "options": ["A) Spraying in air", "B) Thin tubes with emitters", "C) Flooding fields", "D) Buckets"],
                        "correct": "B"
                    },
                    {
                        "question": "What is the main benefit of drip irrigation for farmers?",
                        "options": ["A) Uses more water", "B) Waters faster", "C) Reduces water waste", "D) Cheaper seeds"],
                        "correct": "C"
                    },
                    {
                        "question": "Drip irrigation is best for crops that need:",
                        "options": ["A) Flooded soil", "B) Consistent moisture at roots", "C) Dry conditions", "D) Saltwater"],
                        "correct": "B"
                    }
                ],
                "reward": "Drip Irrigation Block Unlocked!"
            }
        }
    }
}


class SkillTreeUI:
    """
    Skill Tree book UI with two pages:
    - Page 1: Quizzes to complete for skills
    - Page 2: Visual skill tree showing progress
    Press T to open, ESC to close
    """
    
    def __init__(self, player):
        self.display_surface = pygame.display.get_surface()
        self.player = player
        self.font = pygame.font.Font('./font/LycheeSoda.ttf', 24)
        self.title_font = pygame.font.Font('./font/LycheeSoda.ttf', 32)
        self.small_font = pygame.font.Font('./font/LycheeSoda.ttf', 18)
        
        # UI State
        self.is_open = False
        self.current_tab = 0  # 0: Quizzes, 1: Skill Tree
        self.tabs = ["Quizzes", "Skill Tree"]
        
        # Quiz state
        self.selected_quiz = 0
        self.quiz_keys = list(SKILL_QUIZZES.keys())
        self.in_quiz = False
        self.current_quiz_key = None
        self.current_level = 1
        self.current_question_index = 0  # Track which question (0, 1, 2)
        self.correct_answers = 0  # Track correct answers in current level
        self.selected_option = 0
        self.show_result = False
        self.result_correct = False
        self.show_level_complete = False  # Show after all 3 questions
        self.level_passed = False
        
        # Timer
        self.timer = Timer(200)
        self.open_time = 0
        
        # Book dimensions
        self.book_width = 800
        self.book_height = 550
        self.book_x = (SCREEN_WIDTH - self.book_width) // 2
        self.book_y = (SCREEN_HEIGHT - self.book_height) // 2
        
        # Colors
        self.bg_color = (45, 35, 25)
        self.border_color = (139, 90, 43)
        self.highlight_color = (100, 180, 100)
        self.locked_color = (80, 80, 80)
        self.unlocked_color = (80, 200, 80)
    
    def toggle(self):
        """Open/close the skill book"""
        self.is_open = not self.is_open
        if self.is_open:
            self.open_time = pygame.time.get_ticks()
            self.in_quiz = False
            self.show_result = False
            self.show_level_complete = False
    
    def update(self):
        """Handle input"""
        if not self.is_open:
            return
        
        keys = pygame.key.get_pressed()
        self.timer.update()
        current_time = pygame.time.get_ticks()
        
        # Cooldown after opening
        if current_time - self.open_time < 300:
            return
        
        if not self.timer.active:
            # Close book
            if keys[pygame.K_ESCAPE]:
                if self.in_quiz:
                    self.in_quiz = False
                    self.show_result = False
                    self.show_level_complete = False
                else:
                    self.is_open = False
                self.timer.activate()
                return
            
            if self.show_level_complete:
                # After level complete, continue to exit
                if keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
                    self.show_level_complete = False
                    self.in_quiz = False
                    self.timer.activate()
                return
            
            if self.show_result:
                # After each question result, go to next question or complete
                if keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
                    self.show_result = False
                    self.current_question_index += 1
                    self.selected_option = 0
                    
                    # Check if all 3 questions done
                    if self.current_question_index >= 3:
                        self._complete_level()
                    self.timer.activate()
                return
            
            if self.in_quiz:
                # Quiz navigation
                if keys[pygame.K_UP]:
                    self.selected_option = max(0, self.selected_option - 1)
                    self.timer.activate()
                if keys[pygame.K_DOWN]:
                    self.selected_option = min(3, self.selected_option + 1)
                    self.timer.activate()
                if keys[pygame.K_RETURN]:
                    self._submit_answer()
                    self.timer.activate()
            else:
                # Tab switching
                if keys[pygame.K_TAB]:
                    self.current_tab = (self.current_tab + 1) % 2
                    self.timer.activate()
                
                if self.current_tab == 0:  # Quizzes tab
                    # Quiz selection
                    if keys[pygame.K_UP]:
                        self.selected_quiz = max(0, self.selected_quiz - 1)
                        self.timer.activate()
                    if keys[pygame.K_DOWN]:
                        self.selected_quiz = min(len(self.quiz_keys) - 1, self.selected_quiz + 1)
                        self.timer.activate()
                    if keys[pygame.K_RETURN]:
                        self._start_quiz()
                        self.timer.activate()
    
    def _get_quiz_progress(self, quiz_key):
        """Get current level unlocked for a quiz (0 = none, 1-3 = level)"""
        quiz = SKILL_QUIZZES[quiz_key]
        if quiz["skill_type"] == "water":
            return self.player.water_skill_level
        elif quiz["skill_type"] == "speed":
            return self.player.speed_skill_level
        elif quiz["skill_type"] == "drip":
            return 1 if self.player.drip_irrigation_unlocked else 0
        return 0
    
    def _start_quiz(self):
        """Start a quiz at the next unlockable level"""
        quiz_key = self.quiz_keys[self.selected_quiz]
        current_level = self._get_quiz_progress(quiz_key)
        
        if current_level >= 3:
            return  # Already maxed
        
        self.current_quiz_key = quiz_key
        self.current_level = current_level + 1
        self.current_question_index = 0
        self.correct_answers = 0
        self.selected_option = 0
        self.in_quiz = True
        self.show_result = False
        self.show_level_complete = False
    
    def _submit_answer(self):
        """Check the answer for current question"""
        quiz = SKILL_QUIZZES[self.current_quiz_key]
        level_data = quiz["levels"][self.current_level]
        question_data = level_data["questions"][self.current_question_index]
        
        options_map = {0: "A", 1: "B", 2: "C", 3: "D"}
        selected_letter = options_map[self.selected_option]
        
        self.result_correct = (selected_letter == question_data["correct"])
        if self.result_correct:
            self.correct_answers += 1
        
        self.show_result = True
    
    def _complete_level(self):
        """Called after all 3 questions answered"""
        # Need at least 2 out of 3 correct to pass
        self.level_passed = (self.correct_answers >= 2)
        self.show_level_complete = True
        
        if self.level_passed:
            quiz = SKILL_QUIZZES[self.current_quiz_key]
            # Award skill based on type
            if quiz["skill_type"] == "water":
                self.player.water_skill_level = self.current_level
            elif quiz["skill_type"] == "speed":
                self.player.speed_skill_level = self.current_level
            elif quiz["skill_type"] == "drip":
                self.player.drip_irrigation_unlocked = True
            self.player._apply_skill_effects()
    
    def display(self):
        """Render the skill book"""
        if not self.is_open:
            return
        
        # Dim background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.display_surface.blit(overlay, (0, 0))
        
        # Book background
        book_rect = pygame.Rect(self.book_x, self.book_y, self.book_width, self.book_height)
        pygame.draw.rect(self.display_surface, self.bg_color, book_rect, 0, 10)
        pygame.draw.rect(self.display_surface, self.border_color, book_rect, 4, 10)
        
        if self.show_level_complete:
            self._render_level_complete()
        elif self.show_result:
            self._render_question_result()
        elif self.in_quiz:
            self._render_quiz()
        else:
            # Title
            title = self.title_font.render("Skill Book", False, (255, 230, 180))
            title_rect = title.get_rect(midtop=(SCREEN_WIDTH // 2, self.book_y + 15))
            self.display_surface.blit(title, title_rect)
            
            # Tab buttons
            self._render_tabs()
            
            # Content
            if self.current_tab == 0:
                self._render_quizzes_tab()
            else:
                self._render_skill_tree_tab()
            
            # Help text
            help_text = "TAB: Switch Page | Up/Down: Select | ENTER: Start | ESC: Close"
            help_surf = self.small_font.render(help_text, False, (150, 150, 150))
            help_rect = help_surf.get_rect(midbottom=(SCREEN_WIDTH // 2, self.book_y + self.book_height - 10))
            self.display_surface.blit(help_surf, help_rect)
    
    def _render_tabs(self):
        """Render the tab buttons"""
        tab_y = self.book_y + 55
        tab_width = 150
        
        for i, tab_name in enumerate(self.tabs):
            tab_x = self.book_x + 100 + i * (tab_width + 20)
            tab_rect = pygame.Rect(tab_x, tab_y, tab_width, 35)
            
            if i == self.current_tab:
                pygame.draw.rect(self.display_surface, self.highlight_color, tab_rect, 0, 6)
                text_color = (255, 255, 255)
            else:
                pygame.draw.rect(self.display_surface, (60, 50, 40), tab_rect, 0, 6)
                pygame.draw.rect(self.display_surface, (100, 80, 60), tab_rect, 2, 6)
                text_color = (180, 180, 180)
            
            text = self.font.render(tab_name, False, text_color)
            text_rect = text.get_rect(center=tab_rect.center)
            self.display_surface.blit(text, text_rect)
    
    def _render_quizzes_tab(self):
        """Render the quizzes list"""
        start_y = self.book_y + 110
        
        for i, quiz_key in enumerate(self.quiz_keys):
            quiz = SKILL_QUIZZES[quiz_key]
            progress = self._get_quiz_progress(quiz_key)
            
            # Entry rect - taller to show reward info
            entry_rect = pygame.Rect(self.book_x + 50, start_y + i * 130, self.book_width - 100, 115)
            
            # Highlight selected
            if i == self.selected_quiz:
                pygame.draw.rect(self.display_surface, (70, 60, 50), entry_rect, 0, 8)
                pygame.draw.rect(self.display_surface, self.highlight_color, entry_rect, 3, 8)
            else:
                pygame.draw.rect(self.display_surface, (55, 45, 35), entry_rect, 0, 8)
                pygame.draw.rect(self.display_surface, (100, 80, 60), entry_rect, 2, 8)
            
            # Quiz name
            name_surf = self.font.render(quiz["name"], False, (255, 220, 100))
            self.display_surface.blit(name_surf, (entry_rect.left + 20, entry_rect.top + 10))
            
            # Description
            desc_surf = self.small_font.render(quiz["description"], False, (200, 200, 200))
            self.display_surface.blit(desc_surf, (entry_rect.left + 20, entry_rect.top + 38))
            
            # Skill rewards info (handle variable number of rewards)
            rewards = quiz['skill_rewards']
            if len(rewards) == 1:
                reward_text = f"Reward: {rewards[0]}"
            elif len(rewards) == 2:
                reward_text = f"Rewards: {rewards[0]} -> {rewards[1]}"
            else:
                reward_text = f"Rewards: {rewards[0]} -> {rewards[1]} -> {rewards[2]}"
            reward_surf = self.small_font.render(reward_text, False, (100, 200, 255))
            self.display_surface.blit(reward_surf, (entry_rect.left + 20, entry_rect.top + 58))
            
            # Progress indicators (circles based on number of levels)
            num_levels = len(quiz["levels"])
            for lvl in range(1, num_levels + 1):
                circle_x = entry_rect.right - 40 - (num_levels - lvl) * 35
                circle_y = entry_rect.top + 30
                
                if progress >= lvl:
                    color = self.unlocked_color
                    pygame.draw.circle(self.display_surface, color, (circle_x, circle_y), 12)
                    lvl_text = self.small_font.render(str(lvl), False, (255, 255, 255))
                else:
                    color = self.locked_color
                    pygame.draw.circle(self.display_surface, color, (circle_x, circle_y), 12, 2)
                    lvl_text = self.small_font.render(str(lvl), False, (100, 100, 100))
                
                lvl_rect = lvl_text.get_rect(center=(circle_x, circle_y))
                self.display_surface.blit(lvl_text, lvl_rect)
            
            # Next level hint
            if progress < num_levels:
                hint_text = f"Next: Level {progress + 1} (3 questions, need 2 correct)"
                hint_surf = self.small_font.render(hint_text, False, (150, 200, 150))
                self.display_surface.blit(hint_surf, (entry_rect.left + 20, entry_rect.bottom - 25))
            else:
                complete_surf = self.small_font.render("COMPLETE!", False, (100, 255, 100))
                self.display_surface.blit(complete_surf, (entry_rect.left + 20, entry_rect.bottom - 25))
    
    def _render_skill_tree_tab(self):
        """Render the skill tree diagram - Farmer at top, skills branch down"""
        center_x = SCREEN_WIDTH // 2
        start_y = self.book_y + 100
        
        # Root node (Farmer) at TOP
        root_rect = pygame.Rect(center_x - 60, start_y, 120, 40)
        pygame.draw.rect(self.display_surface, (100, 80, 60), root_rect, 0, 8)
        pygame.draw.rect(self.display_surface, self.border_color, root_rect, 2, 8)
        root_text = self.font.render("Farmer", False, (255, 255, 255))
        root_text_rect = root_text.get_rect(center=root_rect.center)
        self.display_surface.blit(root_text, root_text_rect)
        
        # Connecting lines from Farmer to branches
        branch_start_y = start_y + 50
        pygame.draw.line(self.display_surface, (139, 90, 43),
                        (center_x, start_y + 40), (center_x, branch_start_y + 10), 4)
        
        # Horizontal line connecting to both branches
        water_x = center_x - 160
        speed_x = center_x + 160
        pygame.draw.line(self.display_surface, (139, 90, 43),
                        (water_x, branch_start_y + 10), (speed_x, branch_start_y + 10), 4)
        
        # Vertical lines down to branch titles
        pygame.draw.line(self.display_surface, (139, 90, 43),
                        (water_x, branch_start_y + 10), (water_x, branch_start_y + 30), 4)
        pygame.draw.line(self.display_surface, (139, 90, 43),
                        (speed_x, branch_start_y + 10), (speed_x, branch_start_y + 30), 4)
        
        # Water Skills title
        water_title_y = branch_start_y + 55
        water_title_surf = self.font.render("Water Skills", False, (70, 150, 255))
        water_title_rect = water_title_surf.get_rect(center=(water_x, water_title_y))
        self.display_surface.blit(water_title_surf, water_title_rect)
        
        # Horizontal line from Water Skills title to two branches
        sub_branch_y = water_title_y + 25
        water_sub_left = water_x - 70  # Water 1,2,3 branch
        water_sub_right = water_x + 70  # Drip Irrigation branch
        
        pygame.draw.line(self.display_surface, (139, 90, 43),
                        (water_sub_left, sub_branch_y), (water_sub_right, sub_branch_y), 3)
        pygame.draw.line(self.display_surface, (139, 90, 43),
                        (water_x, water_title_y + 15), (water_x, sub_branch_y), 3)
        
        # Vertical lines down from horizontal branch
        pygame.draw.line(self.display_surface, (139, 90, 43),
                        (water_sub_left, sub_branch_y), (water_sub_left, sub_branch_y + 20), 3)
        pygame.draw.line(self.display_surface, (139, 90, 43),
                        (water_sub_right, sub_branch_y), (water_sub_right, sub_branch_y + 20), 3)
        
        # Water 1, 2, 3 nodes (left sub-branch)
        for i, skill_name in enumerate(["Water 1 (100)", "Water 2 (150)", "Water 3 (200)"]):
            node_y = sub_branch_y + 45 + i * 55
            node_rect = pygame.Rect(water_sub_left - 60, node_y, 120, 32)
            
            level = i + 1
            is_unlocked = self.player.water_skill_level >= level
            
            if is_unlocked:
                pygame.draw.rect(self.display_surface, (70, 150, 255), node_rect, 0, 6)
                text_color = (255, 255, 255)
            else:
                pygame.draw.rect(self.display_surface, self.locked_color, node_rect, 0, 6)
                pygame.draw.rect(self.display_surface, (60, 60, 60), node_rect, 2, 6)
                text_color = (120, 120, 120)
            
            skill_text = self.small_font.render(skill_name, False, text_color)
            skill_rect = skill_text.get_rect(center=node_rect.center)
            self.display_surface.blit(skill_text, skill_rect)
            
            # Connector line
            if i < 2:
                pygame.draw.line(self.display_surface, (100, 80, 60),
                                (water_sub_left, node_y + 32), (water_sub_left, node_y + 55), 2)
        
        # Drip Irrigation node (right sub-branch)
        drip_y = sub_branch_y + 45
        drip_unlocked = self.player.drip_irrigation_unlocked
        drip_rect = pygame.Rect(water_sub_right - 65, drip_y, 130, 32)
        
        if drip_unlocked:
            pygame.draw.rect(self.display_surface, (100, 200, 255), drip_rect, 0, 6)
            text_color = (255, 255, 255)
        else:
            pygame.draw.rect(self.display_surface, self.locked_color, drip_rect, 0, 6)
            pygame.draw.rect(self.display_surface, (60, 60, 60), drip_rect, 2, 6)
            text_color = (120, 120, 120)
        
        drip_text = self.small_font.render("Drip Irrigation", False, text_color)
        drip_text_rect = drip_text.get_rect(center=drip_rect.center)
        self.display_surface.blit(drip_text, drip_text_rect)
        
        # Speed Skills Branch (right) - skills go DOWN
        self._render_skill_branch_down(speed_x, branch_start_y + 55, "Speed Skills",
                                 ["Speed 1 (110%)", "Speed 2 (120%)", "Speed 3 (130%)"],
                                 self.player.speed_skill_level, (255, 180, 70))
    
    def _render_skill_branch_down(self, x, start_y, title, skills, current_level, color):
        """Render a skill branch going downward (like tree roots)"""
        # Title
        title_surf = self.font.render(title, False, color)
        title_rect = title_surf.get_rect(center=(x, start_y))
        self.display_surface.blit(title_surf, title_rect)
        
        # Vertical connector line going DOWN
        pygame.draw.line(self.display_surface, (100, 80, 60),
                        (x, start_y + 20), (x, start_y + 200), 3)
        
        # Skill nodes going DOWN
        for i, skill_name in enumerate(skills):
            node_y = start_y + 45 + i * 60
            node_rect = pygame.Rect(x - 70, node_y, 140, 35)
            
            level = i + 1
            is_unlocked = current_level >= level
            
            if is_unlocked:
                pygame.draw.rect(self.display_surface, color, node_rect, 0, 6)
                text_color = (255, 255, 255)
                # Glow effect
                glow_rect = node_rect.inflate(6, 6)
                pygame.draw.rect(self.display_surface, (*color, 100), glow_rect, 2, 8)
            else:
                pygame.draw.rect(self.display_surface, self.locked_color, node_rect, 0, 6)
                pygame.draw.rect(self.display_surface, (60, 60, 60), node_rect, 2, 6)
                text_color = (120, 120, 120)
            
            skill_text = self.small_font.render(skill_name, False, text_color)
            skill_rect = skill_text.get_rect(center=node_rect.center)
            self.display_surface.blit(skill_text, skill_rect)
    
    # Keep old method for compatibility but it's no longer used
    def _render_skill_branch(self, x, start_y, title, skills, current_level, color):
        """Legacy method - use _render_skill_branch_down instead"""
        self._render_skill_branch_down(x, start_y, title, skills, current_level, color)
    
    def _render_quiz(self):
        """Render the active quiz question"""
        quiz = SKILL_QUIZZES[self.current_quiz_key]
        level_data = quiz["levels"][self.current_level]
        question_data = level_data["questions"][self.current_question_index]
        
        # Title with question counter
        title = self.title_font.render(f"{quiz['name']} - Level {self.current_level}", False, (255, 220, 100))
        title_rect = title.get_rect(midtop=(SCREEN_WIDTH // 2, self.book_y + 15))
        self.display_surface.blit(title, title_rect)
        
        # Question counter
        counter_text = f"Question {self.current_question_index + 1}/3"
        counter_surf = self.font.render(counter_text, False, (200, 200, 200))
        counter_rect = counter_surf.get_rect(midtop=(SCREEN_WIDTH // 2, self.book_y + 55))
        self.display_surface.blit(counter_surf, counter_rect)
        
        # Question
        question = self.font.render(question_data["question"], False, (255, 255, 255))
        question_rect = question.get_rect(midtop=(SCREEN_WIDTH // 2, self.book_y + 95))
        self.display_surface.blit(question, question_rect)
        
        # Options
        options_start_y = self.book_y + 150
        for i, option in enumerate(question_data["options"]):
            option_rect = pygame.Rect(self.book_x + 100, options_start_y + i * 65, self.book_width - 200, 50)
            
            if i == self.selected_option:
                pygame.draw.rect(self.display_surface, (180, 150, 50), option_rect, 0, 8)  # Yellow box
                pygame.draw.rect(self.display_surface, (255, 220, 100), option_rect, 3, 8)  # Yellow border
            else:
                pygame.draw.rect(self.display_surface, (60, 50, 40), option_rect, 0, 8)
                pygame.draw.rect(self.display_surface, (100, 80, 60), option_rect, 2, 8)
            
            option_text = self.font.render(option, False, (255, 255, 255))
            option_text_rect = option_text.get_rect(midleft=(option_rect.left + 20, option_rect.centery))
            self.display_surface.blit(option_text, option_text_rect)
        
        # Correct count so far
        score_text = f"Correct so far: {self.correct_answers}/3"
        score_surf = self.small_font.render(score_text, False, (150, 255, 150))
        score_rect = score_surf.get_rect(midbottom=(SCREEN_WIDTH // 2, self.book_y + self.book_height - 50))
        self.display_surface.blit(score_surf, score_rect)
        
        # Help
        help_text = "Up/Down: Select | ENTER: Submit | ESC: Back"
        help_surf = self.small_font.render(help_text, False, (150, 150, 150))
        help_rect = help_surf.get_rect(midbottom=(SCREEN_WIDTH // 2, self.book_y + self.book_height - 15))
        self.display_surface.blit(help_surf, help_rect)
    
    def _render_question_result(self):
        """Render result after answering a question"""
        if self.result_correct:
            title = self.title_font.render("CORRECT!", False, (100, 255, 100))
        else:
            title = self.title_font.render("INCORRECT", False, (255, 100, 100))
        
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, self.book_y + 150))
        self.display_surface.blit(title, title_rect)
        
        # Show correct answer
        quiz = SKILL_QUIZZES[self.current_quiz_key]
        level_data = quiz["levels"][self.current_level]
        question_data = level_data["questions"][self.current_question_index]
        correct_answer = question_data["correct"]
        
        for opt in question_data["options"]:
            if opt.startswith(correct_answer + ")"):
                answer_text = f"Correct answer: {opt}"
                break
        
        answer_surf = self.font.render(answer_text, False, (200, 255, 200))
        answer_rect = answer_surf.get_rect(center=(SCREEN_WIDTH // 2, self.book_y + 220))
        self.display_surface.blit(answer_surf, answer_rect)
        
        # Progress
        progress_text = f"Score: {self.correct_answers}/3 (Need 2 to pass)"
        progress_surf = self.font.render(progress_text, False, (200, 200, 200))
        progress_rect = progress_surf.get_rect(center=(SCREEN_WIDTH // 2, self.book_y + 280))
        self.display_surface.blit(progress_surf, progress_rect)
        
        # Continue prompt
        continue_text = "Press ENTER or SPACE to continue"
        continue_surf = self.small_font.render(continue_text, False, (200, 200, 200))
        continue_rect = continue_surf.get_rect(center=(SCREEN_WIDTH // 2, self.book_y + self.book_height - 50))
        self.display_surface.blit(continue_surf, continue_rect)
    
    def _render_level_complete(self):
        """Render level completion screen"""
        quiz = SKILL_QUIZZES[self.current_quiz_key]
        
        if self.level_passed:
            title = self.title_font.render("LEVEL COMPLETE!", False, (100, 255, 100))
            message = f"You got {self.correct_answers}/3 correct!"
            reward_text = f"Unlocked: {quiz['levels'][self.current_level]['reward']}"
            msg_color = (150, 255, 150)
        else:
            title = self.title_font.render("LEVEL FAILED", False, (255, 100, 100))
            message = f"You got {self.correct_answers}/3 correct (need 2)"
            reward_text = "Try again to unlock the skill!"
            msg_color = (255, 150, 150)
        
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, self.book_y + 120))
        self.display_surface.blit(title, title_rect)
        
        msg_surf = self.font.render(message, False, msg_color)
        msg_rect = msg_surf.get_rect(center=(SCREEN_WIDTH // 2, self.book_y + 200))
        self.display_surface.blit(msg_surf, msg_rect)
        
        reward_surf = self.font.render(reward_text, False, (255, 220, 100))
        reward_rect = reward_surf.get_rect(center=(SCREEN_WIDTH // 2, self.book_y + 270))
        self.display_surface.blit(reward_surf, reward_rect)
        
        # Continue prompt
        continue_text = "Press ENTER or SPACE to continue"
        continue_surf = self.small_font.render(continue_text, False, (200, 200, 200))
        continue_rect = continue_surf.get_rect(center=(SCREEN_WIDTH // 2, self.book_y + self.book_height - 50))
        self.display_surface.blit(continue_surf, continue_rect)


# Singleton
_skill_tree_instance = None

def get_skill_tree(player=None):
    global _skill_tree_instance
    if _skill_tree_instance is None and player is not None:
        _skill_tree_instance = SkillTreeUI(player)
    return _skill_tree_instance
