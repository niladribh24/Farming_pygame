# Sustainable Farming Knowledge Book
# Educational content for the gamified learning platform

# ==============================================================================
# KNOWLEDGE CARDS - Dictionary of sustainable farming practices
# Each card teaches a specific concept with consequences explained
# ==============================================================================

KNOWLEDGE_CARDS = {
    "crop_rotation": {
        "title": "🔄 Crop Rotation",
        "category": "Soil Health",
        "summary": "Alternate different crops each season to maintain soil nutrients.",
        "why_it_matters": """
When you plant the same crop repeatedly (monocropping), it depletes 
specific nutrients from the soil. Different crops have different nutrient 
needs and some even add nutrients back!

Example: Legumes (peas, beans) add nitrogen to soil, which corn loves.
Plant legumes, then corn for healthy soil!
        """,
        "game_effect": "Rotation: +5 soil health, +4 score | Monocropping: -6 soil, -4 score",
        "real_world": "Used by farmers worldwide for thousands of years",
        "unlocked": True
    },
    
    "water_management": {
        "title": "💧 Water Management",
        "category": "Resource Conservation",
        "summary": "Use water efficiently - not too much, not too little.",
        "why_it_matters": """
Over-watering wastes water and causes:
• Waterlogging - roots can't breathe
• Nutrient wash-away
• Fungal diseases

Under-watering stresses plants and reduces yield.
The key is giving JUST the right amount! Best time to water: Early Morning.
        """,
        "game_effect": "Correct watering: +2 soil, +3 score | Over-watering: -5 soil, -3 score",
        "real_world": "Agriculture uses 70% of global freshwater - efficiency matters!",
        "unlocked": True
    },
    
    "organic_fertilizer": {
        "title": "🌿 Organic vs Chemical Fertilizer",
        "category": "Soil Health",
        "summary": "Organic fertilizers improve soil long-term; chemicals give quick but harmful boosts.",
        "why_it_matters": """
ORGANIC FERTILIZER (compost, manure):
✅ Improves soil structure
✅ Feeds beneficial microbes
✅ Slow, steady nutrient release
❌ Slower growth boost

CHEMICAL FERTILIZER:
✅ Fast growth
❌ Kills soil microbes
❌ Pollutes groundwater
❌ Soil becomes dependent
        """,
        "game_effect": "Organic: +8 soil, +6 score | Chemical: -4 soil, -4 score",
        "real_world": "Organic farming is growing 20% annually worldwide",
        "unlocked": True
    },
    
    "rainwater_harvesting": {
        "title": "🌧️ Rainwater Harvesting",
        "category": "Resource Conservation",
        "summary": "Collect and store rainwater for use during dry periods.",
        "why_it_matters": """
Rain is FREE water! Instead of letting it run off:
• Collect it in tanks or ponds
• Use during droughts
• Reduce dependence on groundwater (Aquifer Drain)
• Save money on water bills

Best surface for collection: Clean Roof.
        """,
        "game_effect": "Rainy day: +5 water reserve automatically",
        "real_world": "Ancient technique used from India to Rome",
        "unlocked": True
    },
    
    "drip_irrigation": {
        "title": "🚿 Drip Irrigation",
        "category": "Technology",
        "summary": "Deliver water directly to plant roots, minimizing waste.",
        "why_it_matters": """
Traditional flood irrigation wastes 50% of water!

Drip irrigation:
• Delivers water drop by drop
• Directly to roots
• 90% water efficiency
• Reduces weeds (dry areas between plants)
• Prevents soil erosion

Unlock this by not over-watering for 5 days!
        """,
        "game_effect": "Drip mode: 0.5 water cost, 2x efficiency, harder to over-water",
        "real_world": "Can increase crop yields by 20-90%",
        "unlocked": False
    },
    
    "soil_health": {
        "title": "🌍 Soil Health Basics",
        "category": "Fundamentals",
        "summary": "Healthy soil = healthy crops = healthy planet.",
        "why_it_matters": """
Soil is ALIVE! It contains:
• Billions of microorganisms
• Fungi networks (mycelium)
• Earthworms (sign of health!) and insects
• Organic matter

When soil is healthy:
✅ Better water retention
✅ Natural pest resistance  
✅ Higher yields
✅ Carbon storage (fights climate change!)
        """,
        "game_effect": "Soil 80+: bonus harvest | Soil 30-: reduced yield",
        "real_world": "1 gram of soil contains 1 billion bacteria",
        "unlocked": True
    },
    
    "erosion_control": {
        "title": "🛡️ Erosion Control",
        "category": "Soil Recovery",
        "summary": "Prevent precious topsoil from washing or blowing away.",
        "why_it_matters": """
Soil erosion removes the fertile top layer.
Causes: Wind (on bare fields) and Water runoff.

Solutions:
• Cover Cropping: Keep roots in soil year-round
• Contour Farming: Plow across slopes, not down them
• Mulching: Protect soil surface
• Avoid over-tilling (Deep Tilling destroys structure)
        """,
        "game_effect": "Using cover crops prevents daily soil loss",
        "real_world": "Dust Bowl of 1930s was caused by massive erosion",
        "unlocked": True
    },
    
    "intercropping": {
        "title": "🌱 Intercropping",
        "category": "Advanced",
        "summary": "Grow multiple crops together for mutual benefits.",
        "why_it_matters": """
Some plants help each other grow! Classic combos:

THE THREE SISTERS (Native American):
• Corn - provides structure
• Beans - add nitrogen
• Squash - shades soil, blocks weeds

Benefits:
• Natural pest control
• Better nutrient use
• Higher total yield
• Biodiversity

Unlock by mastering crop rotation!
        """,
        "game_effect": "Requires: Crop Rotation skill + score ≥ 50",
        "real_world": "Used for over 10,000 years",
        "unlocked": False
    },
    
    "fallow_land": {
        "title": "🏜️ Letting Land Rest (Fallow)",
        "category": "Soil Recovery",
        "summary": "Sometimes the best thing to do is... nothing.",
        "why_it_matters": """
Just like humans need sleep, soil needs rest!

Leaving land fallow (unplanted) for a season:
• Allows soil organisms to recover
• Breaks pest and disease cycles
• Lets nutrients rebuild
• Prevents erosion with cover crops

Don't plant everywhere - let some tiles rest!
        """,
        "game_effect": "Fallow tile: +4 soil health, +2 score per day",
        "real_world": "Medieval farmers rotated crops with fallow periods",
        "unlocked": True
    },
    
    "fertilizer_guide": {
        "title": "📋 Fertilizer Guide by Crop",
        "category": "Fundamentals",
        "summary": "Match the right fertilizer to each crop for best results!",
        "why_it_matters": """
🌽 CORN:
   USE: Compost, Blood Meal, Fish Emulsion
   AVOID: NPK 5-10-10 (low nitrogen)

🍅 TOMATO:
   USE: Compost, Bone Meal, Fish Emulsion
   AVOID: Urea (too much nitrogen)

🌾 WHEAT:
   USE: Compost, Blood Meal, Fish Emulsion
   AVOID: NPK 5-10-10

🥕 CARROT:
   USE: Bone Meal, Wood Ash, Compost
   AVOID: Blood Meal, Urea (high nitrogen)

🥔 POTATO:
   USE: Bone Meal, Wood Ash, Compost
   AVOID: Urea (causes green potatoes)
        """,
        "game_effect": "Using recommended: +2 bonus | Using 'avoid': -2 penalty",
        "real_world": "Soil testing helps farmers know exact nutrient needs",
        "unlocked": True
    },
    
    "npk_explained": {
        "title": "🧪 Understanding NPK",
        "category": "Fundamentals",
        "summary": "The three numbers on fertilizer bags explained.",
        "why_it_matters": """
Every fertilizer shows N-P-K ratio (e.g., 10-10-10):

🟢 N = NITROGEN (first number)
   • Promotes leafy, green growth
   • Good for: Corn, Wheat, leafy greens
   • Too much: All leaves, no fruit/roots!

🟡 P = PHOSPHORUS (second number)  
   • Builds strong roots & flowers/fruit
   • Good for: Tomatoes, Carrots, Potatoes
   • Essential for seedlings

🔵 K = POTASSIUM (third number)
   • Overall plant health & disease resistance
   • Improves fruit quality
   • Good for: All crops, especially fruiting ones
        """,
        "game_effect": "Check fertilizer NPK to match crop needs",
        "real_world": "Commercial farms do soil tests before choosing fertilizer",
        "unlocked": True
    }
}

