import pygame

class GameObject(object):
    def __init__(self, imageName, x, y, triggerX = 0, triggerY = 0, triggerWidth = 0, triggerHeight = 0):
        self.image = pygame.image.load(imageName).convert()
        from constants import BLACK
        self.image.set_colorkey(BLACK)
        self.x = x # the x-coordinate of the object on the level
        self.y = y # the y-coordinate of the object on the level
        self.width = self.image.get_width() # the width of the object
        self.height = self.image.get_height() # the height of the object
        self.triggerX = triggerX # the x-coordinate of the object's trigger area relative to the object surface
        self.triggerY = triggerY # the y-coordinate of the object's trigger area relative to the object surface
        self.triggerWidth = triggerWidth # the width of the object's trigger
        self.triggerHeight = triggerHeight # the height of the object's trigger

    def animate(self):
        pass

class Entrance(GameObject):
    status = "closed"
    
    def __init__(self, imageName, x, y):
        GameObject.__init__(self, imageName, x, y, x + 22, y + 21, 1, 1)

    @classmethod
    def open(self):
        Entrance.status = "open"
        
class Exit(GameObject):
    status = "open"
    
    def __init__(self, imageName, x, y):
        GameObject.__init__(self, imageName, x, y, x + 43, y + 155, 7, 11)

    @classmethod
    def close(self):
        Exit.status = "closed"

class Trap(GameObject):
    def __init__(self, imageName, x, y, triggerX, triggerY, triggerWidth, triggerHeight):
        GameObject.__init__(self, imageName, x, y, triggerX, triggerY, triggerWidth, triggerHeight)

class Water(Trap):
    def __init__(self, imageName, x, y, triggerX, triggerY, triggerWidth, triggerHeight):
        Trap.__init__(self, imageName, x, y, triggerX, triggerY, triggerWidth, triggerHeight)

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
        









        
