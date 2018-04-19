import pygame
from gameObject import *

class Skill(object):
    # a skill used by Tech Mechs

    soundEffect = None # the sound effect that plays while the skill is being used
    loops = 0 # the number of times to loop the sound effect; -1 means play endlessly

    @classmethod
    def use(self):
        # this method is called to make a Tech Mech perform a given task
        pass

class Walker(Skill):
    # makes the Tech Mech walk forward and (if necessary) turn around

    @classmethod
    def use(self, techMech, level, unitVec):
        # the Tech Mech walks. Returns False if the Tech Mech walks offscreen
        # to its death, and True otherwise
        if techMech.rotation == 0: # the Tech Mech is walking on the floor (or ceiling)
            newXPos = techMech.x + techMech.direction
            # check if the tech mech is about to hit a wall
            try: # checks to make sure there are no index out of bounds errors
                from constants import BLACK
                if level.image.get_at((newXPos, techMech.y)) != BLACK:
                    # check if the wall is short enough to walk up
                    wallHeight = 1
                    for i in range(1, 11):
                        if level.image.get_at((newXPos, techMech.y - (i * techMech.orientation))) == BLACK:
                            break
                        wallHeight += 1
                    if wallHeight == 11: # the wall was too tall to walk up
                        if MagnetBoots in techMech.permanentSkills:
                            techMech.walkUpWall()
                        else:
                            techMech.turnAround()
                    else: # the wall is short enough to walk up
                        techMech.x = newXPos
                        techMech.y -= (wallHeight * techMech.orientation)
                else: # tech mech can move normally
                    techMech.x = newXPos
                    # check if there is pit short enough to walk down
                    pitHeight = 0
                    for i in range(1, 11):
                        # check if the pit ends
                        if level.image.get_at((techMech.x, techMech.y + (i * techMech.orientation))) != BLACK:
                            break
                        pitHeight += 1
                    # if pit height is less than 10 pixels high, you can walk down it
                    if pitHeight < 10:
                        techMech.y += (pitHeight * techMech.orientation)
                    elif MagnetBoots in techMech.permanentSkills:
                        techMech.y += 1
                        techMech.walkDownWall()
            except IndexError: # IndexError means the Tech Mech walked off the level
                return False
        elif techMech.rotation == 1: # the tech mechs is walking on a right wall
            newYPos = techMech.y - techMech.direction * techMech.orientation
            # check if the Tech Mech is about to hit the floor/ceiling
            try: # ensures if the Tech Mech causes an OutOfBoundsError, he will die rather than crash the game
                from constants import BLACK
                if level.image.get_at((techMech.x, newYPos)) != BLACK:
                    # check if the ceiling/floor is short enough to walk up
                    wallHeight = 1
                    for i in range(1, 11):
                        if level.image.get_at((techMech.x - i, newYPos)) == BLACK: # end of the floor/ceiling
                            break
                        wallHeight += 1
                    if wallHeight == 11: # the floor/ceiling was too high to walk up
                        if techMech.direction == -1: # if the Tech Mech is facing left, he hit the floor; walk off the wall
                            techMech.walkOffWall()
                        else: # the Tech Mech hit the ceiling; turn around
                            techMech.turnAround()
                    else: # the floor/ceiling was short enough to walk up
                        techMech.x -= wallHeight
                        techMech.y = newYPos
                else:
                    techMech.y = newYPos
                    # check to see in the Tech Mech is no longer standing on the wall
                    pitHeight = 0
                    for i in range(1, 11):
                        if level.image.get_at((techMech.x + i, techMech.y)) != BLACK: # it is a small dent in the wall; the Tech Mech can walk down it
                            break
                        pitHeight += 1
                    if pitHeight < 10: # it is just a small dent in the wall; walk down it
                        techMech.x += pitHeight
                    elif techMech.direction == 1: # the Tech Mech reached the top of the wall; walk up to the new floor
                        techMech.x += 1
                        techMech.walkOffWall()
                    else: # the Tech Mech walked off the bottom of the wall; proceed to fall down to the floor
                        techMech.walkOffWall()
                        techMech.assignSkill(Faller)
            except IndexError:
                return False
        else: # the Tech Mech is walking on a left wall
            newYPos = techMech.y + techMech.direction * techMech.orientation
            # check if the Tech Mech is about to hit the floor/ceiling
            try: # ensures if the Tech Mech causes an OutOfBoundsError, he will die rather than crash the game
                from constants import BLACK
                if level.image.get_at((techMech.x, newYPos)) != BLACK:
                    # check if the ceiling/floor is short enough to walk up
                    wallHeight = 1
                    for i in range(1, 11):
                        if level.image.get_at((techMech.x + i, newYPos)) == BLACK: # end of the floor/ceiling
                            break
                        wallHeight += 1
                    if wallHeight == 11: # the floor/ceiling was too high to walk up
                        if techMech.direction == 1: # if the Tech Mech is facing left, he hit the floor; walk off the wall
                            techMech.walkOffWall()
                        else: # the Tech Mech hit the ceiling; turn around
                            techMech.turnAround()
                    else: # the floor/ceiling was short enough to walk up
                        techMech.x += wallHeight
                        techMech.y = newYPos
                else:
                    techMech.y = newYPos
                    # check to see in the Tech Mech is no longer standing on the wall
                    pitHeight = 0
                    for i in range(1, 11):
                        if level.image.get_at((techMech.x - i, techMech.y)) != BLACK: # it is a small dent in the wall; the Tech Mech can walk down it
                            break
                        pitHeight += 1
                    if pitHeight < 10: # it is just a small dent in the wall; walk down it
                        techMech.x -= pitHeight
                    elif techMech.direction == -1: # the Tech Mech reached the top of the wall; walk up to the new floor
                        techMech.x -= 1
                        techMech.walkOffWall()
                    else: # the Tech Mech walked off the bottom of the wall; proceed to fall down to the floor
                        techMech.walkOffWall()
                        techMech.assignSkill(Faller)
            except IndexError:
                return False
        return True

