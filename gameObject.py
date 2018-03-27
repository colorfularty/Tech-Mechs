import pygame

class GameObject(object):
    def __init__(self, graphicSet, imageName):
        self.graphicSet = graphicSet
        self.name = imageName
        self.spriteSheet = pygame.image.load("styles/" + self.graphicSet + "/objects/" + self.name + ".png").convert()
        self.type, self.numFrames, self.triggerXDisp, self.triggerYDisp, self.triggerWidth, self.triggerHeight = GameObject.getData(self.graphicSet, self.name)
        from constants import BLACK
        self.spriteSheet.set_colorkey(BLACK)
        self.width = self.spriteSheet.get_width() # the width of the object
        self.height = self.spriteSheet.get_height() // self.numFrames # the height of the object

    @classmethod
    def getData(self, graphicSet, objName):
        dataFile = open("styles/" + graphicSet + "/data.txt", 'r')
        for line in dataFile:
            objType, name, numFrames, triggerXDisp, triggerYDisp, triggerWidth, triggerHeight = line.split("~")
            if name == objName:
                dataFile.close()
                return objType, int(numFrames), int(triggerXDisp), int(triggerYDisp), int(triggerWidth), int(triggerHeight)

class GameObjectInstance(GameObject):
    # a game object inserted into the level    
    @classmethod
    def insertObject(cls, graphicSet, name, x, y, flipped, inverted, rotated):
        return cls(graphicSet, name, x, y, flipped, inverted, rotated)

    def __init__(self, graphicSet, imageName, x, y, flipped, inverted, rotated):
        GameObject.__init__(self, graphicSet, imageName)
        self.x = x
        self.y = y
        self.triggerX = self.x + self.triggerXDisp
        self.triggerY = self.y + self.triggerYDisp
        self.flipped = flipped
        self.inverted = inverted
        self.rotated = rotated
        self.animationFrame = 0
        self.setImage()

    def __str__(self):
        return self.__class__.__name__ + "~" + self.graphicSet + "~" + self.name + "~" + str(self.x) + "~" + str(self.y) + "~" + str(self.flipped) + "~" + str(self.inverted) + "~" + str(self.rotated)

    @classmethod
    def createObjectFromString(self, string):
        cls, graphicSet, name, x, y, flipped, inverted, rotated = string.split("~")
        if cls == 'Entrance':
            return Entrance(graphicSet, name, int(x), int(y), bool(flipped), bool(inverted), bool(rotated))
        elif cls == 'Exit':
            return Exit(graphicSet, name, int(x), int(y), bool(flipped), bool(inverted), bool(rotated))
        else:
            return GameObjectInstance(graphicSet, name, int(x), int(y), bool(flipped), bool(inverted), bool(rotated))

    def setImage(self):
        self.image = self.spriteSheet.subsurface((0, self.height * self.animationFrame, self.width, self.height))

    def update(self):
        self.__init__(self.graphicSet, self.name, self.x, self.y, self.flipped, self.inverted, self.rotated)
        

class Entrance(GameObjectInstance):
    status = "closed"
    
    def __init__(self, graphicSet, imageName, x, y, flipped, inverted, rotated):
        GameObjectInstance.__init__(self, graphicSet, imageName, x, y, flipped, inverted, rotated)

    @classmethod
    def open(self):
        Entrance.status = "open"
        
class Exit(GameObjectInstance):
    status = "open"
    
    def __init__(self, graphicSet, imageName, x, y, flipped, inverted, rotated):
        GameObjectInstance.__init__(self, graphicSet, imageName, x, y, flipped, inverted, rotated)

    @classmethod
    def close(self):
        Exit.status = "closed"

class TechMechObject(object):
    # an object placed by a Tech Mech

    def __init__(self, imageName, x, y, triggerX, triggerY, triggerWidth, triggerHeight, orientation):
        self.imageName = imageName
        self.image = pygame.image.load(imageName).convert()
        from constants import BLACK
        self.image.set_colorkey(BLACK)
        self.x = x
        self.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.triggerX = triggerX
        self.triggerY = triggerY
        self.triggerWidth = triggerWidth
        self.triggerHeight = triggerHeight
        self.orientation = orientation
        self.image = pygame.transform.flip(self.image, False, self.orientation < 0)

    def render(self, surf):
        surf.blit(self.image, (self.x, self.y))

class CautionSign(TechMechObject):
    # a caution sign which turns Tech Mechs around when they hit the trigger area

    def __init__(self, triggerX, triggerY, orientation):
        y = triggerY - 59
        if orientation < 0:
            y = triggerY
        TechMechObject.__init__(self, "sprites/caution sign.png", triggerX - 12, y, triggerX, triggerY, 1, 1, orientation)

class LandMine(TechMechObject):
    # a land mine that blows up nearby terrain after 3 seconds

    def __init__(self, triggerX, triggerY, orientation):
        y = triggerY - 5
        if orientation < 0:
            y = triggerY
        TechMechObject.__init__(self, "sprites/land mine.png", triggerX - 2, y, triggerX, triggerY, 30, 30, orientation)
        self.timer = 3.0
        









        
