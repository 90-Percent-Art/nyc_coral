'''This file contains some different iterations of the static logic.'''
import math

def generic(pt): 
    return pt.y <= 40.48

def middle(pt): 
    return pt.y <= 40.48 and pt.x < -73.98 and pt.x > -74.02

def fancyEvanMaker(nIntervals, everyNSeeded, bounds):

    def fancyEvanLogic(pt): 
        boundRange = abs(bounds[1]-bounds[0])
        increment = boundRange/nIntervals
        currIncrement = math.floor((pt.x-bounds[0])/increment)
        return pt.y <= 40.48 and currIncrement % everyNSeeded == 0

    return fancyEvanLogic