import pygame
from constants import *
from gameObject import *
from skill import *

class Level(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.startX = 0 # the x-coordinate the screen starts at
        self.startY = 0 # the y-coordinate the screen starts at
        self.terrain = [] # a list of the terrain arranged on the level
        self.objects = [] # a list of the objects arranged on the level
        self.techMechObjects = [] # a list of objects placed by tech mechs
        self.name = "" # the level name
        self.author = "" # the author of the level
        self.numberOfTechMechs = 10 # the number of tech mechs on the level
        self.saveRequirement = 1 # the number of tech mechs you have to save
        # a dict of how many of each skill is given
        self.skillCounts = {Grappler: 10,
                            Driller: 10,
                            Jackhammerer: 10,
                            GravityReverser: 10,
                            Cautioner: 10,
                            Detonator: 10}
        self.timeLimit = -1 # defaults to infinite time, which is -1
        self.releaseRate = 1 # how fast the tech mechs come out of the hatch
        self.music = "" # the filename for the music that plays on the level
        self.techMechSprites = "default" # the sprites for the tech mechs on that level
        self.initializeImage()
        self.initializeTriggerMaps()
        
    def addTerrain(self, terrain):
        self.terrain.append(terrain)
        self.updateImage(terrain)

    def addObject(self, obj):
        self.objects.append(obj)
        self.updateTriggerMaps()

    def addTechMechObject(self, obj):
        self.techMechObjects.append(obj)
        self.updateTriggerMaps()

    def initializeImage(self):
        self.image = pygame.surface.Surface((self.width, self.height))
        self.image.fill(BLACK)

    def updateImage(self, terrain):
        self.image.blit(terrain.image, (terrain.x, terrain.y))

    def updateWholeImage(self):
        self.image.fill(BLACK)
        for terrain in self.terrain:
            self.image.blit(terrain.image, (terrain.x, terrain.y))

    def initializeTriggerMaps(self):
        self.triggersByPoint = {}
        self.triggersByType = {"exit": [],
                               "caution": []}

    def updateTriggerMaps(self):
        self.initializeTriggerMaps()
        for obj in self.objects:
            for x in range(obj.triggerWidth):
                for y in range(obj.triggerHeight):
                    point = (obj.triggerX + x, obj.triggerY + y)
                    if point not in self.triggersByPoint.keys():
                        self.triggersByPoint[point] = []
                    if type(obj) is Exit:
                        self.triggersByPoint[point].append("exit")
                        self.triggersByType["exit"].append(point)
        for obj in self.techMechObjects:
            for x in range(obj.triggerWidth):
                for y in range(obj.triggerHeight):
                    point = (obj.triggerX + x, obj.triggerY + y)
                    if point not in self.triggersByPoint.keys():
                        self.triggersByPoint[point] = []
                    if type(obj) is CautionSign:
                        self.triggersByPoint[point].append("caution")
                        self.triggersByType["caution"].append(point)
            




