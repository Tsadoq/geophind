import pandas as pd
from dataset_generation.image_scraper import get_image_from_area


def generate_img_dataset(file_path:str):
    df = pd.read_pickle(file_path)
    for i in range(0, len(df)):
        if i % 10 == 0:
            print(f'Processing {i} of {len(df)}')
        if i % 1000 == 0:
            print('Changing connection using NordVPN')
            rotate_VPN()
        lat = df.iloc[i]['point'].y
        lon = df.iloc[i]['point'].x
        country = df.iloc[i]['geounit']
        points = get_image_from_area(
            lat=lat,
            lon=lon,
            country=country,
        )
        if points:
            pd.DataFrame(points).to_csv(f'./metadata/{i:10}.csv')


if __name__ == '__main__':
    initialize_VPN(area_input=['complete rotation'])
    filepath = input('Enter the path to the coordinates dataset: ')
    generate_img_dataset(file_path=filepath)
    terminate_VPN(instructions=None)

