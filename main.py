# import libraries
import pygame, os
from pygame.locals import *

import constants

pygame.init()

SCREEN = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption("Tech Mechs")

# import other game files
import widgets
import vector
import terrain
import gameObject
import level
import techmech
import game

CLOCK = pygame.time.Clock()

mousex = 0
mousey = 0

currentMenu = "main"

# menu labels and buttons
playGameButton = widgets.Button(250, 0, "Play")
levelEditorButton = widgets.Button(250, 100, "Level editor")
graphicSetButton = widgets.Button(250, 200, "Graphic sets")
settingsButton = widgets.Button(250, 300, "Settings")
exitButton = widgets.Button(250, 400, "Exit")

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
        SCREEN.fill(constants.BLACK)
        playGameButton.render(SCREEN)
        levelEditorButton.render(SCREEN)
        graphicSetButton.render(SCREEN)
        settingsButton.render(SCREEN)
        exitButton.render(SCREEN)
        pygame.display.update()
        CLOCK.tick(constants.FPS)

    while currentMenu == "play":
        currentLevel = level.Level()
        testTerrain = terrain.Terrain("styles/special/test level.png", 0, 0)
        testEntrance = gameObject.Entrance("styles/special/entrance.png", 100, 0)
        testExit = gameObject.Exit("styles/special/exit.png", 500, 251)
        levelImage = pygame.surface.Surface((currentLevel.image.get_width(), currentLevel.image.get_height()))
        currentLevel.addObject(testEntrance)
        currentLevel.addObject(testExit)
        currentLevel.addTerrain(testTerrain)
        game.startLevel(currentLevel, CLOCK)
        while game.playingLevel:
            game.executeGameFrame(SCREEN)
        currentMenu = "main"

    while currentMenu == "editor":
        currentMenu = "main"

    while currentMenu == "graphics":
        currentMenu = "main"

    while currentMenu == "settings":
        currentMenu = "main"








