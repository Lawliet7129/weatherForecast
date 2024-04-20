from flask import Flask, render_template, request
import requests
from datetime import datetime, timezone

app = Flask(__name__)

API_KEY = 'Enter API_KEY'
BASE_URL = 'https://api.openweathermap.org/data/3.0/onecall'

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

def get_coordinates(city_name):
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
    print("Weather route called")
    city = request.form.get('city')
    units = request.form.get('units', 'metric')
    lang = request.form.get('lang', 'en')
    print(f"Form data received - City: {city}, Units: {units}, Language: {lang}")

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
        # Format dates before returning
        for day in data.get('daily', []):
            dt = datetime.fromtimestamp(day['dt'], tz=timezone.utc)
            day['dt'] = dt.strftime('%Y-%m-%d')
        return data
    return {'error': 'API request failed'}

if __name__ == '__main__':
    print("Flask application is running...")
    app.run(debug=True)