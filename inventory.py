# Inventory System Module
# Defines item categories for educational purposes.

# DATA STRUCTURE: Dictionary
# Categorizes items as 'eco', 'harmful', or 'neutral'
ITEM_CATEGORIES = {
    # Fertilizers
    "compost": "eco",
    "bone_meal": "eco",
    "fish_emulsion": "eco",
    "blood_meal": "eco",
    "wood_ash": "eco",
    "npk_10_10_10": "harmful",
    "npk_5_10_10": "harmful",
    "urea": "harmful",
    
    # Crops (generally neutral/eco, but for inventory display)
    "corn": "neutral",
    "tomato": "neutral",
    "wheat": "neutral",
    "carrot": "neutral",
    "potato": "neutral",
    
    # Resources
    "wood": "neutral",
    "apple": "eco",
    "water": "neutral"
}

def get_item_category(item_name):
    """Return the category of an item (eco, harmful, neutral)"""
    return ITEM_CATEGORIES.get(item_name, "neutral")

class InventoryItem:
    """
    Class representing an item in the inventory.
    Used for object-oriented structure in Viva explanation.
    """
    def __init__(self, name, amount, category):
        self.name = name
        self.amount = amount
        self.category = category
