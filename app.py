from flask import Flask, render_template, request
import requests
from datetime import datetime, timezone

app = Flask(__name__)

API_KEY = 'API KEY'
BASE_URL = 'https://api.openweathermap.org/data/3.0/onecall'

@app.route('/', methods=['GET'])
def home():
    """Serve the home page.
    
    Returns:
        Response object: Renders the 'index.html' page
    """
    return render_template('index.html')

def get_coordinates(city_name):
    """Retrieve the latitude and longitude for a given city name using the OpenWeatherMap Geocoding API.

    Args:
        city_name (str): The name of the city for which coordinates are required.

    Returns:
        tuple: Returns a tuple containing the latitude and longitude of the city if found, otherwise (None, None).
    """
    geocode_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=1&appid={API_KEY}"
    response = requests.get(geocode_url)
    print(f"Geocode API URL: {geocode_url} - Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data:
            return data[0]['lat'], data[0]['lon']
    return None, None

@app.route('/weather', methods=['POST'])
def weather():
    """Handle the form submission for fetching weather data.

    Uses form data to fetch weather details for the specified city and renders the forecast.

    Returns:
        Response object: Depending on the outcome, renders either 'index.html' with an error or 'forecast.html' with the weather data.
    """
    city = request.form.get('city')
    units = request.form.get('units', 'metric')
    lang = request.form.get('lang', 'en')
    lat, lon = get_coordinates(city)
    if not lat or not lon:
        print(f"Coordinates not found for city: {city}")
        return render_template('index.html', error="Could not find the city.")

    weather_data = fetch_weather_data(lat, lon, units, lang)
    if 'error' in weather_data:
        print(f"Error fetching weather data: {weather_data['error']}")
        return render_template('index.html', error='Failed to fetch weather data. Please try again.')
    print("Weather data to be rendered:", weather_data)
    return render_template('forecast.html', weather=weather_data)

def fetch_weather_data(lat, lon, units, lang):
    """Fetch weather data for given coordinates, unit, and language preferences using the OpenWeatherMap API.

    Args:
        lat (float): Latitude of the location.
        lon (float): Longitude of the location.
        units (str): Measurement units ('metric', 'imperial').
        lang (str): Language for the weather description ('en' for English, etc.).

    Returns:
        dict: A dictionary with weather data or an error message.
    """
    params = {
        'lat': lat,
        'lon': lon,
        'exclude': 'minutely,hourly',
        'appid': API_KEY,
        'units': units,
        'lang': lang
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()

        for day in data.get('daily', []):
            dt = datetime.fromtimestamp(day['dt'], tz=timezone.utc)
            day['dt'] = dt.strftime('%Y-%m-%d')
        return data
    return {'error': 'API request failed'}

if __name__ == '__main__':
    print("Flask application is running...")
    app.run(debug=True)
