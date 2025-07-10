import json
import requests
import folium
import os
from geopy import distance
from dotenv import load_dotenv


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lat, lon


def get_coffee_shop_distance(coffee_shop):
    return coffee_shop['distance']


def main():
    load_dotenv()
    api_key = os.getenv('API_KEY')

    with open('coffee.json', 'r', encoding='CP1251') as coffee_file:
        coffee_file_contents = coffee_file.read()
    coffee_shops = json.loads(coffee_file_contents)

    point_a = input('Где вы находитесь? ')
    a_coords = fetch_coordinates(api_key, point_a)

    relative_coffee_shops = []

    for coffee_shop in coffee_shops:
        relative_coffee_shop = {}
        relative_coffee_shop['title'] = coffee_shop['Name']
        b_coords = f'{coffee_shop['Latitude_WGS84']} {coffee_shop['Longitude_WGS84']}'
        relative_coffee_shop['distance'] = distance.distance(a_coords, b_coords).km
        relative_coffee_shop['latitude'] = coffee_shop['Latitude_WGS84']
        relative_coffee_shop['longitude'] = coffee_shop['Longitude_WGS84']
        relative_coffee_shops.append(relative_coffee_shop)

    nearest_coffee_shops = sorted(relative_coffee_shops, key=get_coffee_shop_distance)
    nearest_coffee_shops = nearest_coffee_shops[:5]

    map = folium.Map(location=(a_coords), zoom_start=16)

    for coffee_shop in nearest_coffee_shops:
        folium.Marker(
            location=[coffee_shop['latitude'], coffee_shop['longitude']],
            tooltip=coffee_shop['title'],
            popup=coffee_shop['title'],
            icon=folium.Icon(color='blue'),
        ).add_to(map)

    map.save('index.html')


if __name__ == '__main__':
    main()