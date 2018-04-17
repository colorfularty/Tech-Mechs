import pygame, os
from pygame.locals import *
from constants import *
from widgets import *

# widgets used in the details part of the editor
editorTab = Button(0, 0, "<-Editor")
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
testBoxTimer = 0.0
endDetails = False

# keeps track of the x and y coordinates of the mouse cursor
mousex = 0
mousey = 0

keysPressed = []

def loadDetails(levelInProgress):
    # loads the level object's attributes into the text and numbers boxes on the details screen
    
    global widthBox, heightBox, startXBox, startYBox, numPlayersBox, timeLimitBox, techMechsBox, saveRequirementBox, nameBox, authorBox, musicBox, textBoxTimer, endDetails
    widthBox = NumberBox(300, 37, str(levelInProgress.width), minVal = 128, maxVal = 16384)
    heightBox = NumberBox(500, 37, str(levelInProgress.height), minVal = 128, maxVal = 16384)
    startXBox = NumberBox(300, 161, str(levelInProgress.startX), minVal = 0, maxVal = levelInProgress.width)
    startYBox = NumberBox(500, 161, str(levelInProgress.startY), minVal = 0, maxVal = levelInProgress.height)
    numPlayersBox = NumberBox(0, 110, str(levelInProgress.numPlayers), minVal = 1, maxVal = 2)
    if levelInProgress.timeLimit == -1:
        timeLimitBox = NumberBox(0, 185, "0", minVal = 0, maxVal = 5940)
    else:
        timeLimitBox = NumberBox(0, 185, str(levelInProgress.timeLimit), minVal = 0, maxVal = 5940)
    techMechsBox = NumberBox(200, 249, str(levelInProgress.numberOfTechMechs), minVal = 1, maxVal = 1000)
    saveRequirementBox = NumberBox(400, 249, str(levelInProgress.saveRequirement), minVal = 0, maxVal = levelInProgress.numberOfTechMechs)
    nameBox = TextBox(4, 315, levelInProgress.name)
    authorBox = TextBox(4, 389, levelInProgress.author)
    musicBox = TextBox(4, 463, levelInProgress.music)
    boxEdited = None
    textBoxTimer = 0.0
    endDetails = False

def saveDetails(levelInProgress):
    # saves the new values inputted into the text and number boxes on the details screen into the level object's attributes
    levelInProgress.width = int(widthBox.text)
    levelInProgress.height = int(heightBox.text)
    levelInProgress.initializeImage()
    levelInProgress.updateWholeImage()
    levelInProgress.startX = int(startXBox.text)
    levelInProgress.startY = int(startYBox.text)
    levelInProgress.updateNumPlayers(int(numPlayersBox.text))
    if timeLimitBox.text == "0":
        levelInProgress.timeLimit = -1
    else:
        levelInProgress.timeLimit = int(timeLimitBox.text)
    levelInProgress.numberOfTechMechs = int(techMechsBox.text)
    levelInProgress.saveRequirement = int(saveRequirementBox.text)
    levelInProgress.name = nameBox.text
    levelInProgress.author = authorBox.text
    levelInProgress.music = musicBox.text

def handleDetailsEvents():
    # handle all user interactions with the details screen
    
    global endDetails, boxEdited, mousex, mousey

    for event in pygame.event.get():
        if event.type == MOUSEMOTION:
            # update the mouse cursor coordinates
            mousex, mousey = event.pos
        elif event.type == MOUSEBUTTONDOWN:
            boxEdited = None # set this to None so the user can click to cancel editing
            if nameBox.checkIfClicked(mousex, mousey):
                # allow user to edit the level's name
                boxEdited = "name"
            if authorBox.checkIfClicked(mousex, mousey):
                # allow user to edit the level's author
                boxEdited = "author"
            if musicBox.checkIfClicked(mousex, mousey):
                # allow user to edit the level's music
                boxEdited = "music"
            if widthBox.checkIfClicked(mousex, mousey):
                # allow user to edit the level's width
                boxEdited = "width"
            if heightBox.checkIfClicked(mousex, mousey):
                # allow user to edit the level's height
                boxEdited = "height"
            if startXBox.checkIfClicked(mousex, mousey):
                # allow user to edit the level's starting X coordinate
                boxEdited = "startX"
            if startYBox.checkIfClicked(mousex, mousey):
                # allow user to edit the level's starting Y coordinate
                boxEdited = "startY"
            if numPlayersBox.checkIfClicked(mousex, mousey):
                # allow user to edit the number of players the level is for
                boxEdited = "num players"
            if techMechsBox.checkIfClicked(mousex, mousey):
                # allow user to edit the level's number of Tech Mechs
                boxEdited = "tech mechs"
            if saveRequirementBox.checkIfClicked(mousex, mousey):
                # allow user to edit the level's save requirement
                boxEdited = "save requirement"
            if editorTab.checkIfClicked(mousex, mousey):
                # user clicked editor tab; return to the main part of the editor
                endDetails = True
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

def executeDetailsFrame(SCREEN):
    global textBoxTimer
    
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
    numPlayersLabel.render(SCREEN)
    numPlayersBox.render(SCREEN, textBoxTimer)
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
    return endDetails
