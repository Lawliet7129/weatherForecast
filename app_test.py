import unittest
from flask_testing import TestCase
from app import app, get_coordinates, fetch_weather_data
from unittest.mock import patch

class TestFlaskApp(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        return app

    def test_home_route(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('index.html')

    def test_get_coordinates(self):
        with patch('requests.get') as mocked_get:
            mocked_get.return_value.status_code = 200
            mocked_get.return_value.json.return_value = [{'lat': 40.712776, 'lon': -74.005974}]
            lat, lon = get_coordinates('New York')
            self.assertEqual((lat, lon), (40.712776, -74.005974))

    def test_get_coordinates_multiple_cities_same_name(self):
        with patch('requests.get') as mocked_get:
            mocked_get.return_value.status_code = 200
            mocked_get.return_value.json.return_value = [{'lat': 34.0522, 'lon': -118.2437}, {'lat': 54.0522, 'lon': -118.2437}]
            lat, lon = get_coordinates('Los Angeles')
            self.assertEqual((lat, lon), (34.0522, -118.2437))
    
    def test_get_coordinates_empty_result(self):
        with patch('requests.get') as mocked_get:
            mocked_get.return_value.status_code = 200
            mocked_get.return_value.json.return_value = []
            lat, lon = get_coordinates('Atlantis')
            self.assertEqual((lat, lon), (None, None))

    def test_fetch_weather_data(self):
        with patch('requests.get') as mocked_get:
            mocked_get.return_value.status_code = 200
            mocked_get.return_value.json.return_value = {'daily': [{'dt': 1609459200}]}
            data = fetch_weather_data(40.712776, -74.005974, 'metric', 'en')
            self.assertIn('daily', data)

if __name__ == '__main__':
    unittest.main()