# ==============================================================================
# CATEGORY DEFINITIONS
# ==============================================================================

KNOWLEDGE_CATEGORIES = {
    "Fundamentals": {"icon": "📚", "color": (200, 200, 255)},
    "Soil Health": {"icon": "🌍", "color": (139, 90, 43)},
    "Resource Conservation": {"icon": "💧", "color": (100, 180, 255)},
    "Technology": {"icon": "⚙️", "color": (180, 180, 180)},
    "Advanced": {"icon": "🎓", "color": (255, 215, 0)},
    "Soil Recovery": {"icon": "🌱", "color": (100, 200, 100)}
}

# ==============================================================================
# QUICK TIPS - Short reminders shown during gameplay
# ==============================================================================

QUICK_TIPS = [
    "💡 Rotate crops to keep soil healthy!",
    "💡 Organic fertilizer is slow but sustainable",
    "💡 Don't water more than twice per day",
    "💡 Rainy days fill your water reserve",
    "💡 Different crops have different water needs",
    "💡 Watch your soil health bar - it affects yield!",
    "💡 Press B to open the Knowledge Book",
    "💡 Unlock skills by practicing sustainable farming",
    "💡 Chemical fertilizers harm soil long-term",
    "💡 Let some land rest (fallow) to recover"
]

def get_unlocked_cards():
    """Get list of unlocked knowledge cards"""
    return {k: v for k, v in KNOWLEDGE_CARDS.items() if v.get("unlocked", True)}

def get_card_by_category(category):
    """Get all cards in a specific category"""
    return {k: v for k, v in KNOWLEDGE_CARDS.items() if v.get("category") == category}
