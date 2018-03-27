import pygame, os
from pygame.locals import *
from constants import *
from widgets import *
from level import *
from graphicSet import *
from loadScreen import *

levelInProgress = None # the level object being edited
levelImage = None # the image with all the level's terrain and objects blitted to it
currentGraphicSet = GraphicSet.graphicSets[0] # the current graphic set you have selected
selectedThing = None # the terrain or object you have clicked on in the editor
levelDispX = 0 # the x displacement the level should be blitted to in the editor (in case of large levels needing scrolling)
levelDispY = 0 # the y displacement the level should be blitted to in the editor (in case of large levels needing scrolling)
updateScreen = True # determines if the screen needs updating (only exists to maximize performance)
continueEditor = True # if set to False, it brings the user back to the main menu
currentTab = "editor" # deterines what part of the editor you are on

# tabs to take you to different parts of the editor
backTab = Button(0, 400, "Exit editor")
graphicSetLeft = Button(200, 400, "<-")
graphicSetLabel = None
graphicSetRight = Button(550, 400, "->")
skillsTab = Button(0, 450, "Skills")
detailsTab = Button(170, 450, "Details")
loadTab = Button(340, 450, "Load level")
saveTab = Button(500, 450, "Save level")
editorTab = Button(0, 0, "<-Editor")

# buttons for changing skill counts
releaseRateUp = Button(20, 250, "^")
releaseRateDown = Button(20, 410, "v")
grapplersUp = Button(70, 250, "^")
grapplersDown = Button(70, 410, "v")
drillersUp = Button(120, 250, "^")
drillersDown = Button(120, 410, "v")
jackhammerersUp = Button(170, 250, "^")
jackhammerersDown = Button(170, 410, "v")
gravityReversersUp = Button(220, 250, "^")
gravityReversersDown = Button(220, 410, "v")
cautionersUp = Button(270, 250, "^")
cautionersDown = Button(270, 410, "v")
detonatorsUp = Button(320, 250, "^")
detonatorsDown = Button(320, 410, "v")

# the skill panel displayed in the skills section
skillPanel = pygame.surface.Surface((SKILL_PANEL_WIDTH * NUMBER_OF_SKILL_PANELS, SKILL_PANEL_HEIGHT))
skillFont = pygame.font.SysFont("helvetica", 32)
skillSlot = pygame.image.load("sprites/skill panel.png")

# widgets used in the details part of the editor
widthLabel = Label(300, 0, "Level width:")
widthBox = None
heightLabel = Label(500, 0, "Level height:")
heightBox = None
startLabel = Label(400, 124, "Screen start:")
startXBox = None
startYBox = None
numPlayersLabel = Label(0, 60, "Number of Players:")
numPlayersBox = None
timeLimitLabel = Label(0, 148, "Time Limit (in seconds):")
timeLimitBox = None
techMechsLabel = Label(200, 212, "Tech Mechs")
techMechsBox = None
saveRequirementLabel = Label(400, 212, "Save Requirement:")
saveRequirementBox = None
nameLabel = Label(4, 278, "Name:")
nameBox = None
authorLabel = Label(4, 352, "Author:")
authorBox = None
musicLabel = Label(4, 426, "Music:")
musicBox = None
boxEdited = None

# keeps track of the x and y coordinates of the mouse cursor
mousex = 0
mousey = 0

keysPressed = [] # keeps track of keys being held down (used for fast movement in the editor)

textBoxActive = skillFont.render("_", True, WHITE, BLACK) # used to show when a user is editing a text or number box

# timers used for moving terrain/objects quickly and for blitting text box editing underscore
directionHeldTimer = 0.0
textBoxTimer = 0.0

def startEditor():
    # call everytime the user starts the editor; initializes the important variables to their proper values
    global levelInProgress, levelImage, currentGraphicSet, selectedThing, updateScreen, continueEditor, keysPressed
    levelInProgress = Level(640, 320, 0, 0, [], [], "", "", 1, 1, [{}], -1, 1, "", 1)
    levelImage = pygame.surface.Surface((640, 320))
    currentGraphicSet = GraphicSet.graphicSets[0]
    selectedThing = None
    updateScreen = True
    continueEditor = True
    keysPressed = []

def setGraphicSetLabel():
    # changes the label stating which graphic set is selected and centers it between the arrows

    global graphicSetLabel

    graphicSetLabel = Label(0, 400, currentGraphicSet.name)
    graphicSetLabel.x = 375 - graphicSetLabel.width // 2

# graphicSetLabel is still None, we need to give it the right value now
setGraphicSetLabel()

def changeGraphicSet(direction):
    # changes the selected graphic set based on if the user clicked on left or right arrow
    
    global currentGraphicSet

    index = GraphicSet.graphicSets.index(currentGraphicSet) # the index of the graphic set in the list of all graphic sets
    if direction == "left":
        # direction is left, new index is one less than current index unless current index is 0, then new index is the last one in the list
        if index == 0:
            currentGraphicSet = GraphicSet.graphicSets[-1]
        else:
            currentGraphicSet = GraphicSet.graphicSets[index - 1]
    else:
        # direction is right, new index is one more than the current index unless current index is the last in the list, then new index is 0
        if index == len(GraphicSet.graphicSets) - 1:
            currentGraphicSet = GraphicSet.graphicSets[0]
        else:
            currentGraphicSet = GraphicSet.graphicSets[index + 1]
    # change the graphic set label to the new graphic set
    setGraphicSetLabel()

