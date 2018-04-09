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
    print(levelInProgress.releaseRates)
    renderSkillPanel(skillPanel, levelInProgress, levelInProgress.releaseRates, playerSelected)

def handleSkillsEvents(levelInProgress):
    # handle the user interactions with the skills screen
    
    global endSkills, mousex, mousey, playerSelected
    
    for event in pygame.event.get():
        if event.type == MOUSEMOTION:
            # update the mouse cursor coordinates
            mousex, mousey = event.pos
        elif event.type == MOUSEBUTTONDOWN:
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
            elif grapplersUp.checkIfClicked(mousex, mousey):
                # increase the amount of grapplers if possible
                if levelInProgress.skillCounts[playerSelected][Grappler] < 99:
                    levelInProgress.skillCounts[playerSelected][Grappler] += 1
            elif grapplersDown.checkIfClicked(mousex, mousey):
                # decrease the amount of grapplers if possible
                if levelInProgress.skillCounts[playerSelected][Grappler] > 0:
                    levelInProgress.skillCounts[playerSelected][Grappler] -= 1
            elif drillersUp.checkIfClicked(mousex, mousey):
                # increase the amount of drillers if possible
                if levelInProgress.skillCounts[playerSelected][Driller] < 99:
                    levelInProgress.skillCounts[playerSelected][Driller] += 1
            elif drillersDown.checkIfClicked(mousex, mousey):
                # decrease the amount of drillers if possible
                if levelInProgress.skillCounts[playerSelected][Driller] > 0:
                    levelInProgress.skillCounts[playerSelected][Driller] -= 1
            elif jackhammerersUp.checkIfClicked(mousex, mousey):
                # increase the amount of jackhammerers if possible
                if levelInProgress.skillCounts[playerSelected][Jackhammerer] < 99:
                    levelInProgress.skillCounts[playerSelected][Jackhammerer] += 1
            elif jackhammerersDown.checkIfClicked(mousex, mousey):
                # decrease the amount of jackhammerers if possible
                if levelInProgress.skillCounts[playerSelected][Jackhammerer] > 0:
                    levelInProgress.skillCounts[playerSelected][Jackhammerer] -= 1
            elif gravityReversersUp.checkIfClicked(mousex, mousey):
                # increase the amount of gravity reversers if possible
                if levelInProgress.skillCounts[playerSelected][GravityReverser] < 99:
                    levelInProgress.skillCounts[playerSelected][GravityReverser] += 1
            elif gravityReversersDown.checkIfClicked(mousex, mousey):
                # decrease the amount of gravity reversers if possible
                if levelInProgress.skillCounts[playerSelected][GravityReverser] > 0:
                    levelInProgress.skillCounts[playerSelected][GravityReverser] -= 1
            elif cautionersUp.checkIfClicked(mousex, mousey):
                # increase the amount of cautioners if possible
                if levelInProgress.skillCounts[playerSelected][Cautioner] < 99:
                    levelInProgress.skillCounts[playerSelected][Cautioner] += 1
            elif cautionersDown.checkIfClicked(mousex, mousey):
                # decrease the amount of cautioners if possible
                if levelInProgress.skillCounts[playerSelected][Cautioner] > 0:
                    levelInProgress.skillCounts[playerSelected][Cautioner] -= 1
            elif detonatorsUp.checkIfClicked(mousex, mousey):
                # increase the amount of detonators if possible
                if levelInProgress.skillCounts[playerSelected][Detonator] < 99:
                    levelInProgress.skillCounts[playerSelected][Detonator] += 1
            elif detonatorsDown.checkIfClicked(mousex, mousey):
                # decrease the amount of detonators if possible
                if levelInProgress.skillCounts[playerSelected][Detonator] > 0:
                    levelInProgress.skillCounts[playerSelected][Detonator] -= 1
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

    return endSkills
