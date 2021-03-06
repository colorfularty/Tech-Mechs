import pygame, os
from pygame.locals import *
from constants import *
from gameObject import *
from techmech import *
from skill import *
from vector import *
from client import Client

# keeps track of the mouse pointer's coordinates
mousex = 0
mousey = 0

# used in the skill panel
skillFont = pygame.font.SysFont("helvetica", 32)
skillSlot = pygame.image.load("sprites/skill panel.png")
skillHighlight = pygame.image.load("sprites/skill highlight.png").convert()
skillHighlight.set_colorkey(BLACK)
skillPanel = pygame.surface.Surface((SKILL_PANEL_WIDTH * NUMBER_OF_SKILL_PANELS, SKILL_PANEL_HEIGHT))

# used in determining whose entrance/exit is whose in multiplayer
multiplayerIcons = [pygame.image.load("sprites/multiplayer icon green.png").convert_alpha(),
                    pygame.image.load("sprites/multiplayer icon red.png").convert_alpha()]

playerNum = 0 # the number of the player in the game, is 0 for single player
serverConn = None # the connection to the server, is None for single player
currentLevel = None
levelImage = None # the image of the level, its terrain, objects, tech mechs, etc.
currentReleaseRates = None
increaseReleaseRate = False # will increase the release rate if True
decreaseReleaseRate = False # will decrease the release rate if True
techMechs = [] # a list of the tech mechs currently active on the level
techMechsReleased = [] # a list how many tech mechs each player has released
techMechsSaved = [] # a list of how many tech mechs each player has saved
highlightedTechMech = None # the tech mech you are pointing to with your mouse
playingLevel = False # used to determine when to terminate and return to main.py
currentFrame = 0
framesSinceLastReleases = [] # used for determining when to release a Tech Mech
selectedSkill = None
isPaused = False
screenX = 0 # the x-displacement of the screen relative to the starting x-coordinate of the level
screenY = 0 # the y-displacement of the screen relative to the starting y-coordinate of the level
replay = {} # a dict containing all of the user's actions on each frame; used for executing skill assignments and release rate manipulation
grappler = None # stores the tech mech getting ready to shoot a grappling hook
exitsHaveLeft = False # when true, the exits are closed and blasting off to space; triggers level's end when they leave the screen
exitTimer = 0.0
exitHotkeyPushed = False # used for determining if the user chose to leave the level early

entity = None # the tech mech performing a skill for the replay; is None for release rate changes
action = None # the skill a given tech mech is performing during the replay; is a special value for release rate changes
vec = None # the vector specifying the direction a skill is used in; only used for Grapplers

