import pygame
from settings import *
import os

class PlacedWaterTank(pygame.sprite.Sprite):
    """Water tank placed in the world that collects rainwater - 2x2 tiles"""
    def __init__(self, pos, groups, collision_groups=None):
        super().__init__(groups)
        
        # Tank size: 2x2 tiles = 128x128 pixels
        tank_size = TILE_SIZE * 2
        
        # Load the barrel image
        barrel_path = './graphics/objects/barrel.png'
        if os.path.exists(barrel_path):
            self.image = pygame.image.load(barrel_path).convert_alpha()
            # Scale to 2x2 tile size
            self.image = pygame.transform.scale(self.image, (tank_size, tank_size))
        else:
            # Fallback: simple brown rectangle
            self.image = pygame.Surface((tank_size, tank_size), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (139, 90, 43), (8, 8, tank_size - 16, tank_size - 16), 0, 12)
            pygame.draw.rect(self.image, (101, 67, 33), (8, 8, tank_size - 16, tank_size - 16), 4, 12)
        
        self.rect = self.image.get_rect(topleft=pos)
        self.z = LAYERS['main']
        self.hitbox = self.rect.copy().inflate(-30, -30)
        
        # Add to collision group if provided
        if collision_groups:
            for group in collision_groups:
                group.add(self)
        
        # Tank properties
        self.rain_collection_bonus = 15

