import pygame

BLACK = (0, 0, 0)

class GameObject(object):
    def __init__(self, imageName, x, y):
        self.image = pygame.image.load(imageName).convert()
        self.image.set_colorkey(BLACK)
        self.x = x # the x-coordinate of the object on the level
        self.y = y # the y-coordinate of the object on the level
        self.width = self.image.get_width() # the width of the object
        self.height = self.image.get_height() # the height of the object
        self.triggerX = 0 # the x-coordinate of the object's trigger area relative to the object surface
        self.triggerY = 0 # the y-coordinate of the object's trigger area relative to the object surface
        self.triggerWidth = 0 # the width of the object's trigger
        self.triggerHeight = 0 # the height of the object's trigger

    def animate(self):
        pass

class Entrance(GameObject):
    def __init__(self, imageName, x, y):
        GameObject.__init__(self, imageName, x, y)
        self.status = "closed"
        
    def animate(self, currentFrame):
        if self.status == "closed" and currentFrame > 60:
            self.status = "open"
        
class Exit(GameObject):
    def __init__(self, imageName, x, y):
        GameObject.__init__(self, imageName, x, y)









        
