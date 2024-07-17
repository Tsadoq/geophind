import logging
import os
from time import sleep

import pandas as pd

from image_scraper import get_image_from_area

logging.basicConfig(filename='image_generation.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
logger=logging.getLogger()
logger.setLevel(logging.INFO)


def generate_img_dataset(file_path:str):
    logging.info('Starting the image dataset generation')
    country_counter = {}
    tot_tiles = 49_000
    df = pd.read_pickle(file_path)
    for i in range(0, len(df)):
        lat = df.iloc[i]['point'].y
        lon = df.iloc[i]['point'].x
        country = df.iloc[i]['geounit']
        if country_counter.get(country, 1000) <= 0:
            continue
        if i % 10 == 0:
            print(f'Processing {i} of {len(df)}')
            logging.info(f'Processing {i} of {len(df)}')
        if i % 1000 == 0:
            print('Waiting 10 minutes')
            logging.info('Waiting 10 minutes')
            sleep(600)
        points, n_tiles = get_image_from_area(
            lat=lat,
            lon=lon,
            country=country,
            max_distance_meters=10_000
        )
        country_counter[country] = country_counter.get(country, 1000) - len(points)
        if i % 10 == 0:
            print(f'You still have {tot_tiles} before sleeping for one day')
            logging.info(f'You still have {tot_tiles} before sleeping for one day')
        tot_tiles -= n_tiles
        if points:
            pd.DataFrame(points).to_csv(f'./metadata/{i:05d}.csv')
        if tot_tiles <= 0:
            print('Finished the amount of tiles that can be processed per day, waiting 24 hours')
            logging.info('Finished the amount of tiles that can be processed per day, waiting 24 hours')
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