class Faller(Skill):
    # makes the Tech Mech fall downward

    @classmethod
    def use(self, techMech, level, unitVec):
        # the Tech Mech falls 2 pixels
        # returns False if the Tech Mech falls into a bottomless pit

        # fall the first pixel
        techMech.y += techMech.orientation
        try: # ensure there are no IndexErrors
            # check to see if you hit the ground
            from constants import BLACK
            if level.image.get_at((techMech.x, techMech.y + techMech.orientation)) == BLACK:
                # you didn't hit the ground; fall another pixel
                techMech.y += techMech.orientation
                # check if you hit the ground now
                if level.image.get_at((techMech.x, techMech.y + techMech.orientation)) != BLACK:
                    # you hit the ground; make the Tech Mech a walker
                    techMech.assignSkill(Walker)
            else: # you hit the ground; make the Tech Mech a walker
                techMech.assignSkill(Walker)
        except IndexError: # IndexError means Tech Mech fell into a bottomless pit
            return False
        return True        

class Grappler(Skill):
    # allows a Tech Mech to grapple to a specific point, quickly creating a rope there

    soundEffect = "release grappling hook"

    @classmethod
    def determineGrapplePoints(self, techMech, level, unitVec):
        # returns the start and end points if the Tech Mech is able to grapple in the specified direction
        # returns None if the grappling hook goes out of bounds or is too short to hit terrain

        ropeLength = 0 # the amount of rope currently used
        # depending on the direction, the rope will either be 1 pixel in front
        # or behind the tech mech
        if unitVec.x < 0:
            startX = techMech.x - 1
        else:
            startX = techMech.x + 1

        # currentX and currentY are the locations of the end of the rope
        currentX = startX
        currentY = techMech.y

        # loop through the rope length, extending by 1 pixel each iteration
        while ropeLength < 150:
            # the try-catch checks if the rope moves out of bounds
            try:
                # check if the rope hits solid terrain
                from constants import BLACK
                if level.image.get_at((int(currentX), int(currentY))) != BLACK:
                    return ((startX, techMech.y), (currentX, currentY))
            except IndexError:
                return None
            currentX += unitVec.x
            currentY += unitVec.y
            ropeLength += 1
        return None

    @classmethod
    def use(self, techMech, level, unitVec):
        # creates a grappling line from your starting position to the first
        # part of the terrain it reachs in the specified direction

        # get start and endpoints of grappling line
        points = self.determineGrapplePoints(techMech, level, unitVec)
        # check if the grappling line can be made
        if points != None:
            startX, startY = points[0]
            endX, endY = points[1]
            from constants import WHITE
            pygame.draw.line(level.image, WHITE, (startX, startY), (endX, endY))
        techMech.assignSkill(Walker)
        return True