def loadDetails():
    # loads the level object's attributes into the text and numbers boxes on the details screen
    
    global widthBox, heightBox, startXBox, startYBox, numPlayersBox, timeLimitBox, techMechsBox, saveRequirementBox, nameBox, authorBox, musicBox
    widthBox = NumberBox(300, 37, str(levelInProgress.width))
    heightBox = NumberBox(500, 37, str(levelInProgress.height))
    startXBox = NumberBox(300, 161, str(levelInProgress.startX))
    startYBox = NumberBox(500, 161, str(levelInProgress.startY))
    #numPlayersBox = NumberBox(0, 110, str(levelInProgress.numPlayers))
    if levelInProgress.timeLimit == -1:
        timeLimitBox = NumberBox(0, 185, "0")
    else:
        timeLimitBox = NumberBox(0, 185, str(levelInProgress.timeLimit))
    techMechsBox = NumberBox(200, 249, str(levelInProgress.numberOfTechMechs))
    saveRequirementBox = NumberBox(400, 249, str(levelInProgress.saveRequirement))
    nameBox = TextBox(4, 315, levelInProgress.name)
    authorBox = TextBox(4, 389, levelInProgress.author)
    musicBox = TextBox(4, 463, levelInProgress.music)
    boxEdited = None

def saveDetails():
    # saves the new values inputted into the text and number boxes on the details screen into the level object's attributes
    global levelImage
    levelInProgress.width = int(widthBox.text)
    levelInProgress.height = int(heightBox.text)
    levelImage = pygame.surface.Surface((levelInProgress.width, levelInProgress.height))
    levelInProgress.initializeImage()
    levelInProgress.updateWholeImage()
    levelInProgress.startX = int(startXBox.text)
    levelInProgress.startY = int(startYBox.text)
    #levelInProgress.updateNumPlayers(int(numPlayersBox.text))
    if timeLimitBox.text == "0":
        levelInProgress.timeLimit = -1
    else:
        levelInProgress.timeLimit = int(timeLimitBox.text)
    levelInProgress.numberOfTechMechs = int(techMechsBox.text)
    levelInProgress.saveRequirement = int(saveRequirementBox.text)
    levelInProgress.name = nameBox.text
    levelInProgress.author = authorBox.text
    levelInProgress.music = musicBox.text

def insertTerrain(x, y, name, graphicSet, flipped = False, inverted = False, rotated = False):
    # inserts a piece of terrain into the level you are editing
    return TerrainPiece.insertTerrain(graphicSet, name, x, y, flipped, inverted, rotated)

def insertObject(x, y, name, graphicSet, objType = "Normal", flipped = False, inverted = False, rotated = False):
    # inserts an object into the level you are editing
    if objType == "Entrance":
        return Entrance(graphicSet, name, x, y, flipped, inverted, rotated)
    elif objType == "Exit":
        return Exit(graphicSet, name, x, y, flipped, inverted, rotated)
    else:
        return GameObjectInstance(graphicSet, name, x, y, flipped, inverted, rotated)

def renderSkillPanel():
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
    releaseRate = skillFont.render(str(levelInProgress.releaseRate), True, WHITE, BLACK)
    grapplingHooksLeft = skillFont.render(str(levelInProgress.skillCounts[0][Grappler]), True, WHITE, BLACK)
    drillsLeft = skillFont.render(str(levelInProgress.skillCounts[0][Driller]), True, WHITE, BLACK)
    jackhammersLeft = skillFont.render(str(levelInProgress.skillCounts[0][Jackhammerer]), True, WHITE, BLACK)
    gravityReversersLeft = skillFont.render(str(levelInProgress.skillCounts[0][GravityReverser]), True, WHITE, BLACK)
    cautionSignsLeft = skillFont.render(str(levelInProgress.skillCounts[0][Cautioner]), True, WHITE, BLACK)
    landMinesLeft = skillFont.render(str(levelInProgress.skillCounts[0][Detonator]), True, WHITE, BLACK)

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

