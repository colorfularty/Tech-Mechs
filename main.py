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

mousex = 0
mousey = 0

currentMenu = "main"

# menu labels and buttons
titleScreen = pygame.image.load("sprites/Title Screen.png")
playGameButton = Button(150, 150, "Play")
levelEditorButton = Button(250, 100, "Level editor")
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
        #levelEditorButton.render(SCREEN)
        #graphicSetButton.render(SCREEN)
        #settingsButton.render(SCREEN)
        exitButton.render(SCREEN)
        pygame.display.update()
        CLOCK.tick(FPS)

    while currentMenu == "play":
        testTerrain = Terrain("styles/special/test level 2.png", 0, 0)
        testEntrance = Entrance("styles/special/entrance.png", 200, 0)
        testExit = Exit("styles/special/exit.png", 464 - 46, 479 - 165)
        currentLevel = Level(testTerrain.image.get_width(), testTerrain.image.get_height())
        levelImage = pygame.surface.Surface((currentLevel.image.get_width(), currentLevel.image.get_height()))
        currentLevel.addObject(testEntrance)
        currentLevel.addObject(testExit)
        currentLevel.addTerrain(testTerrain)
        startLevel(currentLevel)
        while playingLevel:
            executeGameFrame(SCREEN)
        currentMenu = "main"

    while currentMenu == "editor":
        currentMenu = "main"

    while currentMenu == "graphics":
        currentMenu = "main"

    while currentMenu == "settings":
        currentMenu = "main"








