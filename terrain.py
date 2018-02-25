import pygame
from constants import *

class Terrain(object):
    # terrain contained in a graphic set
    def __init__(self, imageName):
        self.image = pygame.image.load(imageName).convert()
        self.image.set_colorkey(BLACK)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

class TerrainPiece(Terrain):
    # a piece of terrain inserted into a level
    def __init__(self, imageName, x, y):
        Terrain.__init__(self, imageName)
        self.x = x
        self.y = y
