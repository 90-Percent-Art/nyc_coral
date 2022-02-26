'''
This file contains one-off scripts and utilities for doing things with the coral simulation logic
'''

#!/usr/bin/python3
import glob
import os
import shutil
import time 
import random 
import logging
import geojson
from coral_static_logics import fancyEvanMaker
from coral_simulation import CoralSimulation

def scan_directory_and_move_file(
    source_file_regex='./coral_testing_app/public/coral_tests/*',
    file_target='./coral_testing_app/public/coral_tests/coral_latest.geojson', 
    sleep_time=10, latest=True
    ):
    '''
    Utility script that periodically scans target directory and moves the latest file that matches regex 
    to the file_target location. If latest is set to False, it will move a random file.
    '''

    while True:
        list_of_files = glob.glob(source_file_regex)
        if latest:
            next_file = max(list_of_files, key=os.path.getctime)
        else: 
            next_file = random.choice(list_of_files)
        shutil.copy(next_file, file_target)
        time.sleep(sleep_time)


def grid_search_coral_params(input_path='../../../data/processed/processed_nyc_data_points_200_20220224-154147.geojson', output_dir='./coral_testing_app/public/coral_tests/',):
    '''
    This is a script for grid searching the parameters for the coral simulation.
    '''

    logging.basicConfig(level=logging.INFO, stream=sys.stdout,
                        format='%(asctime)s %(message)s')

    rawdata = geojson.load(open(input_path))

    ever_2050_500_flooded = [x for x in rawdata['features']
                             if x['properties']['flood_2050_500']['in_flood']]

    shockssds = [0.0001, 0.003, 0.005, 0.01, 0.02, 0.04, 0.08]
    ydrifts = [0, 0.0001, 0.0002, 0.003, 0.005, 0.01, 0.02, 0.04, 0.08]
    radii = [0.0005, 0.001, 0.002, 0.004, 0.008]
    everySeeded = [1, 5, 10, 20, 25, 50, 100, 200, 500]
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
                    allowedUnconvergedPoints = 100

                    fancyEvan = fancyEvanMaker(
                        nIntervals, everyNSeeded, bounds)

                    logging.info("Starting simulation with {shock}_{drift}_{radius}_{everySeed}".format(
                        shock=shocksd, drift=ydrift, radius=radius, everySeed=everyNSeeded))
                    sim = CoralSimulation(ever_2050_500_flooded, fancyEvan)
                    sim.run()
                    sim.toMultiPointFeatureCollection(os.path.join(output_dir, "{shock}_{drift}_{radius}_{everySeed}_{time}.geojson".format(shock=shocksd, drift=ydrift, radius=radius, everySeed=everyNSeeded, time=time.strftime(" % Y % m % d-%H % M % S"))))

def run_progressive_coral_simulation(): 
    pass 

def filter_point_list_by_bfe_cutpoint(ptlist, static_bfe_cut_point): 
    '''
    Return all the points that *are flooded* at this cut point. I.e. return all the points that
    have static bfe values greater than the cut point.
    '''
    pass

if __name__ == '__main__':
    input_path = '../../../data/processed/processed_nyc_data_points_200_20220224-154147.geojson'
    flood_key = 'flood_2020_500'

    rawdata = geojson.load(open(input_path))

    ever_flooded = [x for x in rawdata['features']if x['properties'][flood_key]['in_flood']]
    never_flooded = [x for x in rawdata['features'] if not x['properties'][flood_key]['in_flood']]

    # Interesting cut points for the static bfe where significantly more people are affected
    static_bfe_cut_points = [17.0, 15.0, 14.0,13.0,12.0,11.0,10.0,0.0]

    not_yet_flooded = ever_flooded # for readability

    # initialize the simulation (nobody is flooded at 24.0)
    sim = CoralSimulation(filter_point_list_by_bfe_cutpoint(ever_flooded, 24.0), fancyEvanMaker(500, 100, [-74.27, -73.6]))

    for bfe_cut_point in static_bfe_cut_points: 
        # 1. get the points that are NEWLY flooded at this cut point 
        #     --> these are the points that have BFE cut point greater than the current cut point and are in the not yet flooded list
        # 2. add these points to the simulation 
        # 3. run the simulation

        newly_flooded = [] # the points that are going to be added to the simulation 
        still_not_flooded = [] # the points that are still not flooded at this cut point

        for pt in not_yet_flooded:
            if pt['properties'][flood_key]['flood_polygon_aggregate_metadata']['max_static_bfe'] >= bfe_cut_point:
                newly_flooded.append(pt)
            else: 
                still_not_flooded.append(pt)

        not_yet_flooded = still_not_flooded
        sim.addNewActivePointsFromFeatureList(newly_flooded)
        print(len(newly_flooded))
        sim.run()
    
    sim.toMultiPointFeatureCollection('./coral_testing_app/public/coral_progressive_test.geojson')





    
