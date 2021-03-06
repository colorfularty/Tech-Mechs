import pygame, os
from pygame import *
from constants import *
from widgets import *
from level import *

# the buttons used for selecting a level
backButton = Button(500, 0, "Back")
upArrow = Button(0, 0, "^")
downArrow = Button(0, 450, "v")

buttons = [] # a list of the level buttons you can click on

# keeps track of the mouse pointer's coordinates
mousex = 0
mousey = 0

levelFiles = None
levelLoaded = None
topNameIndex = 0 # the index of the top level name

def loadLevelFiles(numPlayers):
    # reads and returns the names of all .txt files in your levels directory
    files = []
    for file in os.listdir("levels"):
        if file.endswith(".txt"):
            openFile = open("levels/" + file, 'r')
            firstLine = openFile.readline()
            if numPlayers == None or int(firstLine) == numPlayers:
                files.append(file.split(".")[0]) # removes the extension
            openFile.close()
    return files

def startLoadScreen(numPlayers = None):
    global levelFiles, levelLoaded, topNameIndex

    levelFiles = loadLevelFiles(numPlayers)
    levelLoaded = None
    topNameIndex = 0

def renderLevelNames(surf):
    # renders the level images on the screen

    global buttons

    buttons = []
    
    for i in range(1, 9):
        if i <= len(levelFiles):
            levelImage = Button(0, i * 50, levelFiles[topNameIndex + i - 1])
            buttons.append(levelImage)
            levelImage.render(surf)
        else:
            break

def handleLoadScreenEvents():
    global levelLoaded, topNameIndex, mousex, mousey
    
    for event in pygame.event.get():
        if event.type == MOUSEMOTION:
            mousex, mousey = event.pos
        elif event.type == MOUSEBUTTONDOWN:
            if backButton.checkIfClicked(mousex, mousey):
                levelLoaded = False
            elif upArrow.checkIfClicked(mousex, mousey) and topNameIndex > 0 and len(levelFiles) > 8:
                topNameIndex -= 1
            elif downArrow.checkIfClicked(mousex, mousey) and topNameIndex + 8 < len(levelFiles) and len(levelFiles) > 8:
                topNameIndex += 1
            for button in buttons:
                if button.checkIfClicked(mousex, mousey):
                    levelLoaded = Level.loadLevel(button.text)
                    break
        elif event.type == QUIT:
            pygame.quit()
            os._exit(0)

def executeLoadScreenFrame(SCREEN):
    handleLoadScreenEvents()

    SCREEN.fill(GREY)
    backButton.render(SCREEN)
    if topNameIndex > 0:
        upArrow.render(SCREEN)
    if topNameIndex + 8 < len(levelFiles):
        downArrow.render(SCREEN)
    renderLevelNames(SCREEN)

    pygame.display.update()
    CLOCK.tick(FPS)
    return levelLoaded
