import requests

from app.models.weather import WeatherData
from app.service.remote.api.routes.routes_name import RoutesName

#класс запросов к апишке
class WeatherAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = RoutesName.base_url

    def get_weather_by_coordinates(self, lat, lon):
        weather_url = f"{self.base_url}{RoutesName.get_weather}"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.api_key
        }
        response = requests.get(weather_url, params=params)
        data = response.json()

        # Обработка того что таких координат не существует
        if data['cod'] == 404:
            return Exception()

        if data:
            weather_data = WeatherData.from_json(data)

            return weather_data
        return None

    def get_weather_by_city(self, city):
        weather_url = f"{self.base_url}{RoutesName.get_weather}"
        params = {
            'q': city,
            'appid': self.api_key
        }

        response = requests.get(weather_url, params=params)
        data = response.json()


        # Обработка того что такого города не существует
        if data['cod'] == 404:
            return Exception()

        if data:
            weather_data = WeatherData.from_json(data)

            return weather_data
        return None
