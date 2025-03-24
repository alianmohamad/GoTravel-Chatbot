import requests  # For getting weather data from the API
from functools import lru_cache  # For caching to save API calls

# Loads the API key from a file
def load_api_key():
    try:
        with open("api_key.txt", "r") as file:  # Opens the file with the key
            key = file.read().strip()
            if not key:
                raise ValueError("API key is empty in 'api_key.txt'!")
            return key
    except FileNotFoundError:
        raise ValueError("Missing API Key! Please include 'api_key.txt' with your API key.")

# Sets up the API key and base URL
API_KEY = load_api_key()
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# List of cities with their locations
LOCATIONS = {
    "Cumbria": (54.4609, -3.0886),
    "Corfe Castle": (50.6395, -2.0566),
    "The Cotswolds": (51.8330, -1.8433),
    "Cambridge": (52.2053, 0.1218),
    "Bristol": (51.4545, -2.5879),
    "Oxford": (51.7520, -1.2577),
    "Norwich": (52.6309, 1.2974),
    "Stonehenge": (51.1789, -1.8262),
    "Watergate Bay": (50.4429, -5.0553),
    "Birmingham": (52.4862, -1.8904),
}

# Caches results to avoid extra API calls
@lru_cache(maxsize=128)
def get_weather(lat, lon):
    """Fetch weather data from OpenWeatherMap API."""
    params = {"lat": lat, "lon": lon, "appid": API_KEY, "units": "metric"}  # Sets up the request
    try:
        response = requests.get(BASE_URL, params=params)  # Gets data from the API
        if response.status_code == 200:  # Checks if it worked
            data = response.json()
            weather_desc = data['weather'][0]['description'].capitalize()
            temp = data['main']['temp']
            humidity = data['main']['humidity']
            icon = data['weather'][0]['icon']

            return {  # Sends back weather info
                "temperature": f"{temp}°C",
                "description": weather_desc,
                "humidity": f"{humidity}%",
                "icon": f"http://openweathermap.org/img/wn/{icon}.png",
                "coordinates": {"lat": lat, "lon": lon}
            }
        else:
            return {"error": f"API request failed with status {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Network error: {str(e)}"}  # Returns an error if the network fails