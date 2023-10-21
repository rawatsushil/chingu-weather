import os

import requests
import argparse

from dotenv import load_dotenv
from termcolor import colored

from constants import CELSIUS_SYMBOL, FAHRENHEIT_SYMBOL, WEATHER_OUTPUT_FILE

# Load API keys from .env file
load_dotenv(".env.py")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
MAPBOX_API_KEY = os.getenv("MAPBOX_API_KEY")


def set_initial_conditions(parser):
    parser.add_argument("city", help="Name of the city.")
    parser.add_argument(
        "-f", "-fahrenheit", dest="fahrenheit", action="store_true", help="Display temperature in Fahrenheit."
    )
    parser.add_argument("-c", "-celsius", dest="celsius", action="store_true", help="Display temperature in Celsius.")
    return parser


def get_coordinates(city_name, mapbox_api_key):
    base_url = "https://api.mapbox.com/geocoding/v5/mapbox.places/"
    endpoint = f"{city_name}.json?access_token={mapbox_api_key}"
    response = requests.get(base_url + endpoint)
    data = response.json()
    # Extract longitude and latitude
    coordinates = data['features'][0]['geometry']['coordinates']
    return tuple(coordinates)


def get_weather(coordinates, openweather_api_key, unit):
    lat, lon = coordinates
    base_url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={openweather_api_key}&units={unit}"
    response = requests.get(base_url)
    data = response.json()

    # Extract required weather details
    current_temp = data['main']['temp']
    description = data['weather'][0]['description']
    forecast = "Sky looks clear throughout the day"

    return current_temp, description, forecast


def transform_temp(temp, user_arg):
    if (
        not (user_arg.fahrenheit or user_arg.celsius) or (user_arg.fahrenheit and user_arg.celsius)
    ):
        return f"{temp}{FAHRENHEIT_SYMBOL} or {round((temp-32)*(5/9), 2)}{CELSIUS_SYMBOL}"
    elif user_arg.fahrenheit:
        return f"{temp}{FAHRENHEIT_SYMBOL}"
    elif user_arg.celsius:
        return f"{round((temp-32)*(5/9), 2)}{CELSIUS_SYMBOL}"


def write_to_file(city_name, current_temp, description, forecast):
    with open(WEATHER_OUTPUT_FILE, 'a') as file:
        file.write(f"Location: {city_name}\n")
        file.write(f"Current temperature: {current_temp}\n")
        file.write(f"Conditions: {description}\n")
        file.write(f"Forecast: {forecast}\n\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get weather information for a given city.")
    parser = set_initial_conditions(parser)
    user_args = parser.parse_args()

    coordinates = get_coordinates(user_args.city, MAPBOX_API_KEY)
    current_temp, description, forecast = get_weather(coordinates, OPENWEATHER_API_KEY, 'imperial')
    current_temp = transform_temp(current_temp, user_args)

    # Display output
    print(colored(f"Current temperature in {user_args.city} is {current_temp}", 'cyan'))
    print(colored(f"Conditions are currently: {description}.", 'magenta'))
    print(colored(f"What you should expect: {forecast}.", 'green'))

    write_to_file(user_args.city, current_temp, description, forecast)
    print(colored(f"Weather was added to your weather tracking file, {WEATHER_OUTPUT_FILE}", 'yellow'))
