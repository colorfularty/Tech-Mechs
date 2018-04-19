import pygame, os
from pygame.locals import *
from threading import Thread
from constants import *
from widgets import Label

dataSent = False # the variable returned to main.py; if False, stop the wait screen
text = Label(0, 0, "") # the text displayed to the user

def startWaitScreen(conn, newText):
    global dataSent

    dataSent = False
    text.changeText(newText)
    text.x = SCREEN_WIDTH // 2 - text.width // 2
    Thread(target = receiveData, args = (conn,)).start()

def receiveData(conn):
    global dataSent

    dataSent = conn.receiveString()

def handleWaitEvents():
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            os._exit(0)

def executeWaitScreenFrame(SCREEN):
    handleWaitEvents()
    SCREEN.fill(BLACK)
    text.render(SCREEN)
    pygame.display.update()
    CLOCK.tick(FPS)
    return dataSent
