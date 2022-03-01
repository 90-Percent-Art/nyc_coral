'''
This file contains one-off scripts and utilities for doing things with the coral simulation logic
'''

#!/usr/bin/python3
import glob
import os
import sys
import shutil
import time 
import random 
import logging
import geojson
from coral_static_logics import intervalLogicMaker, randomIntervalLogicMaker, middle
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

                    intervalLogic = intervalLogicMaker(
                        nIntervals, everyNSeeded, bounds)

                    logging.info("Starting simulation with {shock}_{drift}_{radius}_{everySeed}".format(
                        shock=shocksd, drift=ydrift, radius=radius, everySeed=everyNSeeded))
                    sim = CoralSimulation(ever_2050_500_flooded, intervalLogic)
                    sim.run()
                    sim.toMultiPointFeatureCollection(os.path.join(output_dir, "{shock}_{drift}_{radius}_{everySeed}_{time}.geojson".format(shock=shocksd, drift=ydrift, radius=radius, everySeed=everyNSeeded, time=time.strftime(" % Y % m % d-%H % M % S"))))


def run_progressive_coral_simulation(
    input_path='../../../data/processed/processed_nyc_data_points_200_20220224-154147.geojson', 
    flood_key='flood_2020_500', 
    static_logic=intervalLogicMaker(500, 25, [-74.27, -73.6]),
    shocksd=0.003, ydrift=0.003/6, radius=0.002, 
    output_path='./coral_animation_capture/data/coral_progressive_test2.geojson', 
    static_output_path='./coral_animation_capture/data/coral_progressive_static.geojson',
    make_static=False,
    ):
    """
    This script runs an iterative progressive coral simulation. This means that it releases the particles in waves
    based on some set of cutpoints in the static BFE levels. 
    """

    logging.basicConfig(level=logging.INFO, stream=sys.stdout,
                        format='%(asctime)s %(message)s')

    rawdata = geojson.load(open(input_path))
    ever_flooded = [x for x in rawdata['features']
                    if x['properties'][flood_key]['in_flood']]
    never_flooded = [x for x in rawdata['features']
                    if not x['properties'][flood_key]['in_flood']]

    static_bfe_cut_points = [17.0, 15.0, 14.0, 13.0, 12.0, 11.0, 10.0, 0.0]

    not_yet_flooded = ever_flooded  # for readability

    # initialize the simulation (nobody is flooded at 24.0)
    sim = CoralSimulation([], static_logic, allowedUnconvergedPoints=10,
                          shocksd=0.003, ydrift=0.003/8, radius=0.0025)

    for bfe_cut_point in static_bfe_cut_points:
        # 1. get the points that are NEWLY flooded at this cut point
        #     --> these are the points that have BFE cut point greater than the current cut point and are in the not yet flooded list
        # 2. add these points to the simulation
        # 3. run the simulation

        logging.info('Flood level: {}'.format(bfe_cut_point))

        newly_flooded = []  # the points that are going to be added to the simulation
        still_not_flooded = []  # the points that are still not flooded at this cut point

        for pt in not_yet_flooded:
            if pt['properties'][flood_key]['flood_polygon_aggregate_metadata']['max_static_bfe'] >= bfe_cut_point:
                newly_flooded.append(pt)
            else:
                still_not_flooded.append(pt)

        not_yet_flooded = still_not_flooded
        sim.addNewActivePointsFromFeatureList(newly_flooded)
        sim.run()

        logging.info('Done with: {}'.format(bfe_cut_point))

    sim.toMultiPointFeatureCollection(output_path)

    if(make_static):
        rawdata['features'] = never_flooded
        with open(static_output_path, 'w') as f:
            geojson.dump(rawdata, f)


def run_progressive_coral_simulation_n_at_a_time(
    n = 10,
    input_path='../../../data/processed/processed_nyc_data_points_200_20220224-154147.geojson',
    flood_key='flood_2020_500',
    static_logic=intervalLogicMaker(500, 25, [-74.27, -73.6]),
    shocksd=0.003, ydrift=0.003/6, radius=0.002,
    output_path='./coral_animation_capture/data/coral_progressive_test2.geojson',
    static_output_path='./coral_animation_capture/data/coral_progressive_static.geojson',
    make_static=False,
):
    """
    This script runs an iterative progressive coral simulation. This means that it releases the particles in waves
    based on some set of cutpoints in the static BFE levels. 
    """

    logging.basicConfig(level=logging.INFO, stream=sys.stdout,
                        format='%(asctime)s %(message)s')

    rawdata = geojson.load(open(input_path))
    ever_flooded = [x for x in rawdata['features']
                    if x['properties'][flood_key]['in_flood']]
    never_flooded = [x for x in rawdata['features']
                     if not x['properties'][flood_key]['in_flood']]

    static_bfe_cut_points = [17.0, 15.0, 14.0, 13.0, 12.0, 11.0, 10.0, 0.0]

    not_yet_flooded = ever_flooded  # for readability

    # initialize the simulation (nobody is flooded at 24.0)
    sim = CoralSimulation([], static_logic, allowedUnconvergedPoints=10,
                          shocksd=0.003, ydrift=0.003/8, radius=0.0025)

    for bfe_cut_point in static_bfe_cut_points:
        # 1. get the points that are NEWLY flooded at this cut point
        #     --> these are the points that have BFE cut point greater than the current cut point and are in the not yet flooded list
        # 2. add these points to the simulation
        # 3. run the simulation

        logging.info('Flood level: {}'.format(bfe_cut_point))

        newly_flooded = []  # the points that are going to be added to the simulation
        still_not_flooded = []  # the points that are still not flooded at this cut point

        for pt in not_yet_flooded:
            if pt['properties'][flood_key]['flood_polygon_aggregate_metadata']['max_static_bfe'] >= bfe_cut_point:
                newly_flooded.append(pt)
            else:
                still_not_flooded.append(pt)

        not_yet_flooded = still_not_flooded

        def chunks(lst, num):
            """Yield successive num-sized chunks from lst."""
            for i in range(0, len(lst), num):
                yield lst[i:i + num]

        for chnk in chunks(newly_flooded, n):
            sim.addNewActivePointsFromFeatureList(chnk)
            sim.run()

        logging.info('Done with: {}'.format(bfe_cut_point))

    sim.toMultiPointFeatureCollection(output_path)

    if(make_static):
        rawdata['features'] = never_flooded
        with open(static_output_path, 'w') as f:
            geojson.dump(rawdata, f)


if __name__ == '__main__':
    # run_progressive_coral_simulation(
    #     static_logic=randomIntervalLogicMaker(8, [-74.17, -73.7], 0.01),
    #     output_path="./coral_animation_capture/data/coral_progressive_test6.geojson",
    #     make_static=False,
    #     shocksd=0.002, ydrift=0.003/8, radius=0.002,
    # )
    run_progressive_coral_simulation(
        static_logic=middle,
        output_path="./coral_animation_capture/data/coral_progressive_test10.geojson",
        make_static=False,
        shocksd=0.004, ydrift=0.003/12, radius=0.002,
    )
