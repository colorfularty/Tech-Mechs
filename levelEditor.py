import pygame, os
from pygame.locals import *
from constants import *
from widgets import *
from level import *
from graphicSet import *
from editorSkills import *
from editorDetails import *
from loadScreen import *
from editorHotkeys import loadEditorHotkeys

levelInProgress = None # the level object being edited
levelImage = None # the image with all the level's terrain and objects blitted to it
currentGraphicSet = GraphicSet.graphicSets[0] # the current graphic set you have selected
selectedThing = None # the terrain or object you have clicked on in the editor
levelDispX = 0 # the x displacement the level should be blitted to in the editor (in case of large levels needing scrolling)
levelDispY = 0 # the y displacement the level should be blitted to in the editor (in case of large levels needing scrolling)
continueEditor = True # if set to False, it brings the user back to the main menu
currentTab = "editor" # deterines what part of the editor you are on

# tabs to take you to different parts of the editor
backTab = Button(0, SCREEN_HEIGHT - 100, "Exit editor")
graphicSetLeft = Button(200, SCREEN_HEIGHT - 100, "<-")
graphicSetLabel = None
graphicSetRight = Button(550, SCREEN_HEIGHT - 100, "->")
terrainUp = Button(SCREEN_WIDTH - 50, 0, "^")
terrainIndex = 0
terrainPanels = []
for i in range(NUM_TERRAIN_PANELS):
    terrainPanels.append(pygame.surface.Surface((TERRAIN_PANEL_LENGTH, TERRAIN_PANEL_LENGTH)))
terrainDown = Button(SCREEN_WIDTH - 50, SCREEN_HEIGHT - 50, "v")
skillsTab = Button(0, SCREEN_HEIGHT - 50, "Skills")
detailsTab = Button(170, SCREEN_HEIGHT - 50, "Details")
loadTab = Button(340, SCREEN_HEIGHT - 50, "Load level")
saveTab = Button(500, SCREEN_HEIGHT - 50, "Save level")

# keeps track of the x and y coordinates of the mouse cursor
mousex = 0
mousey = 0

mouseClicked = False # keeps track of the mouse being held down
keysPressed = [] # keeps track of keys being held down (used for fast movement in the editor)

textBoxActive = skillFont.render("_", True, WHITE, BLACK) # used to show when a user is editing a text or number box

# timers used for moving terrain/objects quickly and for blitting text box editing underscore
directionHeldTimer = 0.0
textBoxTimer = 0.0
saveTimer = 0.0

multiplayer_icons = {0: pygame.image.load("sprites/multiplayer icon " + MULTIPLAYER_COLORS[0] + ".png").convert_alpha(),
                     1: pygame.image.load("sprites/multiplayer icon " + MULTIPLAYER_COLORS[1] + ".png").convert_alpha()}

def startEditor():
    # call everytime the user starts the editor; initializes the important variables to their proper values
    global levelInProgress, levelImage, currentGraphicSet, selectedThing, continueEditor, keysPressed, terrainIndex
    levelInProgress = Level(640, 320, 0, 0, [], [], "", "", 1, 1, [{}], -1, [1], "", 1)
    levelImage = pygame.surface.Surface((640, 320))
    currentGraphicSet = GraphicSet.graphicSets[0]
    selectedThing = None
    continueEditor = True
    keysPressed = []
    terrainIndex = 0
    updateTerrainPanels()
    saveTab.changeText("Save level")
    loadEditorHotkeys()

def setGraphicSetLabel():
    # changes the label stating which graphic set is selected and centers it between the arrows

    global graphicSetLabel

    graphicSetLabel = Label(0, SCREEN_HEIGHT - 100, currentGraphicSet.name)
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

