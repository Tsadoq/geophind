import os
from time import sleep

import pandas as pd

from image_scraper import get_image_from_area


def generate_img_dataset(file_path:str):
    tot_tiles = 49_000
    df = pd.read_pickle(file_path)
    for i in range(0, len(df)):
        if i % 10 == 0:
            print(f'Processing {i} of {len(df)}')
        if i % 1000 == 0:
            print('Waiting 10 minutes')
            sleep(600)
        lat = df.iloc[i]['point'].y
        lon = df.iloc[i]['point'].x
        country = df.iloc[i]['geounit']
        points, n_tiles = get_image_from_area(
            lat=lat,
            lon=lon,
            country=country,
            max_distance_meters=100_000
        )
        if i % 10 == 0:
            print(f'You still have {tot_tiles} before sleeping for one day')
        tot_tiles -= n_tiles
        if points:
            pd.DataFrame(points).to_csv(f'./metadata/{i:10}.csv')
        if tot_tiles <= 0:
            print('Finished the amount of tiles that can be processed per day, waiting 24 hours')
            sleep(60*60*24)


if __name__ == '__main__':
    img_dir = './images'
    metadata_dir = './metadata'
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    if not os.path.exists(metadata_dir):
        os.makedirs(metadata_dir)

    filepath = './coord_points.pkl'
    generate_img_dataset(file_path=filepath)

