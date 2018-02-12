import pygame, os
from pygame.locals import *
import constants
import gameObject
import techmech
import vector

mousex = 0
mousey = 0

CLOCK = None

skillFont = pygame.font.SysFont("helvetica", 32)
skillSlot = pygame.image.load("sprites/skill panel.png")
skillHighlight = pygame.image.load("sprites/skill highlight.png").convert()
skillHighlight.set_colorkey(constants.BLACK)
skillPanel = pygame.surface.Surface((constants.SKILL_PANEL_WIDTH * constants.NUMBER_OF_SKILL_PANELS, constants.SKILL_PANEL_HEIGHT))

currentLevel = None
levelImage = None
currentReleaseRate = None
increaseReleaseRate = False
decreaseReleaseRate = False
techMechs = []
techMechsReleased = 0
techMechsSaved = 0
playingLevel = False
currentFrame = 0
framesSinceLastRelease = 0
selectedSkill = None
isPaused = False
screenX = 0
screenY = 0
replay = {}
grappler = None
exitsHaveLeft = False

def readLevelFromFile(fileName):
    level = Level()
    levelFile = open(fileName + ".txt", 'r')
    # first line is TERRAIN
    levelFile.readline()

    levelFile.close()
    return level

def startLevel(level, clock):
    global currentLevel, levelImage, currentReleaseRate, increaseReleaseRate, decreaseReleaseRate, techMechs, techMechsReleased, techMechsSaved, playingLevel
    global currentFrame, framesSinceLastRelease, selectedSkill, isPaused, screenX, screenY, replay, grappler, exitsHaveLeft, CLOCK
    
    currentLevel = level
    levelImage = pygame.surface.Surface((currentLevel.image.get_width(), currentLevel.image.get_height()))
    currentReleaseRate = currentLevel.releaseRate
    increaseReleaseRate = False
    decreaseReleaseRate = False
    techMechs = []
    techMechsReleased = 0
    techMechsSaved = 0
    playingLevel = True
    currentFrame = 0
    framesSinceLastRelease = 0
    selectedSkill = "grappler"
    isPaused = False
    screenX = level.startX
    screenY = level.startY
    replay = {}
    grappler = None
    exitsHaveLeft = False

    renderSkillPanel()

    CLOCK = clock

    gameObject.Entrance.status = "closed"
    gameObject.Exit.status = "open"

