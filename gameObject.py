import pygame
import constants

class GameObject(object):
    def __init__(self, imageName, x, y, triggerX = 0, triggerY = 0, triggerWidth = 0, triggerHeight = 0):
        self.image = pygame.image.load(imageName).convert()
        self.image.set_colorkey(constants.BLACK)
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









        
