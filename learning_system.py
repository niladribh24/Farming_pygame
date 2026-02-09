
from collections import deque
from knowledge_base import (
    CROP_DATA, WEATHER_EFFECTS, FERTILIZER_DATA, SOIL_IMPACTS,
    SKILL_DEFINITIONS, ACHIEVEMENT_DEFINITIONS,
    INITIAL_SOIL_HEALTH, MIN_SOIL_HEALTH, MAX_SOIL_HEALTH
)
from farm_graph import FarmGraph

class SkillNode:
    def __init__(self, skill_id, name, description):
        self.skill_id = skill_id
        self.name = name
        self.description = description
        self.unlocked = False
        self.children = []  # List of child SkillNode objects
    
    def add_child(self, child_node):
        self.children.append(child_node)
    
    def unlock(self):
        self.unlocked = True
        return f"🔓 Skill Unlocked: {self.name}"


class SkillTree:
    def __init__(self):
        self.nodes = {}  # Dictionary to store all nodes by ID
        self.root = None
        self._build_tree()
    
    def _build_tree(self):
        for skill_id, data in SKILL_DEFINITIONS.items():
            node = SkillNode(skill_id, data["name"], data["description"])
            node.unlocked = data.get("unlocked", False)
            self.nodes[skill_id] = node
        
        for skill_id, data in SKILL_DEFINITIONS.items():
            parent_node = self.nodes[skill_id]
            for child_id in data.get("children", []):
                if child_id in self.nodes:
                    parent_node.add_child(self.nodes[child_id])
        
        self.root = self.nodes.get("sustainable_farming")
    
    def check_unlocks(self, stats):
        unlocked_skills = []
        
        if stats.get("avg_soil_health", 0) >= 60:
            if not self.nodes["crop_rotation"].unlocked:
                self.nodes["crop_rotation"].unlock()
                unlocked_skills.append("Crop Rotation")
        
        if stats.get("no_overwater_days", 0) >= 3:
            if not self.nodes["water_management"].unlocked:
                self.nodes["water_management"].unlock()
                unlocked_skills.append("Water Management")
        
        if stats.get("no_overwater_days", 0) >= 5:
            if not self.nodes["drip_irrigation"].unlocked:
                self.nodes["drip_irrigation"].unlock()
                unlocked_skills.append("Drip Irrigation")
        
        if self.nodes["crop_rotation"].unlocked and stats.get("total_score", 0) >= 50:
            if not self.nodes["intercropping"].unlocked:
                self.nodes["intercropping"].unlock()
                unlocked_skills.append("Intercropping")
        
        return unlocked_skills
    
    def get_unlocked_skills(self):
        return [node.name for node in self.nodes.values() if node.unlocked]


