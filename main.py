import pygame, os, random
from pygame.locals import *
from constants import *

SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption("Tech Mechs")
pygame.display.set_icon(pygame.image.load("sprites/icon.png").convert_alpha())

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
from waitScreen import *
from resultsScreen import *
from settingsScreen import *
from client import Client

mousex = 0
mousey = 0

currentMenu = "main"

# menu labels and buttons
titleScreen = pygame.image.load("sprites/Title text.png").convert()
titleScreen.set_colorkey(BLACK)
singlePlayerButton = Button(150, 150, "Single Player")
multiplayerButton = Button(150, 200, "Multiplayer")
levelEditorButton = Button(450, 150, "Level editor")
settingsButton = Button(450, 200, "Settings")
exitButton = Button(450, 250, "Exit")

stars = []
for i in range(200):
    stars.append(Star(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)))

while True: # main game loop
    
    while currentMenu == "main":
        for event in pygame.event.get():
            if event.type == MOUSEMOTION:
                mousex, mousey = event.pos
            elif event.type == MOUSEBUTTONDOWN:
                if singlePlayerButton.checkIfClicked(mousex, mousey):
                    currentMenu = "single player"
                elif multiplayerButton.checkIfClicked(mousex, mousey):
                    currentMenu = "multiplayer"
                elif levelEditorButton.checkIfClicked(mousex, mousey):
                    currentMenu = "editor"
                elif settingsButton.checkIfClicked(mousex, mousey):
                    currentMenu = "settings"
                elif exitButton.checkIfClicked(mousex, mousey):
                    pygame.quit()
                    os._exit(0)
            elif event.type == QUIT:
                pygame.quit()
                os._exit(0)
        SCREEN.fill(BLACK)
        for star in stars:
            star.move(["left"])
            star.render(SCREEN)
        SCREEN.blit(titleScreen, (SCREEN_WIDTH // 2 - titleScreen.get_width() // 2, 0))
        singlePlayerButton.render(SCREEN)
        multiplayerButton.render(SCREEN)
        levelEditorButton.render(SCREEN)
        settingsButton.render(SCREEN)
        exitButton.render(SCREEN)
        pygame.display.update()
        CLOCK.tick(FPS)

    while currentMenu == "single player":
        currentLevel = None
        startLoadScreen(1)
        while currentLevel == None:
            currentLevel = executeLoadScreenFrame(SCREEN)
        if currentLevel != False:
            startLevel(currentLevel)
            playingLevel = True
            while playingLevel:
                playingLevel, techMechsSaved = executeGameFrame(SCREEN)
            continueResults = True
            startResultsScreen(techMechsSaved, currentLevel.saveRequirement)
            while continueResults:
                continueResults = executeResultsScreenFrame(SCREEN)
        currentMenu = "main"

    while currentMenu == "multiplayer":
        continueSetup = True
        try:
            connection = Client()
        except ConnectionRefusedError:
            continueSetup = False
        if continueSetup:
            playerNum = int(connection.receiveString())
            currentLevel = None
            if playerNum == 0:
                startWaitScreen(connection, "Please wait while Player 2 joins the server...")
                dataSent = False
                while dataSent == False:
                    dataSent = executeWaitScreenFrame(SCREEN)
                if dataSent != "False":
                    startLoadScreen(2)
                    while currentLevel == None:
                        currentLevel = executeLoadScreenFrame(SCREEN)
                    if currentLevel != False:
                        connection.sendString(currentLevel.name)
                        startLevel(currentLevel, playerNum, connection)
                        playingLevel = True
                        while playingLevel:
                            playingLevel, techMechsSaved = executeGameFrame(SCREEN)
                        continueResults = True
                        startResultsScreen(techMechsSaved, currentLevel.saveRequirement)
                        while continueResults:
                            continueResults = executeResultsScreenFrame(SCREEN)
                    else:
                        connection.sendString("False")
            else:
                connection.sendString("Start")
                startWaitScreen(connection, "Please wait while Player 1 chooses a 2P level...")
                dataSent = False
                while dataSent == False:
                    dataSent = executeWaitScreenFrame(SCREEN)
                if dataSent != "False":
                    currentLevel = Level.loadLevel(dataSent)
                if currentLevel != None:
                    startLevel(currentLevel, playerNum, connection)
                    playingLevel = True
                    while playingLevel:
                        playingLevel, techMechsSaved = executeGameFrame(SCREEN)
                    continueResults = True
                    startResultsScreen(techMechsSaved, currentLevel.saveRequirement)
                    while continueResults:
                        continueResults = executeResultsScreenFrame(SCREEN)
        currentMenu = "main"

    while currentMenu == "editor":
        startEditor()
        inEditor = True
        while inEditor:
            inEditor = executeEditorFrame(SCREEN)
        currentMenu = "main"

    while currentMenu == "settings":
        startSettingsScreen()
        continueSettings = True
        while continueSettings:
            continueSettings = executeSettingsFrame(SCREEN)
        currentMenu = "main"








