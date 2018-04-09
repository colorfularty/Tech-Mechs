import pygame, os
from pygame.locals import *
from constants import *
from gameObject import *
from techmech import *
from skill import *
from vector import *
from client import Client

mousex = 0
mousey = 0

skillFont = pygame.font.SysFont("helvetica", 32)
skillSlot = pygame.image.load("sprites/skill panel.png")
skillHighlight = pygame.image.load("sprites/skill highlight.png").convert()
skillHighlight.set_colorkey(BLACK)
skillPanel = pygame.surface.Surface((SKILL_PANEL_WIDTH * NUMBER_OF_SKILL_PANELS, SKILL_PANEL_HEIGHT))

multiplayerIcons = [pygame.image.load("sprites/multiplayer icon green.png").convert_alpha(),
                    pygame.image.load("sprites/multiplayer icon red.png").convert_alpha()]

playerNum = 0
serverConn = None
currentLevel = None
levelImage = None
currentReleaseRates = None
increaseReleaseRate = False
decreaseReleaseRate = False
techMechs = []
techMechsReleased = []
techMechsSaved = []
highlightedTechMech = None
playingLevel = False
currentFrame = 0
framesSinceLastReleases = []
selectedSkill = None
isPaused = False
screenX = 0
screenY = 0
replay = {}
grappler = None
exitsHaveLeft = False
exitTimer = 0.0
exitHotkeyPushed = False

entity = None
action = None
vec = None

def startLevel(level, num = 0, conn = None):
    global playerNum, currentLevel, levelImage, currentReleaseRates, increaseReleaseRate, decreaseReleaseRate, techMechs, techMechsReleased
    global techMechsSaved, playingLevel, currentFrame, framesSinceLastReleases, selectedSkill, isPaused, screenX, screenY, replay, grappler, exitsHaveLeft, exitTimer
    global exitHotkeyPushed, serverConn

    currentLevel = level
    currentLevel.updateWholeImage()
    levelImage = pygame.surface.Surface((currentLevel.image.get_width(), currentLevel.image.get_height()))
    increaseReleaseRate = False
    decreaseReleaseRate = False
    techMechs = []
    techMechsReleased = []
    techMechsSaved = []
    currentReleaseRates = []
    framesSinceLastReleases = []
    for i in range(currentLevel.numPlayers):
        techMechs.append([])
        techMechsReleased.append(0)
        techMechsSaved.append(0)
        currentReleaseRates.append(currentLevel.releaseRates[i])
        framesSinceLastReleases.append(0)
    playingLevel = True
    currentFrame = 0
    selectedSkill = Grappler
    isPaused = False
    screenX = level.startX
    screenY = level.startY
    replay = {}
    grappler = None
    exitsHaveLeft = False
    exitTimer = 0.0
    exitHotkeyPushed = False

    playerNum = num
    serverConn = conn

    renderSkillPanel(skillPanel, currentLevel, currentReleaseRates, playerNum)

    Entrance.status = "closed"
    Exit.status = "open"