def handleEditorEvents():
    # handles all user interactions with the main editor screen
    
    global updateScreen, mousex, mousey, continueEditor, selectedThing, currentTab
    
    for event in pygame.event.get():
        if event.type == MOUSEMOTION:
            # update the mouse cursor coordinates
            mousex, mousey = event.pos
        elif event.type == MOUSEBUTTONDOWN:
            if backTab.checkIfClicked(mousex, mousey):
                # user clicked exit editor; terminate loop condition
                continueEditor = False
            elif graphicSetLeft.checkIfClicked(mousex, mousey):
                changeGraphicSet("left")
            elif graphicSetRight.checkIfClicked(mousex, mousey):
                changeGraphicSet("right")
            elif skillsTab.checkIfClicked(mousex, mousey):
                # user clicked skills tab; take them to the skills part of the editor
                renderSkillPanel()
                currentTab = "skills"
            elif detailsTab.checkIfClicked(mousex, mousey):
                # user clicked details tab; take them to the details part of the editor
                loadDetails()
                currentTab = "details"
            elif loadTab.checkIfClicked(mousex, mousey):
                # user clicked load level; take them to the load level screen
                currentTab = "load level"
                startLoadScreen()
            elif saveTab.checkIfClicked(mousex, mousey):
                # user clicked save level; save the level object as a text file in the levels subdirectory
                levelInProgress.saveLevel()
            else:
                # user clicked on something else; check if they clicked on something in the editor
                selectedThing = None
                # prioritize clicking on objects over terrain
                for obj in reversed(levelInProgress.objects): # iterate in reverse order so user can click on most up-front object
                    if mousex + levelDispX >= obj.x and mousex + levelDispX <= obj.x + obj.width and mousey + levelDispY >= obj.y and mousey + levelDispY <= obj.y + obj.height:
                        # user clicked on this object; set selectedThing to object and break out of the loop
                        selectedThing = obj
                        break
                if selectedThing == None:
                    # user hasn't clicked on an object; check if they clicked on terrain
                    for terrain in reversed(levelInProgress.terrain): # iterate in reverse order so user can click on most up-front terrain
                        if mousex + levelDispX >= terrain.x and mousex + levelDispX <= terrain.x + terrain.width and mousey + levelDispY >= terrain.y and mousey + levelDispY <= terrain.y + terrain.height:
                            # user clicked on this terrain; set selectedThing to terrain and break out of the loop
                            selectedThing = terrain
                            break
        elif event.type == KEYDOWN:
            if event.key == K_t: # insert terrain
                if len(currentGraphicSet.terrain) > 0: # make sure the current graphic set has terrain in it
                    # there is terrain; insert the first terrain in the list into the level and make the new insertion the selected thing
                    selectedThing = insertTerrain(0, 0, currentGraphicSet.terrain[0].imageName, currentGraphicSet.name)
                    levelInProgress.addTerrain(selectedThing)
            elif event.key == K_o: # insert object
                if len(currentGraphicSet.objects) > 0: # make sure the current graphic set has an object to insert
                    # there is an object; insert the first object in the list into the level and make the new insertion the selected thing
                    selectedThing = insertObject(0, 0, currentGraphicSet.objects[0].name, currentGraphicSet.name, currentGraphicSet.objects[0].type)
                    levelInProgress.addObject(selectedThing)
            elif event.key == K_a: # change selected terrain/object to the previous one in the graphic set's list
                if selectedThing != None: # make sure the user has something selected
                    if selectedThing.__class__.__name__ == "TerrainPiece": # checks if the selected thing is terrain
                        levelIndex = levelInProgress.terrain.index(selectedThing) # the index of the currently selected terrain in the level object's list
                        # find the graphic set the selected terrain is a part of
                        terrainGraphicSetName = selectedThing.graphicSet
                        for gs in GraphicSet.graphicSets:
                            if gs.name == terrainGraphicSetName:
                                terrainGraphicSetIndex = GraphicSet.graphicSets.index(gs)
                                break
                        terrainGraphicSet = GraphicSet.graphicSets[terrainGraphicSetIndex]
                        # find the index of the selected terrain relative to the graphic set's list
                        for terrain in terrainGraphicSet.terrain:
                            if terrain.imageName == selectedThing.imageName: 
                                terrainIndex = terrainGraphicSet.terrain.index(terrain)
                                if terrainIndex == 0: # make sure if the currently selected terrain is index 0 that the previous terrain is the last one in the list
                                    selectedThing = TerrainPiece.insertTerrain(terrainGraphicSet.name, terrainGraphicSet.terrain[-1].imageName, selectedThing.x, selectedThing.y, selectedThing.flipped, selectedThing.inverted, selectedThing.rotated)
                                else:
                                    selectedThing = TerrainPiece.insertTerrain(terrainGraphicSet.name, terrainGraphicSet.terrain[terrainIndex - 1].imageName, selectedThing.x, selectedThing.y, selectedThing.flipped, selectedThing.inverted, selectedThing.rotated)
                                levelInProgress.terrain[levelIndex] = selectedThing # update the level object
                                updateScreen = True
                                break
                    else: # the selected thing is an object
                        levelIndex = levelInProgress.objects.index(selectedThing) # the index of the object relative to the level object's list
                        # find the graphic set containing the selected object
                        objectGraphicSetName = selectedThing.graphicSet
                        for gs in GraphicSet.graphicSets:
                            if gs.name == objectGraphicSetName:
                                objectGraphicSetIndex = GraphicSet.graphicSets.index(gs)
                                break
                        objectGraphicSet = GraphicSet.graphicSets[objectGraphicSetIndex]
                        # find the index of the selected object relative to the graphic set's list
                        for obj in objectGraphicSet.objects:
                            if obj.name == selectedThing.name:
                                objIndex = currentGraphicSet.objects.index(obj)
                                if objIndex == 0: # make sure if the currently selected object is index 0 that the previous object is the last one in the list
                                    if objectGraphicSet.objects[-1].type == "Entrance":
                                        selectedThing = Entrance(objectGraphicSet.name, objectGraphicSet.objects[-1].name, selectedThing.x, selectedThing.y, selectedThing.flipped, selectedThing.inverted, selectedThing.rotated)
                                    elif objectGraphicSet.objects[-1].type == "Exit":
                                        selectedThing = Exit(objectGraphicSet.name, objectGraphicSet.objects[-1].name, selectedThing.x, selectedThing.y, selectedThing.flipped, selectedThing.inverted, selectedThing.rotated)
                                    else:
                                        selectedThing = GameObjectInstance(objectGraphicSet.name, objectGraphicSet.objects[-1].name, selectedThing.x, selectedThing.y, selectedThing.flipped, selectedThing.inverted, selectedThing.rotated)
                                else:
                                    if objectGraphicSet.objects[objIndex - 1].type == "Entrance":
                                        selectedThing = Entrance(objectGraphicSet.name, objectGraphicSet.objects[objIndex - 1].name, selectedThing.x, selectedThing.y, selectedThing.flipped, selectedThing.inverted, selectedThing.rotated)
                                    elif objectGraphicSet.objects[objIndex - 1].type == "Exit":
                                        selectedThing = Exit(objectGraphicSet.name, objectGraphicSet.objects[objIndex - 1].name, selectedThing.x, selectedThing.y, selectedThing.flipped, selectedThing.inverted, selectedThing.rotated)
                                    else:
                                        selectedThing = GameObjectInstance(currentGraphicSet.name, currentGraphicSet.objects[objIndex - 1].name, selectedThing.x, selectedThing.y, selectedThing.flipped, selectedThing.inverted, selectedThing.rotated)
                                levelInProgress.objects[levelIndex] = selectedThing # update the level object
                                updateScreen = True
                                break
            elif event.key == K_s: # change the selected terrain/object to the next one in the graphic set's list
                if selectedThing != None: # make sure the user has selected something
                    if selectedThing.__class__.__name__ == "TerrainPiece": # check if the selected thing is terrain
                        levelIndex = levelInProgress.terrain.index(selectedThing)
                        # find the graphic set the selected terrain is a part of
                        terrainGraphicSetName = selectedThing.graphicSet
                        for gs in GraphicSet.graphicSets:
                            if gs.name == terrainGraphicSetName:
                                terrainGraphicSetIndex = GraphicSet.graphicSets.index(gs)
                                break
                        terrainGraphicSet = GraphicSet.graphicSets[terrainGraphicSetIndex]
                        # find the index of the selected terrain relative to the graphic set's list
                        for terrain in terrainGraphicSet.terrain:
                            if terrain.imageName == selectedThing.imageName:
                                terrainIndex = terrainGraphicSet.terrain.index(terrain)
                                # make sure if the selected terrain is the last one in the list that the next terrain is the first one in the list
                                if terrainIndex == len(terrainGraphicSet.terrain) - 1:
                                    selectedThing = TerrainPiece.insertTerrain(terrainGraphicSet.name, terrainGraphicSet.terrain[0].imageName, selectedThing.x, selectedThing.y, selectedThing.flipped, selectedThing.inverted, selectedThing.rotated)
                                else:
                                    selectedThing = TerrainPiece.insertTerrain(terrainGraphicSet.name, terrainGraphicSet.terrain[terrainIndex + 1].imageName, selectedThing.x, selectedThing.y, selectedThing.flipped, selectedThing.inverted, selectedThing.rotated)
                                levelInProgress.terrain[levelIndex] = selectedThing # update the level object
                                updateScreen = True
                                break
                    else: # the selected thing is an object
                        levelIndex = levelInProgress.objects.index(selectedThing)
                        # find the graphic set containing the selected object
                        objectGraphicSetName = selectedThing.graphicSet
                        for gs in GraphicSet.graphicSets:
                            if gs.name == objectGraphicSetName:
                                objectGraphicSetIndex = GraphicSet.graphicSets.index(gs)
                                break
                        objectGraphicSet = GraphicSet.graphicSets[objectGraphicSetIndex]
                        # find the index of the selected object relative to the graphic set's list
                        for obj in objectGraphicSet.objects:
                            if obj.name == selectedThing.name:
                                objIndex = currentGraphicSet.objects.index(obj)
                                # make sure if the selected object is the last one in the list that the next object is the first one in the list
                                if objIndex == len(objectGraphicSet.objects) - 1:
                                    if objectGraphicSet.objects[0].type == "Entrance":
                                        selectedThing = Entrance(objectGraphicSet.name, objectGraphicSet.objects[0].name, selectedThing.x, selectedThing.y, selectedThing.flipped, selectedThing.inverted, selectedThing.rotated)
                                    elif objectGraphicSet.objects[0].type == "Exit":
                                        selectedThing = Exit(objectGraphicSet.name, objectGraphicSet.objects[0].name, selectedThing.x, selectedThing.y, selectedThing.flipped, selectedThing.inverted, selectedThing.rotated)
                                    else:
                                        selectedThing = GameObjectInstance(objectGraphicSet.name, objectGraphicSet.objects[0].name, selectedThing.x, selectedThing.y, selectedThing.flipped, selectedThing.inverted, selectedThing.rotated)
                                else:
                                    if objectGraphicSet.objects[objIndex + 1].type == "Entrance":
                                        selectedThing = Entrance(currentGraphicSet.name, currentGraphicSet.objects[objIndex + 1].name, selectedThing.x, selectedThing.y, selectedThing.flipped, selectedThing.inverted, selectedThing.rotated)
                                    elif objectGraphicSet.objects[objIndex + 1].type == "Exit":
                                        selectedThing = Exit(currentGraphicSet.name, currentGraphicSet.objects[objIndex + 1].name, selectedThing.x, selectedThing.y, selectedThing.flipped, selectedThing.inverted, selectedThing.rotated)
                                    else:
                                        selectedThing = GameObjectInstance(currentGraphicSet.name, currentGraphicSet.objects[objIndex + 1].name, selectedThing.x, selectedThing.y, selectedThing.flipped, selectedThing.inverted, selectedThing.rotated)
                                levelInProgress.objects[levelIndex] = selectedThing # update the level object
                                updateScreen = True
                                break
            elif event.key == K_c: # copy the selected thing and paste a new copy of it 16 pixels right and down
                if selectedThing != None:
                    # check if the selected thing is terrain
                    if selectedThing.__class__.__name__ == "TerrainPiece":
                        # duplicate the terrain
                        selectedThing = insertTerrain(selectedThing.x + 16, selectedThing.y + 16, selectedThing.imageName, selectedThing.graphicSet, selectedThing.flipped, selectedThing.inverted, selectedThing.rotated)
                        levelInProgress.addTerrain(selectedThing)
                    else: # the selected thing is an object
                        selectedThing = insertObject(selectedThing.x + 16, selectedThing.y + 16, selectedThing.name, selectedThing.graphicSet, selectedThing.__class__.__name__, selectedThing.flipped, selectedThing.inverted, selectedThing.rotated)
                        levelInProgress.addObject(selectedThing)
            elif event.key == K_f: # flip the selected thing
                if selectedThing != None:
                    selectedThing.flipped = not selectedThing.flipped
                    selectedThing.update()
                    updateScreen = True
            elif event.key == K_i: # invert the selected thing
                if selectedThing != None:
                    selectedThing.inverted = not selectedThing.inverted
                    selectedThing.update()
                    updateScreen = True
            elif event.key == K_r: # rotate the selected thing
                if selectedThing != None:
                    selectedThing.rotated = not selectedThing.rotated
                    selectedThing.update()
                    updateScreen = True
            elif event.key == K_DELETE: # delete the selected thing
                if selectedThing != None:
                    if selectedThing.__class__.__name__ == 'TerrainPiece':
                        levelInProgress.terrain.remove(selectedThing)
                    else:
                        levelInProgress.objects.remove(selectedThing)
                    selectedThing = None
                    updateScreen = True
            elif event.key == K_LCTRL or event.key == K_RCTRL: # if ctrl is held, this can affect other held button commands
                if "ctrl" not in keysPressed:
                    keysPressed.append("ctrl")
            elif event.key == K_RIGHT: # will move the selected thing right as long as it's held
                if "right" not in keysPressed:
                    keysPressed.append("right")
            elif event.key == K_LEFT: # will move the selected thing left as long as it's held
                if "left" not in keysPressed:
                    keysPressed.append("left")
            elif event.key == K_DOWN: # will move the selected thing down as long as it's held
                if "down" not in keysPressed:
                    keysPressed.append("down")
            elif event.key == K_UP: # will move the selected thing up as long as it's held
                if "up" not in keysPressed:
                    keysPressed.append("up")
            elif event.key == K_j: # will move the perspective on the level right as long as it's held
                if "camera right" not in keysPressed:
                    keysPressed.append("camera right")
            elif event.key == K_g: # will move the perspective on the level left as long as it's held
                if "camera left" not in keysPressed:
                    keysPressed.append("camera left")
            elif event.key == K_h: # will move the perspective on the level down as long as it's held
                if "camera down" not in keysPressed:
                    keysPressed.append("camera down")
            elif event.key == K_y: # will move the perspective on the level up as long as it's held
                if "camera up" not in keysPressed:
                    keysPressed.append("camera up")
            elif event.key == K_ESCAPE: # a shortcut to leave the editor
                continueEditor = False
        elif event.type == KEYUP: # if the user releases a held key, this will stop some actions
            if event.key == K_LCTRL: # if user stops holding down ctrl, this will change some actions
                if "ctrl" in keysPressed:
                    keysPressed.remove("ctrl")
            elif event.key == K_RIGHT: # stop moving selected thing right
                if "right" in keysPressed:
                    keysPressed.remove("right")
            elif event.key == K_LEFT: # stop moving selected thing left
                if "left" in keysPressed:
                    keysPressed.remove("left")
            elif event.key == K_DOWN: # stop moving selected thing down
                if "down" in keysPressed:
                    keysPressed.remove("down")
            elif event.key == K_UP: # stop moving selected thing up
                if "up" in keysPressed:
                    keysPressed.remove("up")
            elif event.key == K_j: # stop moving perspective right
                if "camera right" in keysPressed:
                    keysPressed.remove("camera right")
            elif event.key == K_g: # stop moving perspective left
                if "camera left" in keysPressed:
                    keysPressed.remove("camera left")
            elif event.key == K_h: # stop moving perspective down
                if "camera down" in keysPressed:
                    keysPressed.remove("camera down")
            elif event.key == K_y: # stop moving perspective up
                if "camera up" in keysPressed:
                    keysPressed.remove("camera up")
        elif event.type == QUIT: # terminate the program; all progress will be lost
            pygame.quit()
            os._exit(0)