def startLevel(level, num = 0, conn = None):
    # called before a level begins; sets variables to their default value
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
    selectedSkill = MagnetBoots
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

    # blit the skill icons
    skillIcons = []
    skillsLeft = []
    for skill in SKILLS:
        skillIcons.append(pygame.image.load("sprites/" + SKILL_STRING_CONVERSIONS[skill] + " Icon.png").convert_alpha())
        skillLeft = skillFont.render(str(currentLevel.skillCounts[playerNum][skill]), True, WHITE, BLACK)
        skillLeft.set_colorkey(BLACK)
        skillsLeft.append(skillLeft)
        
    pauseIcon = pygame.image.load("sprites/pause.png").convert_alpha()
    exitIcon = pygame.image.load("sprites/end level.png").convert_alpha()

    # blit the skills left numbers to the panel
    skillPanel.blit(releaseRateIncrease, (25 - SKILL_WIDTH // 2, 50))
    skillPanel.blit(releaseRateDecrease, (25 - SKILL_WIDTH // 2, 80))
    for i in range(len(skillIcons)):
        skillPanel.blit(skillIcons[i], (75 + (i * 50) - SKILL_WIDTH // 2, 60))
    skillPanel.blit(pauseIcon, ((NUMBER_OF_SKILL_PANELS - 2) * 50 + SKILL_WIDTH // 2, 40))
    skillPanel.blit(exitIcon, ((NUMBER_OF_SKILL_PANELS - 1) * 50 + SKILL_WIDTH // 2, 30))

    # compute the skills left and blit those to the skill panel
    releaseRate = skillFont.render(str(currentReleaseRates[playerNum]), True, WHITE, BLACK)
    releaseRate.set_colorkey(BLACK)

    skillPanel.blit(releaseRate, (25 - releaseRate.get_width() // 2, 10))
    for i in range(len(skillsLeft)):
        skillPanel.blit(skillsLeft[i], (75 + (i * 50) - skillsLeft[i].get_width() // 2, 10))

def addToReplay(techMech, skill, vec, pNum):
    # add a skill assignment or release rate change to the replay, which is executed this frame
    if techMech != None or skill != None or vec != None:
        if currentFrame not in replay:
            replay[currentFrame] = []
        replay[currentFrame].append((techMech, skill, vec, pNum))

def executeReplay():
    # execute all skill assignments/release rate changes that occured THIS frame
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
                    if techMech.assignSkill(skill):
                        currentLevel.skillCounts[pNum][skill] -= 1
        renderSkillPanel(skillPanel, currentLevel, currentReleaseRates, playerNum)

def renderGameObjects():
    global techMechsReleased, framesSinceLastReleases, exitsHaveLeft
    
    for obj in currentLevel.objects:
        if type(obj) is Entrance and not isPaused: # check if a tech mech should be released from the entrance (is based on time and release rate
            shouldReleaseTechMech = framesSinceLastReleases[obj.owner] >= 100 - currentReleaseRates[obj.owner] and techMechsReleased[obj.owner] < currentLevel.numberOfTechMechs and Entrance.status == "open"
            if shouldReleaseTechMech:
                owner = obj.owner
                if currentLevel.numPlayers > 1:
                    owner += 1
                techMechs[obj.owner].append(TechMech(obj.x + obj.width // 2, obj.y + obj.height // 2, owner))
                techMechsReleased[obj.owner] += 1
                framesSinceLastReleases[obj.owner] = 0
        elif type(obj) is Exit:
            if Exit.status == "closed" and not isPaused: # check if the exit rocket is launching into space
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
                if not techMech.act(currentLevel, techMechsSaved, i):
                    techMechs[i].remove(techMech)
                    continue
            techMechX = techMech.getXCoordinate()
            techMechY = techMech.getYCoordinate()
            if mousex >= techMechX and mousex <= techMechX + TECH_MECH_SPRITE_WIDTH and mousey >= techMechY and mousey <= techMechY + TECH_MECH_SPRITE_HEIGHT and i == playerNum:
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
                    selectedSkill = SKILLS[0]
                # check if user clicked on the drill skill
                elif mousex < 150:
                    selectedSkill = SKILLS[1]
                # check if user clicked on the jackhammer skill
                elif mousex < 200:
                    selectedSkill = SKILLS[2]
                # check if the user clicked on the gravity reverser skill
                elif mousex < 250:
                    selectedSkill = SKILLS[3]
                # check if the user clicked on the caution sign skill
                elif mousex < 300:
                    selectedSkill = SKILLS[4]
                # check if the user clicked on the detonator skill
                elif mousex < 350:
                    selectedSkill = SKILLS[5]
                # check if the user clicked on the energizer skill
                elif mousex < 400:
                    selectedSkill = SKILLS[6]
                elif mousex < 450:
                    selectedSkill = SKILLS[7]
                elif mousex < 1200:
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
                        if currentLevel.skillCounts[playerNum][selectedSkill] > 0:
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
            # check for hotkey presses
            if pygame.key.name(event.key) == GAME_HOTKEYS["DECREASE RELEASE RATE"]:
                decreaseReleaseRate = True
            elif pygame.key.name(event.key) == GAME_HOTKEYS["INCREASE RELEASE RATE"]:
                increaseReleaseRate = True
            elif pygame.key.name(event.key) == GAME_HOTKEYS["SELECT MAGNET BOOTS SKILL"]:
                selectedSkill = MagnetBoots
            elif pygame.key.name(event.key) == GAME_HOTKEYS["SELECT ENERGIZER SKILL"]:
                selectedSkill = Energizer
            elif pygame.key.name(event.key) == GAME_HOTKEYS["SELECT DETONATOR SKILL"]:
                selectedSkill = Detonator
            elif pygame.key.name(event.key) == GAME_HOTKEYS["SELECT CAUTIONER SKILL"]:
                selectedSkill = Cautioner
            elif pygame.key.name(event.key) == GAME_HOTKEYS["SELECT GRAPPLER SKILL"]:
                selectedSkill = Grappler
            elif pygame.key.name(event.key) == GAME_HOTKEYS["SELECT DRILLER SKILL"]:
                selectedSkill = Driller
            elif pygame.key.name(event.key) == GAME_HOTKEYS["SELECT GRAVITY REVERSER SKILL"]:
                selectedSkill = GravityReverser
            elif pygame.key.name(event.key) == GAME_HOTKEYS["SELECT JACKHAMMERER SKILL"]:
                selectedSkill = Jackhammerer
            elif pygame.key.name(event.key) == GAME_HOTKEYS["PAUSE"]:
                if currentLevel.numPlayers == 1:
                    isPaused = not isPaused
            elif pygame.key.name(event.key) == GAME_HOTKEYS["END LEVEL"]:
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

    handleGameEvents()

    # check if user increased or decreased the release rate
    if increaseReleaseRate and currentReleaseRates[playerNum] < 99:
        entity = None
        action = currentReleaseRates[playerNum] + 1
        vec = None
    elif decreaseReleaseRate and currentReleaseRates[playerNum] > currentLevel.releaseRates[playerNum]:
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
        pygame.draw.rect(levelImage, WHITE, (highlightedTechMech.getXCoordinate(), highlightedTechMech.getYCoordinate(), highlightedTechMech.image.get_width(), highlightedTechMech.image.get_height()), 1)

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

    # check if the exit should be closed due to all Tech Mechs exiting or dying
    shouldLeave = techMechsReleased[playerNum] == currentLevel.numberOfTechMechs
    for i in range(len(techMechs)):
        if len(techMechs[i]) != 0:
            shouldLeave = False
            break
    if shouldLeave:
        Exit.close()

    if exitsHaveLeft:
        Exit.sound.stop()
        try:
            pygame.mixer.music.stop()
        except pygame.error:
            pass
        playingLevel = False

    return playingLevel, techMechsSaved[playerNum]




