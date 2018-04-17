import pygame, os
from pygame.locals import *
from game import renderSkillPanel
from constants import *
from widgets import *

editorTab = Button(0, 0, "<-Editor")
playerLabel = Label(0, 100, "Green player")
playerLeft = Button(100, 100, "<")
playerRight = Button(1000, 100, ">")

# buttons for changing skill counts
releaseRateUp = Button(20, 250, "^")
releaseRateDown = Button(20, 410, "v")
upButtons = []
downButtons = []
for i in range(len(SKILLS)):
    upButtons.append(Button(70 + i * 50, 250, "^"))
    downButtons.append(Button(70 + i * 50, 410, "v"))

# the skill panel displayed in the skills section
skillPanel = pygame.surface.Surface((SKILL_PANEL_WIDTH * NUMBER_OF_SKILL_PANELS, SKILL_PANEL_HEIGHT))
skillFont = pygame.font.SysFont("helvetica", 32)
skillSlot = pygame.image.load("sprites/skill panel.png")

# keeps track of the x and y coordinates of the mouse cursor
mousex = 0
mousey = 0

endSkills = False
numPlayers = 0
playerSelected = 0

def startEditorSkills(levelInProgress):
    global endSkills, numPlayers, playerSelected

    endSkills = False
    numPlayers = levelInProgress.numPlayers
    playerSelected = 0
    playerLabel.changeText("Green player")
    playerLabel.x = SCREEN_WIDTH // 2 - playerLabel.width // 2
    renderSkillPanel(skillPanel, levelInProgress, levelInProgress.releaseRates, playerSelected)

def handleSkillsEvents(levelInProgress):
    # handle the user interactions with the skills screen
    
    global endSkills, mousex, mousey, playerSelected
    
    for event in pygame.event.get():
        if event.type == MOUSEMOTION:
            # update the mouse cursor coordinates
            mousex, mousey = event.pos
        elif event.type == MOUSEBUTTONDOWN:
            for i in range(len(upButtons)):
                if upButtons[i].checkIfClicked(mousex, mousey):
                    if levelInProgress.skillCounts[playerSelected][SKILLS[i]] < 99:
                        levelInProgress.skillCounts[playerSelected][SKILLS[i]] += 1
                        break
                elif downButtons[i].checkIfClicked(mousex, mousey):
                    if levelInProgress.skillCounts[playerSelected][SKILLS[i]] > 0:
                        levelInProgress.skillCounts[playerSelected][SKILLS[i]] -= 1
                        break
            if editorTab.checkIfClicked(mousex, mousey):
                # user clicked editor button; go back to the main editor screen
                endSkills = True
            elif playerLeft.checkIfClicked(mousex, mousey) and numPlayers > 1:
                # user clicked previous player; change the skill panel to the one belonging to the previous player
                playerSelected = not playerSelected
            elif playerRight.checkIfClicked(mousex, mousey) and numPlayers > 1:
                # user clicked next player; change the skill panel to the one belonging to the next player
                playerSelected = not playerSelected
            elif releaseRateUp.checkIfClicked(mousex, mousey):
                # increase the level's minimum release rate if possible
                if levelInProgress.releaseRates[playerSelected] < 99:
                    levelInProgress.releaseRates[playerSelected] += 1
            elif releaseRateDown.checkIfClicked(mousex, mousey):
                # decrease the level's minimum release rate if possible
                if levelInProgress.releaseRates[playerSelected] > 1:
                    levelInProgress.releaseRates[playerSelected] -= 1
            renderSkillPanel(skillPanel, levelInProgress, levelInProgress.releaseRates, playerSelected)
        elif event.type == QUIT: # terminate program; all progress will be lost
            pygame.quit()
            os._exit(0)

def executeEditorSkillsFrame(SCREEN, levelInProgress):
    handleSkillsEvents(levelInProgress) # handle user interactions

    # update the screen
    SCREEN.fill(GREY)
    SCREEN.blit(skillPanel, (0, 300))
    editorTab.render(SCREEN)
    if numPlayers > 1:
        if playerSelected == 0:
            playerLabel.changeText("Green player")
        else:
            playerLabel.changeText("Red player")
        playerLabel.render(SCREEN)
        playerLeft.render(SCREEN)
        playerRight.render(SCREEN)
    releaseRateUp.render(SCREEN)
    releaseRateDown.render(SCREEN)
    for i in range(len(upButtons)):
        upButtons[i].render(SCREEN)
        downButtons[i].render(SCREEN)
    
    pygame.display.update()
    CLOCK.tick(FPS)

    return endSkills
