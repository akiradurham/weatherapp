import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from urllib.request import urlopen
import json

# from open-meteo weather api docs
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
open_meteo = openmeteo_requests.Client(session=retry_session)

user_input = input("What city's weather do you want?\nEnter in form: City, State/Province, Country\n")
location = user_input.replace(' ', '+')

city_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1&language=en&format=json"
cities = json.loads(urlopen(city_url).read())

latitude = cities['results'][0]['latitude']
longitude = cities['results'][0]['longitude']
country = cities['results'][0]['country']

url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": 52.52,
    "longitude": 13.41,
    "hourly": "temperature_2m"
}
responses = open_meteo.weather_api(url, params=params)

response = responses[0]
print(f"Coordinates {response.Latitude()}°E {response.Longitude()}°N")
print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

# hourly = response.Hourly()
# hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
#
# hourly_data = {"date": pd.date_range(
#     start=pd.to_datetime(hourly.Time(), unit="s"),
#     end=pd.to_datetime(hourly.TimeEnd(), unit="s"),
#     freq=pd.Timedelta(seconds=hourly.Interval()),
#     inclusive="left"
# ), "temperature_2m": hourly_temperature_2m}
#
# hourly_dataframe = pd.DataFrame(data=hourly_data)
# print(hourly_dataframe)
