import pygame, os
from pygame.locals import *
from constants import *
from widgets import *

continueGameHotkeys = True # returned to settings.py; terminates when False
hotkeyEdited = None # the current hotkey being edited

# used to determine the mouse pointer's coordinates
mousex = 0
mousey = 0

hotkeyFunctions = [] # a list of all of the labels of the hotkey functions
hotkeys = [] # a list of all of the buttons of the hotkey values
backButton = Button(0, SCREEN_HEIGHT - 50, "Back to settings")

def loadGameHotkeys():
    # loads the hotkey values from game hotkeys.txt and modifies the variables in constants.py
    hotkeyFile = open("game hotkeys.txt", 'r')
    for line in hotkeyFile:
        function, hotkey = line.split(": ")
        if hotkey[-1] == '\n':
            hotkey = hotkey[:-1]
        GAME_HOTKEYS[function] = hotkey
    hotkeyFile.close()

def saveGameHotkeys():
    # saves the current game hotkey values to the text file
    hotkeyFile = open("game hotkeys.txt", 'w')
    for i in range(len(hotkeys)):
        hotkeyFile.write(hotkeyFunctions[i].text + ": " + hotkeys[i].text)
    hotkeyFile.close()
    loadGameHotkeys()

def startGameHotkeys():
    global continueGameHotkeys, hotkeyEdited, hotkeyFunctions, hotkeys

    continueGameHotkeys = True
    hotkeyEdited = None
    hotkeyFunctions = []
    hotkeys = []
    hotkeyFile = open("game hotkeys.txt", 'r')
    count = 0
    for line in hotkeyFile:
        function, hotkey = line.split(": ")
        if hotkey[-1] == '\n':
            hotkey = hotkey[:-1]
        hotkeyFunctions.append(Label(0, count * 50, function))
        hotkeys.append(Button(SCREEN_WIDTH // 2, count * 50, hotkey))
        count += 1
    hotkeyFile.close()

def handleGameHotkeysEvents():
    global mousex, mousey, continueGameHotkeys, hotkeyEdited

    for event in pygame.event.get():
        if event.type == MOUSEMOTION:
            mousex, mousey = event.pos
        elif event.type == MOUSEBUTTONDOWN:
            hotkeyEdited = None
            for i in range(len(hotkeys)):
                if hotkeys[i].checkIfClicked(mousex, mousey):
                    hotkeyEdited = i
                    break
            if backButton.checkIfClicked(mousex, mousey):
                continueGameHotkeys = False
        elif event.type == KEYDOWN:
            if hotkeyEdited != None:
                hotkeys[hotkeyEdited].changeText(pygame.key.name(event.key))
        elif event.type == QUIT:
            pygame.quit()
            os._exit(0)

def executeGameHotkeysFrame(SCREEN):
    handleGameHotkeysEvents()
    SCREEN.fill(BLACK)
    for i in range(len(hotkeys)):
        hotkeyFunctions[i].render(SCREEN)
        hotkeys[i].render(SCREEN)
    backButton.render(SCREEN)
    pygame.display.update()
    CLOCK.tick(FPS)
    return continueGameHotkeys
