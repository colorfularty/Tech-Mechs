import pygame
from pygame.locals import *
from constants import *

font = pygame.font.SysFont('helvetica', 32)

class Label(object):    
    def __init__(self, x, y, text):
        self.x = x
        self.y = y
        self.text = text
        self.image = font.render(self.text, True, WHITE, BLACK)
        self.image.set_colorkey(BLACK)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def render(self, surf):
        surf.blit(self.image, (self.x, self.y))

class Button(Label):
    def __init__(self, x, y, text):
        Label.__init__(self, x, y, text)

    def checkIfClicked(self, mousex, mousey):
        return mousex >= self.x and mousex <= self.x + self.image.get_width() and mousey >= self.y and mousey <= self.y + self.image.get_height()
        
class TextBox(object):
    def __init__(self, x, y, text = "", fontColor = WHITE, backColor = BLACK, size = 32):
        self.x = x
        self.y = y
        self.text = text
        self.fontColor = fontColor
        self.backColor = backColor
        self.size = size
        self.isClicked = False
        self.underscore = font.render("_", True, self.fontColor, self.backColor)
        self.setImage()

    def setImage(self, timer = 1.0):
        self.baseImage = font.render("Q" * self.size, True, self.fontColor, self.backColor)
        self.baseImage.fill(self.backColor)
        self.textImage = font.render(self.text, True, self.fontColor, self.backColor)
        self.baseImage.blit(self.textImage, (0, 0))
        if self.isClicked and timer < 0.5:
            self.baseImage.blit(self.underscore, (self.textImage.get_width(), 0))
        
    def render(self, surf, timer):
        self.setImage(timer)
        surf.blit(self.baseImage, (self.x, self.y))

    def checkIfClicked(self, mousex, mousey):
        self.isClicked = mousex >= self.x and mousex <= self.x + self.baseImage.get_width() and mousey >= self.y and mousey <= self.y + self.baseImage.get_height()
        return self.isClicked

    def changeText(self, key, shiftHeld = False):
        if key == K_BACKSPACE:
            if len(self.text) > 0:
                self.text = self.text[0:-1]
        elif key < 127 and len(self.text) < self.size:
            if key == K_SPACE:
                self.text += " "
            else:
                if shiftHeld:
                    self.text += pygame.key.name(key).upper()
                else:
                    self.text += pygame.key.name(key)
        self.setImage()

class NumberBox(TextBox):
    def __init__(self, x, y, text, fontColor = WHITE, backColor = BLACK, size = 6):
        TextBox.__init__(self, x, y, text, fontColor, backColor, size)

    def checkIfClicked(self, mousex, mousey):
        self.isClicked = mousex >= self.x and mousex <= self.x + self.baseImage.get_width() and mousey >= self.y and mousey <= self.y + self.baseImage.get_height()
        if self.text == "":
            self.text = "0"
            self.setImage()
        return self.isClicked

    def changeText(self, key):
        if key == K_BACKSPACE:
            if len(self.text) > 0:
                self.text = self.text[0:-1]
        elif key >= 48 and key <= 57 and len(self.text) < self.size:
            if len(self.text) > 0 or key != 48:
                self.text += pygame.key.name(key)
        for i in range(len(self.text)):
            if self.text[i] != "0":
                self.text = self.text[i:]
                break
        self.setImage()