class Driller(Skill):
    # makes the Tech Mech destroy terrain in a horizontal direction

    soundEffect = "drill"
    loops = -1

    @classmethod
    def use(self, techMech, level, unitVec):
        if techMech.animationFrame % 4 == 0:
            techMech.x += techMech.direction
            from constants import BLACK
            pygame.draw.polygon(level.image, BLACK, (
                (techMech.x, techMech.y),
                (techMech.x, techMech.y - techMech.orientation * 14),
                (techMech.x + 10 * techMech.direction, techMech.y - techMech.orientation * 14),
                (techMech.x + 17 * techMech.direction, techMech.y - techMech.orientation * 7),
                (techMech.x + 10 * techMech.direction, techMech.y)))
            # check if there is enough terrain in front of you to keep drilling
            for i in range(1, 7):
                try:
                    if level.image.get_at((techMech.x + techMech.direction * (i + 17), techMech.y - 7)) != BLACK:
                        return True
                except IndexError:
                    break
            techMech.assignSkill(Walker)
        return True

class Jackhammerer(Skill):
    # makes the Tech Mech destroy terrain in a downards direction

    soundEffect = "jackhammer"
    loops = -1

    @classmethod
    def use(self, techMech, level, unitVec):
        # The Tech Mech drills into the ground, destroying terrain in the way

        if techMech.animationFrame % 4 == 0:
            # move down 1 pixel, regardless of terrain being there
            techMech.y += techMech.orientation
            # terrain is destroyed by drawing a black polygon in the shape of the
            # jackhammer point. Black pixels are counted as no terrain
            from constants import BLACK
            pygame.draw.polygon(level.image, BLACK, (
                (techMech.x, techMech.y),
                (techMech.x - 1, techMech.y - techMech.orientation * 3),
                (techMech.x - 2, techMech.y - techMech.orientation * 6),
                (techMech.x - 3, techMech.y - techMech.orientation * 8),
                (techMech.x - 4, techMech.y - techMech.orientation * 10),
                (techMech.x - 5, techMech.y - techMech.orientation * 15),
                (techMech.x + 5, techMech.y - techMech.orientation * 15),
                (techMech.x + 4, techMech.y - techMech.orientation * 10),
                (techMech.x + 3, techMech.y - techMech.orientation * 8),
                (techMech.x + 2, techMech.y - techMech.orientation * 6),
                (techMech.x + 1, techMech.y - techMech.orientation * 3)))
        return True

class GravityReverser(Skill):
    # flips the Tech Mech upside-down
    pass

class Cautioner(Skill):
    # makes the Tech Mech place a Sign which turns Tech Mechs around

    soundEffect = "place caution sign"

    @classmethod
    def use(self, techMech, level, unitVec):
        cautionSign = CautionSign(techMech.x + techMech.direction, techMech.y, techMech.orientation)
        level.addTechMechObject(cautionSign)
        techMech.assignSkill(Walker)
        return True

class Detonator(Skill):
    # makes the Tech Mech place a land mine which blows up terrain after a few seconds

    @classmethod
    def use(self, techMech, level, unitVec):
        landMine = LandMine(techMech.x, techMech.y, techMech.orientation)
        level.addTechMechObject(landMine)
        techMech.assignSkill(Walker)
        return True

class PermanentSkill(Skill):
    # a skill that permanently affects a Tech Mech's behavior

    pass

class Energizer(PermanentSkill):
    # makes a Tech Mech move and act twice as fast

    pass

class MagnetBoots(PermanentSkill):
    # lets a Tech Mech walk on walls

    pass
