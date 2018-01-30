# import libraries
import pygame, os
from pygame.locals import *

pygame.init()

# colors
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)

SCREEN_WIDTH = 650
SCREEN_HEIGHT = 500
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption("Tech Mechs")

# import other game files
import widgets
import vector
import terrain
import gameObject
import level
import techmech

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

# game images
skillFont = pygame.font.SysFont("helvetica", 32)
skillPanel = pygame.image.load("sprites/skill panel.png")
skillHighlight = pygame.image.load("sprites/skill highlight.png").convert()
skillHighlight.set_colorkey(BLACK)

# level variables
currentLevel = None # the level you are playing
levelImage = None
currentFrame = 0
framesSinceLastRelease = 119
selectedSkill = "grappler"
isPaused = False
techMechs = [] # a list of the tech mechs currently out
techMechsReleased = 0
techMechsSaved = 0
screenX = 0
screenY = 0
replay = {}

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

def renderSkillPanel():
    # blits the skill panel, the images, and the number of skills left
    # to the bottom of the screen

    # start by blitting the empty skill panels
    for i in range(13):
        SCREEN.blit(skillPanel, (i * 50, SCREEN_HEIGHT - 100))
        
    # TODO: now blit the skill images on each panel
    grapplingHookSkill = pygame.image.load("sprites/grappling hook skill.png").convert()
    drillSkill = pygame.image.load("sprites/drill skill.png").convert()
    jackhammerSkill = pygame.image.load("sprites/jackhammer skill.png").convert()
    gravitySkill = pygame.image.load("sprites/gravity skill.png").convert()

    grapplingHookSkill.set_colorkey(BLACK)
    drillSkill.set_colorkey(BLACK)
    jackhammerSkill.set_colorkey(BLACK)
    gravitySkill.set_colorkey(BLACK)

    SCREEN.blit(grapplingHookSkill, (25 - grapplingHookSkill.get_width() // 2, SCREEN_HEIGHT - 40))
    SCREEN.blit(drillSkill, (75 - drillSkill.get_width() // 2, SCREEN_HEIGHT - 40))
    SCREEN.blit(jackhammerSkill, (125 - jackhammerSkill.get_width() // 2, SCREEN_HEIGHT - 40))
    SCREEN.blit(gravitySkill, (175 - gravitySkill.get_width() // 2, SCREEN_HEIGHT - 40))

    # compute the skills left and TODO: blit those to the skill panel
    grapplingHooksLeft = skillFont.render(str(currentLevel.skillCounts["grappler"]), True, WHITE, BLACK)
    drillsLeft = skillFont.render(str(currentLevel.skillCounts["driller"]), True, WHITE, BLACK)
    jackhammersLeft = skillFont.render(str(currentLevel.skillCounts["jackhammerer"]), True, WHITE, BLACK)
    gravityReversersLeft = skillFont.render(str(currentLevel.skillCounts["gravity reverser"]), True, WHITE, BLACK)

    grapplingHooksLeft.set_colorkey(BLACK)
    drillsLeft.set_colorkey(BLACK)
    jackhammersLeft.set_colorkey(BLACK)
    gravityReversersLeft.set_colorkey(BLACK)

    SCREEN.blit(grapplingHooksLeft, (25 - grapplingHooksLeft.get_width() // 2, SCREEN_HEIGHT - 90))
    SCREEN.blit(drillsLeft, (75 - drillsLeft.get_width() // 2, SCREEN_HEIGHT - 90))
    SCREEN.blit(jackhammersLeft, (125 - jackhammersLeft.get_width() // 2, SCREEN_HEIGHT - 90))
    SCREEN.blit(gravityReversersLeft, (175 - gravityReversersLeft.get_width() // 2, SCREEN_HEIGHT - 90))

def addToReplay(techMech, skill, vec = None):
    if currentFrame not in replay:
        replay[currentFrame] = []
    replay[currentFrame].append((techMech, skill, vec))

def handleGameEvents():
    global mousex, mousey, isPaused, selectedSkill, grappler
    
    for event in pygame.event.get():
        if event.type == MOUSEMOTION:
            mousex, mousey = event.pos
        elif event.type == MOUSEBUTTONDOWN:
            # check if the user clicked on the skill bar
            if mousey >= SCREEN_HEIGHT - 100:
                # check if user clicked on the grappling hook skill
                if mousex < 50:
                    selectedSkill = "grappler"
                # check if user clicked on the drill skill
                elif mousex < 100:
                    selectedSkill = "driller"
                # check if user clicked on the jackhammer skill
                elif mousex < 150:
                    selectedSkill = "jackhammerer"
                elif mousex < 200:
                    selectedSkill = "gravity reverser"
                elif mousex < 250:
                    # skill 5
                    pass
                elif mousex < 300:
                    # skill 6
                    pass
                elif mousex < 350:
                    # skill 7
                    pass
                elif mousex < 400:
                    # skill 8
                    pass
                elif mousex < 450:
                    isPaused = not isPaused
            # check if there is a Tech Mech waiting to grapple
            elif grappler != None:
                # the click is for determining where the grappler shoots
                # make a unit vector in the direction of the click
                vec = vector.Vector(mousex - grappler.x, mousey - grappler.y)
                vec.normalize()
                # add the grappler, the skill, and the unit vector to the replay
                addToReplay(grappler, "grappler", vec)
                grappler = None
                isPaused = False
            else: # normal assignment, not a grappling confirmation
                # check if you clicked on a techmech
                for techMech in techMechs:
                    if techMech.wasClicked(mousex, mousey):
                        # tech mech was clicked, make sure they're not falling
                        if techMech.currentSkill != "faller" and currentLevel.skillCounts[selectedSkill] > 0:
                            # if skill assigned is grappler, this is a special case
                            # simply change the grappler variable to this tech mech
                            if selectedSkill == "grappler":
                                grappler = techMech
                            else: # normal skill assignment; add it to the replay
                                # the vector is None, because it is not required
                                addToReplay(techMech, selectedSkill)
                            break
                isPaused = False
        elif event.type == KEYDOWN:
            if event.key == K_F1:
                selectedSkill = "gravity reverser"
            elif event.key == K_F7:
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
    global currentFrame, framesSinceLastRelease, techMechs, techMechsReleased, techMechsSaved
    global screenX, screenY

    # check if a Tech Mech should be dropped from the entrances
    release = framesSinceLastRelease == 120 - currentLevel.releaseRate
    if release:
        framesSinceLastRelease = 0

    # handle the user-related events like mouse clicks or keyboard presses
    handleGameEvents()

    # read replay for skill assignments
    if currentFrame in replay.keys():
        for assignment in replay[currentFrame]:
            techMech = assignment[0]
            skill = assignment[1]
            vec = assignment[2]
            if currentLevel.skillCounts[skill] > 0:
                techMech.skillVector = vec
                techMech.assignSkill(skill)
                currentLevel.skillCounts[skill] -= 1

    # render everything on screen; start by filling the screen with black,
    # to overwrite everything that happened last frame
    levelImage.fill(BLACK)

    # next, we blit the terrain
    levelImage.blit(currentLevel.image, (0, 0))

    # now, we blit the objects, which are rendered over the terrain
    for obj in currentLevel.objects:
        levelImage.blit(obj.image, (obj.x, obj.y))
        if type(obj) is gameObject.Entrance:
            if release and techMechsReleased < currentLevel.numberOfTechMechs:
                techMechs.append(techmech.TechMech(obj.x + 30, obj.y + 30))
                techMechsReleased += 1

    # next, we animate and blit the Tech Mechs, who overlap all terrain and objects
    for techMech in techMechs:
        if not isPaused:
            if not techMech.act(currentLevel.image) or "exit" in currentLevel.triggerMap[techMech.x][techMech.y]:
                techMechs.remove(techMech)
                techMechsSaved += 1
        techMech.render(levelImage)

    # finally, we blit any skill masks needed to help users see where the skills
    # will be used
    if grappler != None:
        pygame.draw.circle(levelImage, WHITE, (grappler.x, grappler.y), 150, 1)

    # now we check if the screen needs to scroll
    # first, check if it needs to be scrolled right
    if mousex >= SCREEN_WIDTH - 1 and -screenX + SCREEN_WIDTH < currentLevel.width:
        screenX -= 1
    # now we check if it needs to be scrolled left
    elif mousex <= 0 and screenX < 0:
        screenX += 1
    # now we check if it needs to be scrolled down
    elif mousey >= SCREEN_HEIGHT - 1 and -screenY + SCREEN_HEIGHT - 100 < currentLevel.height:
        screenY -= 1
    # finally we check if it needs to be scrolled up
    elif mousey <= 0 and screenY < 0:
        screenY += 1
    # now we blit the newly rendered game frame to the screen, taking scrolling
    # into effect
    SCREEN.blit(levelImage, (screenX, screenY))

    # now we blit the skill panel on the bottom of the screen
    renderSkillPanel()

    # now we blit the highlight on the selected skill
    if selectedSkill == "grappler":
        SCREEN.blit(skillHighlight, (0, SCREEN_HEIGHT - 100))
    elif selectedSkill == "driller":
        SCREEN.blit(skillHighlight, (50, SCREEN_HEIGHT - 100))
    elif selectedSkill == "jackhammerer":
        SCREEN.blit(skillHighlight, (100, SCREEN_HEIGHT - 100))
    elif selectedSkill == "gravity reverser":
        SCREEN.blit(skillHighlight, (150, SCREEN_HEIGHT - 100))

    # show screen updates and advance time
    pygame.display.update()
    CLOCK.tick(FPS)
    if not isPaused:
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








