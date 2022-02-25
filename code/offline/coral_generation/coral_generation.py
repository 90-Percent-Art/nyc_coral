'''This script generates the coral positions'''

# Setup
import geojson
import json
import sys 
import time
import math
import timeit
import logging
from random import gauss
from scipy.spatial import KDTree
from staticLogics import fancyEvanMaker

class Point:
    def __init__(self, xy, bounds, properties):
        self.initial = xy  # doesn't change
        self.final = xy
        self.x = xy[0]
        self.y = xy[1]
        self.bounds = bounds
        self.properties = properties  # demo information etc.
        self.static = False

    def update(self, magnitude, ydrift):
        self.shock(magnitude, ydrift)
        self.wrap(self.bounds[0], self.bounds[1],
                   self.bounds[2], self.bounds[3])

    def shock(self, magnitude, ydrift):
        self.x += gauss(0, magnitude)
        self.y += gauss(0, magnitude)-ydrift

    def makeStatic(self):
        '''Make the point static and set its final position'''
        self.static = True
        self.final = [self.x, self.y]

    def clamp(self, minX, maxX, minY, maxY):
        self.x = min(max(self.x, minX), maxX)
        self.y = min(max(self.y, minY), maxY)
    
    def wrap(self, minX, maxX, minY, maxY):
        '''If the point is outside the bounds, wrap it around to the opposite edge'''
        if self.x < minX:
            self.x = maxX
        elif self.x > maxX:
            self.x = minX
        if self.y < minY:
            self.y = maxY
        elif self.y > maxY:
            self.y = minY

    def __str__(self):
        return 'Point({0}, {1})'.format(self.x, self.y)


class CoralSimulation:

    def __init__(
        self, pointFeatureList, staticConditionLogic, 
        shocksd=0.003, ydrift = 0.003/6, radius=0.002, 
        sea_floor_level=40.48, bounds=[-74.27, -73.6, 40.48, 40.94], 
        maxIter=30000, allowedUnconvergedPoints=100
    ):

        # simulation parameters
        self.shocksd = shocksd
        self.ydrift = ydrift
        self.radius = radius
        self.sea_floor_level = sea_floor_level
        self.bounds = bounds
        self.maxIter = maxIter
        self.allowedUnconvergedPoints = allowedUnconvergedPoints
        self.staticCondtionLogic = staticConditionLogic

        # Initialization 
        self.points = []
        self.tree = None

        # Add points and update static
        self.addNewActivePointsFromFeatureList(pointFeatureList)
        logging.info("Initialized all the simulation data")

    def addNewActivePointsFromFeatureList(self, pointFeatureList):
        '''
        This function adds the points in the pointFeatureList to the simulation as new active points. 

        pointFeatureList: a list of geojson point features with a geometry.coordinates field and a properties field
        '''
        self.points = self.points + \
            [Point(x['geometry']['coordinates'], self.bounds, x['properties'])
             for x in pointFeatureList]
        self.updateStatic()

    def updateStatic(self):
        self.active_points = [
            point for point in self.points if not point.static]
        self.static_points = [point for point in self.points if point.static]

        if self.static_points:
            self.tree = KDTree([(p.x, p.y) for p in self.static_points])

    def pointMeetsStaticConditions(self, point):
        return self.staticCondtionLogic(point)

    def iterate(self):
        for point in self.active_points:
            point.update(self.shocksd, self.ydrift)
            if self.pointMeetsStaticConditions(point):
                point.makeStatic()
            if self.tree:
                neighbors = self.tree.query_ball_point(
                    (point.x, point.y), self.radius)
                if neighbors:
                    point.makeStatic()

        self.updateStatic()

    def run(self):
        '''
        Run the simulation until the maximum number of iterations is reached or all points are static.
        '''
        logging.info("Starting the simulation")
        iters = 0
        start = timeit.default_timer()
        while iters < self.maxIter and len(self.active_points) > 100:
            self.iterate()
            iters += 1
            curr = timeit.default_timer()
            if iters % 200 == 0:
                logging.info("{} {} {} {} {}".format(round(curr-start), iters, len(self.active_points),
                            len(self.static_points), self.tree.size if self.tree else 0))

    def toJSON(self, path):
        output = []
        for point in self.points:
            output.append([point.x, point.y, 1])  # final loc
            # initial loc
            output.append([point.initial[0], point.initial[1], 0])
        with open(path, 'w') as f:
            f.write(json.dumps(output))

    def toMultiPointFeatureCollection(self, path):
        output = []
        for point in self.points:
            output.append(geojson.Feature(geometry=geojson.MultiPoint(
                [point.initial, point.final]), properties=point.properties))
        fc = geojson.FeatureCollection(output)
        with open(path, 'w') as f:
            geojson.dump(fc, f)


if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO, stream=sys.stdout,
                        format='%(asctime)s %(message)s')

    GEOJSON_PATH = '../../../data/processed/processed_nyc_data_points_200_20220224-154147.geojson'
    rawdata = geojson.load(open(GEOJSON_PATH))

    ever_2050_500_flooded = [x for x in rawdata['features']
                             if x['properties']['flood_2050_500']['in_flood']]

    shockssds = [0.0001, 0.003, 0.005, 0.01, 0.02, 0.04, 0.08]
    ydrifts = [0, 0.0001, 0.0002, 0.003, 0.005, 0.01, 0.02, 0.04, 0.08]
    radii = [0.0005, 0.001, 0.002, 0.004, 0.008]
    everySeeded = [1,5,10,20,25,50,100,200,500]
    nIntervals = 500

    everyNSeeded = 100
    bounds = [-74.27, -73.6]

    for shocksd in shockssds:
        for ydrift in ydrifts:
            for radius in radii:
                for everyNSeeded in everySeeded:
                    nIntervals = 500
                    bounds = [-74.27, -73.6]
                    maxIter = 30000
                    sea_floor_level = 40.48
                    allowedUnconvergedPoints=100

                    fancyEvan = fancyEvanMaker(
                        nIntervals, everyNSeeded, bounds)

                    logging.info("Starting simulation with {shock}_{drift}_{radius}_{everySeed}".format(
                        shock=shocksd, drift=ydrift, radius=radius, everySeed=everyNSeeded))
                    sim = CoralSimulation(ever_2050_500_flooded, fancyEvan)
                    sim.run()
                    sim.toMultiPointFeatureCollection(
                        "./coral_testing_app/public/coral_tests/coral_{shock}_{drift}_{radius}_{everySeed}_{time}.geojson".format(shock=shocksd, drift=ydrift, radius=radius, everySeed=everyNSeeded, time=time.strftime("%Y%m%d-%H%M%S")))  # save the results
