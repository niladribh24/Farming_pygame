import pygame, sys
from settings import *
from level import Level
import settings_menu as sm_module

class Game:
	def __init__(self):
		pygame.init()
		self.screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
		pygame.display.set_caption('Sprout land')
		self.clock = pygame.time.Clock()
		self.level = Level()

	def run(self):
		while True:
			events = pygame.event.get()
			for event in events:
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
  
			dt = self.clock.tick() / 1000
			self.level.run(dt, events)
            
			# Check for game reset
			if getattr(self.level, 'reset_pending', False):
				self.level = Level()
				sm_module.settings_menu = None # Reset singleton
                
			pygame.display.update()

if __name__ == '__main__':
	game = Game()
	game.run()