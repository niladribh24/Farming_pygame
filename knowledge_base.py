# ==============================================================================
# CROP DATA DICTIONARY
# Each crop has water needs and soil effects for consequence-based gameplay
# Researched real-world values for educational accuracy
# ==============================================================================
CROP_DATA = {
    "corn": {
        "water_need": 2,          # Ideal water per day
        "soil_effect": -2,        # Effect on soil health when harvested
        "base_yield": 1,          # Base harvest amount
        "grow_speed": 1.0,        # Growth multiplier
        "sale_price": 10,
        "seed_price": 4,
        "best_fertilizer": ["compost", "blood_meal", "fish_emulsion"],
        "category": "grain",
        "info": "Heavy nitrogen feeder - rotates well with legumes"
    },
    "tomato": {
        "water_need": 3,
        "soil_effect": -1,
        "base_yield": 1,
        "grow_speed": 0.7,
        "sale_price": 20,
        "seed_price": 5,
        "best_fertilizer": ["compost", "bone_meal", "fish_emulsion"],
        "category": "fruit",
        "info": "Needs phosphorus for fruiting - moderate water needs"
    },
    "wheat": {
        "water_need": 1,          # Low water needs
        "soil_effect": -1,
        "base_yield": 2,
        "grow_speed": 0.8,
        "sale_price": 8,
        "seed_price": 3,
        "best_fertilizer": ["compost", "blood_meal"],
        "category": "grain",
        "info": "Low water, high nitrogen needs - good for dry climates"
    },
    "carrot": {
        "water_need": 2,
        "soil_effect": 0,         # Root crops don't deplete much
        "base_yield": 2,
        "grow_speed": 0.6,
        "sale_price": 12,
        "seed_price": 4,
        "best_fertilizer": ["bone_meal", "wood_ash", "compost"],
        "category": "root",
        "info": "Low nitrogen! Too much = leafy tops, tiny roots"
    },
    "potato": {
        "water_need": 2,
        "soil_effect": -3,        # Heavy feeders
        "base_yield": 3,
        "grow_speed": 0.9,
        "sale_price": 8,
        "seed_price": 6,
        "best_fertilizer": ["bone_meal", "wood_ash", "compost"],
        "category": "root",
        "info": "Needs phosphorus for tubers - avoid excessive nitrogen"
    }
}

# ==============================================================================
# WEATHER EFFECTS DICTIONARY
# Used with Queue (deque) for FIFO weather event processing
# ==============================================================================
WEATHER_EFFECTS = {
    "rain": {
        "description": "Rainy day - crops auto-watered",
        "auto_water": True,
        "extra_water_need": 0,
        "soil_effect": 1,
        "manual_water_penalty": -3  # Penalty if player waters during rain
    },
    "heatwave": {
        "description": "Heatwave - crops need extra water",
        "auto_water": False,
        "extra_water_need": 1,
        "soil_effect": -2,
        "manual_water_penalty": 0
    },
    "drought": {
        "description": "Drought - water efficiency rewarded",
        "auto_water": False,
        "extra_water_need": 2,
        "soil_effect": -1,
        "manual_water_penalty": 0
    },
    "normal": {
        "description": "Normal weather",
        "auto_water": False,
        "extra_water_need": 0,
        "soil_effect": 0,
        "manual_water_penalty": 0
    }
}

