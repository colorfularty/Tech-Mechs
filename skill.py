import pygame
from constants import *
from gameObject import *

class Skill(object):
    # a skill used by Tech Mechs

    @classmethod
    def use(self):
        pass

class Walker(Skill):
    # makes the Tech Mech walk forward and (if necessary) turn around

    @classmethod
    def use(self, techMech, level):
        # the Tech Mech walks. Returns False if the Tech Mech walks offscreen
        # to its death, and True otherwise
        newXPos = techMech.x + techMech.direction
        # check if the tech mech is about to hit a wall
        try: # checks to make sure there are no index out of bounds errors
            if level.image.get_at((newXPos, techMech.y)) != BLACK:
                # check if the wall is short enough to walk up
                wallHeight = 1
                for i in range(1, 7):
                    if level.image.get_at((newXPos, techMech.y - (i * techMech.orientation))) == BLACK:
                        break
                    wallHeight += 1
                if wallHeight == 7: # the wall was too tall to walk up
                    techMech.turnAround()
                else: # the wall is short enough to walk up
                    techMech.x = newXPos
                    techMech.y -= (wallHeight * techMech.orientation)
            else: # tech mech can move normally
                techMech.x = newXPos
                # check if there is pit short enough to walk down
                pitHeight = 0
                for i in range(1, 7):
                    # check if the pit ends
                    if level.image.get_at((techMech.x, techMech.y + (i * techMech.orientation))) != BLACK:
                        break
                    pitHeight += 1
                # if pit height is less than 6 pixels high, you can walk down it
                if pitHeight < 6:
                    techMech.y += (pitHeight * techMech.orientation)
        except IndexError: # IndexError means the Tech Mech walked off the level
            return False
        return True

class Faller(Skill):
    # makes the Tech Mech fall downward

    @classmethod
    def use(self, techMech, level):
        # the Tech Mech falls 2 pixels
        # returns False if the Tech Mech falls into a bottomless pit

        # fall the first pixel
        techMech.y += techMech.orientation
        try: # ensure there are no IndexErrors
            # check to see if you hit the ground
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
                if level.image.get_at((int(currentX), int(currentY))) != BLACK:
                    return ((startX, techMech.y), (currentX, currentY))
            except IndexError:
                return None
            currentX += unitVec.x
            currentY += unitVec.y
            ropeLength += 1
        return None

    @classmethod
    def use(self, techMech, level):
        # creates a grappling line from your starting position to the first
        # part of the terrain it reachs in the specified direction

        # get start and endpoints of grappling line
        points = self.determineGrapplePoints(techMech, level, unitVec)
        # check if the grappling line can be made
        if points != None:
            startX, startY = points[0]
            endX, endY = points[1]
            pygame.draw.line(level, WHITE, (startX, startY), (endX, endY))
        techMech.assignSkill(Walker)

class Driller(Skill):
    # makes the Tech Mech destroy terrain in a horizontal direction

    @classmethod
    def use(self, techMech, level):
        if techMech.animationFrame % 4 == 0:
            techMech.x += techMech.direction
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
            return False
        return True

class Jackhammerer(Skill):
    # makes the Tech Mech destroy terrain in a downards direction

    @classmethod
    def use(self, techMech, level):
        # The Tech Mech drills into the ground, destroying terrain in the way

        if techMech.animationFrame % 4 == 0:
            # move down 1 pixel, regardless of terrain being there
            techMech.y += techMech.orientation
            # terrain is destroyed by drawing a black polygon in the shape of the
            # jackhammer point. Black pixels are counted as no terrain
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

class GravityReverser(Skill):
    # flips the Tech Mech upside-down
    pass

class Cautioner(Skill):
    # makes the Tech Mech place a Sign which turns Tech Mechs around

    @classmethod
    def use(self, techMech, level):
        cautionSign = CautionSign(techMech.x + techMech.direction, techMech.y, techMech.orientation)
        level.addTechMechObject(cautionSign)
        techMech.assignSkill(Walker)

class Detonator(Skill):
    # makes the Tech Mech place a land mine which blows up terrain after a few seconds

    @classmethod
    def use(self, techMech, level):
        landMine = LandMine(techMech.x, techMech.y, techMech.orientation)
        level.addTechMechObject(landMine)
        techMech.assignSkill(Walker)








    
