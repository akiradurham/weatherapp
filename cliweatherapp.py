import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from urllib.request import urlopen
import json

# some code from open-meteo weather api docs

def search_location():
    city_url = f"https://geocoding-api.open-meteo.com/v1/search?name={input_city}&count=1&language=en&format=json"
    cities = json.loads(urlopen(city_url).read())

    latitude = cities['results'][0]['latitude']
    longitude = cities['results'][0]['longitude']
    country = cities['results'][0]['country']

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

cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
open_meteo = openmeteo_requests.Client(session=retry_session)

user_input = input("What city's weather do you want?\nEnter in form: City, State/Province, Country\n")
entered = user_input.split(", ")

if len(entered) > 3 or len(entered) <= 0:
    print("Input is not valid, ensure to follow input guidelines")
elif len(entered) == 1:
    print("Defaulting to largest population with city name match")
    input_city = entered[0].replace(' ', '+')
    search_location()
elif len(entered) == 2:
    print("Matching largest population city and within the state/province")
    input_city = entered[0].replace(' ', '+')
    input_state = entered[1].replace(' ', '+')
    search_location()
else:
    print("Matching all city name, state/province, and country")
    input_city = entered[0].replace(' ', '+')
    input_state = entered[1].replace(' ', '+')
    input_country = entered[2].replace(' ', '+')
    search_location()
