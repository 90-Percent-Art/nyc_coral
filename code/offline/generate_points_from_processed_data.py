import os
import geojson
import random
import time
import sys
import logging
import math
import pandas as pd
import numpy as np
from numpy.random import default_rng
from geojson import Feature, FeatureCollection, Point as GeoPoint
from shapely.geometry import Polygon, Point as ShapelyPoint
from utils import load_file_from_path

def convert_sea_geojson_to_polygons(gj):
    """
    Convert one of the sea level geojson files to a list of objects with 
    the polygon and the associated metadata for the polygon
    """
    sea_polygons = []
    for feat in gj['features']:
        try:
            poly = Polygon(feat['geometry']['coordinates'][0][0]) # TODO: this is broken for 2050 data
            metadata = feat['properties']
            sea_polygons.append({'polygon': poly, 'metadata': metadata})
        except Exception as e:
            print(e)
            # print(feat['geometry']['coordinates'])

    return sea_polygons

def create_cbg_demos_dict(gj, df_poverty_ny, df_race_ny): 
    '''
    Create a dictionary of the cbg and the demographics for that cbg
    '''

    def normalize_dict(inp_dict, total):
        probs = []
        vals = []
        for k, v in inp_dict.items():
            if 'total' not in k:
                probs.append(v / total) if total > 0 else probs.append(0)
                vals.append(k)
        return {'probs': probs, 'vals': vals}

    def get_raw_demo_data_for_cbg(cbg: str, df):
        return {k: v[0] for k, v in df[df['census_block_group'] == cbg].to_dict('list').items() if k != 'census_block_group'}

    def get_race_poverty_demo_data_for_cbg(cbg, df_poverty_ny, df_race_ny):
        race = get_raw_demo_data_for_cbg(cbg, df_race_ny)
        poverty = get_raw_demo_data_for_cbg(cbg, df_poverty_ny)
        return {'total': race['Race_total'],
                'race_counts': race,
                'poverty_counts': poverty,
                'race_share': normalize_dict(race, race['Race_total']),
                'poverty_share': normalize_dict(poverty, race['Race_total'])}

    # Main loop 
    cbg_demos_dict = {}
    for feat in gj['features']:
        cbg = feat['properties']['CensusBlockGroup']
        cbg_demos_dict[cbg] = get_race_poverty_demo_data_for_cbg(
            cbg, df_poverty_ny, df_race_ny)
    return cbg_demos_dict

def generate_output_points(people_per_point, nyc_cbg_gj, sea_level_polygon_dict, cbg_demo_dict):
    ''' 
    Main loop to generate random points in polygons based on population and demographic info, and attach
    the relevant metadata to them as geojson features
    '''

    rng = default_rng()

    def get_draw_from_props(props, k='race_share'):
        return props[k]['vals'][np.where(rng.multinomial(
        n=1, pvals=props[k]['probs']) == 1)[0][0]]

    def random_points_in_polygon(number, polygon):
        points = []
        min_x, min_y, max_x, max_y = polygon.bounds
        i = 0
        while i < number:
            point = ShapelyPoint(random.uniform(min_x, max_x),
                                random.uniform(min_y, max_y))
            if polygon.contains(point):
                points.append(point)
                i += 1
        return points  # returns list of shapely point

    def pop_to_total_points(pop, people_per_point):
        cnt = math.floor(pop / people_per_point)
        prob = (pop % people_per_point) / people_per_point
        if random.random() < prob:
            cnt += 1
        return cnt

    def get_point_flood_info(point, flood_data):
        inFlood = False
        floodMetadata = []
        for i in flood_data:
            poly = i['polygon']
            if poly.contains(point):
                inFlood = True
                floodMetadata.append(i['metadata'])
        return inFlood, floodMetadata
        
    def get_demo_props(p, demo_dat):
        return {
            'race': get_draw_from_props(demo_dat, k='race_share'),
            'poverty': get_draw_from_props(demo_dat, k='poverty_share')
        }

    def get_flood_props(p, sea_level_polygon_dict):

        flood_props = {}

        for flood_key in sea_level_polygon_dict.keys():

            flood_data = sea_level_polygon_dict[flood_key] # array of dicts with keys 'polygon' and 'metadata'
            flood_props[flood_key] = get_point_flood_info(p, flood_data)

        return flood_props

    # Main loop 
    feature_collection_points = []
    pts = 0

    for feature in nyc_cbg_gj['features']:
        
        cbg = feature['properties']['CensusBlockGroup']
        county = feature['properties']['County']
        poly = Polygon((feature['geometry']['coordinates'][0][0]))
        demo_dat = cbg_demo_dict[cbg]

        point_list = random_points_in_polygon(pop_to_total_points(
            demo_dat['total'], people_per_point), poly)

        for p in point_list:

            demo_props = get_demo_props(p, demo_dat)
            flood_props = get_flood_props(p, sea_level_polygon_dict)

            feature_collection_points.append(Feature(
                geometry = GeoPoint((p.x, p.y)),
                properties={**demo_props, **flood_props, 'county': county, 'cbg': cbg}
            ))

            if pts % 1000 == 0:
                logging.info("{}: Generated {} points. Current: {}".format(time.strftime("%H%M%S"), pts, p))
            pts += 1
    
    return FeatureCollection(feature_collection_points)


if __name__ == '__main__':

    people_per_point = 200
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    nyc_cbg_gj = load_file_from_path('../../data/processed/cbg_nyc.geojson', 'geojson')
    df_poverty = pd.read_csv('../../data/processed/df_poverty_ny.csv', dtype={
        'census_block_group': str})
    df_race_ethnicity = pd.read_csv('../../data/processed/df_race_ethnicity_ny.csv', dtype={
        'census_block_group': str})

    sea_level_2020_100_clean = convert_sea_geojson_to_polygons(load_file_from_path(
        "../../data/raw/sea_level_geoms/clean/sea_level_rise_2020s_100.geojson", 'geojson'))
    sea_level_2020_500_clean = convert_sea_geojson_to_polygons(load_file_from_path(
        "../../data/raw/sea_level_geoms/clean/sea_level_rise_2020s_500.geojson", 'geojson'))
    sea_level_2050_100_clean = convert_sea_geojson_to_polygons(load_file_from_path(
        "../../data/raw/sea_level_geoms/clean/sea_level_rise_2050s_100.geojson", 'geojson'))
    sea_level_2050_500_clean = convert_sea_geojson_to_polygons(load_file_from_path(
        "../../data/raw/sea_level_geoms/clean/sea_level_rise_2050s_500.geojson", 'geojson'))

    logging.info('Loaded the Data')

    # dict with precomputed cbg demographic shares
    cbg_demo_dict = create_cbg_demos_dict(
        nyc_cbg_gj, df_poverty, df_race_ethnicity)
    logging.info('Built the CBG demos dict')

    # main loop
    output_feature_collection = generate_output_points(
        people_per_point=people_per_point,
        nyc_cbg_gj=nyc_cbg_gj,
        sea_level_polygon_dict={'flood_2020_100':sea_level_2020_100_clean, 
                                'flood_2020_500':sea_level_2020_500_clean, 
                                'flood_2050_100':sea_level_2050_100_clean,
                                'flood_2050_500':sea_level_2050_500_clean},
        cbg_demo_dict=cbg_demo_dict
    )
    logging.info('Generated the output feature collection')

    with open("../../data/processed/nyc_data_points_{}_{}.geojson".format(people_per_point, time.strftime("%Y%m%d-%H%M%S")), "w") as f:
        geojson.dump(output_feature_collection, f)
    
    logging.info('Wrote feature collection to file')