# ==============================================================================
# FERTILIZER DATA DICTIONARY (Researched Real-World Values)
# NPK = Nitrogen-Phosphorus-Potassium ratio
# Trade-off between short-term growth and long-term soil health
# ==============================================================================
FERTILIZER_DATA = {
    # ORGANIC FERTILIZERS (Sustainable)
    "compost": {
        "name": "Compost",
        "type": "organic",
        "npk": "2-1-1",
        "growth_boost": 1,
        "soil_effect": 10,
        "score_effect": 8,
        "cost": 8,
        "best_for": ["corn", "tomato", "wheat", "carrot", "potato"],
        "description": "Balanced organic matter - improves soil structure",
        "real_info": "Rich in micronutrients and beneficial bacteria"
    },
    "bone_meal": {
        "name": "Bone Meal",
        "type": "organic",
        "npk": "3-15-0",
        "growth_boost": 1,
        "soil_effect": 6,
        "score_effect": 6,
        "cost": 12,
        "best_for": ["carrot", "potato", "tomato"],
        "description": "High phosphorus - excellent for root crops",
        "real_info": "Made from ground animal bones, releases slowly"
    },
    "fish_emulsion": {
        "name": "Fish Emulsion",
        "type": "organic",
        "npk": "5-2-2",
        "growth_boost": 2,
        "soil_effect": 5,
        "score_effect": 5,
        "cost": 15,
        "best_for": ["tomato", "corn", "wheat"],
        "description": "Fast-acting nitrogen boost for leafy growth",
        "real_info": "Liquid fertilizer from fish byproducts"
    },
    "blood_meal": {
        "name": "Blood Meal",
        "type": "organic",
        "npk": "12-0-0",
        "growth_boost": 3,
        "soil_effect": 3,
        "score_effect": 4,
        "cost": 18,
        "best_for": ["corn", "wheat"],
        "description": "Very high nitrogen - for heavy feeders",
        "real_info": "Dried animal blood, fast nitrogen release"
    },
    "wood_ash": {
        "name": "Wood Ash",
        "type": "organic",
        "npk": "0-1-3",
        "growth_boost": 1,
        "soil_effect": 4,
        "score_effect": 5,
        "cost": 5,
        "best_for": ["carrot", "potato", "tomato"],
        "description": "Potassium boost - improves fruit quality",
        "real_info": "From burned wood, also raises soil pH"
    },
    
    # CHEMICAL FERTILIZERS (Faster but harmful long-term)
    "npk_10_10_10": {
        "name": "NPK 10-10-10",
        "type": "chemical",
        "npk": "10-10-10",
        "growth_boost": 3,
        "soil_effect": -3,
        "score_effect": -2,
        "cost": 10,
        "best_for": ["tomato", "corn"],
        "description": "Balanced chemical - fast but harms soil life",
        "real_info": "Common synthetic fertilizer"
    },
    "npk_5_10_10": {
        "name": "NPK 5-10-10",
        "type": "chemical",
        "npk": "5-10-10",
        "growth_boost": 2,
        "soil_effect": -2,
        "score_effect": -2,
        "cost": 10,
        "best_for": ["carrot", "potato"],
        "description": "Low nitrogen for root crops - chemical",
        "real_info": "Designed for root vegetables"
    },
    "urea": {
        "name": "Urea (46-0-0)",
        "type": "chemical",
        "npk": "46-0-0",
        "growth_boost": 4,
        "soil_effect": -5,
        "score_effect": -4,
        "cost": 8,
        "best_for": ["corn", "wheat"],
        "description": "Pure nitrogen - very fast, very harmful",
        "real_info": "Synthetic, can burn plants if overused"
    }
}

# Quick lookup for crop-specific fertilizer recommendations
CROP_FERTILIZER_GUIDE = {
    "tomato": {
        "recommended": ["compost", "bone_meal", "fish_emulsion"],
        "avoid": ["urea"],
        "tip": "Tomatoes need phosphorus for fruiting. Use bone meal when planting, fish emulsion during growth."
    },
    "corn": {
        "recommended": ["compost", "blood_meal", "fish_emulsion"],
        "avoid": ["npk_5_10_10"],
        "tip": "Corn is a heavy nitrogen feeder. Blood meal or fish emulsion provides quick nitrogen."
    },
    "carrot": {
        "recommended": ["compost", "bone_meal", "wood_ash"],
        "avoid": ["blood_meal", "urea"],
        "tip": "Carrots need low nitrogen! Too much nitrogen = leafy tops, small roots. Use bone meal."
    },
    "potato": {
        "recommended": ["compost", "bone_meal", "wood_ash"],
        "avoid": ["urea"],
        "tip": "Potatoes need phosphorus for tuber development. Wood ash adds potassium for quality."
    },
    "wheat": {
        "recommended": ["compost", "blood_meal", "fish_emulsion"],
        "avoid": ["npk_5_10_10"],
        "tip": "Wheat needs nitrogen for grain filling. Apply compost before planting."
    }
}

