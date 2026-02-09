import pygame
from settings import *
import os

class PlacedWaterTank(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_groups=None):
        super().__init__(groups)
        
        tank_size = TILE_SIZE * 2
        
        barrel_path = './graphics/objects/barrel.png'
        if os.path.exists(barrel_path):
            self.image = pygame.image.load(barrel_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (tank_size, tank_size))
        else:
            self.image = pygame.Surface((tank_size, tank_size), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (139, 90, 43), (8, 8, tank_size - 16, tank_size - 16), 0, 12)
            pygame.draw.rect(self.image, (101, 67, 33), (8, 8, tank_size - 16, tank_size - 16), 4, 12)
        
        self.rect = self.image.get_rect(topleft=pos)
        self.z = LAYERS['main']
        self.hitbox = self.rect.copy().inflate(-30, -30)
        
        if collision_groups:
            for group in collision_groups:
                group.add(self)
        
        self.rain_collection_bonus = 15

