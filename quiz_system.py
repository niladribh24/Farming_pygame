

QUIZZES = {
    "water_conservation": {
        "title": "Water Conservation",
        "badge": "Water Saver",
        "description": "Experts at water conservation!",
        "questions": [
            {
                "q": "Which irrigation method saves the most water?",
                "options": ["Flood Irrigation", "Sprinkler System", "Drip Irrigation", "Hand Watering"],
                "a": "Drip Irrigation"
            },
            {
                "q": "When is the best time to water crops?",
                "options": ["High Noon", "Midnight", "Early Morning", "Late Afternoon"],
                "a": "Early Morning"
            },
            {
                "q": "What protects soil moisture from evaporating?",
                "options": ["Tilling", "Mulching", "Leaving it bare", "Over-watering"],
                "a": "Mulching"
            },
            {
                "q": "Which crop is known to be drought-resistant?",
                "options": ["Rice", "Sugar Cane", "Millet", "Cotton"],
                "a": "Millet"
            }
        ]
    },
    "soil_health": {
        "title": "Soil Health",
        "badge": "Soil Guardian",
        "description": "Protector of the earth beneath us.",
        "questions": [
            {
                "q": "What is best for long-term soil fertility?",
                "options": ["Chemical Nitrogen", "Organic Compost", "Daily Tilling", "Leaving Soil Bare"],
                "a": "Organic Compost"
            },
            {
                "q": "What does N-P-K stand for?",
                "options": ["Nitrogen-Potassium-Krypton", "Nitrogen-Phosphorus-Potassium", "No-Plant-Kill", "Natural-Plant-Care"],
                "a": "Nitrogen-Phosphorus-Potassium"
            },
            {
                "q": "Which of these harms soil structure?",
                "options": ["Cover Cropping", "Deep Tilling", "Composting", "Crop Rotation"],
                "a": "Deep Tilling"
            },
            {
                "q": "Earthworms in soil are a sign of...",
                "options": ["Disease", "Good Health", "Over-watering", "Pests"],
                "a": "Good Health"
            }
        ]
    },
    "crop_rotation": {
        "title": "Crop Rotation",
        "badge": "Rotation Master",
        "description": "Master of seasonal planning.",
        "questions": [
            {
                "q": "Why should you rotate crops every season?",
                "options": ["To look pretty", "Replenish Nutrients", "Use more water", "Grow faster"],
                "a": "Replenish Nutrients"
            },
            {
                "q": "Legumes (like beans) are good for...",
                "options": ["Fixing Nitrogen", "Using up Nitrogen", "Drying the soil", "Attracting pests"],
                "a": "Fixing Nitrogen"
            },
            {
                "q": "Planting the same crop repeatedly is called...",
                "options": ["Polyculture", "Monocropping", "Rotation", "Permaculture"],
                "a": "Monocropping"
            },
            {
                "q": "Which pest cycle does rotation break?",
                "options": ["Migratory birds", "Soil-borne pathogens", "Flying insects", "Weeds"],
                "a": "Soil-borne pathogens"
            }
        ]
    },
    "rainwater": {
        "title": "Rainwater Harvesting",
        "badge": "Rain Walker",
        "description": "Harnessing the storm.",
        "questions": [
            {
                "q": "What is the primary benefit of rainwater harvesting?",
                "options": ["Prevents floods", "Reduces Aquifer Drain", "Makes plants blue", "Costs more money"],
                "a": "Reduces Aquifer Drain"
            },
            {
                "q": "Rainwater is generally...",
                "options": ["Salty", "Free of salts/chemicals", "Polluted", "Hard water"],
                "a": "Free of salts/chemicals"
            },
            {
                "q": "What surface is best for collecting rain?",
                "options": ["Grass", "Dirt road", "Clean Roof", "Tree canopy"],
                "a": "Clean Roof"
            },
            {
                "q": "Stored rainwater can be used for...",
                "options": ["Drinking only", "Irrigation", "Nothing", "Creating clouds"],
                "a": "Irrigation"
            }
        ]
    },
    "erosion": {
        "title": "Erosion Control",
        "badge": "Root Keeper",
        "description": "Keeping the land together.",
        "questions": [
            {
                "q": "Which practice prevents soil erosion?",
                "options": ["Deforestation", "Monocropping", "Cover Cropping", "Over-grazing"],
                "a": "Cover Cropping"
            },
            {
                "q": "Roots help soil by...",
                "options": ["Eating it", "Holding it together", "Drying it out", "Heating it"],
                "a": "Holding it together"
            },
            {
                "q": "Wind erosion is worst on...",
                "options": ["Forest floors", "Bare fields", "Wetlands", "Rocky mountains"],
                "a": "Bare fields"
            },
            {
                "q": "Contour farming involves...",
                "options": ["Plowing vertically", "Plowing across slopes", "Removing hills", "Farming in valleys only"],
                "a": "Plowing across slopes"
            }
        ]
    }
}

earned_badges = set()

def has_badge(badge_name):
    return badge_name in earned_badges

def get_shop_discount():
    discount = 1.0
    
    if "Water Saver" in earned_badges:
        discount *= 0.9  # 10% off water supplies
        
    if "Soil Guardian" in earned_badges:
        discount *= 0.9  # 10% off fertilizers
        
    if "Rotation Master" in earned_badges:
        discount *= 0.9  # 10% off seeds
        
    return discount

def get_total_badges():
    return len(earned_badges)
