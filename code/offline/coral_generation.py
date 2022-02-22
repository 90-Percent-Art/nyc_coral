'''This script generates the coral shapes'''
'''TODO: needs to be update with new paths + stages of coral growth'''

# Setup
import geojson
import json
import timeit
from random import gauss
from scipy.spatial import KDTree


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
        self.clamp(self.bounds[0], self.bounds[1],
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

    def __str__(self):
        return 'Point({0}, {1})'.format(self.x, self.y)


class CoralSimulation:

    def __init__(self, data):

        # simulation parameters
        self.shocksd = 0.003
        self.radius = 0.002
        self.sea_floor_level = 40.48
        self.maxIter = 30000
        self.bounds = [-74.27, -73.6, 40.48, 40.94]

        # initialize
        self.points = [Point(x['geometry']['coordinates'],
                             self.bounds, x['properties']) for x in data]
        self.iters = 0
        self.tree = None
        self.updateStatic()

    def updateStatic(self):

        self.active_points = [
            point for point in self.points if not point.static]
        self.static_points = [point for point in self.points if point.static]

        if self.static_points:
            self.tree = KDTree([(p.x, p.y) for p in self.static_points])

    def iterate(self):

        for point in self.active_points:
            point.update(self.shocksd, self.shocksd/6)
            if point.y <= self.sea_floor_level and point.x < -73.98 and point.x > -74.02:
                point.makeStatic()
            if self.tree:
                neighbors = self.tree.query_ball_point(
                    (point.x, point.y), self.radius)
                if neighbors:
                    point.makeStatic()

        self.updateStatic()

    def run(self):
        start = timeit.default_timer()
        while self.iters < self.maxIter and len(self.active_points) > 100:
            self.iterate()
            self.iters += 1
            curr = timeit.default_timer()
            print(round(curr-start), self.iters, len(self.active_points),
                  len(self.static_points), self.tree.size if self.tree else 0)

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

    GEOJSON_PATH = '../final_data_points_250.geojson'
    rawdata = geojson.load(open(GEOJSON_PATH))

    # first run simulation with the 2020 100 year data.
    sim = CoralSimulation([x for x in rawdata['features']
                          if x['properties']['in_2020_500']])
    sim.run()
    results_2020_100 = sim.toMultiPointFeatureCollection(
        "../coral_generation/coral_qt_test3.geojson")  # save the results

    # next run simulation with 2020 500 year data.
    #sim = CoralSimulation([x for x in results_2020_100], [x for x in rawdata['features'] if x['properties']['in_2020_500']])