class LearningSystem:
    
    def __init__(self):
        self.daily_actions = []
        
        self.event_queue = deque()
        self._initialize_weather_queue()
        
        self.action_stack = []
        
        self.achievements = set()
        
        self.skill_tree = SkillTree()
        
        self.farm_graph = FarmGraph()
        
        self.total_score = 0
        self.day_score = 0
        self.current_day = 1
        self.no_overwater_days = 0
        self.overwatered_today = False
        self.watered_today = False
        self.organic_fertilizer_count = 0
        self.rotation_count = 0
        
        self.notifications = []
    
    def _initialize_weather_queue(self):
        import random
        weather_types = ["normal", "rain", "heatwave", "drought"]
        weights = [0.5, 0.25, 0.15, 0.1]
        
        for _ in range(7):
            weather = random.choices(weather_types, weights=weights)[0]
            self.event_queue.append(weather)
    
    def get_current_weather(self):
        if self.event_queue:
            return self.event_queue[0]
        return "normal"
    
    def advance_day(self):
        import random
        
        if self.event_queue:
            self.event_queue.popleft()
        
        weather_types = ["normal", "rain", "heatwave", "drought"]
        weights = [0.5, 0.25, 0.15, 0.1]
        new_weather = random.choices(weather_types, weights=weights)[0]
        self.event_queue.append(new_weather)
        
        if self.watered_today and not self.overwatered_today:
            self.no_overwater_days += 1
        elif self.overwatered_today:
            self.no_overwater_days = 0
        
        self.watered_today = False
        self.overwatered_today = False
        self.current_day += 1
    
    def log_action(self, action_type, details=""):
        impact = SOIL_IMPACTS.get(action_type, {})
        message = impact.get("message", f"{action_type}: {details}")
        self.daily_actions.append(message)
        
        score_change = impact.get("score", 0)
        self.day_score += score_change
        self.total_score += score_change
        
        if message:
            self.notifications.append(message)
    
    def get_daily_summary(self):
        summary = []
        summary.append("═" * 40)
        summary.append("           DAY SUMMARY")
        summary.append("═" * 40)
        
        for action in self.daily_actions:
            summary.append(action)
        
        summary.append("")
        summary.append(f"Day Score: {'+' if self.day_score >= 0 else ''}{self.day_score}")
        summary.append(f"Total Score: {self.total_score}")
        summary.append("═" * 40)
        
        return "\n".join(summary)
    
    def clear_daily_log(self):
        self.daily_actions = []
        self.day_score = 0
    
    def push_action(self, action_type, tile_pos, previous_state):
        self.action_stack.append({
            "type": action_type,
            "pos": tile_pos,
            "previous": previous_state
        })
    
    def pop_action(self):
        if self.action_stack:
            return self.action_stack.pop()
        return None
    
    def can_undo(self):
        return len(self.action_stack) > 0
    
    def check_achievements(self, stats):
        newly_unlocked = []
        
        if stats.get("avg_soil_health", 0) >= 80:
            if "eco_farmer" not in self.achievements:
                self.achievements.add("eco_farmer")
                newly_unlocked.append(ACHIEVEMENT_DEFINITIONS["eco_farmer"])
        
        if self.no_overwater_days >= 5:
            if "water_saver" not in self.achievements:
                self.achievements.add("water_saver")
                newly_unlocked.append(ACHIEVEMENT_DEFINITIONS["water_saver"])
        
        if self.organic_fertilizer_count > 0:
            if "sustainable_starter" not in self.achievements:
                self.achievements.add("sustainable_starter")
                newly_unlocked.append(ACHIEVEMENT_DEFINITIONS["sustainable_starter"])
        
        if self.rotation_count >= 3:
            if "rotation_master" not in self.achievements:
                self.achievements.add("rotation_master")
                newly_unlocked.append(ACHIEVEMENT_DEFINITIONS["rotation_master"])
        
        for achievement in newly_unlocked:
            self.total_score += achievement["points"]
            self.notifications.append(f"🏆 Achievement: {achievement['name']} (+{achievement['points']})")
        
        return newly_unlocked
    
    def get_achievement_count(self):
        return len(self.achievements)
    
    def check_skill_unlocks(self, stats):
        stats["total_score"] = self.total_score
        stats["no_overwater_days"] = self.no_overwater_days
        
        unlocked = self.skill_tree.check_unlocks(stats)
        for skill_name in unlocked:
            self.notifications.append(f"🔓 Skill Unlocked: {skill_name}")
        
        return unlocked
    
    def get_notifications(self):
        notifs = self.notifications.copy()
        self.notifications = []
        return notifs
    
    def add_notification(self, message):
        self.notifications.append(message)
    
    def add_score(self, points, reason=""):
        if not hasattr(self, 'score'):
            self.score = 0
        self.score += points
    
    def calculate_yield_modifier(self, soil_health):
        return soil_health / 50.0
    
    def check_overwater(self, water_count, crop_type, weather):
        if crop_type and crop_type in CROP_DATA:
            water_need = CROP_DATA[crop_type]["water_need"]
            weather_data = WEATHER_EFFECTS.get(weather, WEATHER_EFFECTS["normal"])
            
            if weather == "rain":
                water_need = 0  # Rain provides all water
            else:
                water_need += weather_data.get("extra_water_need", 0)
            
            return water_count > water_need
        return water_count > 2  # Default threshold for empty soil
    
    def check_monocrop(self, last_crop, current_crop):
        if last_crop and current_crop and last_crop == current_crop:
            return True
        return False