# ==============================================================================
# SOIL HEALTH IMPACT RULES
# Central reference for all soil health changes
# ==============================================================================
SOIL_IMPACTS = {
    "correct_water": {"soil": 2, "score": 1, "message": "✔ Correct watering (+1)"},
    "over_water": {"soil": -5, "score": -5, "message": "✖ Over-watering detected (-5)"},
    "under_water": {"soil": -2, "score": -3, "message": "✖ Under-watering detected (-3)"},
    "monocrop": {"soil": -6, "score": -6, "message": "✖ Monocropping depletes soil (-6)"},
    "rotation": {"soil": 5, "score": 2, "message": "✔ Crop rotation bonus (+2)"},
    "fallow": {"soil": 4, "score": 1, "message": "✔ Fallow land recovered (+1)"},
    "rain_overwater": {"soil": -3, "score": -4, "message": "✖ Watered during rain (-4)"}
}

# ==============================================================================
# SKILL TREE DEFINITIONS (for Tree data structure)
# Hierarchical unlock system
# ==============================================================================
SKILL_DEFINITIONS = {
    "sustainable_farming": {
        "name": "Sustainable Farming",
        "description": "Root of the skill tree",
        "unlocked": True,
        "children": ["crop_rotation", "water_management"]
    },
    "crop_rotation": {
        "name": "Crop Rotation",
        "description": "Rotate crops to improve soil",
        "unlock_condition": "soil_health >= 60",
        "unlocked": False,
        "children": ["intercropping"]
    },
    "intercropping": {
        "name": "Intercropping",
        "description": "Plant multiple crops together",
        "unlock_condition": "crop_rotation_unlocked and score >= 50",
        "unlocked": False,
        "children": []
    },
    "water_management": {
        "name": "Water Management",
        "description": "Efficient water usage",
        "unlock_condition": "no_overwater_days >= 3",
        "unlocked": False,
        "children": ["drip_irrigation"]
    },
    "drip_irrigation": {
        "name": "Drip Irrigation",
        "description": "Use less water for same effect",
        "unlock_condition": "no_overwater_days >= 5",
        "unlocked": False,
        "children": []
    }
}

# ==============================================================================
# ACHIEVEMENT DEFINITIONS (for Set data structure)
# Fast membership check for unlocked achievements
# ==============================================================================
ACHIEVEMENT_DEFINITIONS = {
    "eco_farmer": {
        "name": "Eco Farmer",
        "description": "Achieve soil health >= 80",
        "condition": "soil_health >= 80",
        "points": 10
    },
    "water_saver": {
        "name": "Water Saver",
        "description": "No over-watering for 5 days",
        "condition": "no_overwater_days >= 5",
        "points": 8
    },
    "sustainable_starter": {
        "name": "Sustainable Starter",
        "description": "Use organic fertilizer for the first time",
        "condition": "organic_fertilizer_used",
        "points": 5
    },
    "rotation_master": {
        "name": "Rotation Master",
        "description": "Successfully rotate crops 3 times",
        "condition": "rotation_count >= 3",
        "points": 8
    },
    "perfect_harvest": {
        "name": "Perfect Harvest",
        "description": "Harvest with soil health >= 70",
        "condition": "harvest_soil_health >= 70",
        "points": 6
    }
}

# ==============================================================================
# INITIAL GAME VALUES
# ==============================================================================
INITIAL_SOIL_HEALTH = 0
MIN_SOIL_HEALTH = 0
MAX_SOIL_HEALTH = 100
INITIAL_WATER_RESERVE = 10
MAX_WATER_RESERVE = 50

# ==============================================================================
# IRRIGATION TECHNIQUES
# Different watering methods with efficiency bonuses
# ==============================================================================
IRRIGATION_DATA = {
    "manual": {
        "name": "Manual Watering",
        "water_cost": 2,           # Water used per action
        "efficiency": 1.0,         # Multiplier (1.0 = standard)
        "overwater_threshold": 3,  # Times before penalty
        "unlocked": True,
        "description": "Standard watering can"
    },
    "efficient": {
        "name": "Efficient Watering",
        "water_cost": 1,
        "efficiency": 1.5,         # 50% better
        "overwater_threshold": 4,  # Harder to overwater
        "unlocked": False,         # Requires Water Management skill
        "description": "Better water distribution"
    },
    "drip": {
        "name": "Drip Irrigation",
        "water_cost": 0.5,         # Uses less water
        "efficiency": 2.0,         # Double efficiency
        "overwater_threshold": 6,  # Very hard to overwater
        "unlocked": False,         # Requires Drip Irrigation skill
        "description": "Automated drip system - saves water"
    }
}

