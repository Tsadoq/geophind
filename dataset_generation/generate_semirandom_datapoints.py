import geopandas
import numpy as np
import pandas as pd
from shapely import Polygon, MultiPolygon
from tqdm.auto import trange
import random
import timeit
from shapely.geometry import Point


def random_points_within(poly: Polygon | MultiPolygon, num_points: int):
    min_x, min_y, max_x, max_y = poly.bounds
    points = []
    coef = 1_000_000.0
    start_time = timeit.default_timer()
    while len(points) < num_points:
        random_point = Point(
            [random.uniform(min_x * coef, max_x * coef) / coef, random.uniform(min_y * coef, max_y * coef) / coef])
        if poly.contains(random_point):
            points.append(random_point)
        if timeit.default_timer() - start_time >= 600.0:
            print('Timeout')
            break
    return points


def generate_coordinates_dataset(
        path_shape_file: str = './NE 10m Admin 0 Countries/ne_10m_admin_0_countries.shp',
        max_num_points: int = 1000,
        output_path: str = './coord_points.pkl',
) -> None:
    list_points = []
    df = geopandas.read_file(path_shape_file)
    df['area'] = df['geometry'].area
    df['dim_coeff'] = (
            (np.log10(df['area']) - np.log10(df['area']).min()) /
            (np.log10(df['area']).max() - np.log10(df['area']).min())
    )
    for i in trange(0, len(df), desc='Generating points'):
        row = df.iloc[i]
        country_name = row['SOVEREIGNT']
        geounit = row['GEOUNIT']
        shape = row['geometry']
        dim_coeff = row['dim_coeff']
        points = random_points_within(shape, int(max_num_points * dim_coeff) + 30)
        for points in points:
            list_points.append({'country': country_name, 'geounit': geounit, 'point': points})
        return pd.DataFrame(list_points).to_pickle(output_path)
