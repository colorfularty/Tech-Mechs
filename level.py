import pygame
from constants import *
from gameObject import *
from terrain import *
from skill import *

class Level(object):
    def __init__(self, width, height, startX, startY, terrain, objects, name, author, numberOfTechMechs, saveRequirement, skillCounts, timeLimit, releaseRate, music, numPlayers):
        self.width = width
        self.height = height
        self.startX = startX # the x-coordinate the screen starts at
        self.startY = startY # the y-coordinate the screen starts at
        self.terrain = terrain # a list of the terrain arranged on the level
        self.objects = objects # a list of the objects arranged on the level
        self.techMechObjects = [] # a list of objects placed by tech mechs
        self.name = name # the level name
        self.author = author # the author of the level
        self.numberOfTechMechs = numberOfTechMechs # the number of tech mechs on the level
        self.saveRequirement = saveRequirement # the number of tech mechs you have to save
        # a dict of how many of each skill is given to each player
        self.skillCounts = skillCounts
        self.initSkillCounts()
        self.timeLimit = timeLimit # defaults to infinite time, which is -1
        self.releaseRate = releaseRate # how fast the tech mechs come out of the hatch
        self.music = music # the filename for the music that plays on the level
        self.numPlayers = numPlayers
        self.techMechSprites = "default" # the sprites for the tech mechs on that level
        self.initializeImage()
        self.initializeTriggerMaps()

    def initSkillCounts(self):
        # ensures all skills are in skill counts even if you have 0 of them
        for player in self.skillCounts:
            if Grappler not in player:
                player[Grappler] = 0
            if Driller not in player:
                player[Driller] = 0
            if Jackhammerer not in player:
                player[Jackhammerer] = 0
            if GravityReverser not in player:
                player[GravityReverser] = 0
            if Cautioner not in player:
                player[Cautioner] = 0
            if Detonator not in player:
                player[Detonator] = 0

    def updateNumPlayers(self, numPlayers):
        # update the number of players and modify the skill counts to match the current number of players
        self.numPlayers = numPlayers
        while len(self.skillCounts) < self.numPlayers:
            self.skillCounts.append({})
        while len(self.skillCounts) > self.numPlayers:
            self.skillCounts.remove(self.skillCounts[-1])
        
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

    def saveLevel(self):
        levelFile = open("levels/" + self.name + ".txt", 'w')
        levelFile.write(str(self.numPlayers) + "\n")
        levelFile.write(self.name + "\n")
        levelFile.write(self.author + "\n")
        levelFile.write(str(self.width) + "\n")
        levelFile.write(str(self.height) + "\n")
        levelFile.write(str(self.startX) + "\n")
        levelFile.write(str(self.startY) + "\n")
        levelFile.write(str(self.numberOfTechMechs) + "\n")
        levelFile.write(str(self.saveRequirement) + "\n")
        levelFile.write(str(self.timeLimit) + "\n")
        levelFile.write(str(self.releaseRate) + "\n")
        levelFile.write(self.music + "\n")
        levelFile.write("SKILLS\n")
        for player in self.skillCounts:
            for skill in player.keys():
                levelFile.write(SKILL_STRING_CONVERSIONS[skill] + ": " + str(player[skill]) + ": " + str(self.skillCounts.index(player)) + "\n")
        levelFile.write("TERRAIN\n")
        for terrain in self.terrain:
            levelFile.write(str(terrain) + "\n")
        levelFile.write("OBJECTS\n")
        for obj in self.objects:
            levelFile.write(str(obj) + "\n")
        levelFile.write("END\n")
        levelFile.close()

    @classmethod
    def loadLevel(self, name):
        levelFile = open("levels/" + name + ".txt", 'r')
        numPlayers = levelFile.readline()
        levelName = levelFile.readline()
        author = levelFile.readline()
        width  = levelFile.readline()
        height = levelFile.readline()
        startX = levelFile.readline()
        startY = levelFile.readline()
        numberOfTechMechs = levelFile.readline()
        saveRequirement = levelFile.readline()
        timeLimit = levelFile.readline()
        releaseRate = levelFile.readline()
        music = levelFile.readline()
        levelFile.readline() # line that just says SKILLS
        currentLine = levelFile.readline()
        skillCounts = []
        for i in range(int(numPlayers)):
            skillCounts.append({Driller: 0,
                       Jackhammerer: 0,
                       Cautioner: 0,
                       Detonator: 0,
                       Grappler: 0,
                       GravityReverser: 0})
        while currentLine != "TERRAIN\n":
            skill, amount, player = currentLine.split(": ")
            skillCounts[int(player)][STRING_SKILL_CONVERSIONS[skill]] = int(amount)
            currentLine = levelFile.readline()
        currentLine = levelFile.readline()
        terrain = []
        while currentLine != "OBJECTS\n":
            terrainGraphicSet, terrainName, x, y, flipped, inverted, rotated = currentLine.split("~")
            newTerrain = TerrainPiece(terrainGraphicSet, terrainName, int(x), int(y), flipped == 'True', inverted == 'True', rotated == 'True\n')
            terrain.append(newTerrain)
            currentLine = levelFile.readline()
        currentLine = levelFile.readline()
        objects = []
        while currentLine != "END\n":
            objType, objGraphicSet, objName, x, y, flipped, inverted, rotated = currentLine.split("~")
            if objType == "Entrance":
                newObject = Entrance(objGraphicSet, objName, int(x), int(y), flipped == "True", inverted == "True", rotated == "True\n")
            elif objType == "Exit":
                newObject = Exit(objGraphicSet, objName, int(x), int(y), flipped == "True", inverted == "True", rotated == "True\n")
            else:
                newObject = GameObjectInstance(objGraphicSet, objName, int(x), int(y), flipped == "True", inverted == "True", rotated == "True\n")
            objects.append(newObject)
            currentLine = levelFile.readline()
        levelFile.close()
        level = Level(int(width), int(height), int(startX), int(startY), terrain, objects, levelName[:-1], author[:-1], int(numberOfTechMechs), int(saveRequirement), skillCounts, int(timeLimit), int(releaseRate), music[:-1], int(numPlayers))
        return level
            




