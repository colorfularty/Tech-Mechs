import pygame, os, random
from pygame.locals import *
from constants import *

# initialize game window
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

# keeps track of the mouse pointer's coordinates
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

# used for the starfield on the title screen
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

        # update screen; fill with black, then blit starfield and widgets
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
        # allow user to specify a level to load
        currentLevel = None
        startLoadScreen(1)
        while currentLevel == None:
            currentLevel = executeLoadScreenFrame(SCREEN)
            
        if currentLevel != False:
            # start the level
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
        # create a connection to the server (if server is running)
        continueSetup = True
        try:
            connection = Client()
        except ConnectionRefusedError:
            continueSetup = False
            
        if continueSetup:
            # get your player number from the server
            playerNum = int(connection.receiveString())

            # load level (level is selected by player 0, while player 1 waits)
            currentLevel = None
            if playerNum == 0:
                # wait until the second player connects before selecting a level
                startWaitScreen(connection, "Please wait while Player 2 joins the server...")
                dataSent = False
                while dataSent == False:
                    dataSent = executeWaitScreenFrame(SCREEN)

                # choose a level and send it to the other player
                if dataSent != "False":
                    startLoadScreen(2)
                    while currentLevel == None:
                        currentLevel = executeLoadScreenFrame(SCREEN)

                    # play the level
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
                # receive the level from the other player
                connection.sendString("Start")
                startWaitScreen(connection, "Please wait while Player 1 chooses a 2P level...")
                dataSent = False
                while dataSent == False:
                    dataSent = executeWaitScreenFrame(SCREEN)

                # play the level
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
        # enter the level editor
        startEditor()
        inEditor = True
        while inEditor:
            inEditor = executeEditorFrame(SCREEN)
        currentMenu = "main"

    while currentMenu == "settings":
        # enter the settings screen
        startSettingsScreen()
        continueSettings = True
        while continueSettings:
            continueSettings = executeSettingsFrame(SCREEN)
        currentMenu = "main"








