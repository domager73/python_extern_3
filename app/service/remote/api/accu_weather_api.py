import requests

from app.models.coordinate import Coordinate
from app.models.variables_by_times import VariablesByTimes
from app.models.weather import WeatherData
from app.service.remote.api.routes.routes_name import RoutesName
from app.utils.consts import WeatherVariables
from app.utils.functions import UtilFunctions


#класс запросов к апишке
class WeatherAPI:
    @classmethod
    def get_weather_by_coordinates(cls, lat, lon):
        weather_url = f"{RoutesName.forecast_api}{RoutesName.forecast}"
        params = {
            'latitude': lat,
            'longitude': lon,
            'current': ','.join(WeatherVariables.all_variables()),
            'forecast_days': 1,
        }
        response = requests.get(weather_url, params=params)

        if response.status_code != 200:
            return Exception()

        data = response.json()

        try:
            weather_data = WeatherData.from_json(data)

            return weather_data
        except Exception as e:
            return e

    @classmethod
    def get_coordinates_by_city(cls, city):
        weather_url = f"{RoutesName.geocoding_api}{RoutesName.search_coordinates}"

        params = {
            'name': city,
            'language': UtilFunctions.getLanguage(city),
        }

        response = requests.get(weather_url, params=params)

        if response.status_code != 200:
            return Exception("Error fetching data from API")

        data = response.json()

        try:
            coordinate = Coordinate.from_json(data)
            return coordinate
        except Exception as e:
            return e

    @classmethod
    def get_weather_variables_by_time(cls, lat, lon, hourly, forecast_days):
        weather_url = f"{RoutesName.forecast_api}{RoutesName.forecast}"
        params = {
            'latitude': lat,
            'longitude': lon,
            'hourly': hourly,
            'forecast_days': forecast_days
        }

        response = requests.get(weather_url, params=params)

        if response.status_code != 200:
            return Exception()

        data = response.json()

        try:
            variable_by_times = VariablesByTimes.from_json(data, hourly)

            return variable_by_times
        except Exception as e:
            return e
