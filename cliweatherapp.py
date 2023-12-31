import openmeteo_requests
import requests_cache
from retry_requests import retry
from urllib.request import urlopen
import json
# some code from open-meteo weather api docs


def get_input():
    user_input = input("What city's weather do you want?\nEnter in form: City, State/Province, Country\n")
    return user_input.split(", ")


def validate_input(entered):
    if len(entered) == 1:
        print("Defaulting to largest population with city name match ...")
        get_location(entered)
    elif len(entered) == 2:
        print("Matching largest population city and within the state/province ...")
        get_location(entered)
    elif len:
        print("Matching all three, city name, state/province, and country ...")
        get_location(entered)
    else:
        print("Input is not valid, ensure to follow input guidelines")
        validate_input(get_input())


def get_location(data):
    input_city = data[0].trim().replace(' ', '+')
    input_state = data[1].trim().replace(' ', '+') if len(data) >= 2 else None
    input_country = data[2].trim().replace(' ', '+') if len(data) >= 3 else None
    geocaching(input_city, input_state, input_country)


def geocaching(input_city, input_state, input_country):
    try:
        city_url = f"https://geocoding-api.open-meteo.com/v1/search?name={input_city}&count=10&language=en&format=json"
        cities = json.loads(urlopen(city_url).read())

        latitude = cities['results'][0]['latitude']
        longitude = cities['results'][0]['longitude']
        country = cities['results'][0]['country']
        state = cities['results'][0]['admin1']

        if not country == input_country:
            raise Exception
        if not input_state == state:
            raise Exception

        search_location(latitude, longitude)
    except Exception as e:
        print(e.__repr__())
        print("Input is not valid location")


def search_location(latitude, longitude):
    try:
        cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        open_meteo = openmeteo_requests.Client(session=retry_session)
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": "temperature_2m"
        }
        responses = open_meteo.weather_api(url, params=params)

        response = responses[0]
        print(f"Coordinates {response.Latitude()}°E {response.Longitude()}°N")
        print(f"Elevation {response.Elevation()} m asl")
        print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
        print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")
    except Exception as e:
        print(e.__repr__())
        print("API connection error")


validate_input(get_input())

