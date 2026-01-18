# Learning System - Core Data Structures Module
# Contains: List (daily log), Queue (events), Stack (undo), Set (achievements), Tree (skills)

from collections import deque
from knowledge_base import (
    CROP_DATA, WEATHER_EFFECTS, FERTILIZER_DATA, SOIL_IMPACTS,
    SKILL_DEFINITIONS, ACHIEVEMENT_DEFINITIONS,
    INITIAL_SOIL_HEALTH, MIN_SOIL_HEALTH, MAX_SOIL_HEALTH
)
from farm_graph import FarmGraph

# ==============================================================================
# SKILL NODE CLASS (Tree Data Structure)
# ==============================================================================
class SkillNode:
    """
    Represents a node in the skill tree.
    Each node can have multiple children, forming a hierarchical structure.
    
    Data Structure: TREE
    Purpose: Hierarchical skill unlock system for gamified learning
    """
    def __init__(self, skill_id, name, description):
        self.skill_id = skill_id
        self.name = name
        self.description = description
        self.unlocked = False
        self.children = []  # List of child SkillNode objects
    
    def add_child(self, child_node):
        """Add a child skill node"""
        self.children.append(child_node)
    
    def unlock(self):
        """Unlock this skill"""
        self.unlocked = True
        return f"🔓 Skill Unlocked: {self.name}"


# ==============================================================================
# SKILL TREE CLASS
# ==============================================================================
class SkillTree:
    """
    Hierarchical tree structure for sustainable farming skills.
    
    Data Structure: TREE (nodes with parent-child relationships)
    Purpose: Players unlock skills by practicing sustainable farming
    """
    def __init__(self):
        self.nodes = {}  # Dictionary to store all nodes by ID
        self.root = None
        self._build_tree()
    
    def _build_tree(self):
        """Build the skill tree from definitions"""
        # Create all nodes first
        for skill_id, data in SKILL_DEFINITIONS.items():
            node = SkillNode(skill_id, data["name"], data["description"])
            node.unlocked = data.get("unlocked", False)
            self.nodes[skill_id] = node
        
        # Set up parent-child relationships
        for skill_id, data in SKILL_DEFINITIONS.items():
            parent_node = self.nodes[skill_id]
            for child_id in data.get("children", []):
                if child_id in self.nodes:
                    parent_node.add_child(self.nodes[child_id])
        
        # Set root
        self.root = self.nodes.get("sustainable_farming")
    
    def check_unlocks(self, stats):
        """Check if any skills should be unlocked based on current stats"""
        unlocked_skills = []
        
        # Crop Rotation: soil_health >= 60
        if stats.get("avg_soil_health", 0) >= 60:
            if not self.nodes["crop_rotation"].unlocked:
                self.nodes["crop_rotation"].unlock()
                unlocked_skills.append("Crop Rotation")
        
        # Water Management: no overwater for 3 days
        if stats.get("no_overwater_days", 0) >= 3:
            if not self.nodes["water_management"].unlocked:
                self.nodes["water_management"].unlock()
                unlocked_skills.append("Water Management")
        
        # Drip Irrigation: no overwater for 5 days
        if stats.get("no_overwater_days", 0) >= 5:
            if not self.nodes["drip_irrigation"].unlocked:
                self.nodes["drip_irrigation"].unlock()
                unlocked_skills.append("Drip Irrigation")
        
        # Intercropping: crop_rotation unlocked and score >= 50
        if self.nodes["crop_rotation"].unlocked and stats.get("total_score", 0) >= 50:
            if not self.nodes["intercropping"].unlocked:
                self.nodes["intercropping"].unlock()
                unlocked_skills.append("Intercropping")
        
        return unlocked_skills
    
    def get_unlocked_skills(self):
        """Return list of all unlocked skill names"""
        return [node.name for node in self.nodes.values() if node.unlocked]


