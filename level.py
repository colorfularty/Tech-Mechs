import pygame
from constants import *
from gameObject import *
from terrain import *
from skill import *

class Level(object):
    def __init__(self, width, height, startX, startY, terrain, objects, name, author, numberOfTechMechs, saveRequirement, skillCounts, timeLimit, releaseRates, music, numPlayers):
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
        self.releaseRates = releaseRates # how fast the tech mechs come out of the hatch
        self.music = music # the filename for the music that plays on the level
        self.numPlayers = numPlayers # the number of players the level is made for
        self.techMechSprites = "default" # the sprites for the tech mechs on that level
        self.initializeImage()
        self.initializeTriggerMaps()

    def initSkillCounts(self):
        # ensures all skills are in skill counts even if you have 0 of them
        for player in self.skillCounts:
            for skill in SKILLS:
                if skill not in player:
                    player[skill] = 0

    def updateNumPlayers(self, numPlayers):
        # update the number of players and modify the skill counts to match the current number of players
        self.numPlayers = numPlayers
        while len(self.skillCounts) < self.numPlayers:
            self.skillCounts.append({})
        while len(self.skillCounts) > self.numPlayers:
            self.skillCounts.remove(self.skillCounts[-1])
        while len(self.releaseRates) < self.numPlayers:
            self.releaseRates.append(1)
        while len(self.releaseRates) > self.numPlayers:
            self.releaseRates.remove(self.releaseRates[-1])
        
    def addTerrain(self, terrain):
        # insert a piece of terrain into the level
        self.terrain.append(terrain)
        self.updateImage(terrain)

    def addObject(self, obj):
        # insert an object into the level
        self.objects.append(obj)
        self.updateTriggerMaps()

    def addTechMechObject(self, obj):
        # insert a Tech Mech-specific object (i.e. a caution sign) into the level
        self.techMechObjects.append(obj)
        self.updateTriggerMaps()

    def initializeImage(self):
        self.image = pygame.surface.Surface((self.width, self.height))
        self.image.fill(BLACK)

    def updateImage(self, terrain):
        # add a given piece of terrain to the level's image
        self.image.blit(terrain.image, (terrain.x, terrain.y))

    def updateWholeImage(self):
        # re-initialize the level image and blit every piece of terrain to it
        self.image.fill(BLACK)
        for terrain in self.terrain:
            self.image.blit(terrain.image, (terrain.x, terrain.y))

    def initializeTriggerMaps(self):
        self.triggersByPoint = {}
        self.triggersByType = {"water": [],
                               "caution": []}
        for i in range(self.numPlayers):
            self.triggersByType["exit" + str(i)] = []

    def updateTriggerMaps(self):
        # update the trigger maps with all necessary triggers
        self.initializeTriggerMaps()
        for obj in self.objects:
            for x in range(obj.triggerWidth):
                for y in range(obj.triggerHeight):
                    point = (obj.triggerX + x, obj.triggerY + y)
                    if point not in self.triggersByPoint.keys():
                        self.triggersByPoint[point] = []
                    if type(obj) is Exit:
                        self.triggersByPoint[point].append("exit" + str(obj.owner))
                        self.triggersByType["exit" + str(obj.owner)].append(point)
                    elif type(obj) is Water:
                        self.triggersByPoint[point].append("water")
                        self.triggersByType["water"].append(point)
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
        # encode the level and save as a .txt file
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
        for i in range(len(self.releaseRates)):
            if i < len(self.releaseRates) - 1:
                levelFile.write(str(self.releaseRates[i]) + ",")
            else:
                levelFile.write(str(self.releaseRates[i]) + "\n")
        levelFile.write(self.music + "\n")
        levelFile.write("SKILLS\n")
        for i in range(len(self.skillCounts)):
            player = self.skillCounts[i]
            for skill in player.keys():
                levelFile.write(SKILL_STRING_CONVERSIONS[skill] + ": " + str(player[skill]) + ": " + str(i) + "\n")
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
        # create a level from data included in a valid .txt file
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
        releaseRatesString = levelFile.readline()
        splitReleaseRates = releaseRatesString.split(",")
        releaseRates = []
        for s in splitReleaseRates:
            releaseRates.append(int(s))
        music = levelFile.readline()
        levelFile.readline() # line that just says SKILLS
        currentLine = levelFile.readline()
        skillCounts = []
        for i in range(int(numPlayers)):
            skillCount = {}
            for skill in SKILLS:
                skillCount[skill] = 0
            skillCounts.append(skillCount)
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
            objects.append(GameObjectInstance.createObjectFromString(currentLine))
            currentLine = levelFile.readline()
        levelFile.close()
        level = Level(int(width), int(height), int(startX), int(startY), terrain, objects, levelName[:-1], author[:-1], int(numberOfTechMechs), int(saveRequirement), skillCounts, int(timeLimit), releaseRates, music[:-1], int(numPlayers))
        return level
            




