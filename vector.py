import math

class Vector(object):
    # an object that represents a 2D vector
    
    def __init__(self, x, y):
        self.x = x # the horizontal distance of the vector
        self.y = y # the vertical distance of the vector

    def getMagnitude(self):
        return math.sqrt(self.x**2 + self.y**2)

    def getAngle(self):
        return math.atan(self.y / self.x)

    def normalize(self):
        magnitude = self.getMagnitude()
        self.x /= magnitude
        self.y /= magnitude
