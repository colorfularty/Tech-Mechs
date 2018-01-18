import pygame
import gameObject

BLACK = (0, 0, 0)

class Level(object):
    def __init__(self):
        self.width = 640
        self.height = 480
        self.startX = 0 # the x-coordinate the screen starts at
        self.startY = 0 # the y-coordinate the screen starts at
        self.terrain = [] # a list of the terrain arranged on the level
        self.objects = [] # a list of the objects arranged on the level
        self.name = "" # the level name
        self.author = "" # the author of the level
        self.numberOfTechMechs = 100 # the number of tech mechs on the level
        self.saveRequirement = 100 # the number of tech mechs you have to save
        self.skillCounts = [] # a list of how many of each skill is given
        self.timeLimit = -1 # defaults to infinite time, which is -1
        self.releaseRate = 1 # how fast the tech mechs come out of the hatch
        self.music = "" # the filename for the music that plays on the level
        self.techMechSprites = "default" # the sprites for the tech mechs on that level
        self.initializeImage()
        self.initializeTriggerMap()
        
    def addTerrain(self, terrain):
        self.terrain.append(terrain)
        self.updateImage(terrain)

    def addObject(self, obj):
        self.objects.append(obj)
        self.updateTriggerMap(obj)

    def initializeImage(self):
        self.image = pygame.surface.Surface((self.width, self.height))
        self.image.fill(BLACK)

    def updateImage(self, terrain):
        self.image.blit(terrain.image, (terrain.x, terrain.y))

    def initializeTriggerMap(self):
        self.triggerMap = []
        for x in range(self.width):
            self.triggerMap.append([])
            for y in range(self.height):
                self.triggerMap[x].append([])

    def updateTriggerMap(self, obj):
        if type(obj) is gameObject.Exit:
            for x in range(obj.width):
                for y in range(obj.height):
                    self.triggerMap[obj.x + x][obj.y + y].append("exit")
            




