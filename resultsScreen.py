import pygame, os
from pygame.locals import *
from constants import *
from widgets import Label

continueResults = True
savedText = None
requiredText = None
finalText = None
clickText = Label(0, SCREEN_HEIGHT - 50, "Click anywhere to go back to the main menu.")

def startResultsScreen(techMechsSaved, saveRequirement):
    global continueResults, savedText, requiredText, finalText

    continueResults = True
    savedText = Label(0, 0, "You saved " + str(techMechsSaved) + " Tech Mechs.")
    requiredText = Label(0, 50, "You needed " + str(saveRequirement) + " Tech Mechs.")
    if techMechsSaved >= saveRequirement:
        finalText = Label(0, 100, "Congratulations! You beat the level!")
    else:
        finalText = Label(0, 100, "Too bad! You didn't save enough.")

def handleResultsScreenEvents():
    global continueResults
    
    for event in pygame.event.get():
        if event.type == MOUSEBUTTONDOWN:
            continueResults = False
        elif event.type == QUIT:
            pygame.quit()
            os._exit(0)

def executeResultsScreenFrame(SCREEN):
    handleResultsScreenEvents()
    SCREEN.fill(BLACK)
    savedText.render(SCREEN)
    requiredText.render(SCREEN)
    finalText.render(SCREEN)
    clickText.render(SCREEN)
    pygame.display.update()
    CLOCK.tick(FPS)
    return continueResults
