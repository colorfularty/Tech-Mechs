import pygame, os
from pygame.locals import *
from constants import *
from gameObject import *
from techmech import *
from skill import *
from vector import *

mousex = 0
mousey = 0

skillFont = pygame.font.SysFont("helvetica", 32)
skillSlot = pygame.image.load("sprites/skill panel.png")
skillHighlight = pygame.image.load("sprites/skill highlight.png").convert()
skillHighlight.set_colorkey(BLACK)
skillPanel = pygame.surface.Surface((SKILL_PANEL_WIDTH * NUMBER_OF_SKILL_PANELS, SKILL_PANEL_HEIGHT))

playerNum = 0
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

def startLevel(level, num):
    global playerNum, currentLevel, levelImage, currentReleaseRate, increaseReleaseRate, decreaseReleaseRate, techMechs, techMechsReleased, techMechsSaved
    global playingLevel, currentFrame, framesSinceLastRelease, selectedSkill, isPaused, screenX, screenY, replay, grappler, exitsHaveLeft

    playerNum = num
    currentLevel = level
    currentLevel.updateWholeImage()
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
    selectedSkill = Grappler
    isPaused = False
    screenX = level.startX
    screenY = level.startY
    replay = {}
    grappler = None
    exitsHaveLeft = False

    renderSkillPanel(skillPanel)

    Entrance.status = "closed"
    Exit.status = "open"

