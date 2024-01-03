import openmeteo_requests
import requests_cache
from retry_requests import retry
from urllib.request import urlopen
import datetime as dt
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
                print('\033[1m' + "Weather for: " + input_city.lower().capitalize() + ", " + country + '\033[0m')
                search_location(latitude, longitude)
                break
            elif country_valid and input_state is None:
                print('\033[1m' + "Weather for: " + input_city.lower().capitalize() + ", " + country + '\033[0m')
                search_location(latitude, longitude)
                break
            elif country_valid and state_valid:
                print('\033[1m' + "Weather for: " + input_city.lower().capitalize() + ", " + country
                      + ", " + input_state.lower().capitalize() + '\033[0m')
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

    except Exception:
        print("Input is not valid location")
        accepting_input()


def search_location(latitude, longitude):
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": ["temperature_2m", "relative_humidity_2m", "is_day",
                        "weather_code", "wind_speed_10m", "wind_direction_10m"],
            "temperature_unit": "fahrenheit",
            "wind_speed_unit": "mph",
            "precipitation_unit": "inch"
        }

        open_meteo = open_connection()
        responses = open_meteo.weather_api(url, params=params)

        response = responses[0]
        current = response.Current()

        temperature_2m = current.Variables(0).Value()
        relative_humidity_2m = current.Variables(1).Value()
        is_day = current.Variables(2).Value()
        weather_code = current.Variables(3).Value()
        wind_speed = current.Variables(4).Value()
        wind_direction = current.Variables(5).Value()

        print(f"Most Recent Measurement: {dt.datetime.fromtimestamp(current.Time()).strftime("%I:%M %p")}")
        print(f"Temperature: {round(temperature_2m, 2)}\u00b0F")
        print(f"Humidity: {round(relative_humidity_2m, 2)}%")
        print(f"Weather: {code_to_desc(weather_code)}")
        print(f"Wind: {round(wind_speed, 2)} MPH {deg_to_compass(wind_direction)}")
    except Exception:
        print("API connection error\n")
        accepting_input()


def open_connection():
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    open_meteo = openmeteo_requests.Client(session=retry_session)
    return open_meteo


def deg_to_compass(num):
    val = int((num/22.5)+.5)
    arr = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
           "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW", "N"]
    return arr[(val % 16)]


def code_to_desc(code):
    codes = {
        0:  'Clear Sky',
        1:  'Mainly Clear',
        2:  'Partly Cloudy',
        3:  'Overcast',
        45: 'Fog',
        48: 'Depositing Rime Fog',
        51: 'Light Drizzle',
        53: 'Moderate Drizzle',
        55: 'Dense Drizzle',
        56: 'Light Freezing Drizzle',
        57: 'Dense Freezing Drizzle',
        61: 'Slight Rain',
        63: 'Moderate Rain',
        65: 'Heavy Rain',
        66: 'Light Freezing Rain',
        67: 'Heavy Freezing Rain',
        71: 'Slight Snow Fall',
        73: 'Moderate Snow Fall',
        75: 'Heavy Snow Fall',
        77: 'Snow Grains',
        80: 'Slight Rain Shower',
        81: 'Moderate Rain Shower',
        82: 'Violent Rain Shower',
        85: 'Slight Snow Shower',
        86: 'Heavy Snow Shower',
        95: 'Thunderstorm',
        96: 'Slight Hail Thunderstorm',
        99: 'Heavy Hail Thunderstorm'
    }
    return codes[code]


accepting_input()
