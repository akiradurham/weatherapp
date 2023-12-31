import openmeteo_requests
import requests_cache
from retry_requests import retry
from urllib.request import urlopen
import json
# some code from open-meteo weather api docs


def get_input():
    user_input = input("What city's weather do you want?\nEnter in form: City, State/Province, Country\n")
    return user_input.split(",")


def call_api_func():
    entered = get_input()

    if len(entered) < 1 or len(entered) > 3:
        print("Too many or too few inputs, ensure to follow input guidelines")
        call_api_func()
        return

    if validate_input(entered):
        message = "Defaulting to largest population with city name match ..." if len(entered) == 1 else (
            "Matching largest population city and within the state/province ..." if len(entered) == 2
            else "Matching all three, city name, state/province, and country ..."
        )
        print(message)
        get_location(entered)


def validate_input(entered):
    messages = ["First", "Second", "Third"]

    for idx, input_data in enumerate(entered):
        if not input_data.strip() or input_data.strip() == '\n':
            print(f"{messages[idx]} input is not valid, ensure to follow input guidelines")
            call_api_func()
            return False
    return True


def get_location(data):
    input_city = data[0].strip().replace(' ', '+')
    input_state = data[1].strip().replace(' ', '+') if len(data) >= 2 else None
    input_country = data[2].strip().replace(' ', '+') if len(data) >= 3 else None
    geocaching(input_city, input_state, input_country)


def geocaching(input_city, input_state, input_country):
    try:
        city_url = f"https://geocoding-api.open-meteo.com/v1/search?name={input_city}&count=10&language=en&format=json"
        cities = json.loads(urlopen(city_url).read())

        latitude = cities['results'][0]['latitude']
        longitude = cities['results'][0]['longitude']
        country = cities['results'][0]['country']

        if input_state is not None:
            state = ''
            for i in range(1, 4):
                try:
                    string = f"admin{i}"
                    state = cities['results'][0][string]
                    if input_state.lower() is state.lower():
                        break
                except KeyError:
                    break
            if not input_state.lower() is state.lower():
                raise Exception

        if input_country is not None:
            if country.lower() is not input_country.lower():
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
