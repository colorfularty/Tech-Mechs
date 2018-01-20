import pygame, os
import widgets
import vector
import terrain
import gameObject
import level
import techmech
from pygame.locals import *

pygame.init()

# colors
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption("Tech Mechs")

CLOCK = pygame.time.Clock()
FPS = 30

mousex = 0
mousey = 0

currentMenu = "main"

# menu labels and buttons
playGameButton = widgets.Button(250, 0, "Play")
levelEditorButton = widgets.Button(250, 100, "Level editor")
graphicSetButton = widgets.Button(250, 200, "Graphic sets")
settingsButton = widgets.Button(250, 300, "Settings")
exitButton = widgets.Button(250, 400, "Exit")

# level variables
currentLevel = None # the level you are playing
levelImage = None
currentFrame = 0
framesSinceLastRelease = 119
selectedSkill = "grappler"
isPaused = False
techMechs = [] # a list of the tech mechs currently out
techMechsOut = 0
techMechsSaved = 0
screenX = 0
screenY = 0

grappler = None

def readLevelFromFile(fileName):
    level = Level()
    levelFile = open(fileName + ".txt", 'r')
    # first line is TERRAIN
    levelFile.readline()

    levelFile.close()
    return level

def startupLevel(levelFile):
    global level, screenX, screenY

    level = readLevelFromFile(levelFile)
    
    screenX = level.startX
    screenY = level.startY

def handleGameEvents():
    global mousex, mousey, isPaused, selectedSkill, grappler
    
    for event in pygame.event.get():
        if event.type == MOUSEMOTION:
            mousex, mousey = event.pos
        elif event.type == MOUSEBUTTONDOWN:
            # check if there is a Tech Mech waiting to grapple
            if grappler != None:
                vec = vector.Vector(mousex - grappler.x, mousey - grappler.y)
                vec.normalize()
                grappler.grapple(currentLevel.image, vec)
                grappler = None
            else:
                # check if you clicked on a techmech
                for techMech in techMechs:
                    if techMech.wasClicked(mousex, mousey):
                        if techMech.currentSkill != "faller": # left click
                            if selectedSkill == "grappler":
                                grappler = techMech
                            else:
                                techMech.assignSkill(selectedSkill)
                            break
        elif event.type == KEYDOWN:
            if event.key == K_F7:
                selectedSkill = "grappler"
            elif event.key == K_F8:
                selectedSkill = "driller"
            elif event.key == K_F10:
                selectedSkill = "jackhammerer"
            elif event.key == K_F11:
                isPaused = not isPaused
        elif event.type == QUIT:
            pygame.quit()
            os._exit(0)

def executeGameFrame():
    global currentFrame, framesSinceLastRelease, techMechs, techMechsOut, techMechsSaved

    release = framesSinceLastRelease == 120 - currentLevel.releaseRate
    if release:
        framesSinceLastRelease = 0
    
    handleGameEvents()

    levelImage.fill(BLACK)

    # blit the terrain
    levelImage.blit(currentLevel.image, (0, 0))

    # blit the objects
    for obj in currentLevel.objects:
        levelImage.blit(obj.image, (obj.x, obj.y))
        if type(obj) is gameObject.Entrance:
            if release and techMechsOut < currentLevel.numberOfTechMechs:
                techMechs.append(techmech.TechMech(obj.x + 30, obj.y + 30))
                techMechsOut += 1

    # blit the tech mechs
    for techMech in techMechs:
        if not isPaused:
            if not techMech.act(currentLevel.image) or "exit" in currentLevel.triggerMap[techMech.x][techMech.y]:
                techMechs.remove(techMech)
                techMechsSaved += 1
        techMech.render(levelImage)

    # blit masks (if applicable)
    if grappler != None:
        pygame.draw.circle(levelImage, WHITE, (grappler.x, grappler.y), 150, 1)

    # orient the screen
    SCREEN.blit(levelImage, (screenX, screenY))

    # show screen updates and advance time
    pygame.display.update()
    CLOCK.tick(FPS)
    currentFrame += 1
    framesSinceLastRelease += 1

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
        playGameButton.render(SCREEN)
        levelEditorButton.render(SCREEN)
        graphicSetButton.render(SCREEN)
        settingsButton.render(SCREEN)
        exitButton.render(SCREEN)
        pygame.display.update()
        CLOCK.tick(FPS)

    while currentMenu == "play":
        currentLevel = level.Level()
        testTerrain = terrain.Terrain("styles/special/test level.png", 0, 0)
        testEntrance = gameObject.Entrance("styles/special/entrance.png", 100, 0)
        testExit = gameObject.Exit("styles/special/exit.png", 500, 375)
        levelImage = pygame.surface.Surface((currentLevel.image.get_width(), currentLevel.image.get_height()))
        currentLevel.addObject(testEntrance)
        currentLevel.addObject(testExit)
        currentLevel.addTerrain(testTerrain)
        while True:
            executeGameFrame()

    while currentMenu == "editor":
        currentMenu = "main"

    while currentMenu == "graphics":
        currentMenu = "main"

    while currentMenu == "settings":
        currentMenu = "main"