def renderSkillPanel(skillPanel):
    # blits the panels, the images, and the number of skills left
    # to the skill panel

    skillPanel.fill(BLACK)

    # start by blitting the empty skill panels
    for i in range(13):
        skillPanel.blit(skillSlot, (i * SKILL_PANEL_WIDTH, 0))
        
    # now blit the skill images on each panel
    releaseRateIncrease = pygame.image.load("sprites/release rate increase.png").convert()
    releaseRateDecrease = pygame.image.load("sprites/release rate decrease.png")
    grapplingHookSkill = pygame.image.load("sprites/grappling hook skill.png").convert()
    drillSkill = pygame.image.load("sprites/drill skill.png").convert()
    jackhammerSkill = pygame.image.load("sprites/jackhammer skill.png").convert()
    gravitySkill = pygame.image.load("sprites/gravity skill.png").convert()
    cautionSkill = pygame.image.load("sprites/caution skill.png").convert()
    detonatorSkill = pygame.image.load("sprites/detonator skill.png").convert()

    releaseRateIncrease.set_colorkey(BLACK)
    grapplingHookSkill.set_colorkey(BLACK)
    drillSkill.set_colorkey(BLACK)
    jackhammerSkill.set_colorkey(BLACK)
    gravitySkill.set_colorkey(BLACK)
    cautionSkill.set_colorkey(BLACK)
    detonatorSkill.set_colorkey(BLACK)

    skillPanel.blit(releaseRateIncrease, (25 - SKILL_WIDTH // 2, 50))
    skillPanel.blit(releaseRateDecrease, (25 - SKILL_WIDTH // 2, 80))
    skillPanel.blit(grapplingHookSkill, (75 - SKILL_WIDTH // 2, 60))
    skillPanel.blit(drillSkill, (125 - SKILL_WIDTH // 2, 60))
    skillPanel.blit(jackhammerSkill, (175 - SKILL_WIDTH // 2, 60))
    skillPanel.blit(gravitySkill, (225 - SKILL_WIDTH // 2, 60))
    skillPanel.blit(cautionSkill, (275 - SKILL_WIDTH // 2, 60))
    skillPanel.blit(detonatorSkill, (325 - SKILL_WIDTH // 2, 60))

    # compute the skills left and blit those to the skill panel
    releaseRate = skillFont.render(str(currentReleaseRate), True, WHITE, BLACK)
    grapplingHooksLeft = skillFont.render(str(currentLevel.skillCounts[playerNum][Grappler]), True, WHITE, BLACK)
    drillsLeft = skillFont.render(str(currentLevel.skillCounts[playerNum][Driller]), True, WHITE, BLACK)
    jackhammersLeft = skillFont.render(str(currentLevel.skillCounts[playerNum][Jackhammerer]), True, WHITE, BLACK)
    gravityReversersLeft = skillFont.render(str(currentLevel.skillCounts[playerNum][GravityReverser]), True, WHITE, BLACK)
    cautionSignsLeft = skillFont.render(str(currentLevel.skillCounts[playerNum][Cautioner]), True, WHITE, BLACK)
    landMinesLeft = skillFont.render(str(currentLevel.skillCounts[playerNum][Detonator]), True, WHITE, BLACK)

    releaseRate.set_colorkey(BLACK)
    grapplingHooksLeft.set_colorkey(BLACK)
    drillsLeft.set_colorkey(BLACK)
    jackhammersLeft.set_colorkey(BLACK)
    gravityReversersLeft.set_colorkey(BLACK)
    cautionSignsLeft.set_colorkey(BLACK)
    landMinesLeft.set_colorkey(BLACK)

    skillPanel.blit(releaseRate, (25 - releaseRate.get_width() // 2, 10))
    skillPanel.blit(grapplingHooksLeft, (75 - grapplingHooksLeft.get_width() // 2, 10))
    skillPanel.blit(drillsLeft, (125 - drillsLeft.get_width() // 2, 10))
    skillPanel.blit(jackhammersLeft, (175 - jackhammersLeft.get_width() // 2, 10))
    skillPanel.blit(gravityReversersLeft, (225 - gravityReversersLeft.get_width() // 2, 10))
    skillPanel.blit(cautionSignsLeft, (275 - cautionSignsLeft.get_width() // 2, 10))
    skillPanel.blit(landMinesLeft, (325 - landMinesLeft.get_width() // 2, 10))

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
                if currentLevel.skillCounts[playerNum][skill] > 0:
                    techMech.skillVector = vec
                    techMech.assignSkill(skill)
                    currentLevel.skillCounts[playerNum][skill] -= 1
        renderSkillPanel(skillPanel)

def renderGameObjects():
    global techMechsReleased, framesSinceLastRelease, exitsHaveLeft
    
    for obj in currentLevel.objects:
        if type(obj) is Entrance and not isPaused:
            shouldReleaseTechMech = framesSinceLastRelease >= 100 - currentReleaseRate and techMechsReleased < currentLevel.numberOfTechMechs and Entrance.status == "open"
            if shouldReleaseTechMech:
                techMechs.append(TechMech(obj.x + obj.width // 2, obj.y + obj.height // 2))
                techMechsReleased += 1
                framesSinceLastRelease = 0
        elif type(obj) is Exit:
            if Exit.status == "closed" and not isPaused:
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
            if (techMech.x, techMech.y) in currentLevel.triggersByType["exit"] and Exit.status == "open":
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
        if type(obj) is CautionSign:
            # check if there is no terrain to support the sign base
            if currentLevel.image.get_at((obj.triggerX, obj.triggerY + obj.orientation)) == BLACK:
                # there is no terrain support, so destroy the sign
                currentLevel.techMechObjects.remove(obj)
                continue
            else: # the sign is supported, so add its triggers to the triggerMaps
                currentLevel.triggersByPoint[(obj.triggerX, obj.triggerY)] = "caution"
                currentLevel.triggersByType["caution"].append((obj.triggerX, obj.triggerY))
        elif type(obj) is LandMine:
            # check if the ground supporting the land mine has disappeared
            if currentLevel.image.get_at((obj.triggerX, obj.triggerY + obj.orientation)) == BLACK:
                # there is no terrain to support, so destroy the land mine SUBJECT TO CHANGE
                currentLevel.techMechObjects.remove(obj)
                continue
            # decrease the timer if the game is unpaused
            if not isPaused:
                obj.timer -= TIME_PASSED
            # check if the timer has run out
            if obj.timer <= 0.0:
                # the land mine blows up, destroying nearby terrain
                currentLevel.techMechObjects.remove(obj)
                pygame.draw.ellipse(currentLevel.image, BLACK, (obj.triggerX - obj.triggerWidth // 2, obj.triggerY - obj.triggerHeight // 2, obj.triggerWidth, obj.triggerHeight))
                continue
        obj.render(levelImage)

def scrollScreen():
    global screenX, screenY
    
    # first, check if it needs to be scrolled right
    if mousex >= SCREEN_WIDTH - 1:
        for i in range(SCROLL_SPEED):
            if screenX + SCREEN_WIDTH < currentLevel.width:
                screenX += 1
            else:
                break
    # now we check if it needs to be scrolled left
    elif mousex <= 0:
        for i in range(SCROLL_SPEED):
            if screenX > 0:
                screenX -= 1
            else:
                break
    # now we check if it needs to be scrolled down
    elif mousey >= SCREEN_HEIGHT - 1:
        for i in range(SCROLL_SPEED):
            if screenY + SCREEN_HEIGHT - SKILL_PANEL_HEIGHT < currentLevel.height:
                screenY += 1
            else:
                break
    # finally we check if it needs to be scrolled up
    elif mousey <= 0 and screenY > 0:
        for i in range(SCROLL_SPEED):
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
            if mousey >= SCREEN_HEIGHT - 100:
                # check if the user clicked on the release rate
                if mousex < 50:
                    # check if the user wants to increase the release rate
                    if mousey >= SCREEN_HEIGHT - 50 and mousey <= SCREEN_HEIGHT - 50 + SKILL_HEIGHT:
                        increaseReleaseRate = True
                    elif mousey >= SCREEN_HEIGHT - 20 and mousey <= SCREEN_HEIGHT - 15: # the user wants to decrease the release rate
                        decreaseReleaseRate = True
                # check if user clicked on the grappling hook skill
                elif mousex < 100:
                    selectedSkill = Grappler
                # check if user clicked on the drill skill
                elif mousex < 150:
                    selectedSkill = Driller
                # check if user clicked on the jackhammer skill
                elif mousex < 200:
                    selectedSkill = Jackhammerer
                # check if the user clicked on the gravity reverser skill
                elif mousex < 250:
                    selectedSkill = GravityReverser
                # check if the user clicked on the caution sign skill
                elif mousex < 300:
                    selectedSkill = Cautioner
                # check if the user clicked on the detonator skill
                elif mousex < 350:
                    selectedSkill = Detonator
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
                vec = Vector(screenX + mousex - grappler.x, screenY + mousey - grappler.y)
                vec.normalize()
                # add the grappler, the skill, and the unit vector to the replay
                addToReplay(grappler, Grappler, vec)
                grappler = None
                isPaused = False
            else: # normal assignment, not a grappling confirmation
                # check if you clicked on a techmech
                for techMech in techMechs:
                    if techMech.wasClicked(mousex + screenX, mousey + screenY):
                        # tech mech was clicked, make sure they're not falling
                        if techMech.currentSkill != Faller and currentLevel.skillCounts[playerNum][selectedSkill] > 0:
                            # if skill assigned is grappler, this is a special case
                            # simply change the grappler variable to this tech mech
                            if selectedSkill == Grappler:
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
            elif event.key == K_F5:
                selectedSkill = Detonator
            elif event.key == K_F6:
                selectedSkill = Cautioner
            elif event.key == K_F7:
                selectedSkill = Grappler
            elif event.key == K_F8:
                selectedSkill = Driller
            elif event.key == K_F10:
                selectedSkill = Jackhammerer
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
        Entrance.open()

    # check if the exit should be closed due to all Tech Mechs exiting or dying
    if techMechsReleased == currentLevel.numberOfTechMechs and len(techMechs) == 0:
        Exit.close()

    handleGameEvents()

    # check if user increased or decreased the release rate
    if increaseReleaseRate and currentReleaseRate < 99:
        addToReplay(None, currentReleaseRate + 1, None)
    elif decreaseReleaseRate and currentReleaseRate > 1:
        addToReplay(None, currentReleaseRate - 1, None)
    
    executeReplay()

    # render everything on screen; start by filling the screen with black,
    # to overwrite everything that happened last frame
    levelImage.fill(BLACK)

    # next, we blit the terrain
    levelImage.blit(currentLevel.image, (0, 0))

    exitsHaveLeft = True

    renderGameObjects()

    renderTechMechObjects()

    renderTechMechs()

    # finally, we blit any skill masks needed to help users see where the skills will be used
    if grappler != None:
        pygame.draw.circle(levelImage, WHITE, (grappler.x, grappler.y), GRAPPLER_RANGE, 1)

    # now we check if the screen needs to scroll
    scrollScreen()
    
    # now we blit the newly rendered game frame to the screen, taking scrolling into effect
    SCREEN.blit(levelImage, (-screenX, -screenY))

    # now we blit the skill panel on the bottom of the screen
    SCREEN.blit(skillPanel, (0, SCREEN_HEIGHT - SKILL_PANEL_HEIGHT))

    # now we blit the highlight on the selected skill
    if selectedSkill == Grappler:
        SCREEN.blit(skillHighlight, (50, SCREEN_HEIGHT - SKILL_PANEL_HEIGHT))
    elif selectedSkill == Driller:
        SCREEN.blit(skillHighlight, (100, SCREEN_HEIGHT - SKILL_PANEL_HEIGHT))
    elif selectedSkill == Jackhammerer:
        SCREEN.blit(skillHighlight, (150, SCREEN_HEIGHT - SKILL_PANEL_HEIGHT))
    elif selectedSkill == GravityReverser:
        SCREEN.blit(skillHighlight, (200, SCREEN_HEIGHT - SKILL_PANEL_HEIGHT))
    elif selectedSkill == Cautioner:
        SCREEN.blit(skillHighlight, (250, SCREEN_HEIGHT - SKILL_PANEL_HEIGHT))
    elif selectedSkill == Detonator:
        SCREEN.blit(skillHighlight, (300, SCREEN_HEIGHT - SKILL_PANEL_HEIGHT))

    # show screen updates and advance time
    pygame.display.update()
    CLOCK.tick(FPS)
    if not isPaused:
        currentFrame += 1
        framesSinceLastRelease += 1

    if exitsHaveLeft:
        playingLevel = False

    return playingLevel




