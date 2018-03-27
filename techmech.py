import pygame

from skill import *
from constants import *

class TechMech(object):
    # the main characters in the game

    # sprite sheets
    walkerSprites = pygame.image.load("sprites/walker.png").convert()
    fallerSprites = pygame.image.load("sprites/faller.png").convert()
    grapplerSprites = pygame.image.load("sprites/grappler.png").convert()
    drillerSprites = pygame.image.load("sprites/driller.png").convert()
    jackhammererSprites = pygame.image.load("sprites/jackhammerer.png").convert()
    cautionerSprites = pygame.image.load("sprites/cautioner.png").convert()
    detonatorSprites = pygame.image.load("sprites/detonator.png").convert()

    walkerSprites.set_colorkey(BLACK)
    fallerSprites.set_colorkey(BLACK)
    grapplerSprites.set_colorkey(BLACK)
    drillerSprites.set_colorkey(BLACK)
    jackhammererSprites.set_colorkey(BLACK)
    cautionerSprites.set_colorkey(BLACK)
    detonatorSprites.set_colorkey(BLACK)

    spriteSheets = {Walker:       walkerSprites,
                    Faller:       fallerSprites,
                    Grappler:     grapplerSprites,
                    Driller:      drillerSprites,
                    Jackhammerer: jackhammererSprites,
                    Cautioner: cautionerSprites,
                    Detonator: detonatorSprites}
    
    def __init__(self, x, y):
        self.x = x # their x-coordinate relative to the map (trigger area)
        self.y = y # their y-coordinate relative to the map (trigger area)
        self.currentSkill = Walker # what the tech mech is currently doing
        self.direction = 1 # this is 1 for right and -1 for left
        self.orientation = 1 # this is 1 for upright, and -1 for upside-down
        self.skillVector = None # used to store a vector needed for certain skills (i.e. grappling hook)
        self.animationFrame = 0
        self.setImage(self.currentSkill)

    def setImage(self, newSkill):
        self.image = self.spriteSheets[newSkill].subsurface((0, self.animationFrame * TECH_MECH_SPRITE_HEIGHT, TECH_MECH_SPRITE_WIDTH, TECH_MECH_SPRITE_HEIGHT))
        self.image = pygame.transform.flip(self.image, self.direction < 0, self.orientation < 0)

    def wasClicked(self, x, y):
        if self.orientation > 0:
            if x >= self.x - TECH_MECH_SPRITE_WIDTH // 2 and x <= self.x + TECH_MECH_SPRITE_WIDTH // 2 and y >= self.y - self.image.get_height() and y <= self.y:
                return True
        else:
            if x >= self.x - TECH_MECH_SPRITE_WIDTH // 2 and x <= self.x + TECH_MECH_SPRITE_WIDTH // 2 and y >= self.y and y <= self.y + self.image.get_height():
                return True
        return False

    def render(self, surf):
        # blit the tech mech's image to the surface
        # the trigger area is 9 pixels left and 47 pixels down from the
        # upper-left corner
        if self.orientation > 0:
            surf.blit(self.image, (self.x - 17, self.y - 47))
        else:
            surf.blit(self.image, (self.x - 17, self.y))
        
    def assignSkill(self, newSkill):
        # changes a tech mech's current skill, either because the user gave
        # them a tool, or they walked off a cliff, etc.
        if newSkill == GravityReverser:
            self.reverseGravity()
            self.currentSkill = Walker
            self.animationFrame = 0
            self.setImage(Walker)
        else:
            self.currentSkill = newSkill
            self.animationFrame = 0
            self.setImage(newSkill)

    def turnAround(self):
        self.direction *= -1
        self.image = pygame.transform.flip(self.image, True, False)

    def reverseGravity(self):
        self.orientation *= -1
        self.image = pygame.transform.flip(self.image, False, True)

    def act(self, level):
        self.setImage(self.currentSkill)

        if not self.currentSkill.use(self, level, self.skillVector):
            return False

        # adjust the animation frame
        if self.animationFrame >= ANIMATION_FRAMES[self.currentSkill] - 1:
            self.animationFrame = 0
        else:
            self.animationFrame += 1
            
        # check if tech mech is over a pit
        try:
            if level.image.get_at((self.x, self.y + self.orientation)) == BLACK and self.currentSkill != Faller:
                self.assignSkill(Faller)
        except IndexError: # the Tech Mech fell in a bottomless pit
            return False
        return True




