def handleSkillsEvents():
    # handle the user interactions with the skills screen
    
    global currentTab, mousex, mousey
    
    for event in pygame.event.get():
        if event.type == MOUSEMOTION:
            # update the mouse cursor coordinates
            mousex, mousey = event.pos
        elif event.type == MOUSEBUTTONDOWN:
            if editorTab.checkIfClicked(mousex, mousey):
                # user clicked editor button; go back to the main editor screen
                currentTab = "editor"
            elif releaseRateUp.checkIfClicked(mousex, mousey):
                # increase the level's minimum release rate if possible
                if levelInProgress.releaseRate < 99:
                    levelInProgress.releaseRate += 1
                    renderSkillPanel()
            elif releaseRateDown.checkIfClicked(mousex, mousey):
                # decrease the level's minimum release rate if possible
                if levelInProgress.releaseRate > 1:
                    levelInProgress.releaseRate -= 1
                    renderSkillPanel()
            elif grapplersUp.checkIfClicked(mousex, mousey):
                # increase the amount of grapplers if possible
                if levelInProgress.skillCounts[0][Grappler] < 99:
                    levelInProgress.skillCounts[0][Grappler] += 1
                    renderSkillPanel()
            elif grapplersDown.checkIfClicked(mousex, mousey):
                # decrease the amount of grapplers if possible
                if levelInProgress.skillCounts[0][Grappler] > 0:
                    levelInProgress.skillCounts[0][Grappler] -= 1
                    renderSkillPanel()
            elif drillersUp.checkIfClicked(mousex, mousey):
                # increase the amount of drillers if possible
                if levelInProgress.skillCounts[0][Driller] < 99:
                    levelInProgress.skillCounts[0][Driller] += 1
                    renderSkillPanel()
            elif drillersDown.checkIfClicked(mousex, mousey):
                # decrease the amount of drillers if possible
                if levelInProgress.skillCounts[0][Driller] > 0:
                    levelInProgress.skillCounts[0][Driller] -= 1
                    renderSkillPanel()
            elif jackhammerersUp.checkIfClicked(mousex, mousey):
                # increase the amount of jackhammerers if possible
                if levelInProgress.skillCounts[0][Jackhammerer] < 99:
                    levelInProgress.skillCounts[0][Jackhammerer] += 1
                    renderSkillPanel()
            elif jackhammerersDown.checkIfClicked(mousex, mousey):
                # decrease the amount of jackhammerers if possible
                if levelInProgress.skillCounts[0][Jackhammerer] > 0:
                    levelInProgress.skillCounts[0][Jackhammerer] -= 1
                    renderSkillPanel()
            elif gravityReversersUp.checkIfClicked(mousex, mousey):
                # increase the amount of gravity reversers if possible
                if levelInProgress.skillCounts[0][GravityReverser] < 99:
                    levelInProgress.skillCounts[0][GravityReverser] += 1
                    renderSkillPanel()
            elif gravityReversersDown.checkIfClicked(mousex, mousey):
                # decrease the amount of gravity reversers if possible
                if levelInProgress.skillCounts[0][GravityReverser] > 0:
                    levelInProgress.skillCounts[0][GravityReverser] -= 1
                    renderSkillPanel()
            elif cautionersUp.checkIfClicked(mousex, mousey):
                # increase the amount of cautioners if possible
                if levelInProgress.skillCounts[0][Cautioner] < 99:
                    levelInProgress.skillCounts[0][Cautioner] += 1
                    renderSkillPanel()
            elif cautionersDown.checkIfClicked(mousex, mousey):
                # decrease the amount of cautioners if possible
                if levelInProgress.skillCounts[0][Cautioner] > 0:
                    levelInProgress.skillCounts[0][Cautioner] -= 1
                    renderSkillPanel()
            elif detonatorsUp.checkIfClicked(mousex, mousey):
                # increase the amount of detonators if possible
                if levelInProgress.skillCounts[0][Detonator] < 99:
                    levelInProgress.skillCounts[0][Detonator] += 1
                    renderSkillPanel()
            elif detonatorsDown.checkIfClicked(mousex, mousey):
                # decrease the amount of detonators if possible
                if levelInProgress.skillCounts[0][Detonator] > 0:
                    levelInProgress.skillCounts[0][Detonator] -= 1
                    renderSkillPanel()
        elif event.type == QUIT: # terminate program; all progress will be lost
            pygame.quit()
            os._exit(0)

