import json 
import geojson 
import pandas as pd

def load_file_from_path(path, ftype, **kwargs):
    ''' Loads a file from a path'''
    if ftype == 'geojson':
        with open(path, 'r') as f:
            return geojson.load(f, **kwargs)
    elif ftype == 'json':
        with open(path, 'r') as f:
            return json.load(f, **kwargs)
    elif ftype == 'csv':
        return pd.read_csv(path, **kwargs)
