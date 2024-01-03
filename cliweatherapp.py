import openmeteo_requests
import requests_cache
from retry_requests import retry
from urllib.request import urlopen
import json
# some code from open-meteo weather api docs


def get_input():
    user_input = input("\nWhat city's weather do you want?\nEnter in form: City, Country, State/Province\n")
    return user_input.split(",")


def accepting_input():
    entered = get_input()
    if validate_input(entered):
        if len(entered) == 1:
            message = "Defaulting to largest population with city name match ..."
        elif len(entered) == 2:
            message = "Matching largest population city with country ..."
        else:
            message = "Matching all three, city name, country, and state/province ..."
        print(message)
        get_location(entered)


def validate_input(entered):
    messages = ["First", "Second", "Third"]

    if len(entered) < 1 or len(entered) > 3:
        print("Too many or too few inputs, ensure to follow input guidelines\n")
        accepting_input()

    for i, input_data in enumerate(entered):
        if not input_data.strip() or input_data.strip() == '\n':
            print(f"{messages[i]} input is not valid, ensure to follow input guidelines\n")
            accepting_input()
    return True


def get_location(data):
    city = data[0].strip().replace(' ', '+')
    country = data[1].strip() if len(data) >= 2 else None
    state = data[2].strip() if len(data) >= 3 else None
    geocaching(city, country, state)


def geocaching(input_city, input_country, input_state):
    try:
        city_url = f"https://geocoding-api.open-meteo.com/v1/search?name={input_city}&count=10&language=en&format=json"
        cities = json.loads(urlopen(city_url).read())
        state_valid = country_valid = False

        for city in cities['results']:
            latitude = city['latitude']
            longitude = city['longitude']
            country = city['country']

            if input_country is not None and not country_valid:
                if country.lower() == input_country.lower():
                    country_valid = True

            if input_state is not None and not state_valid:
                for i in range(1, 4):
                    try:
                        string = f"admin{i}"
                        state = city[string]
                        if input_state.lower() == state.lower():
                            state_valid = True
                            break
                    except KeyError:
                        pass

            if input_state is None and input_country is None:
                search_location(latitude, longitude)
                break
            elif country_valid and input_state is None:
                search_location(latitude, longitude)
                break
            elif country_valid and state_valid:
                search_location(latitude, longitude)
                break

        if not country_valid and input_country is not None:
            if not state_valid and input_state is not None:
                print("No matching countries and states/provinces found")
                accepting_input()
            elif state_valid and input_state is not None:
                print("The country does not match the given city, but there is a state/province match")
                accepting_input()
            else:
                print("The country does not match the given city")
                accepting_input()
        elif not state_valid and (input_state and input_country) is not None:
            print("No matching states/provinces found, but the country matches")
            accepting_input()

    except Exception as e:
        print("Input is not valid location")
        accepting_input()


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
    except Exception:
        print("API connection error\n")
        accepting_input()


accepting_input()
