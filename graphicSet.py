import os
from terrain import *
from gameObject import *

class GraphicSet(object):
    # a collection of terrain and objects
    
    graphicSets = [] # a list of all the graphic sets in the game
    
    def __init__(self, name):
        self.name = name
        self.terrain = [] # a list of all of the terrain in the graphic set
        self.objects = [] # a list of all of the objects in the graphic set

    def addTerrain(self, newTerrain):
        self.terrain.append(newTerrain)

    def addObject(self, newObject):
        self.objects.append(newObject)

    @classmethod
    def loadGraphicSets(self):
        # loads every single graphic set and adds them to the class variable
        graphicSetNames = []
        allFiles = os.listdir("styles/")
        for file in allFiles:
            if os.path.isdir("styles/" + file):
                graphicSetNames.append(file)

        for name in graphicSetNames:
            graphicSet = GraphicSet(name)
            allTerrain = os.listdir("styles/" + name + "/terrain/")
            for terrainPiece in allTerrain:
                terrain = Terrain(name, terrainPiece.split(".")[0])
                graphicSet.addTerrain(terrain)
            allObjects = os.listdir("styles/" + name + "/objects/")
            for obj in allObjects:
                o = GameObject(name, obj.split(".")[0])
                graphicSet.addObject(o)
            GraphicSet.graphicSets.append(graphicSet)

        