def renderSkillPanel(skillPanel, currentLevel, currentReleaseRates, playerNum):
    # blits the panels, the images, and the number of skills left
    # to the skill panel

    skillPanel.fill(BLACK)

    # start by blitting the empty skill panels
    for i in range(NUMBER_OF_SKILL_PANELS):
        skillPanel.blit(skillSlot, (i * SKILL_PANEL_WIDTH, 0))
        
    # now blit the skill images on each panel
    releaseRateIncrease = pygame.image.load("sprites/release rate increase.png").convert_alpha()
    releaseRateDecrease = pygame.image.load("sprites/release rate decrease.png")
    grapplingHookSkill = pygame.image.load("sprites/grappling hook skill.png").convert_alpha()
    drillSkill = pygame.image.load("sprites/drill skill.png").convert_alpha()
    jackhammerSkill = pygame.image.load("sprites/jackhammer skill.png").convert_alpha()
    gravitySkill = pygame.image.load("sprites/gravity skill.png").convert_alpha()
    cautionSkill = pygame.image.load("sprites/caution skill.png").convert_alpha()
    detonatorSkill = pygame.image.load("sprites/detonator skill.png").convert_alpha()
    pauseIcon = pygame.image.load("sprites/pause.png").convert_alpha()
    exitIcon = pygame.image.load("sprites/end level.png").convert_alpha()

    skillPanel.blit(releaseRateIncrease, (25 - SKILL_WIDTH // 2, 50))
    skillPanel.blit(releaseRateDecrease, (25 - SKILL_WIDTH // 2, 80))
    skillPanel.blit(grapplingHookSkill, (75 - SKILL_WIDTH // 2, 60))
    skillPanel.blit(drillSkill, (125 - SKILL_WIDTH // 2, 60))
    skillPanel.blit(jackhammerSkill, (175 - SKILL_WIDTH // 2, 60))
    skillPanel.blit(gravitySkill, (225 - SKILL_WIDTH // 2, 60))
    skillPanel.blit(cautionSkill, (275 - SKILL_WIDTH // 2, 60))
    skillPanel.blit(detonatorSkill, (325 - SKILL_WIDTH // 2, 60))
    skillPanel.blit(pauseIcon, ((NUMBER_OF_SKILL_PANELS - 2) * 50 + SKILL_WIDTH // 2, 40))
    skillPanel.blit(exitIcon, ((NUMBER_OF_SKILL_PANELS - 1) * 50 + SKILL_WIDTH // 2, 30))

    # compute the skills left and blit those to the skill panel
    releaseRate = skillFont.render(str(currentReleaseRates[playerNum]), True, WHITE, BLACK)
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

def addToReplay(techMech, skill, vec, pNum):
    if techMech != None or skill != None or vec != None:
        if currentFrame not in replay:
            replay[currentFrame] = []
        replay[currentFrame].append((techMech, skill, vec, pNum))

def executeReplay():
    global currentReleaseRates
    if currentFrame in replay.keys():
        for assignment in replay[currentFrame]:
            pNum = assignment[3]
            # check if the replay step is a release rate change
            if assignment[0] == None:
                currentReleaseRates[pNum] = assignment[1]
            else: # the replay step is a skill assignment
                techMech = techMechs[pNum][assignment[0]]
                skill = assignment[1]
                vec = assignment[2]
                if currentLevel.skillCounts[pNum][skill] > 0:
                    techMech.skillVector = vec
                    techMech.assignSkill(skill)
                    currentLevel.skillCounts[pNum][skill] -= 1
        renderSkillPanel(skillPanel, currentLevel, currentReleaseRates, playerNum)

def renderGameObjects():
    global techMechsReleased, framesSinceLastReleases, exitsHaveLeft
    
    for obj in currentLevel.objects:
        if type(obj) is Entrance and not isPaused:
            shouldReleaseTechMech = framesSinceLastReleases[obj.owner] >= 100 - currentReleaseRates[obj.owner] and techMechsReleased[obj.owner] < currentLevel.numberOfTechMechs and Entrance.status == "open"
            if shouldReleaseTechMech:
                owner = obj.owner
                if currentLevel.numPlayers > 1:
                    owner += 1
                techMechs[obj.owner].append(TechMech(obj.x + obj.width // 2, obj.y + obj.height // 2, owner))
                techMechsReleased[obj.owner] += 1
                framesSinceLastReleases[obj.owner] = 0
        elif type(obj) is Exit:
            if Exit.status == "closed" and not isPaused:
                obj.y -= 5
            if obj.y + obj.height > 0:
                exitsHaveLeft = False
        obj.render(levelImage)

def renderMultiplayerIcons():
    for obj in currentLevel.objects:
        if type(obj) is Entrance or type(obj) is Exit:
            levelImage.blit(multiplayerIcons[obj.owner], (obj.x + obj.width // 2 - multiplayerIcons[obj.owner].get_width() // 2, obj.y - multiplayerIcons[obj.owner].get_height()))

def renderTechMechs():
    global techMechsSaved, highlightedTechMech

    highlightedTechMech = None

    for i in range(len(techMechs)):
        for techMech in reversed(techMechs[i]):
            if not isPaused:
                if not techMech.act(currentLevel):
                    techMechs[i].remove(techMech)
                    continue
                if (techMech.x, techMech.y) in currentLevel.triggersByType["exit" + str(i)] and Exit.status == "open":
                    techMechs[i].remove(techMech)
                    techMechsSaved[i] += 1
                    continue
                elif (techMech.x, techMech.y) in currentLevel.triggersByType["water"]:
                    techMechs[i].remove(techMech)
                    continue
                elif (techMech.x + techMech.direction, techMech.y) in currentLevel.triggersByType["caution"]:
                    techMech.turnAround()
            techMechX = techMech.getXCoordinate()
            techMechY = techMech.getYCoordinate()
            if mousex >= techMechX and mousex <= techMechX + TECH_MECH_SPRITE_WIDTH and mousey >= techMechY and mousey <= techMechY + TECH_MECH_SPRITE_HEIGHT:
                highlightedTechMech = techMech
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
    global mousex, mousey, increaseReleaseRate, decreaseReleaseRate, isPaused, selectedSkill, grappler, exitHotkeyPushed
    global entity, action, vec
    
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
                elif mousex < 1250:
                    if currentLevel.numPlayers == 1:
                        isPaused = not isPaused
                elif mousex < 1300 and currentLevel.numPlayers == 1:
                    # launch the ship early
                    Exit.close()
            # check if there is a Tech Mech waiting to grapple
            elif grappler != None:
                # the click is for determining where the grappler shoots
                # make a unit vector in the direction of the click
                vec = Vector(screenX + mousex - grappler.x, screenY + mousey - grappler.y)
                vec.normalize()
                # add the grappler, the skill, and the unit vector to the replay
                entity = techMechs[playerNum].index(grappler)
                action = Grappler
                grappler = None
                isPaused = False
            else: # normal assignment, not a grappling confirmation
                # check if you clicked on a techmech
                for techMech in techMechs[playerNum]:
                    if techMech.wasClicked(mousex + screenX, mousey + screenY):
                        # tech mech was clicked, make sure they're not falling
                        if techMech.currentSkill != Faller and currentLevel.skillCounts[playerNum][selectedSkill] > 0:
                            # if skill assigned is grappler, this is a special case
                            # simply change the grappler variable to this tech mech
                            if selectedSkill == Grappler:
                                grappler = techMech
                            else: # normal skill assignment; add it to the replay
                                # the vector is None, because it is not required
                                entity = techMechs[playerNum].index(techMech)
                                action = selectedSkill
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
                if currentLevel.numPlayers == 1:
                    isPaused = not isPaused
            elif event.key == K_F12:
                if exitTimer == 0.0:
                    exitHotkeyPushed = True
                elif exitHotkeyPushed and currentLevel.numPlayers == 1:
                    Exit.close()
        elif event.type == KEYUP:
            if event.key == K_F1:
                decreaseReleaseRate = False
            elif event.key == K_F2:
                increaseReleaseRate = False
        elif event.type == QUIT:
            pygame.quit()
            os._exit(0)

def executeGameFrame(SCREEN):
    global currentFrame, framesSinceLastReleases, currentReleaseRates, techMechs, techMechsReleased, techMechsSaved, playingLevel, exitsHaveLeft, exitTimer, exitHotkeyPushed
    global entity, action, vec

    entity = None
    action = None
    vec = None

    # check if the entrances should be opened
    if currentFrame >= 60 and Entrance.status == "closed":
        Entrance.open()
        try:
            pygame.mixer.music.load("music/" + currentLevel.music + ".mod")
            pygame.mixer.music.play(-1)
        except pygame.error:
            pass

    # check if the exit should be closed due to all Tech Mechs exiting or dying
    shouldLeave = techMechsReleased[playerNum] == currentLevel.numberOfTechMechs
    for i in range(len(techMechs)):
        if len(techMechs[i]) != 0:
            shouldLeave = False
            break
    if shouldLeave:
        Exit.close()

    handleGameEvents()

    # check if user increased or decreased the release rate
    if increaseReleaseRate and currentReleaseRates[playerNum] < 99:
        entity = None
        action = currentReleaseRates[playerNum] + 1
        vec = None
    elif decreaseReleaseRate and currentReleaseRates[playerNum] > currentLevel.releaseRate[playerNum]:
        entity = None
        action = currentReleaseRates[playerNum] - 1
        vec = None

    addToReplay(entity, action, vec, playerNum)

    if currentLevel.numPlayers > 1:
        serverConn.sendTuple((entity, action, vec, playerNum))
        entity, action, vec, pNum = serverConn.receiveTuple()
        addToReplay(entity, action, vec, pNum)

    executeReplay()

    # render everything on screen; start by filling the screen with black,
    # to overwrite everything that happened last frame
    levelImage.fill(BLACK)

    # next, we blit the terrain
    levelImage.blit(currentLevel.image, (0, 0))

    exitsHaveLeft = True

    renderGameObjects()

    if currentLevel.numPlayers > 1:
        renderMultiplayerIcons()

    renderTechMechObjects()

    currentLevel.updateTriggerMaps()

    renderTechMechs()

    if highlightedTechMech != None:
        pygame.draw.rect(levelImage, WHITE, (highlightedTechMech.getXCoordinate(), highlightedTechMech.getYCoordinate(), TECH_MECH_SPRITE_WIDTH, TECH_MECH_SPRITE_HEIGHT), 1)

    # finally, we blit any skill masks needed to help users see where the skills will be used
    if grappler != None:
        pygame.draw.circle(levelImage, WHITE, (grappler.x, grappler.y), GRAPPLER_RANGE, 1)

    # now we check if the screen needs to scroll
    scrollScreen()

    SCREEN.fill(GREY)
    
    # now we blit the newly rendered game frame to the screen, taking scrolling into effect
    SCREEN.blit(levelImage, (-screenX, -screenY))

    # now we blit the skill panel on the bottom of the screen
    SCREEN.blit(skillPanel, (0, SCREEN_HEIGHT - SKILL_PANEL_HEIGHT))

    # now we blit the highlight on the selected skill
    SCREEN.blit(skillHighlight, ((SKILLS.index(selectedSkill) + 1) * 50, SCREEN_HEIGHT - SKILL_PANEL_HEIGHT))
    if isPaused:
        SCREEN.blit(skillHighlight, ((NUMBER_OF_SKILL_PANELS - 2) * 50, SCREEN_HEIGHT - SKILL_PANEL_HEIGHT))

    if exitHotkeyPushed:
        exitTimer += TIME_PASSED
    if exitTimer >= 0.2:
        exitTimer = 0.0
        exitHotkeyPushed = False

    # show screen updates and advance time
    pygame.display.update()
    CLOCK.tick(FPS)
    if not isPaused:
        currentFrame += 1
        for i in range(currentLevel.numPlayers):
            framesSinceLastReleases[i] += 1

    if exitsHaveLeft:
        Exit.sound.stop()
        try:
            pygame.mixer.music.stop()
        except pygame.error:
            pass
        playingLevel = False
        if currentLevel.numPlayers > 1:
            serverConn.sendString("Quit server")

    return playingLevel, techMechsSaved[playerNum]




