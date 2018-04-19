import pygame
from pygame.locals import *
from constants import *

font = pygame.font.SysFont('helvetica', 32) # the font used for the widgets

class Label(object):
    # a text label
    
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

    def changeText(self, text):
        self.text = text
        self.image = font.render(self.text, True, WHITE, BLACK)
        self.image.set_colorkey(BLACK)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

class Button(Label):
    # a button you can push
    
    def __init__(self, x, y, text):
        Label.__init__(self, x, y, text)

    def checkIfClicked(self, mousex, mousey):
        return mousex >= self.x and mousex <= self.x + self.image.get_width() and mousey >= self.y and mousey <= self.y + self.image.get_height()
        
class TextBox(object):
    # a box you can input text into
    
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
    # a box you can enter a number into
    
    def __init__(self, x, y, text, fontColor = WHITE, backColor = BLACK, size = 6, minVal = 0, maxVal = 1000):
        TextBox.__init__(self, x, y, text, fontColor, backColor, size)
        self.minValue = minVal
        self.maxValue = maxVal

    def checkIfClicked(self, mousex, mousey):
        self.isClicked = mousex >= self.x and mousex <= self.x + self.baseImage.get_width() and mousey >= self.y and mousey <= self.y + self.baseImage.get_height()
        if self.text == "":
            self.text = "0"
            self.setImage()
        if not self.isClicked:
            if int(self.text) < self.minValue:
                self.text = str(self.minValue)
            elif int(self.text) > self.maxValue:
                self.text = str(self.maxValue)
        return self.isClicked

    def changeText(self, key):
        if key == K_BACKSPACE:
            if len(self.text) > 0:
                self.text = self.text[0:-1]
        elif key >= 48 and key <= 57 and len(self.text) < self.size:
            self.text += pygame.key.name(key)
        for i in range(len(self.text)):
            if self.text[i] != "0":
                self.text = self.text[i:]
                break
        self.setImage()

class SimpleImage(object):
    # a surface with a simple pygame.draw operation performed on it

    def __init__(self, startX, startY, width, height, speed, doesWrap):
        self.x = startX
        self.y = startY
        self.width = width
        self.height = height
        self.image = pygame.surface.Surface((self.width, self.height))
        self.speed = speed
        self.doesWrap = doesWrap

    def render(self, surf):
        surf.blit(self.image, (self.x, self.y))

    def checkForWrapping(self):
        if self.x < 0:
            self.x += SCREEN_WIDTH
        elif self.x >= SCREEN_WIDTH:
            self.x -= SCREEN_WIDTH
        if self.y < 0:
            self.y += SCREEN_HEIGHT
        elif self.y >= SCREEN_HEIGHT:
            self.y -= SCREEN_HEIGHT

    def move(self, direction):
        if "left" in direction:
            self.x -= self.speed
        if "right" in direction:
            self.x += self.speed
        if "up" in direction:
            self.y -= self.speed
        if "down" in direction:
            self.y += self.speed
        if self.doesWrap:
            self.checkForWrapping()

class Star(SimpleImage):
    # a star used for menus

    def __init__(self, startX, startY, radius = 5, speed = 15, doesWrap = True):
        SimpleImage.__init__(self, startX, startY, radius, radius, speed, doesWrap)
        pygame.draw.circle(self.image, WHITE, (self.width // 2, self.height // 2), self.width // 2)
