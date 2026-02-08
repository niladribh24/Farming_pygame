# Rainwater Harvesting System
# Teaches water conservation logic.

class RainTank:
    """
    Simulates a rainwater harvesting tank.
    
    Data Structure: Queue (for rain events - implicitly handled by Level)
    Object-Oriented: Class with capacity logic.
    """
    def __init__(self, capacity=100):
        self.capacity = capacity
        self.current_amount = 0
        
    def collect_rain(self, amount):
        """Add rain to the tank, adhering to capacity"""
        old_amount = self.current_amount
        self.current_amount = min(self.capacity, self.current_amount + amount)
        collected = self.current_amount - old_amount
        return collected
        
    def use_water(self, amount):
        """
        Use water from the tank.
        Returns True if successful, False if empty.
        """
        if self.current_amount >= amount:
            self.current_amount -= amount
            return True
        return False
        
    def get_fill_percentage(self):
        return self.current_amount / self.capacity
