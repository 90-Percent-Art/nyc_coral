'''This script filters the CBG data to only include those in NYC'''
import logging
import geojson
import sys
from utils import load_file_from_path

def main(cbg_path, nyc_counties_path, output_path): 
    gj = load_file_from_path(cbg_path, 'geojson')
    NYC_counties = load_file_from_path(nyc_counties_path, 'json')
    filtered_gj = gj.copy()
    filtered_gj['features'] = []  # clear out the features field
    logging.info('Loaded Data')

    for x in gj['features']:
        cbg = x["properties"]["CensusBlockGroup"]
        if any(cbg.startswith(y['fips_starter']) for y in NYC_counties):
            filtered_gj['features'].append(x)

    logging.info('Filtered Data')

    with open(output_path, "w") as f:
        f.write(geojson.dumps(filtered_gj))

    logging.info('Wrote filtered data')


if __name__ == "__main__": 

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    PATH_TO_CBG_GJ_DATA = "../../data/raw/safegraph_open_census_data_2010_to_2019_geometry/cbg.geojson"
    PATH_TO_NYC_COUNTIES = "../../data/raw/nyc_counties.json"
    OUTPUT_PATH = "../../data/processed/cbg_nyc.geojson"

    main(PATH_TO_CBG_GJ_DATA, PATH_TO_NYC_COUNTIES, OUTPUT_PATH)