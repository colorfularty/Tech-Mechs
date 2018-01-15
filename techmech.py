import pygame

BLACK = (0, 0, 0)

class TechMech(object):
    # the main characters in the game
    
    def __init__(self, x, y):
        self.x = x # their x-coordinate relative to the map (trigger area)
        self.y = y # their y-coordinate relative to the map (trigger area)
        self.currentSkill = "walker" # what the tech mech is currently doing
        self.direction = 1 # this is 1 for right and -1 for left
        self.setImage(self.currentSkill)

    def setImage(self, skill):
        self.image = pygame.image.load("sprites/" + skill + ".png").convert()
        self.image.set_colorkey(BLACK)
        if self.direction < 0:
            pygame.transform.flip(self.image, True, False)

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

    def act(self, level):
        if self.currentSkill == "walker":
            newXPos = self.x + self.direction
            # check if the tech mech is about to hit a wall
            try:
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
            except IndexError:
                return False
                
        elif self.currentSkill == "faller":
            self.y += 1
            try:
                if level.get_at((self.x, self.y + 1)) == BLACK:
                    self.y += 1
                    if level.get_at((self.x, self.y + 1)) != BLACK:
                        self.assignSkill("walker")
                else:
                    self.assignSkill("walker")
            except IndexError:
                return False

        elif self.currentSkill == "driller":
            self.x += self.direction
            try:
                pygame.draw.polygon(level, BLACK, ((self.x, self.y), (self.x, self.y - 14), (self.x + 10 * self.direction, self.y - 14), (self.x + 17 * self.direction, self.y - 7), (self.x + 10 * self.direction, self.y)))
            except IndexError:
                pass
            
        # check if tech mech is over a pit
        try:
            if level.get_at((self.x, self.y + 1)) == BLACK:
                self.assignSkill("faller")
        except IndexError:
            return False
        return True




















