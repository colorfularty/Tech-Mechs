import pygame
from constants import *

class Terrain(object):
    # terrain contained in a graphic set
    def __init__(self, graphicSet, imageName):
        self.graphicSet = graphicSet
        self.imageName = imageName
        self.image = pygame.image.load("styles/" + graphicSet + "/terrain/" + imageName + ".png")
        self.width = self.image.get_width()
        self.height = self.image.get_height()

class TerrainPiece(Terrain):
    # a piece of terrain inserted into a level
    @classmethod
    def insertTerrain(cls, graphicSet, name, x, y, flipped, inverted, rotated):
        return cls(graphicSet, name, x, y, flipped, inverted, rotated)
    
    def __init__(self, graphicSet, imageName, x, y, flipped, inverted, rotated):
        Terrain.__init__(self, graphicSet, imageName)
        self.x = x
        self.y = y
        self.flipped = flipped
        self.inverted = inverted
        self.rotated = rotated
        self.image = pygame.transform.flip(self.image, self.flipped, self.inverted)
        if self.rotated:
            self.image = pygame.transform.rotate(self.image, 90)

    def __str__(self):
        return self.graphicSet + "~" + self.imageName + "~" + str(self.x) + "~" + str(self.y) + "~" + str(self.flipped) + "~" + str(self.inverted) + "~" + str(self.rotated)

    @classmethod
    def createTerrainFromString(self, string):
        graphicSet, imageName, x, y, flipped, inverted, rotated = string.split("~")
        return TerrainPiece(graphicSet, imageName, int(x), int(y), bool(flipped), bool(inverted), bool(rotated))

    def update(self):
        self.__init__(self.graphicSet, self.imageName, self.x, self.y, self.flipped, self.inverted, self.rotated)
