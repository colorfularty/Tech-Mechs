import pygame, os
from pygame.locals import *
from constants import *
from widgets import *
from gameHotkeys import *
from editorHotkeys import *

continueSettings = True # returned to main.py; terminates when False

# keeps track of the mouse pointer's coordinates
mousex = 0
mousey = 0

# buttons for navigating the menu
gameHotkeysButton = Button(0, 0, "Game Hotkeys")
editorHotkeysButton = Button(0, 50, "Editor Hotkeys")
backButton = Button(0, SCREEN_HEIGHT - 50, "Back to menu")

def startSettingsScreen():
    global continueSettings

    continueSettings = True

def handleSettingsEvents(SCREEN):
    global mousex, mousey, continueSettings
    
    for event in pygame.event.get():
        if event.type == MOUSEMOTION:
            mousex, mousey = event.pos
        elif event.type == MOUSEBUTTONDOWN:
            if gameHotkeysButton.checkIfClicked(mousex, mousey):
                startGameHotkeys()
                continueGameHotkeys = True
                while continueGameHotkeys:
                    continueGameHotkeys = executeGameHotkeysFrame(SCREEN)
            elif editorHotkeysButton.checkIfClicked(mousex, mousey):
                startEditorHotkeys()
                continueEditorHotkeys = True
                while continueEditorHotkeys:
                    continueEditorHotkeys = executeEditorHotkeysFrame(SCREEN)
            elif backButton.checkIfClicked(mousex, mousey):
                continueSettings = False
        elif event.type == QUIT:
            pygame.quit()
            os._exit(0)

def executeSettingsFrame(SCREEN):
    handleSettingsEvents(SCREEN)
    SCREEN.fill(BLACK)
    gameHotkeysButton.render(SCREEN)
    editorHotkeysButton.render(SCREEN)
    backButton.render(SCREEN)
    pygame.display.update()
    CLOCK.tick(FPS)
    return continueSettings
