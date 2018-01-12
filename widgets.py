import pygame

pygame.init()

# colors
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)

class Label(object):
    font = pygame.font.SysFont('helvetica', 32)
    
    def __init__(self, x, y, text):
        self.x = x
        self.y = y
        self.text = text
        self.image = self.font.render(self.text, True, WHITE, BLACK)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def render(self, surf):
        surf.blit(self.image, (self.x, self.y))

class Button(Label):
    def __init__(self, x, y, text):
        Label.__init__(self, x, y, text)

    def render(self, surf):
        Label.render(self, surf)

    def checkIfClicked(self, mousex, mousey):
        if mousex >= self.x and mousex <= self.x + self.width:
            if mousey >= self.y and mousey <= self.y + self.height:
                return True
        return False
        
