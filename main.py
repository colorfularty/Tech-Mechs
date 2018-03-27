import pygame, os
from pygame.locals import *

pygame.init()

from constants import *

SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption("Tech Mechs")

# import other game files
from widgets import *
from terrain import *
from gameObject import *
from level import *
from game import *
from graphicSet import *
GraphicSet.loadGraphicSets()
from levelEditor import *
from loadScreen import *

mousex = 0
mousey = 0

currentMenu = "main"

# menu labels and buttons
titleScreen = pygame.image.load("sprites/Title Screen.png")
playGameButton = Button(150, 150, "Play")
levelEditorButton = Button(150, 200, "Level editor")
graphicSetButton = Button(250, 200, "Graphic sets")
settingsButton = Button(250, 300, "Settings")
exitButton = Button(450, 150, "Exit")

while True: # main game loop
    
    while currentMenu == "main":
        for event in pygame.event.get():
            if event.type == MOUSEMOTION:
                mousex, mousey = event.pos
            elif event.type == MOUSEBUTTONDOWN:
                if playGameButton.checkIfClicked(mousex, mousey):
                    currentMenu = "play"
                elif levelEditorButton.checkIfClicked(mousex, mousey):
                    currentMenu = "editor"
                elif graphicSetButton.checkIfClicked(mousex, mousey):
                    currentMenu = "graphics"
                elif settingsButton.checkIfClicked(mousex, mousey):
                    currentMenu = "settings"
                elif exitButton.checkIfClicked(mousex, mousey):
                    pygame.quit()
                    os._exit(0)
            elif event.type == QUIT:
                pygame.quit()
                os._exit(0)
        SCREEN.fill(BLACK)
        SCREEN.blit(titleScreen, (0, 0))
        playGameButton.render(SCREEN)
        levelEditorButton.render(SCREEN)
        #graphicSetButton.render(SCREEN)
        #settingsButton.render(SCREEN)
        exitButton.render(SCREEN)
        pygame.display.update()
        CLOCK.tick(FPS)

    while currentMenu == "play":
        currentLevel = None
        startLoadScreen()
        while currentLevel == None:
            currentLevel = executeLoadScreenFrame(SCREEN)
        if currentLevel != False:
            startLevel(currentLevel, 0)
            playingLevel = True
            while playingLevel:
                playingLevel = executeGameFrame(SCREEN)
        currentMenu = "main"

    while currentMenu == "editor":
        startEditor()
        inEditor = True
        while inEditor:
            inEditor = executeEditorLoop(SCREEN)
        currentMenu = "main"

    while currentMenu == "graphics":
        currentMenu = "main"

    while currentMenu == "settings":
        currentMenu = "main"








