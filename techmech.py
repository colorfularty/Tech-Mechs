import pygame
import vector

BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)

class TechMech(object):
    # the main characters in the game
    
    def __init__(self, x, y):
        self.x = x # their x-coordinate relative to the map (trigger area)
        self.y = y # their y-coordinate relative to the map (trigger area)
        self.currentSkill = "walker" # what the tech mech is currently doing
        self.direction = 1 # this is 1 for right and -1 for left
        self.orientation = 1 # this is 1 for upright, and -1 for upside-down
        self.skillVector = None # used to store a vector needed for certain skills (i.e. grappling hook)
        self.setImage(self.currentSkill)

    def setImage(self, skill):
        self.image = pygame.image.load("sprites/" + skill + ".png").convert()
        self.image.set_colorkey(BLACK)
        if self.direction < 0:
            self.image = pygame.transform.flip(self.image, True, False)

    def wasClicked(self, x, y):
        if x >= self.x - 17 and x <= self.x + 17 and y >= self.y - self.image.get_height() and y <= self.y:
            return True
        return False

    def render(self, surf):
        # blit the tech mech's image to the surface
        # the trigger area is 9 pixels left and 47 pixels down from the
        # upper-left corner
        surf.blit(self.image, (self.x - 17, self.y - 47))
        
    def assignSkill(self, skill):
        # changes a tech mech's current skill, either because the user gave
        # them a tool, or they walked off a cliff, etc.
        self.currentSkill = skill
        self.setImage(skill)

    def turnAround(self):
        self.direction *= -1
        self.image = pygame.transform.flip(self.image, True, False)

    def walk(self, level):
        # the Tech Mech walks. Returns False if the Tech Mech walks offscreen
        # to its death, and True otherwise
        newXPos = self.x + self.direction
        # check if the tech mech is about to hit a wall
        try: # checks to make sure there are no index out of bounds errors
            if level.get_at((newXPos, self.y)) != BLACK:
                # check if the wall is short enough to walk up
                wallHeight = 1
                for i in range(1, 7):
                    if level.get_at((newXPos, self.y - i)) == BLACK:
                        break
                    wallHeight += 1
                if wallHeight == 7: # the wall was too tall to walk up
                    self.turnAround()
                else: # the wall is short enough to walk up
                    self.x = newXPos
                    self.y -= wallHeight
            else: # tech mech can move normally
                self.x = newXPos
                # check if there is pit short enough to walk down
                pitHeight = 0
                for i in range(1, 7):
                    # check if the pit ends
                    if level.get_at((self.x, self.y + i)) != BLACK:
                        break
                    pitHeight += 1
                # if pit height is less than 6 pixels high, you can walk down it
                if pitHeight < 6:
                    self.y += pitHeight
        except IndexError: # IndexError means the Tech Mech walked off the level
            return False
        return True

    def fall(self, level):
        # the Tech Mech falls 2 pixels
        # returns False if the Tech Mech falls into a bottomless pit

        # fall the first pixel
        self.y += 1
        try: # ensure there are no IndexErrors
            # check to see if you hit the ground
            if level.get_at((self.x, self.y + 1)) == BLACK:
                # you didn't hit the ground; fall another pixel
                self.y += 1
                # check if you hit the ground now
                if level.get_at((self.x, self.y + 1)) != BLACK:
                    # you hit the ground; make the Tech Mech a walker
                    self.assignSkill("walker")
            else: # you hit the ground; make the Tech Mech a walker
                self.assignSkill("walker")
        except IndexError: # IndexError means Tech Mech fell into a bottomless pit
            return False
        return True

    def drill(self, level):
        self.x += self.direction
        pygame.draw.polygon(level, BLACK, ((self.x, self.y), (self.x, self.y - 14), (self.x + 10 * self.direction, self.y - 14), (self.x + 17 * self.direction, self.y - 7), (self.x + 10 * self.direction, self.y)))

    def jackhammer(self, level):
        # The Tech Mech drills into the ground, destroying terrain in the way

        # move down 1 pixel, regardless of terrain being there
        self.y += 1
        # terrain is destroyed by drawing a black polygon in the shape of the
        # jackhammer point. Black pixels are counted as no terrain
        pygame.draw.polygon(level, BLACK, ((self.x, self.y), (self.x - 1, self.y - 3), (self.x - 2, self.y - 6), (self.x - 3, self.y - 8), (self.x - 4, self.y - 10), (self.x - 5, self.y - 15), (self.x + 5, self.y - 15), (self.x + 4, self.y - 10), (self.x + 3, self.y - 8), (self.x + 2, self.y - 6), (self.x + 1, self.y - 3)))

    def determineGrapplePoints(self, level, unitVec):
        # returns the start and end points if the Tech Mech is able to grapple in the specified direction
        # returns None if the grappling hook goes out of bounds or is too short to hit terrain

        ropeLength = 0 # the amount of rope currently used
        # depending on the direction, the rope will either be 1 pixel in front
        # or behind the tech mech
        if unitVec.x < 0:
            startX = self.x - 1
        else:
            startX = self.x + 1

        # currentX and currentY are the locations of the end of the rope
        currentX = startX
        currentY = self.y

        # loop through the rope length, extending by 1 pixel each iteration
        while ropeLength < 150:
            # the try-catch checks if the rope moves out of bounds
            try:
                # check if the rope hits solid terrain
                if level.get_at((int(currentX), int(currentY))) != BLACK:
                    return ((startX, self.y), (currentX, currentY))
            except IndexError:
                return None
            currentX += unitVec.x
            currentY += unitVec.y
            ropeLength += 1
        return None

    def grapple(self, level, unitVec):
        # creates a grappling line from your starting position to the first
        # part of the terrain it reachs in the specified direction

        # get start and endpoints of grappling line
        points = self.determineGrapplePoints(level, unitVec)
        # check if the grappling line can be made
        if points != None:
            startX, startY = points[0]
            endX, endY = points[1]
            pygame.draw.line(level, WHITE, (startX, startY), (endX, endY))
        self.assignSkill("walker")

    def act(self, level):
        if self.currentSkill == "walker":
            if not self.walk(level):
                return False
                
        elif self.currentSkill == "faller":
            if not self.fall(level):
                return False

        elif self.currentSkill == "driller":
            self.drill(level)

        elif self.currentSkill == "jackhammerer":
            self.jackhammer(level)

        elif self.currentSkill == "grappler":
            self.grapple(level, self.skillVector)
            
        # check if tech mech is over a pit
        try:
            if level.get_at((self.x, self.y + 1)) == BLACK:
                self.assignSkill("faller")
        except IndexError: # the Tech Mech fell in a bottomless pit
            return False
        return True




















