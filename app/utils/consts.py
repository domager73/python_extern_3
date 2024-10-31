# Константные надписи для юзера

class Constants:
    REQUIRED_CITY_MESSAGE = "Необходимо указать оба города."
    DEPARTURE_CITY_NOT_FOUND = "Город отправления не найден."
    DESTINATION_CITY_NOT_FOUND = "Город назначения не найден."
    REQUIRED_COORDINATES_MESSAGE = "Необходимо указать оба набора координат."
    DEPARTURE_LOCATION_NOT_FOUND = "Местоположение отправления не найдено."
    DESTINATION_LOCATION_NOT_FOUND = "Местоположение назначения не найдено."
    WEATHER_NOT_AVAILABLE = "Данные о погоде недоступны."
    LAT_LONG_REQUIRED = "Необходимо указать широту и долготу"
    CITY_NOT_FOUND = "Город не найден"


class WeatherVariables:
    TEMPERATURE = "temperature_2m"
    HUMIDITY = "relative_humidity_2m"
    RAIN = "rain"
    CLOUD_COVER = "cloud_cover"
    PRESSURE = "surface_pressure"
    WIND_SPEED = "wind_speed_10m"

    @classmethod
    def all_variables(cls):
        return [value for key, value in vars(cls).items() if not key.startswith('__') and key != 'all_variables']

parameter_labels = {
    'temperature_2m': 'Температура (°C)',
    'relative_humidity_2m': 'Влажность (%)',
    'rain': 'Дождь (мм)',
    'cloud_cover': 'Облачность (%)',
    'surface_pressure': 'Атмосферное давление (гПа)',
    'wind_speed_10m': 'Скорость ветра (м/с)'
}

