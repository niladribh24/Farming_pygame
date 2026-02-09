
class RainTank:
    def __init__(self, capacity=100):
        self.capacity = capacity
        self.current_amount = 0
        
    def collect_rain(self, amount):
        old_amount = self.current_amount
        self.current_amount = min(self.capacity, self.current_amount + amount)
        collected = self.current_amount - old_amount
        return collected
        
    def use_water(self, amount):
        if self.current_amount >= amount:
            self.current_amount -= amount
            return True
        return False
        
    def get_fill_percentage(self):
        return self.current_amount / self.capacity