def renderSkillPanel():
    # blits the panels, the images, and the number of skills left
    # to the skill panel

    skillPanel.fill(constants.BLACK)

    # start by blitting the empty skill panels
    for i in range(13):
        skillPanel.blit(skillSlot, (i * constants.SKILL_PANEL_WIDTH, 0))
        
    # now blit the skill images on each panel
    releaseRateIncrease = pygame.image.load("sprites/release rate increase.png").convert()
    releaseRateDecrease = pygame.image.load("sprites/release rate decrease.png")
    grapplingHookSkill = pygame.image.load("sprites/grappling hook skill.png").convert()
    drillSkill = pygame.image.load("sprites/drill skill.png").convert()
    jackhammerSkill = pygame.image.load("sprites/jackhammer skill.png").convert()
    gravitySkill = pygame.image.load("sprites/gravity skill.png").convert()
    cautionSkill = pygame.image.load("sprites/caution skill.png").convert()

    releaseRateIncrease.set_colorkey(constants.BLACK)
    grapplingHookSkill.set_colorkey(constants.BLACK)
    drillSkill.set_colorkey(constants.BLACK)
    jackhammerSkill.set_colorkey(constants.BLACK)
    gravitySkill.set_colorkey(constants.BLACK)
    cautionSkill.set_colorkey(constants.BLACK)

    skillPanel.blit(releaseRateIncrease, (25 - constants.SKILL_WIDTH // 2, 50))
    skillPanel.blit(releaseRateDecrease, (25 - constants.SKILL_WIDTH // 2, 80))
    skillPanel.blit(grapplingHookSkill, (75 - constants.SKILL_WIDTH // 2, 60))
    skillPanel.blit(drillSkill, (125 - constants.SKILL_WIDTH // 2, 60))
    skillPanel.blit(jackhammerSkill, (175 - constants.SKILL_WIDTH // 2, 60))
    skillPanel.blit(gravitySkill, (225 - constants.SKILL_WIDTH // 2, 60))
    skillPanel.blit(cautionSkill, (275 - constants.SKILL_WIDTH // 2, 60))

    # compute the skills left and blit those to the skill panel
    releaseRate = skillFont.render(str(currentReleaseRate), True, constants.WHITE, constants.BLACK)
    grapplingHooksLeft = skillFont.render(str(currentLevel.skillCounts["grappler"]), True, constants.WHITE, constants.BLACK)
    drillsLeft = skillFont.render(str(currentLevel.skillCounts["driller"]), True, constants.WHITE, constants.BLACK)
    jackhammersLeft = skillFont.render(str(currentLevel.skillCounts["jackhammerer"]), True, constants.WHITE, constants.BLACK)
    gravityReversersLeft = skillFont.render(str(currentLevel.skillCounts["gravity reverser"]), True, constants.WHITE, constants.BLACK)
    cautionSignsLeft = skillFont.render(str(currentLevel.skillCounts["cautioner"]), True, constants.WHITE, constants.BLACK)

    releaseRate.set_colorkey(constants.BLACK)
    grapplingHooksLeft.set_colorkey(constants.BLACK)
    drillsLeft.set_colorkey(constants.BLACK)
    jackhammersLeft.set_colorkey(constants.BLACK)
    gravityReversersLeft.set_colorkey(constants.BLACK)
    cautionSignsLeft.set_colorkey(constants.BLACK)

    skillPanel.blit(releaseRate, (25 - releaseRate.get_width() // 2, 10))
    skillPanel.blit(grapplingHooksLeft, (75 - grapplingHooksLeft.get_width() // 2, 10))
    skillPanel.blit(drillsLeft, (125 - drillsLeft.get_width() // 2, 10))
    skillPanel.blit(jackhammersLeft, (175 - jackhammersLeft.get_width() // 2, 10))
    skillPanel.blit(gravityReversersLeft, (225 - gravityReversersLeft.get_width() // 2, 10))
    skillPanel.blit(cautionSignsLeft, (275 - cautionSignsLeft.get_width() // 2, 10))

def addToReplay(techMech, skill, vec = None):
    if currentFrame not in replay:
        replay[currentFrame] = []
    replay[currentFrame].append((techMech, skill, vec))

def executeReplay():
    global currentReleaseRate
    if currentFrame in replay.keys():
        for assignment in replay[currentFrame]:
            # check if the replay step is a release rate change
            if assignment[0] == None:
                currentReleaseRate = assignment[1]
            else: # the replay step is a skill assignment
                techMech = assignment[0]
                skill = assignment[1]
                vec = assignment[2]
                if currentLevel.skillCounts[skill] > 0:
                    techMech.skillVector = vec
                    techMech.assignSkill(skill)
                    currentLevel.skillCounts[skill] -= 1
        renderSkillPanel()

def renderGameObjects():
    global techMechsReleased, framesSinceLastRelease, exitsHaveLeft
    
    for obj in currentLevel.objects:
        if type(obj) is gameObject.Entrance:
            shouldReleaseTechMech = framesSinceLastRelease >= 100 - currentLevel.releaseRate and techMechsReleased < currentLevel.numberOfTechMechs and gameObject.Entrance.status == "open"
            if shouldReleaseTechMech:
                techMechs.append(techmech.TechMech(obj.x + obj.width // 2, obj.y + obj.height // 2))
                techMechsReleased += 1
                framesSinceLastRelease = 0
        elif type(obj) is gameObject.Exit:
            if gameObject.Exit.status == "closed":
                obj.y -= 5
            if obj.y + obj.height > 0:
                exitsHaveLeft = False
        levelImage.blit(obj.image, (obj.x, obj.y))

def renderTechMechs():
    global techMechsSaved
    
    for techMech in techMechs:
        if not isPaused:
            if not techMech.act(currentLevel):
                techMechs.remove(techMech)
                continue
            if (techMech.x, techMech.y) in currentLevel.triggersByType["exit"] and gameObject.Exit.status == "open":
                techMechs.remove(techMech)
                techMechsSaved += 1
                continue
            elif (techMech.x + techMech.direction, techMech.y) in currentLevel.triggersByType["caution"]:
                techMech.turnAround()
        techMech.render(levelImage)

def renderTechMechObjects():
    # first, we remove all tech mech object-specific triggers to update them
    currentLevel.triggersByPoint = {point: trigger for point, trigger in currentLevel.triggersByPoint.items() if trigger != "caution"}
    currentLevel.triggersByType["caution"] = []

    for obj in currentLevel.techMechObjects:
        if type(obj) is gameObject.CautionSign:
            # check if there is no terrain to support the sign base
            if currentLevel.image.get_at((obj.triggerX, obj.triggerY + 1)) == constants.BLACK:
                # there is no terrain support, so destroy the sign
                currentLevel.techMechObjects.remove(obj)
                continue
            else: # the sign is supported, so add its triggers to the triggerMaps
                currentLevel.triggersByPoint[(obj.triggerX, obj.triggerY)] = "caution"
                currentLevel.triggersByType["caution"].append((obj.triggerX, obj.triggerY))
        obj.render(levelImage)

def scrollScreen():
    global screenX, screenY
    
    # first, check if it needs to be scrolled right
    if mousex >= constants.SCREEN_WIDTH - 1:
        for i in range(constants.SCROLL_SPEED):
            if screenX + constants.SCREEN_WIDTH < currentLevel.width:
                screenX += 1
            else:
                break
    # now we check if it needs to be scrolled left
    elif mousex <= 0:
        for i in range(constants.SCROLL_SPEED):
            if screenX > 0:
                screenX -= 1
            else:
                break
    # now we check if it needs to be scrolled down
    elif mousey >= constants.SCREEN_HEIGHT - 1:
        for i in range(constants.SCROLL_SPEED):
            if screenY + constants.SCREEN_HEIGHT - constants.SKILL_PANEL_HEIGHT < currentLevel.height:
                screenY += 1
            else:
                break
    # finally we check if it needs to be scrolled up
    elif mousey <= 0 and screenY > 0:
        for i in range(constants.SCROLL_SPEED):
            if screenY > 0:
                screenY -= 1
            else:
                break

def handleGameEvents():
    global mousex, mousey, increaseReleaseRate, decreaseReleaseRate, isPaused, selectedSkill, grappler
    
    for event in pygame.event.get():
        if event.type == MOUSEMOTION:
            mousex, mousey = event.pos
        elif event.type == MOUSEBUTTONDOWN:
            # check if the user clicked on the skill bar
            if mousey >= constants.SCREEN_HEIGHT - 100:
                # check if the user clicked on the release rate
                if mousex < 50:
                    # check if the user wants to increase the release rate
                    if mousey >= constants.SCREEN_HEIGHT - 50 and mousey <= constants.SCREEN_HEIGHT - 50 + constants.SKILL_HEIGHT:
                        increaseReleaseRate = True
                    elif mousey >= constants.SCREEN_HEIGHT - 20 and mousey <= constants.SCREEN_HEIGHT - 15: # the user wants to decrease the release rate
                        decreaseReleaseRate = True
                # check if user clicked on the grappling hook skill
                elif mousex < 100:
                    selectedSkill = "grappler"
                # check if user clicked on the drill skill
                elif mousex < 150:
                    selectedSkill = "driller"
                # check if user clicked on the jackhammer skill
                elif mousex < 200:
                    selectedSkill = "jackhammerer"
                # check if the user clicked on the gravity reverser skill
                elif mousex < 250:
                    selectedSkill = "gravity reverser"
                # check if the user clicked on the caution sign skill
                elif mousex < 300:
                    selectedSkill = "cautioner"
                elif mousex < 350:
                    # skill 6
                    pass
                elif mousex < 400:
                    # skill 7
                    pass
                elif mousex < 450:
                    # skill 8
                    pass
                elif mousex < 500:
                    # fast forward
                    pass
                elif mousex < 550:
                    isPaused = not isPaused
                elif mousex < 600:
                    # launch the ship early
                    pass
            # check if there is a Tech Mech waiting to grapple
            elif grappler != None:
                # the click is for determining where the grappler shoots
                # make a unit vector in the direction of the click
                vec = vector.Vector(screenX + mousex - grappler.x, screenY + mousey - grappler.y)
                vec.normalize()
                # add the grappler, the skill, and the unit vector to the replay
                addToReplay(grappler, "grappler", vec)
                grappler = None
                isPaused = False
            else: # normal assignment, not a grappling confirmation
                # check if you clicked on a techmech
                for techMech in techMechs:
                    if techMech.wasClicked(mousex + screenX, mousey + screenY):
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
        elif event.type == MOUSEBUTTONUP:
            increaseReleaseRate = False
            decreaseReleaseRate = False
        elif event.type == KEYDOWN:
            if event.key == K_F1:
                decreaseReleaseRate = True
            elif event.key == K_F2:
                increaseReleaseRate = True
            elif event.key == K_F6:
                selectedSkill = "cautioner"
            elif event.key == K_F7:
                selectedSkill = "grappler"
            elif event.key == K_F8:
                selectedSkill = "driller"
            elif event.key == K_F10:
                selectedSkill = "jackhammerer"
            elif event.key == K_F11:
                isPaused = not isPaused
        elif event.type == KEYUP:
            if event.key == K_F1:
                decreaseReleaseRate = False
            elif event.key == K_F2:
                increaseReleaseRate = False
        elif event.type == QUIT:
            pygame.quit()
            os._exit(0)

def executeGameFrame(SCREEN):
    global currentFrame, framesSinceLastRelease, currentReleaseRate, techMechs, techMechsReleased, techMechsSaved, playingLevel, exitsHaveLeft
    
    # check if the entrances should be opened
    if currentFrame >= 60:
        gameObject.Entrance.open()

    # check if the exit should be closed due to all Tech Mechs exiting or dying
    if techMechsReleased == currentLevel.numberOfTechMechs and len(techMechs) == 0:
        gameObject.Exit.close()

    handleGameEvents()

    # check if user increased or decreased the release rate
    if increaseReleaseRate and currentReleaseRate < 99:
        addToReplay(None, currentReleaseRate + 1, None)
    elif decreaseReleaseRate and currentReleaseRate > 1:
        addToReplay(None, currentReleaseRate - 1, None)
    
    executeReplay()

    # render everything on screen; start by filling the screen with black,
    # to overwrite everything that happened last frame
    levelImage.fill(constants.BLACK)

    # next, we blit the terrain
    levelImage.blit(currentLevel.image, (0, 0))

    exitsHaveLeft = True

    renderGameObjects()

    renderTechMechObjects()

    renderTechMechs()

    # finally, we blit any skill masks needed to help users see where the skills will be used
    if grappler != None:
        pygame.draw.circle(levelImage, constants.WHITE, (grappler.x, grappler.y), constants.GRAPPLER_RANGE, 1)

    # now we check if the screen needs to scroll
    scrollScreen()
    
    # now we blit the newly rendered game frame to the screen, taking scrolling into effect
    SCREEN.blit(levelImage, (-screenX, -screenY))

    # now we blit the skill panel on the bottom of the screen
    SCREEN.blit(skillPanel, (0, constants.SCREEN_HEIGHT - constants.SKILL_PANEL_HEIGHT))

    # now we blit the highlight on the selected skill
    if selectedSkill == "grappler":
        SCREEN.blit(skillHighlight, (50, constants.SCREEN_HEIGHT - constants.SKILL_PANEL_HEIGHT))
    elif selectedSkill == "driller":
        SCREEN.blit(skillHighlight, (100, constants.SCREEN_HEIGHT - constants.SKILL_PANEL_HEIGHT))
    elif selectedSkill == "jackhammerer":
        SCREEN.blit(skillHighlight, (150, constants.SCREEN_HEIGHT - constants.SKILL_PANEL_HEIGHT))
    elif selectedSkill == "gravity reverser":
        SCREEN.blit(skillHighlight, (200, constants.SCREEN_HEIGHT - constants.SKILL_PANEL_HEIGHT))
    elif selectedSkill == "cautioner":
        SCREEN.blit(skillHighlight, (250, constants.SCREEN_HEIGHT - constants.SKILL_PANEL_HEIGHT))

    # show screen updates and advance time
    pygame.display.update()
    CLOCK.tick(constants.FPS)
    if not isPaused:
        currentFrame += 1
        framesSinceLastRelease += 1

    if exitsHaveLeft:
        playingLevel = False



