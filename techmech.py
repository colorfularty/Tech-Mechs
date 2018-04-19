import pygame

from skill import *
from constants import *

class TechMech(object):
    # the main characters in the game

    # sprite sheets
    walkerSprites = pygame.image.load("sprites/walker.png").convert_alpha()
    fallerSprites = pygame.image.load("sprites/faller.png").convert_alpha()
    grapplerSprites = pygame.image.load("sprites/grappler.png").convert_alpha()
    drillerSprites = pygame.image.load("sprites/driller.png").convert_alpha()
    jackhammererSprites = pygame.image.load("sprites/jackhammerer.png").convert_alpha()
    cautionerSprites = pygame.image.load("sprites/cautioner.png").convert_alpha()
    detonatorSprites = pygame.image.load("sprites/detonator.png").convert_alpha()

    # sprite sheets for multiplayer
    greenWalkerSprites = pygame.image.load("sprites/walker green.png").convert_alpha()
    greenFallerSprites = pygame.image.load("sprites/faller green.png").convert_alpha()
    greenGrapplerSprites = pygame.image.load("sprites/grappler green.png").convert_alpha()
    greenDrillerSprites = pygame.image.load("sprites/driller green.png").convert_alpha()
    greenJackhammererSprites = pygame.image.load("sprites/jackhammerer green.png").convert_alpha()
    greenCautionerSprites = pygame.image.load("sprites/cautioner green.png").convert_alpha()
    greenDetonatorSprites = pygame.image.load("sprites/detonator green.png").convert_alpha()

    redWalkerSprites = pygame.image.load("sprites/walker red.png").convert_alpha()
    redFallerSprites = pygame.image.load("sprites/faller red.png").convert_alpha()
    redGrapplerSprites = pygame.image.load("sprites/grappler red.png").convert_alpha()
    redDrillerSprites = pygame.image.load("sprites/driller red.png").convert_alpha()
    redJackhammererSprites = pygame.image.load("sprites/jackhammerer red.png").convert_alpha()
    redCautionerSprites = pygame.image.load("sprites/cautioner red.png").convert_alpha()
    redDetonatorSprites = pygame.image.load("sprites/detonator red.png").convert_alpha()

    # list of sprite sheets by player number
    spriteSheets = [{Walker:      walkerSprites,
                    Faller:       fallerSprites,
                    Grappler:     grapplerSprites,
                    Driller:      drillerSprites,
                    Jackhammerer: jackhammererSprites,
                    Cautioner:    cautionerSprites,
                    Detonator:    detonatorSprites},

                    {Walker:       greenWalkerSprites,
                     Faller:       greenFallerSprites,
                     Grappler:     greenGrapplerSprites,
                     Driller:      greenDrillerSprites,
                     Jackhammerer: greenJackhammererSprites,
                     Cautioner:    greenCautionerSprites,
                     Detonator:    greenDetonatorSprites},

                    {Walker:       redWalkerSprites,
                     Faller:       redFallerSprites,
                     Grappler:     redGrapplerSprites,
                     Driller:      redDrillerSprites,
                     Jackhammerer: redJackhammererSprites,
                     Cautioner:    redCautionerSprites,
                     Detonator:    redDetonatorSprites}]
    
    def __init__(self, x, y, owner = 0):
        self.x = x # their x-coordinate relative to the map (trigger area)
        self.y = y # their y-coordinate relative to the map (trigger area)
        self.owner = owner # the player the Tech Mech belongs to
        self.currentSkill = Walker # what the tech mech is currently doing
        self.direction = 1 # this is 1 for right and -1 for left
        self.orientation = 1 # this is 1 for upright, and -1 for upside-down
        self.rotation = 0 # this is 0 for upright, 1 for walking on a right wall, and -1 for walking on a left wall
        self.permanentSkills = [] # a list of all permanent skills assigned to the Tech Mech
        self.skillVector = None # used to store a vector needed for certain skills (i.e. grappling hook)
        self.animationFrame = 0 # the current frame of the Tech Mech's skill animation
        self.soundEffect = None # the sound effect of the skill the Tech Mech is using
        self.setImage(self.currentSkill)

    def setImage(self, newSkill):
        # sets the Tech Mech's current image for the given frame based on its current animation sequence
        self.image = self.spriteSheets[self.owner][newSkill].subsurface((0, self.animationFrame * TECH_MECH_SPRITE_HEIGHT, TECH_MECH_SPRITE_WIDTH, TECH_MECH_SPRITE_HEIGHT))
        self.image = pygame.transform.flip(self.image, self.direction < 0, self.orientation < 0)
        self.image = pygame.transform.rotate(self.image, 90 * self.rotation)

    def wasClicked(self, x, y):
        # returns True if the user clicked on the Tech Mech
        if self.orientation > 0:
            if x >= self.x - TECH_MECH_SPRITE_WIDTH // 2 and x <= self.x + TECH_MECH_SPRITE_WIDTH // 2 and y >= self.y - self.image.get_height() and y <= self.y:
                return True
        else:
            if x >= self.x - TECH_MECH_SPRITE_WIDTH // 2 and x <= self.x + TECH_MECH_SPRITE_WIDTH // 2 and y >= self.y and y <= self.y + self.image.get_height():
                return True
        return False

    def getXCoordinate(self):
        # returns the x-coordinate of the Tech Mech relative to image blitting
        if self.rotation == 1:
            return self.x - 47
        elif self.rotation == -1:
            return self.x
        return self.x - 17

    def getYCoordinate(self):
        # returns the y-coordinate of the Tech Mech relative to image blitting
        if self.rotation != 0:
            return self.y - 17
        if self.orientation == -1:
            return self.y
        return self.y - 47

    def render(self, surf):
        # blit the tech mech's image to the surface
        # the trigger area is 9 pixels left and 47 pixels down from the
        # upper-left corner
        if self.orientation > 0:
            surf.blit(self.image, (self.getXCoordinate(), self.getYCoordinate()))
        else:
            surf.blit(self.image, (self.x - 17, self.y))
        
    def assignSkill(self, newSkill):
        # changes a tech mech's current skill, either because the user gave
        # them a tool, or they walked off a cliff, etc.

        # if this method returns False, the user is refunded the skill they tried to use

        if issubclass(newSkill, PermanentSkill): # checks if the skill is a permanent skill (i.e. Magnet Boots, Energizer, etc.)
            if newSkill == MagnetBoots and self.orientation == -1: # you can't assign Magnet Boots to an upside-down Tech Mech
                return False
            if newSkill in self.permanentSkills: # you can't assign a permanent skill to a Tech Mech who already has that permanent skill
                return False
            self.permanentSkills.append(newSkill) # add the assigned skill to the Tech Mech's list of permanent skills
        elif newSkill == GravityReverser:
            if MagnetBoots in self.permanentSkills: # you can't flip a Tech Mech with Magnet Boots upside-down
                return False
            # flip the Tech Mech upside-down
            self.reverseGravity()
            self.currentSkill = Walker
            self.animationFrame = 0
            self.setImage(Walker)
        else:
            if self.currentSkill == Faller and newSkill != Walker or self.rotation != 0: # you can't assign a skill to a Tech Mech on the wall or free-falling
                return False
            # change the Tech Mech's current skill to the assigned skill
            self.currentSkill = newSkill
            self.animationFrame = 0
            self.setImage(newSkill)
        if self.soundEffect != None: # stop the sound effect the Tech Mech was currently making (if any)
            self.soundEffect.stop()
        if newSkill.soundEffect != None: # start the new skill's sound effect (if any)
            self.soundEffect = pygame.mixer.Sound("sound/" + newSkill.soundEffect + ".wav")
            self.soundEffect.play(newSkill.loops)
        return True

    def turnAround(self):
        self.direction *= -1
        self.image = pygame.transform.flip(self.image, True, False)

    def walkUpWall(self):
        self.rotation = self.direction
        self.image = pygame.transform.rotate(self.image, 90 * self.rotation)

    def walkDownWall(self):
        self.rotation = -self.direction
        self.image = pygame.transform.rotate(self.image, 90 * self.rotation)

    def walkOffWall(self):
        self.image = pygame.transform.rotate(self.image, -90 * self.rotation)
        self.rotation = 0

    def reverseGravity(self):
        self.orientation *= -1
        self.image = pygame.transform.flip(self.image, False, True)

    def act(self, level, savedCounter, player):
        actions = 1
        if Energizer in self.permanentSkills:
            actions = 2
        for i in range(actions):
            self.setImage(self.currentSkill)

            if not self.currentSkill.use(self, level, self.skillVector):
                return False

            # adjust the animation frame
            if self.animationFrame >= ANIMATION_FRAMES[self.currentSkill] - 1:
                self.animationFrame = 0
            else:
                self.animationFrame += 1
                
            # check if tech mech is over a pit
            if MagnetBoots not in self.permanentSkills:
                try:
                    if level.image.get_at((self.x, self.y + self.orientation)) == BLACK and self.currentSkill != Faller:
                        self.assignSkill(Faller)
                except IndexError: # the Tech Mech fell in a bottomless pit
                    return False

            if (self.x, self.y) in level.triggersByType["exit" + str(player)] and Exit.status == "open":
                savedCounter[player] += 1
                return False
            elif (self.x, self.y) in level.triggersByType["water"]:
                return False
            elif (self.x + self.direction, self.y) in level.triggersByType["caution"]:
                self.turnAround()
        return True




















