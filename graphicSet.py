import os
from terrain import *

class GraphicSet(object):
    graphicSets = []
    
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
        graphicSetNames = []
        allFiles = os.listdir("styles/")
        for file in allFiles:
            if os.path.isdir("styles/" + file):
                graphicSetNames.append(file)

        for name in graphicSetNames:
            graphicSet = GraphicSet(name)
            allTerrain = os.listdir("styles/" + name + "/")
            for terrainPiece in allTerrain:
                terrain = Terrain("styles/" + name + "/" + terrainPiece)
                graphicSet.addTerrain(terrain)

        