def handleDetailsEvents():
    # handle all user interactions with the details screen
    
    global currentTab, boxEdited, mousex, mousey

    for event in pygame.event.get():
        if event.type == MOUSEMOTION:
            # update the mouse cursor coordinates
            mousex, mousey = event.pos
        elif event.type == MOUSEBUTTONDOWN:
            boxEdited = None # set this to None so the user can click to cancel editing
            if nameBox.checkIfClicked(mousex, mousey):
                # allow user to edit the level's name
                boxEdited = "name"
            elif authorBox.checkIfClicked(mousex, mousey):
                # allow user to edit the level's author
                boxEdited = "author"
            elif musicBox.checkIfClicked(mousex, mousey):
                # allow user to edit the level's music
                boxEdited = "music"
            elif widthBox.checkIfClicked(mousex, mousey):
                # allow user to edit the level's width
                boxEdited = "width"
            elif heightBox.checkIfClicked(mousex, mousey):
                # allow user to edit the level's height
                boxEdited = "height"
            elif startXBox.checkIfClicked(mousex, mousey):
                # allow user to edit the level's starting X coordinate
                boxEdited = "startX"
            elif startYBox.checkIfClicked(mousex, mousey):
                # allow user to edit the level's starting Y coordinate
                boxEdited = "startY"
            #elif numPlayersBox.checkIfClicked(mousex, mousey):
                # allow user to edit the number of players the level is for
                #boxEdited = "num players"
            elif techMechsBox.checkIfClicked(mousex, mousey):
                # allow user to edit the level's number of Tech Mechs
                boxEdited = "tech mechs"
            elif saveRequirementBox.checkIfClicked(mousex, mousey):
                # allow user to edit the level's save requirement
                boxEdited = "save requirement"
            elif editorTab.checkIfClicked(mousex, mousey):
                # user clicked editor tab; save the details inputted to the level object
                saveDetails()
                currentTab = "editor"
        elif event.type == KEYDOWN:
            if event.key == K_LSHIFT: # shift is held; allow user to type capital letters
                if "shift" not in keysPressed:
                    keysPressed.append("shift")
            elif boxEdited == "name": # edit the level's name
                nameBox.changeText(event.key, "shift" in keysPressed)
            elif boxEdited == "author": # edit the level's author
                authorBox.changeText(event.key, "shift" in keysPressed)
            elif boxEdited == "music": # edit the level's music
                musicBox.changeText(event.key, "shift" in keysPressed)
            elif boxEdited == "width": # edit the level's width
                widthBox.changeText(event.key)
            elif boxEdited == "height": # edit the level's height
                heightBox.changeText(event.key)
            elif boxEdited == "startX": # edit the level's starting X coordinate
                startXBox.changeText(event.key)
            elif boxEdited == "startY": # edit the level's starting Y coordinate
                startYBox.changeText(event.key)
            elif boxEdited == "num players": # edit the level's number of players
                numPlayersBox.changeText(event.key)
            elif boxEdited == "tech mechs": # edit the level's number of Tech Mechs
                techMechsBox.changeText(event.key)
            elif boxEdited == "save requirement": # edit the level's save requirement
                saveRequirementBox.changeText(event.key)
        elif event.type == KEYUP:
            if event.key == K_LSHIFT: # stop capital letters from being typed
                if "shift" in keysPressed:
                    keysPressed.remove("shift")
        elif event.type == QUIT: # terminate the program; all progress will be lost
            pygame.quit()
            os._exit(0)

