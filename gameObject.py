import pygame

class GameObject(object):
    # an object included in a graphic set
    
    def __init__(self, graphicSet, imageName):
        self.graphicSet = graphicSet # the NAME of the graphic set this object belongs to
        self.name = imageName # the NAME of the object's sprite sheet
        self.spriteSheet = pygame.image.load("styles/" + self.graphicSet + "/objects/" + self.name + ".png").convert_alpha()
        self.type, self.numFrames, self.triggerXDisp, self.triggerYDisp, self.triggerWidth, self.triggerHeight = GameObject.getData(self.graphicSet, self.name)
        self.width = self.spriteSheet.get_width() # the width of the object
        self.height = self.spriteSheet.get_height() // self.numFrames # the height of the object

    @classmethod
    def getData(self, graphicSet, objName):
        # gets the data regarding this specific object from the graphic set's data.txt file
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
        # returns an object to be inserted into a level
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
        # returns an object made from a string (used for loading levels from .txt files)
        owner = "0"
        splitString = string.split("~")
        if len(splitString) == 8:
            cls, graphicSet, name, x, y, flipped, inverted, rotated = splitString
        else:
            cls, graphicSet, name, x, y, flipped, inverted, rotated, owner = splitString
        if cls == 'Entrance':
            return Entrance(graphicSet, name, int(x), int(y), bool(flipped), bool(inverted), bool(rotated), int(owner))
        elif cls == 'Exit':
            return Exit(graphicSet, name, int(x), int(y), bool(flipped), bool(inverted), bool(rotated), int(owner))
        elif cls == 'Water':
            return Water(graphicSet, name, int(x), int(y), bool(flipped), bool(inverted), bool(rotated))
        else:
            return GameObjectInstance(graphicSet, name, int(x), int(y), bool(flipped), bool(inverted), bool(rotated))

    def setImage(self):
        self.image = self.spriteSheet.subsurface((0, self.height * self.animationFrame, self.width, self.height)).convert_alpha()

    def update(self):
        # re-initializes the object, useful for updating coordinates and images
        self.__init__(self.graphicSet, self.name, self.x, self.y, self.flipped, self.inverted, self.rotated)

    def render(self, surf):
        # blits the image to a surface
        surf.blit(self.image, (self.x, self.y))
        if self.animationFrame == self.numFrames - 1:
            self.animationFrame = 0
        else:
            self.animationFrame += 1
        self.setImage()
        

class Entrance(GameObjectInstance):
    # An object that releases Tech Mechs into the level
    
    status = "closed" # will only release Tech Mechs when it's opened
    
    def __init__(self, graphicSet, imageName, x, y, flipped, inverted, rotated, owner = 0):
        GameObjectInstance.__init__(self, graphicSet, imageName, x, y, flipped, inverted, rotated)
        self.owner = owner # the owner of the entrance; determines which colored Tech Mechs should be released from the entrance

    def __str__(self):
        return GameObjectInstance.__str__(self) + "~" + str(self.owner)

    @classmethod
    def open(self):
        Entrance.status = "open"

    def render(self, surf):
        surf.blit(self.image, (self.x, self.y))
        if Entrance.status == "open":
            if self.animationFrame < self.numFrames - 1:
                self.animationFrame += 1
        self.setImage()
        
        
class Exit(GameObjectInstance):
    # an object that lets Tech Mechs exit the level
    
    status = "open" # an exit can only be entered when it's open; when it's closed it blasts off to space
    sound = pygame.mixer.Sound("sound/rocket.wav")
    
    def __init__(self, graphicSet, imageName, x, y, flipped, inverted, rotated, owner = 0):
        GameObjectInstance.__init__(self, graphicSet, imageName, x, y, flipped, inverted, rotated)
        self.owner = owner # determines which Tech Mechs can enter it

    def __str__(self):
        return GameObjectInstance.__str__(self) + "~" + str(self.owner)

    @classmethod
    def close(self):
        Exit.status = "closed"
        Exit.sound.play(-1)
        
    def render(self, surf):
        surf.blit(self.image, (self.x, self.y))
        if Exit.status == "closed":
            if self.animationFrame == self.numFrames - 1:
                self.animationFrame = 0
            else:
                self.animationFrame += 1
        self.setImage()

class Water(GameObjectInstance):
    # an object that shorts out Tech Mechs who touch it; killing them
    
    def __init__(self, graphicSet, imageName, x, y, flipped, inverted, rotated):
        GameObjectInstance.__init__(self, graphicSet, imageName, x, y, flipped, inverted, rotated)

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
        









        