def updateTerrainPanels():
    index = terrainIndex
    for i in range(NUM_TERRAIN_PANELS):
        terrainPanels[i].fill(BLACK)
        terrainImage = currentGraphicSet.terrain[index].image
        while terrainImage.get_width() > TERRAIN_PANEL_LENGTH or terrainImage.get_height() > TERRAIN_PANEL_LENGTH:
            terrainImage = pygame.transform.scale(terrainImage, (terrainImage.get_width() // 2, terrainImage.get_height() // 2))
        terrainPanels[i].blit(terrainImage, (0, 0))
        if index == len(currentGraphicSet.terrain) - 1:
            index = 0
        else:
            index += 1

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

def updateObjectOwners():
    entranceOwner = 0
    exitOwner = 0
    for obj in levelInProgress.objects:
        if obj.__class__.__name__ == "Entrance":
            obj.owner = entranceOwner
            entranceOwner = int(not entranceOwner)
        elif obj.__class__.__name__ == "Exit":
            obj.owner = exitOwner
            exitOwner = int(not exitOwner)

def handleEditorEvents():
    # handles all user interactions with the main editor screen
    
    global mousex, mousey, mouseClicked, continueEditor, selectedThing, currentTab, terrainIndex, saveTimer
    
    for event in pygame.event.get():
        if event.type == MOUSEMOTION:
            # update the mouse cursor coordinates
            mousex, mousey = event.pos
            # move the selected thing to the mouse's coordinates
            if selectedThing != None and mouseClicked:
                selectedThing.x = mousex + levelDispX
                selectedThing.y = mousey + levelDispY
        elif event.type == MOUSEBUTTONDOWN:
            mouseClicked = True
            index = terrainIndex
            if backTab.checkIfClicked(mousex, mousey):
                # user clicked exit editor; terminate loop condition
                continueEditor = False
            elif graphicSetLeft.checkIfClicked(mousex, mousey):
                changeGraphicSet("left")
            elif graphicSetRight.checkIfClicked(mousex, mousey):
                changeGraphicSet("right")
            elif terrainUp.checkIfClicked(mousex, mousey):
                if terrainIndex == 0:
                    terrainIndex = len(currentGraphicSet.terrain) - 1
                else:
                    terrainIndex -= 1
            elif terrainDown.checkIfClicked(mousex, mousey):
                if terrainIndex == len(currentGraphicSet.terrain) - 1:
                    terrainIndex = 0
                else:
                    terrainIndex += 1
            elif skillsTab.checkIfClicked(mousex, mousey):
                # user clicked skills tab; take them to the skills part of the editor
                currentTab = "skills"
                startEditorSkills(levelInProgress)
            elif detailsTab.checkIfClicked(mousex, mousey):
                # user clicked details tab; take them to the details part of the editor
                currentTab = "details"
                loadDetails(levelInProgress)
            elif loadTab.checkIfClicked(mousex, mousey):
                # user clicked load level; take them to the load level screen
                currentTab = "load level"
                startLoadScreen()
            elif saveTab.checkIfClicked(mousex, mousey):
                # user clicked save level; save the level object as a text file in the levels subdirectory
                levelInProgress.saveLevel()
                saveTab.changeText("Level saved")
                saveTimer = 1.0
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
            if mousex >= SCREEN_WIDTH - 150:
                for i in range(len(terrainPanels)):
                    if mousey >= 50 + 125 * i and mousey < 150 + 125 * i:
                        selectedThing = insertTerrain(levelDispX, levelDispY, currentGraphicSet.terrain[index].imageName, currentGraphicSet.name)
                        levelInProgress.addTerrain(selectedThing)
                        break
                    if index == len(currentGraphicSet.terrain) - 1:
                        index = 0
                    else:
                        index += 1
        elif event.type == MOUSEBUTTONUP:
            mouseClicked = False
        elif event.type == KEYDOWN:
            if pygame.key.name(event.key) == EDITOR_HOTKEYS["INSERT PIECE OF TERRAIN"]: # insert terrain
                if len(currentGraphicSet.terrain) > 0: # make sure the current graphic set has terrain in it
                    # there is terrain; insert the first terrain in the list into the level and make the new insertion the selected thing
                    selectedThing = insertTerrain(levelDispX, levelDispY, currentGraphicSet.terrain[0].imageName, currentGraphicSet.name)
                    levelInProgress.addTerrain(selectedThing)
            elif pygame.key.name(event.key) == EDITOR_HOTKEYS["INSERT OBJECT"]: # insert object
                if len(currentGraphicSet.objects) > 0: # make sure the current graphic set has an object to insert
                    # there is an object; insert the first object in the list into the level and make the new insertion the selected thing
                    selectedThing = insertObject(levelDispX, levelDispY, currentGraphicSet.objects[0].name, currentGraphicSet.name, currentGraphicSet.objects[0].type)
                    levelInProgress.addObject(selectedThing)
            elif pygame.key.name(event.key) == EDITOR_HOTKEYS["CHANGE TERRAIN/OBJECT TO PREVIOUS ONE IN LIST"]: # change selected terrain/object to the previous one in the graphic set's list
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
                                    elif objectGraphicSet.objects[-1].type == "Water":
                                        selectedThing = Water(objectGraphicSet.name, objectGraphicSet.objects[-1].name, selectedThing.x, selectedThing.y, selectedThing.flipped, selectedThing.inverted, selectedThing.rotated)
                                    else:
                                        selectedThing = GameObjectInstance(objectGraphicSet.name, objectGraphicSet.objects[-1].name, selectedThing.x, selectedThing.y, selectedThing.flipped, selectedThing.inverted, selectedThing.rotated)
                                else:
                                    if objectGraphicSet.objects[objIndex - 1].type == "Entrance":
                                        selectedThing = Entrance(objectGraphicSet.name, objectGraphicSet.objects[objIndex - 1].name, selectedThing.x, selectedThing.y, selectedThing.flipped, selectedThing.inverted, selectedThing.rotated)
                                    elif objectGraphicSet.objects[objIndex - 1].type == "Exit":
                                        selectedThing = Exit(objectGraphicSet.name, objectGraphicSet.objects[objIndex - 1].name, selectedThing.x, selectedThing.y, selectedThing.flipped, selectedThing.inverted, selectedThing.rotated)
                                    elif objectGraphicSet.objects[objIndex - 1].type == "Water":
                                        selectedThing = Water(objectGraphicSet.name, objectGraphicSet.objects[objIndex - 1].name, selectedThing.x, selectedThing.y, selectedThing.flipped, selectedThing.inverted, selectedThing.rotated)
                                    else:
                                        selectedThing = GameObjectInstance(currentGraphicSet.name, currentGraphicSet.objects[objIndex - 1].name, selectedThing.x, selectedThing.y, selectedThing.flipped, selectedThing.inverted, selectedThing.rotated)
                                levelInProgress.objects[levelIndex] = selectedThing # update the level object
                                break
            elif pygame.key.name(event.key) == EDITOR_HOTKEYS["CHANGE TERRAIN/OBJECT TO NEXT ONE IN LIST"]: # change the selected terrain/object to the next one in the graphic set's list
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
                                    elif objectGraphicSet.objects[0].type == "Water":
                                        selectedThing = Water(objectGraphicSet.name, objectGraphicSet.objects[0].name, selectedThing.x, selectedThing.y, selectedThing.flipped, selectedThing.inverted, selectedThing.rotated)
                                    else:
                                        selectedThing = GameObjectInstance(objectGraphicSet.name, objectGraphicSet.objects[0].name, selectedThing.x, selectedThing.y, selectedThing.flipped, selectedThing.inverted, selectedThing.rotated)
                                else:
                                    if objectGraphicSet.objects[objIndex + 1].type == "Entrance":
                                        selectedThing = Entrance(objectGraphicSet.name, objectGraphicSet.objects[objIndex + 1].name, selectedThing.x, selectedThing.y, selectedThing.flipped, selectedThing.inverted, selectedThing.rotated)
                                    elif objectGraphicSet.objects[objIndex + 1].type == "Exit":
                                        selectedThing = Exit(objectGraphicSet.name, objectGraphicSet.objects[objIndex + 1].name, selectedThing.x, selectedThing.y, selectedThing.flipped, selectedThing.inverted, selectedThing.rotated)
                                    elif objectGraphicSet.objects[objIndex + 1].type == "Water":
                                        selectedThing = Water(objectGraphicSet.name, objectGraphicSet.objects[objIndex + 1].name, selectedThing.x, selectedThing.y, selectedThing.flipped, selectedThing.inverted, selectedThing.rotated)
                                    else:
                                        selectedThing = GameObjectInstance(currentGraphicSet.name, currentGraphicSet.objects[objIndex + 1].name, selectedThing.x, selectedThing.y, selectedThing.flipped, selectedThing.inverted, selectedThing.rotated)
                                levelInProgress.objects[levelIndex] = selectedThing # update the level object
                                break
            elif pygame.key.name(event.key) == EDITOR_HOTKEYS["COPY SELECTED TERRAIN/OBJECT"]: # copy the selected thing and paste a new copy of it 16 pixels right and down
                if selectedThing != None:
                    # check if the selected thing is terrain
                    if selectedThing.__class__.__name__ == "TerrainPiece":
                        # duplicate the terrain
                        selectedThing = insertTerrain(selectedThing.x + 16, selectedThing.y + 16, selectedThing.imageName, selectedThing.graphicSet, selectedThing.flipped, selectedThing.inverted, selectedThing.rotated)
                        levelInProgress.addTerrain(selectedThing)
                    else: # the selected thing is an object
                        selectedThing = insertObject(selectedThing.x + 16, selectedThing.y + 16, selectedThing.name, selectedThing.graphicSet, selectedThing.__class__.__name__, selectedThing.flipped, selectedThing.inverted, selectedThing.rotated)
                        levelInProgress.addObject(selectedThing)
            elif pygame.key.name(event.key) == EDITOR_HOTKEYS["FLIP SELECTED TERRAIN/OBJECT"]: # flip the selected thing
                if selectedThing != None:
                    selectedThing.flipped = not selectedThing.flipped
                    selectedThing.update()
            elif pygame.key.name(event.key) == EDITOR_HOTKEYS["INVERT SELECTED TERRAIN/OBJECT"]: # invert the selected thing
                if selectedThing != None:
                    selectedThing.inverted = not selectedThing.inverted
                    selectedThing.update()
            elif pygame.key.name(event.key) == EDITOR_HOTKEYS["ROTATE SELECTED TERRAIN/OBJECT"]: # rotate the selected thing
                if selectedThing != None:
                    selectedThing.rotated = not selectedThing.rotated
                    selectedThing.update()
            elif pygame.key.name(event.key) == EDITOR_HOTKEYS["MOVE SELECTED TERRAIN/OBJECT TOWARD BACKGROUND"]: # move the selected thing toward the background (i.e. further back in the level list)
                if selectedThing != None:
                    if selectedThing.__class__.__name__ == "TerrainPiece":
                        index = levelInProgress.terrain.index(selectedThing)
                        if index > 0:
                            levelInProgress.terrain[index] = levelInProgress.terrain[index - 1]
                            levelInProgress.terrain[index - 1] = selectedThing
                    else:
                        index = levelInProgress.objects.index(selectedThing)
                        if index > 0:
                            levelInProgress.objects[index] = levelInProgress.objects[index - 1]
                            levelInProgress.objects[index - 1] = selectedThing
            elif pygame.key.name(event.key) == EDITOR_HOTKEYS["MOVE SELECTED TERRAIN/OBJECT TOWARD FOREGROUND"]: # move the selected thing toward the foreground (i.e. further up in the level list)
                if selectedThing != None:
                    if selectedThing.__class__.__name__ == "TerrainPiece":
                        index = levelInProgress.terrain.index(selectedThing)
                        if index < len(levelInProgress.terrain) - 1:
                            levelInProgress.terrain[index] = levelInProgress.terrain[index + 1]
                            levelInProgress.terrain[index + 1] = selectedThing
                    else:
                        index = levelInProgress.objects.index(selectedThing)
                        if index > len(levelInProgress.objects) - 1:
                            levelInProgress.objects[index] = levelInProgress.objects[index + 1]
                            levelInProgress.objects[index + 1] = selectedThing
            elif pygame.key.name(event.key) == EDITOR_HOTKEYS["DELETE SELECTED TERRAIN/OBJECT"]: # delete the selected thing
                if selectedThing != None:
                    if selectedThing.__class__.__name__ == 'TerrainPiece':
                        levelInProgress.terrain.remove(selectedThing)
                    else:
                        levelInProgress.objects.remove(selectedThing)
                    selectedThing = None
            elif pygame.key.name(event.key) == EDITOR_HOTKEYS["INCREASE MOVEMENT SPEED (HOLD)"]: # if ctrl is held, this can affect other held button commands
                if "ctrl" not in keysPressed:
                    keysPressed.append("ctrl")
            elif pygame.key.name(event.key) == EDITOR_HOTKEYS["MOVE SELECTED TERRAIN/OBJECT RIGHT"]: # will move the selected thing right as long as it's held
                if "right" not in keysPressed:
                    keysPressed.append("right")
            elif pygame.key.name(event.key) == EDITOR_HOTKEYS["MOVE SELECTED TERRAIN/OBJECT LEFT"]: # will move the selected thing left as long as it's held
                if "left" not in keysPressed:
                    keysPressed.append("left")
            elif pygame.key.name(event.key) == EDITOR_HOTKEYS["MOVE SELECTED TERRAIN/OBJECT DOWN"]: # will move the selected thing down as long as it's held
                if "down" not in keysPressed:
                    keysPressed.append("down")
            elif pygame.key.name(event.key) == EDITOR_HOTKEYS["MOVE SELECTED TERRAIN/OBJECT UP"]: # will move the selected thing up as long as it's held
                if "up" not in keysPressed:
                    keysPressed.append("up")
            elif pygame.key.name(event.key) == EDITOR_HOTKEYS["MOVE PERSPECTIVE RIGHT"]: # will move the perspective on the level right as long as it's held
                if "camera right" not in keysPressed:
                    keysPressed.append("camera right")
            elif pygame.key.name(event.key) == EDITOR_HOTKEYS["MOVE PERSPECTIVE LEFT"]: # will move the perspective on the level left as long as it's held
                if "camera left" not in keysPressed:
                    keysPressed.append("camera left")
            elif pygame.key.name(event.key) == EDITOR_HOTKEYS["MOVE PERSPECTIVE DOWN"]: # will move the perspective on the level down as long as it's held
                if "camera down" not in keysPressed:
                    keysPressed.append("camera down")
            elif pygame.key.name(event.key) == EDITOR_HOTKEYS["MOVE PERSPECTIVE UP"]: # will move the perspective on the level up as long as it's held
                if "camera up" not in keysPressed:
                    keysPressed.append("camera up")
            elif pygame.key.name(event.key) == EDITOR_HOTKEYS["LEAVE EDITOR"]: # a shortcut to leave the editor
                continueEditor = False
        elif event.type == KEYUP: # if the user releases a held key, this will stop some actions
            if pygame.key.name(event.key) == EDITOR_HOTKEYS["INCREASE MOVEMENT SPEED (HOLD)"]: # if user stops holding down ctrl, this will change some actions
                if "ctrl" in keysPressed:
                    keysPressed.remove("ctrl")
            elif pygame.key.name(event.key) == EDITOR_HOTKEYS["MOVE SELECTED TERRAIN/OBJECT RIGHT"]: # stop moving selected thing right
                if "right" in keysPressed:
                    keysPressed.remove("right")
            elif pygame.key.name(event.key) == EDITOR_HOTKEYS["MOVE SELECTED TERRAIN/OBJECT LEFT"]: # stop moving selected thing left
                if "left" in keysPressed:
                    keysPressed.remove("left")
            elif pygame.key.name(event.key) == EDITOR_HOTKEYS["MOVE SELECTED TERRAIN/OBJECT DOWN"]: # stop moving selected thing down
                if "down" in keysPressed:
                    keysPressed.remove("down")
            elif pygame.key.name(event.key) == EDITOR_HOTKEYS["MOVE SELECTED TERRAIN/OBJECT UP"]: # stop moving selected thing up
                if "up" in keysPressed:
                    keysPressed.remove("up")
            elif pygame.key.name(event.key) == EDITOR_HOTKEYS["MOVE PERSPECTIVE RIGHT"]: # stop moving perspective right
                if "camera right" in keysPressed:
                    keysPressed.remove("camera right")
            elif pygame.key.name(event.key) == EDITOR_HOTKEYS["MOVE PERSPECTIVE LEFT"]: # stop moving perspective left
                if "camera left" in keysPressed:
                    keysPressed.remove("camera left")
            elif pygame.key.name(event.key) == EDITOR_HOTKEYS["MOVE PERSPECTIVE DOWN"]: # stop moving perspective down
                if "camera down" in keysPressed:
                    keysPressed.remove("camera down")
            elif pygame.key.name(event.key) == EDITOR_HOTKEYS["MOVE PERSPECTIVE UP"]: # stop moving perspective up
                if "camera up" in keysPressed:
                    keysPressed.remove("camera up")
        elif event.type == QUIT: # terminate the program; all progress will be lost
            pygame.quit()
            os._exit(0)

def executeEditorFrame(SCREEN):
    # execute a frame in level editor
    
    global directionHeldTimer, textBoxTimer, levelDispX, levelDispY, currentTab, levelInProgress, levelImage, saveTimer

    if currentTab == "editor": # the user is in the main part of the editor
        handleEditorEvents() # handle the user interactions
        updateTerrainPanels()

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
        if "left" in keysPressed: # move selected thing to the left
            if selectedThing != None:
                distanceMoved = 1
                if "ctrl" in keysPressed: # if ctrl is held, move 8 pixels instead of 1
                    distanceMoved = 8
                # move the selected thing only if the key has been held for 1 frame or more than half a second
                if directionHeldTimer == TIME_PASSED or directionHeldTimer >= 0.5:
                    selectedThing.x -= distanceMoved
        if "down" in keysPressed: # move selected thing to the down
            if selectedThing != None:
                distanceMoved = 1
                if "ctrl" in keysPressed: # if ctrl is held, move 8 pixels instead of 1
                    distanceMoved = 8
                # move the selected thing only if the key has been held for 1 frame or more than half a second
                if directionHeldTimer == TIME_PASSED or directionHeldTimer >= 0.5:
                    selectedThing.y += distanceMoved
        if "up" in keysPressed: # move selected thing to the up
            if selectedThing != None:
                distanceMoved = 1
                if "ctrl" in keysPressed: # if ctrl is held, move 8 pixels instead of 1
                    distanceMoved = 8
                # move the selected thing only if the key has been held for 1 frame or more than half a second
                if directionHeldTimer == TIME_PASSED or directionHeldTimer >= 0.5:
                    selectedThing.y -= distanceMoved
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
        levelInProgress.updateWholeImage() # update the level's image with all the terrain
        # update levelImage with level's terrain and objects
        levelImage.fill(BLACK)
        levelImage.blit(levelInProgress.image, (0, 0))
        updateObjectOwners()
        for obj in levelInProgress.objects:
            levelImage.blit(obj.image, (obj.x, obj.y))
            if levelInProgress.numPlayers > 1:
                if obj.__class__.__name__ == "Entrance" or obj.__class__.__name__ == "Exit":
                    levelImage.blit(multiplayer_icons[obj.owner], (obj.x - multiplayer_icons[obj.owner].get_width() // 2 + obj.width // 2, obj.y - multiplayer_icons[obj.owner].get_height()))
        # draw a thin rectangle around the selected thing to show the user what they've selected
        if selectedThing != None:
            pygame.draw.rect(levelImage, WHITE, (selectedThing.x, selectedThing.y, selectedThing.width, selectedThing.height), 1)
        # blit the levelImage to the screen, accomodating the perspective movement
        SCREEN.blit(levelImage, (-levelDispX, -levelDispY))
        # draw an area and render all the buttons and tabs for the editor
        pygame.draw.rect(SCREEN, GREY, (0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100))
        pygame.draw.rect(SCREEN, GREY, (SCREEN_WIDTH - 150, 0, 150, SCREEN_HEIGHT))
        backTab.render(SCREEN)
        graphicSetLeft.render(SCREEN)
        graphicSetLabel.render(SCREEN)
        graphicSetRight.render(SCREEN)
        terrainUp.render(SCREEN)
        for panel in terrainPanels:
            SCREEN.blit(panel, (SCREEN_WIDTH - 100, 50 + 125 * terrainPanels.index(panel)))
        terrainDown.render(SCREEN)
        skillsTab.render(SCREEN)
        detailsTab.render(SCREEN)
        loadTab.render(SCREEN)
        if saveTimer > 0.0:
            saveTimer -= TIME_PASSED
            if saveTimer <= 0.0:
                saveTab.changeText("Save level")
        saveTab.render(SCREEN)
        pygame.display.update()
        CLOCK.tick(FPS)

    elif currentTab == "skills": # the user is in the skills part of the editor
        endSkills = executeEditorSkillsFrame(SCREEN, levelInProgress)
        if endSkills:
            currentTab = "editor"

    elif currentTab == "details": # the user is in the details section of the editor
        endDetails = executeDetailsFrame(SCREEN)
        if endDetails:
            saveDetails(levelInProgress)
            levelImage = pygame.surface.Surface((levelInProgress.width, levelInProgress.height))
            currentTab = "editor"

    elif currentTab == "load level": # user is in the load screen part of the editor
        levelLoaded = executeLoadScreenFrame(SCREEN) # execute a frame for the loading screen
        if levelLoaded == False:
            currentTab = "editor"
        elif levelLoaded != None:
            currentTab = "editor"
            levelInProgress = levelLoaded
            levelImage = pygame.surface.Surface((levelInProgress.width, levelInProgress.height))

    return continueEditor