def executeEditorLoop(SCREEN):
    # execute a frame in level editor
    
    global updateScreen, directionHeldTimer, textBoxTimer, levelDispX, levelDispY, currentTab, levelInProgress, levelImage

    if currentTab == "editor": # the user is in the main part of the editor
        handleEditorEvents() # handle the user interactions

        # if no direction keys are held, restart the direction timer; otherwise increase it
        if "right" not in keysPressed and "left" not in keysPressed and "down" not in keysPressed and "up" not in keysPressed:
            directionHeldTimer = 0.0
        else:
            directionHeldTimer += TIME_PASSED

        
        if "right" in keysPressed: # move selected thing to the right
            if selectedThing != None:
                distanceMoved = 1
                if "ctrl" in keysPressed: # if ctrl is held, move 8 pixels instead of 1
                    distanceMoved = 8
                # move the selected thing only if the key has been held for 1 frame or more than half a second
                if directionHeldTimer == TIME_PASSED or directionHeldTimer >= 0.5:
                    selectedThing.x += distanceMoved
                    updateScreen = True
        if "left" in keysPressed: # move selected thing to the left
            if selectedThing != None:
                distanceMoved = 1
                if "ctrl" in keysPressed: # if ctrl is held, move 8 pixels instead of 1
                    distanceMoved = 8
                # move the selected thing only if the key has been held for 1 frame or more than half a second
                if directionHeldTimer == TIME_PASSED or directionHeldTimer >= 0.5:
                    selectedThing.x -= distanceMoved
                    updateScreen = True
        if "down" in keysPressed: # move selected thing to the down
            if selectedThing != None:
                distanceMoved = 1
                if "ctrl" in keysPressed: # if ctrl is held, move 8 pixels instead of 1
                    distanceMoved = 8
                # move the selected thing only if the key has been held for 1 frame or more than half a second
                if directionHeldTimer == TIME_PASSED or directionHeldTimer >= 0.5:
                    selectedThing.y += distanceMoved
                    updateScreen = True
        if "up" in keysPressed: # move selected thing to the up
            if selectedThing != None:
                distanceMoved = 1
                if "ctrl" in keysPressed: # if ctrl is held, move 8 pixels instead of 1
                    distanceMoved = 8
                # move the selected thing only if the key has been held for 1 frame or more than half a second
                if directionHeldTimer == TIME_PASSED or directionHeldTimer >= 0.5:
                    selectedThing.y -= distanceMoved
                    updateScreen = True
        if "camera right" in keysPressed: # move perspective right
            if levelDispX + SCREEN_WIDTH < levelInProgress.width: # make sure moving the camera will show more of the level
                distanceMoved = 1
                if "ctrl" in keysPressed: # if ctrl is held, move 8 pixels instead of 1
                    distanceMoved = 8
                    if levelInProgress.width - levelDispX - SCREEN_WIDTH < 8:
                        distanceMoved = levelInProgress.width - levelDispX - SCREEN_WIDTH
                levelDispX += distanceMoved
        if "camera left" in keysPressed: # move perspective left
            if levelDispX > 0: # make sure moving the camera will show more of the level
                distanceMoved = 1
                if "ctrl" in keysPressed: # if ctrl is held, move 8 pixels instead of 1
                    distanceMoved = 8
                    if levelDispX < 8:
                        distanceMoved = levelDispX
                levelDispX -= distanceMoved
        if "camera down" in keysPressed: # move perspective down
            if levelDispY + SCREEN_HEIGHT - 100 < levelInProgress.height: # make sure moving the camera will show more of the level
                distanceMoved = 1
                if "ctrl" in keysPressed: # if ctrl is held, move 8 pixels instead of 1
                    distanceMoved = 8
                    if levelInProgress.height - levelDispY - SCREEN_HEIGHT + 100 < 8:
                        distanceMoved = levelInProgress.height - levelDispY - SCREEN_HEIGHT + 100
                levelDispY += distanceMoved
        if "camera up" in keysPressed: # move perspective up
            if levelDispY > 0: # make sure moving the camera will show more of the level
                distanceMoved = 1
                if "ctrl" in keysPressed: # if ctrl is held, move 8 pixels instead of 1
                    distanceMoved = 8
                    if levelDispY < 8:
                        distanceMoved = levelDispY
                levelDispY -= distanceMoved
        
        SCREEN.fill(GREY) # fill the screen with GREY
        if updateScreen:
            levelInProgress.updateWholeImage() # update the level's image with all the terrain
            updateScreen = False
        # update levelImage with level's terrain and objects
        levelImage.fill(BLACK)
        levelImage.blit(levelInProgress.image, (0, 0))
        for obj in levelInProgress.objects:
            levelImage.blit(obj.image, (obj.x, obj.y))
        # draw a thin rectangle around the selected thing to show the user what they've selected
        if selectedThing != None:
            pygame.draw.rect(levelImage, WHITE, (selectedThing.x, selectedThing.y, selectedThing.width, selectedThing.height), 1)
        # blit the levelImage to the screen, accomodating the perspective movement
        SCREEN.blit(levelImage, (-levelDispX, -levelDispY))
        # draw an area and render all the buttons and tabs for the editor
        pygame.draw.rect(SCREEN, GREY, (0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100))
        backTab.render(SCREEN)
        graphicSetLeft.render(SCREEN)
        graphicSetLabel.render(SCREEN)
        graphicSetRight.render(SCREEN)
        skillsTab.render(SCREEN)
        detailsTab.render(SCREEN)
        loadTab.render(SCREEN)
        saveTab.render(SCREEN)
        pygame.display.update()
        CLOCK.tick(FPS)

    elif currentTab == "skills": # the user is in the skills part of the editor
        handleSkillsEvents() # handle user interactions

        # update the screen
        SCREEN.fill(GREY)
        SCREEN.blit(skillPanel, (0, 300))
        editorTab.render(SCREEN)
        releaseRateUp.render(SCREEN)
        releaseRateDown.render(SCREEN)
        grapplersUp.render(SCREEN)
        grapplersDown.render(SCREEN)
        drillersUp.render(SCREEN)
        drillersDown.render(SCREEN)
        jackhammerersUp.render(SCREEN)
        jackhammerersDown.render(SCREEN)
        gravityReversersUp.render(SCREEN)
        gravityReversersDown.render(SCREEN)
        cautionersUp.render(SCREEN)
        cautionersDown.render(SCREEN)
        detonatorsUp.render(SCREEN)
        detonatorsDown.render(SCREEN)
        
        pygame.display.update()
        CLOCK.tick(FPS)

    elif currentTab == "details": # the user is in the details section of the editor
        handleDetailsEvents() # handle user interactions

        # update the screen
        SCREEN.fill(GREY)
        editorTab.render(SCREEN)
        widthLabel.render(SCREEN)
        widthBox.render(SCREEN, textBoxTimer)
        heightLabel.render(SCREEN)
        heightBox.render(SCREEN, textBoxTimer)
        startLabel.render(SCREEN)
        startXBox.render(SCREEN, textBoxTimer)
        startYBox.render(SCREEN, textBoxTimer)
        #numPlayersLabel.render(SCREEN)
        #numPlayersBox.render(SCREEN, textBoxTimer)
        timeLimitLabel.render(SCREEN)
        timeLimitBox.render(SCREEN, textBoxTimer)
        techMechsLabel.render(SCREEN)
        techMechsBox.render(SCREEN, textBoxTimer)
        saveRequirementLabel.render(SCREEN)
        saveRequirementBox.render(SCREEN, textBoxTimer)
        nameLabel.render(SCREEN)
        nameBox.render(SCREEN, textBoxTimer)
        authorLabel.render(SCREEN)
        authorBox.render(SCREEN, textBoxTimer)
        musicLabel.render(SCREEN)
        musicBox.render(SCREEN, textBoxTimer)
        pygame.display.update()
        CLOCK.tick(FPS)
        textBoxTimer += TIME_PASSED
        if textBoxTimer >= 1.0:
            textBoxTimer -= 1.0

    elif currentTab == "load level": # user is in the load screen part of the editor
        levelLoaded = executeLoadScreenFrame(SCREEN) # execute a frame for the loading screen
        if levelLoaded == False:
            currentTab = "editor"
            updateScreen = True
        elif levelLoaded != None:
            currentTab = "editor"
            levelInProgress = levelLoaded
            levelImage = pygame.surface.Surface((levelInProgress.width, levelInProgress.height))
            updateScreen = True

    return continueEditor
