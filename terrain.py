import pygame
import constants

class Terrain(object):
    # a piece of terrain used for levels
    def __init__(self, imageName, x, y):
        self.image = pygame.image.load(imageName).convert()
        self.image.set_colorkey(constants.BLACK)
        self.width = self.image.get_width() # the width of the terrain
        self.height = self.image.get_height() # the height of the terrain
        self.x = x
        self.y = y
