from time import sleep

import mercantile
import os
import requests
from dotenv import load_dotenv
from urllib3.exceptions import DecodeError
from vt2geojson.tools import vt_bytes_to_geojson

load_dotenv()


def get_image_from_area(
        lat: float,
        lon: float,
        country: str,
        max_distance_meters: float = 1000.0,
        max_images: int = 20,
        basepath: str = './images',
):
    lon_coef = 0.000002
    lat_coef = 0.00001

    west = lon - lon_coef * max_distance_meters / 2
    east = lon + lon_coef * max_distance_meters / 2
    south = lat - lat_coef * max_distance_meters / 2
    north = lat + lat_coef * max_distance_meters / 2

    output = {"type": "FeatureCollection", "features": []}
    tile_coverage = 'mly1_public'
    tile_layer = "image"
    access_token = os.environ['MAPILLARY_ACCESS_TOKEN']
    tiles = list(mercantile.tiles(west, south, east, north, 14))
    list_of_images_info = []
    counter = 0
    try:
        for tile in tiles:
            tile_url = f'https://tiles.mapillary.com/maps/vtp/{tile_coverage}/2/{tile.z}/{tile.x}/{tile.y}?access_token={access_token}'
            response = requests.get(tile_url)
            data = vt_bytes_to_geojson(response.content, tile.x, tile.y, tile.z, layer=tile_layer)
            for feature in data['features']:
                lng = feature['geometry']['coordinates'][0]
                lat = feature['geometry']['coordinates'][1]
                if west < lng < east and south < lat < north:
                    sequence_id = feature['properties']['sequence_id']
                    if not os.path.exists(sequence_id):
                        os.makedirs(sequence_id)
                    image_id = feature['properties']['id']
                    header = {'Authorization': 'OAuth {}'.format(access_token)}
                    url = 'https://graph.mapillary.com/{}?fields=thumb_2048_url'.format(image_id)
                    r = requests.get(url, headers=header)
                    data = r.json()
                    image_url = data['thumb_2048_url']
                    img_identifier = '{}{}'.format(sequence_id, image_id)
                    with open(f'{basepath}/{img_identifier}.jpg', 'wb') as handler:
                        image_data = requests.get(image_url, stream=True).content
                        handler.write(image_data)
                        list_of_images_info.append(
                            {
                                'img_identifier': img_identifier,
                                'sequence_id': sequence_id,
                                'image_id': image_id,
                                'lat': lat,
                                'lon': lng,
                                'country': country,
                            }
                        )
                        counter += 1
                if counter >= max_images:
                    return list_of_images_info
        return list_of_images_info
    except Exception as e:
        print(e)
        sleep(60)
        return []

    except DecodeError as de:
        print(de)
        sleep(60)
        return []

