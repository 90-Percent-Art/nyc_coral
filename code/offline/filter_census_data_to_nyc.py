import logging
import os
import sys
import pandas as pd
from utils import load_file_from_path


def main(poverty_path, race_path, race_ethnicity_path, nyc_counties_path, output_folder_path):

    # Load the data 
    df_poverty = pd.read_csv(poverty_path, dtype={
        'census_block_group': str})
    df_race = pd.read_csv(race_path, dtype={'census_block_group': str})
    df_race_ethniticy = pd.read_csv(race_ethnicity_path, dtype={
                                    'census_block_group': str})

    NYC_counties = load_file_from_path(nyc_counties_path, "json")

    logging.info('Loaded Demographic Data')

    reg = '|'.join([c['fips_starter'] for c in NYC_counties])
    reg = '^(' + reg + ')'

    df_race_ny = df_race[df_race.census_block_group.str.contains(reg)]
    df_poverty_ny = df_poverty[df_poverty.census_block_group.str.contains(reg)]
    df_race_ethniticy_ny = df_race_ethniticy[df_race_ethniticy.census_block_group.str.contains(
        reg)]

    logging.info('Filtered Demographic Data')

    df_race_ny.to_csv(os.path.join(output_folder_path, "df_race_ny.csv"), index=False)
    df_poverty_ny.to_csv(os.path.join(output_folder_path, "df_poverty_ny.csv"), index=False)
    df_race_ethniticy_ny.to_csv(os.path.join(output_folder_path,
                                             "df_race_ethniticy_ny.csv"), index=False)

    logging.info('Wrote Demographic Data')


if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    PATH_TO_POVERTY_DATA = "../../data/raw/acs_data/df_poverty_cbg.csv"
    PATH_TO_RACE_DATA = "../../data/raw/acs_data/df_race_cbg.csv"
    PATH_TO_RACE_ETHNICITY_DATA = "../../data/raw/acs_data/df_race_ethnicity_cbg.csv"
    PATH_TO_NYC_COUNTIES = "../../data/raw/nyc_counties.json"
    PATH_TO_OUTPUT_FOLDER = "../../data/processed/"
    
    main(PATH_TO_POVERTY_DATA, PATH_TO_RACE_DATA, PATH_TO_RACE_ETHNICITY_DATA, PATH_TO_NYC_COUNTIES, PATH_TO_OUTPUT_FOLDER)