#!/usr/bin/python3
'''
This file contains some different iterations of the static logic for coral generation.
'''
import math
import random 

def generic(pt): 
    return pt.y <= 40.48

def middle(pt): 
    return pt.y <= 40.48 and pt.x < -73.98 and pt.x > -74.02

def intervalLogicMaker(nIntervals, everyNSeeded, bounds):

    def intervalLogic(pt): 
        boundRange = abs(bounds[1]-bounds[0])
        increment = boundRange/nIntervals
        currIncrement = math.floor((pt.x-bounds[0])/increment)
        return pt.y <= 40.48 and currIncrement % everyNSeeded == 0

    return intervalLogic

def randomIntervalLogicMaker(nIntervals, bounds, shockSize):

    boundRange = abs(bounds[1]-bounds[0])
    increment = boundRange/(2*nIntervals)
    endpoint = bounds[0]
    seedIntervals = []
    while endpoint < bounds[1]:
        newEndpt = endpoint+increment/5 + random.uniform(-1, 1)*shockSize
        seedIntervals.append([endpoint, newEndpt])
        endpoint = newEndpt + increment + random.uniform(-1,1)*shockSize;

    def randomIntervalLogic(pt): 
        return pt.y <= 40.48 and any([pt.x >= x[0] and pt.x <= x[1] for x in seedIntervals])

    return randomIntervalLogic