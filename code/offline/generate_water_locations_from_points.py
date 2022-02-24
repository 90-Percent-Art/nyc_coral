'''
This script reads in the point data generated by the initial home point generation logic and then does two things
1. It adds the AGGREGATED flood polygon metadata to the point data (i.e. what is your highest water level)
[Not implemented] 2. It creates a "water location" for each point that will be used as intermediate step between home and coral
'''

import logging
import sys
import geojson
import numpy as np
from utils import load_file_from_path
from geojson import Point, MultiPoint

def main_compute_point_water_Location(path_to_point_data): 
    '''
    TODO: Implement this function. It will compute the water location of a point.
    Steps are as follows:
        - For each point, choose location in direction of unit vector from borough_center(point) to point, with some randomness and max distance
        - Repeat this process until you find a point that is is in a flood polygon or a hydrography polygon
    '''

    def create_county_center_hashmap(nyc_county_data):
        return {c['county']:c['center'] for c in nyc_county_data}

    # function to get unit vector pointing from center point to point
    def get_unit_vector(center, pt):

        center_np = np.array(center)
        pt_np = np.array(pt)
        result = (pt_np - center_np) / np.linalg.norm(pt_np - center_np)

        return result.tolist()

    # Set up county stuff
    PATH_TO_NYC_COUNTIES = "../../data/raw/nyc_counties.json"
    NYC_counties = load_file_from_path(PATH_TO_NYC_COUNTIES, "json")
    NYC_center_hashmap = create_county_center_hashmap(NYC_counties)

    # Load the hydrography data
    PATH_TO_HYDROGRAPHY = "../../data/raw/Hydrography.geojson"
    HYDROGRAPHY = load_file_from_path(PATH_TO_HYDROGRAPHY, "geojson")


def main_add_flood_polygon_aggregate_metadata(path_to_point_data, output_path):
    '''
    This function takes in the point data and computes the derived properties of the flood polygon metadata, 
    and also re-organizes the flood properties data 

    Note to self: POINTS_DATE['features'] is initially a list of elements like this:
        {"geometry": {"coordinates": [-73.91535, 40.829755], "type": "Point"},
        "properties": {"cbg": "360050175002", "county": "Bronx County",
        "flood_2020_100": [false, []],
        "flood_2020_500": [false, []],
        "flood_2050_100": [false, []],
        "flood_2050_500": [true, [{flood_polygon_metadata1}, {flood_polygon_metadata2}]], <- for each flood polygon you're in, there is a metadata dict
        "poverty": "1.00 to 1.24",
        "race": "Black_or_African_American_alone"}, "type": "Feature"}
    '''

    def get_flood_polygon_metadata_for_point(pt, flood='flood_2020_500'):
        ''' Given a point in the feature set, return the list of dicts re: what floods polygons it is in'''
        return pt['properties'][flood][1]

    def get_flood_polygon_aggregate_metadata_for_point(pt, flood='flood_2020_500'):
        '''Given a point in the feature set, return the aggregated metadata about what floods polygons it is in'''
        flood_metadata = get_flood_polygon_metadata_for_point(pt, flood)
        return {
            'max_static_bfe': max([float(m['static_bfe']) for m in flood_metadata]),
            'max_abfe_0_2pc': max([float(m['abfe_0_2pc']) for m in flood_metadata]),
        }

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    # Load the point data
    POINTS_DATA = load_file_from_path(path_to_point_data, "geojson")
    floods = ["flood_2020_100", "flood_2020_500",
            "flood_2050_100", "flood_2050_500"]

    logging.info("Loaded the data")

    for feat in POINTS_DATA['features']:

        # Process the flood polygon metadata for this point
        for flood in floods:

            try:
                floodtmp = feat['properties'][flood]  # reorganizing
                feat['properties'][flood] = {
                    'in_flood': floodtmp[0],
                    'flood_polygon_metadata': floodtmp[1],
                    'flood_polygon_aggregate_metadata': get_flood_polygon_aggregate_metadata_for_point(feat, flood) if feat['properties'][flood][0] else {}
                }
            except KeyError as e:
                logging.error("Had a KeyError for {}".format(
                    feat['properties'][flood]))
                break

    logging.info("Processed the data")

    with open(output_path, "w") as f:
        geojson.dump(POINTS_DATA, f)
    
    logging.info("Wrote the data to {}".format(output_path))


if __name__ == "__main__": 

    path_to_points_data = "../../data/processed/nyc_data_points_200_20220224-154147.geojson"
    output_path = "../../data/processed/processed_nyc_data_points_200_20220224-154147.geojson"
    main_add_flood_polygon_aggregate_metadata(path_to_point_data=path_to_points_data, output_path=output_path)