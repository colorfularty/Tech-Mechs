import pygame, os
from pygame.locals import *
from constants import *
from widgets import *

continueEditorHotkeys = True # returned to settings.py; terminate if False
hotkeyEdited = None # the hotkey currently being edited

# keeps track of the mouse pointer's coordinates
mousex = 0
mousey = 0

hotkeys = [] # a list of all of the hotkeys taken from the text file
hotkeyFunctions = [] # a list of all of the labels regarding what the hotkeys do
hotkeyValues = [] # a list of all of the buttons allowing you to change hotkey values
topHotkey = 0 # the index of the hotkey at the top of the screen

# buttons for navigating the hotkey menu
hotkeyUp = Button(0, 0, "^")
hotkeyDown = Button(0, SCREEN_HEIGHT - 100, "v")
backButton = Button(0, SCREEN_HEIGHT - 50, "Back to settings")

def loadHotkeyPanels():
    # loads as many hotkeys onto the screen as possible
    global hotkeyFunctions, hotkeyValues

    hotkeyFunctions = []
    hotkeyValues = []
    for i in range(NUM_HOTKEY_PANELS):
        function, value = hotkeys[topHotkey + i]
        hotkeyFunctions.append(Label(0, (i + 1) * 50, function))
        hotkeyValues.append(Button(2 * SCREEN_WIDTH // 3, (i + 1) * 50, value))

def loadEditorHotkeys():
    # loads the hotkeys from the text file and updates the variable in constants.py
    hotkeyFile = open("editor hotkeys.txt", 'r')
    for line in hotkeyFile:
        function, hotkey = line.split(": ")
        if hotkey[-1] == '\n':
            hotkey = hotkey[:-1]
        EDITOR_HOTKEYS[function] = hotkey
    hotkeyFile.close()

def saveEditorHotkeys():
    # saves the current hotkey configuration to the text file
    hotkeyFile = open("editor hotkeys.txt", 'w')
    for i in range(len(hotkeys)):
        hotkeyFile.write(hotkeys[i][0] + ": " + hotkeys[i][1] + '\n')
    hotkeyFile.close()
    loadEditorHotkeys()

def startEditorHotkeys():
    global continueEditorHotkeys, hotkeyEdited, hotkeys, topHotkey

    continueEditorHotkeys = True
    hotkeyEdited = None
    topHotkey = 0
    hotkeys = []
    hotkeyFile = open("editor hotkeys.txt", 'r')
    for line in hotkeyFile:
        function, hotkey = line.split(": ")
        if hotkey[-1] == '\n':
            hotkey = hotkey[:-1]
        hotkeys.append([function, hotkey])
    hotkeyFile.close()
    loadHotkeyPanels()

def handleEditorHotkeysEvents():
    global mousex, mousey, continueEditorHotkeys, hotkeyEdited, topHotkey

    for event in pygame.event.get():
        if event.type == MOUSEMOTION:
            mousex, mousey = event.pos
        elif event.type == MOUSEBUTTONDOWN:
            hotkeyEdited = None
            for i in range(len(hotkeyValues)):
                if hotkeyValues[i].checkIfClicked(mousex, mousey):
                    hotkeyEdited = i
                    break
            if backButton.checkIfClicked(mousex, mousey):
                continueEditorHotkeys = False
                saveEditorHotkeys()
                loadEditorHotkeys()
            elif hotkeyUp.checkIfClicked(mousex, mousey):
                if topHotkey > 0:
                    topHotkey -= 1
                    loadHotkeyPanels()
            elif hotkeyDown.checkIfClicked(mousex, mousey):
                if topHotkey < len(hotkeys) - NUM_HOTKEY_PANELS:
                    topHotkey += 1
                    loadHotkeyPanels()
        elif event.type == KEYDOWN:
            if hotkeyEdited != None:
                hotkeyValues[hotkeyEdited].changeText(pygame.key.name(event.key))
                hotkeys[topHotkey + hotkeyEdited][1] = pygame.key.name(event.key)
        elif event.type == QUIT:
            pygame.quit()
            os._exit(0)

def executeEditorHotkeysFrame(SCREEN):
    handleEditorHotkeysEvents()
    SCREEN.fill(BLACK)
    if topHotkey > 0:
        hotkeyUp.render(SCREEN)
    if topHotkey + NUM_HOTKEY_PANELS < len(hotkeys):
        hotkeyDown.render(SCREEN)
    for i in range(NUM_HOTKEY_PANELS):
        hotkeyFunctions[i].render(SCREEN)
        hotkeyValues[i].render(SCREEN)
    backButton.render(SCREEN)
    pygame.display.update()
    CLOCK.tick(FPS)
    return continueEditorHotkeys