# ==============================================================================
# LEARNING SYSTEM - MAIN CLASS
# ==============================================================================
class LearningSystem:
    """
    Central learning system that tracks all player actions and their consequences.
    
    Contains:
    - List: daily_actions (sequential action log)
    - Queue (deque): event_queue (FIFO weather events)  
    - Stack (list): action_stack (LIFO undo functionality)
    - Set: achievements (fast membership check)
    - Tree: skill_tree (hierarchical unlocks)
    """
    
    def __init__(self):
        # DATA STRUCTURE 1: LIST - Daily Action Log
        # Tracks all actions performed today for end-of-day summary
        self.daily_actions = []
        
        # DATA STRUCTURE 2: QUEUE (deque) - Event Queue
        # FIFO structure for weather events
        self.event_queue = deque()
        self._initialize_weather_queue()
        
        # DATA STRUCTURE 3: STACK - Action Stack for Undo
        # LIFO structure - last action can be undone first
        self.action_stack = []
        
        # DATA STRUCTURE 4: SET - Achievements
        # Fast O(1) membership check for unlocked achievements
        self.achievements = set()
        
        # DATA STRUCTURE 5: TREE - Skill Tree
        self.skill_tree = SkillTree()
        
        # DATA STRUCTURE 6: GRAPH - Farm Map Network
        # Models farm locations and paths for traversal/pathfinding
        self.farm_graph = FarmGraph()
        
        # Game statistics
        self.total_score = 0
        self.day_score = 0
        self.current_day = 1
        self.no_overwater_days = 0
        self.overwatered_today = False
        self.watered_today = False
        self.organic_fertilizer_count = 0
        self.rotation_count = 0
        
        # Notification queue for UI
        self.notifications = []
    
    def _initialize_weather_queue(self):
        """Initialize weather queue with some events"""
        import random
        weather_types = ["normal", "rain", "heatwave", "drought"]
        weights = [0.5, 0.25, 0.15, 0.1]
        
        # Pre-populate 7 days of weather
        for _ in range(7):
            weather = random.choices(weather_types, weights=weights)[0]
            self.event_queue.append(weather)
    
    def get_current_weather(self):
        """Get today's weather (peek at front of queue)"""
        if self.event_queue:
            return self.event_queue[0]
        return "normal"
    
    def advance_day(self):
        """Process day transition - dequeue current weather, enqueue new"""
        import random
        
        # Dequeue today's weather (FIFO - remove from left)
        if self.event_queue:
            self.event_queue.popleft()
        
        # Enqueue new weather for future (add to right)
        weather_types = ["normal", "rain", "heatwave", "drought"]
        weights = [0.5, 0.25, 0.15, 0.1]
        new_weather = random.choices(weather_types, weights=weights)[0]
        self.event_queue.append(new_weather)
        
        # Track consecutive no-overwater days
        # Track consecutive no-overwater days (must have watered to count)
        if self.watered_today and not self.overwatered_today:
            self.no_overwater_days += 1
        elif self.overwatered_today:
            self.no_overwater_days = 0
        
        self.watered_today = False
        self.overwatered_today = False
        self.current_day += 1
    
    # =========================================================================
    # ACTION LOGGING (List)
    # =========================================================================
    def log_action(self, action_type, details=""):
        """Log an action to the daily list"""
        impact = SOIL_IMPACTS.get(action_type, {})
        message = impact.get("message", f"{action_type}: {details}")
        self.daily_actions.append(message)
        
        # Update day score
        score_change = impact.get("score", 0)
        self.day_score += score_change
        self.total_score += score_change
        
        # Add notification
        if message:
            self.notifications.append(message)
    
    def get_daily_summary(self):
        """Get end-of-day summary from action list"""
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
        """Clear daily actions for new day"""
        self.daily_actions = []
        self.day_score = 0
    
    # =========================================================================
    # UNDO SYSTEM (Stack)
    # =========================================================================
    def push_action(self, action_type, tile_pos, previous_state):
        """Push an action onto the undo stack"""
        self.action_stack.append({
            "type": action_type,
            "pos": tile_pos,
            "previous": previous_state
        })
    
    def pop_action(self):
        """Pop the last action from stack for undo"""
        if self.action_stack:
            return self.action_stack.pop()
        return None
    
    def can_undo(self):
        """Check if undo is available"""
        return len(self.action_stack) > 0
    
    # =========================================================================
    # ACHIEVEMENTS (Set)
    # =========================================================================
    def check_achievements(self, stats):
        """Check and unlock achievements based on current stats"""
        newly_unlocked = []
        
        # Eco Farmer: soil_health >= 80
        if stats.get("avg_soil_health", 0) >= 80:
            if "eco_farmer" not in self.achievements:
                self.achievements.add("eco_farmer")
                newly_unlocked.append(ACHIEVEMENT_DEFINITIONS["eco_farmer"])
        
        # Water Saver: no overwater for 5 days
        if self.no_overwater_days >= 5:
            if "water_saver" not in self.achievements:
                self.achievements.add("water_saver")
                newly_unlocked.append(ACHIEVEMENT_DEFINITIONS["water_saver"])
        
        # Sustainable Starter: used organic fertilizer
        if self.organic_fertilizer_count > 0:
            if "sustainable_starter" not in self.achievements:
                self.achievements.add("sustainable_starter")
                newly_unlocked.append(ACHIEVEMENT_DEFINITIONS["sustainable_starter"])
        
        # Rotation Master: 3 successful rotations
        if self.rotation_count >= 3:
            if "rotation_master" not in self.achievements:
                self.achievements.add("rotation_master")
                newly_unlocked.append(ACHIEVEMENT_DEFINITIONS["rotation_master"])
        
        # Award points for new achievements
        for achievement in newly_unlocked:
            self.total_score += achievement["points"]
            self.notifications.append(f"🏆 Achievement: {achievement['name']} (+{achievement['points']})")
        
        return newly_unlocked
    
    def get_achievement_count(self):
        """Return number of unlocked achievements"""
        return len(self.achievements)
    
    # =========================================================================
    # SKILL TREE
    # =========================================================================
    def check_skill_unlocks(self, stats):
        """Check for new skill unlocks"""
        stats["total_score"] = self.total_score
        stats["no_overwater_days"] = self.no_overwater_days
        
        unlocked = self.skill_tree.check_unlocks(stats)
        for skill_name in unlocked:
            self.notifications.append(f"🔓 Skill Unlocked: {skill_name}")
        
        return unlocked
    
    # =========================================================================
    # NOTIFICATIONS
    # =========================================================================
    def get_notifications(self):
        """Get and clear pending notifications"""
        notifs = self.notifications.copy()
        self.notifications = []
        return notifs
    
    def add_notification(self, message):
        """Add a notification message"""
        self.notifications.append(message)
    
    # =========================================================================
    # CONSEQUENCE CALCULATIONS
    # =========================================================================
    def calculate_yield_modifier(self, soil_health):
        """Calculate yield based on soil health"""
        # soil_health 50 = 100% yield, 100 = 200%, 0 = 0%
        return soil_health / 50.0
    
    def check_overwater(self, water_count, crop_type, weather):
        """Check if tile is over-watered"""
        if crop_type and crop_type in CROP_DATA:
            water_need = CROP_DATA[crop_type]["water_need"]
            weather_data = WEATHER_EFFECTS.get(weather, WEATHER_EFFECTS["normal"])
            
            # Adjust for weather
            if weather == "rain":
                water_need = 0  # Rain provides all water
            else:
                water_need += weather_data.get("extra_water_need", 0)
            
            return water_count > water_need
        return water_count > 2  # Default threshold for empty soil
    
    def check_monocrop(self, last_crop, current_crop):
        """Check if player is monocropping"""
        if last_crop and current_crop and last_crop == current_crop:
            return True
        return False
