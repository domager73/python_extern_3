import json


# Weather model
class WeatherData:
    def __init__(self, temperature=None, humidity=None, wind_speed=None, pressure=None,
                 cloud_coverage=None, rain=None):
        self.temperature = temperature
        self.humidity = humidity
        self.wind_speed = wind_speed
        self.pressure = pressure
        self.cloud_coverage = cloud_coverage
        self.rain = rain

    @classmethod
    def from_json(cls, json_data):
        current_data = json_data['current']

        temperature = current_data.get('temperature_2m')
        humidity = current_data.get('relative_humidity_2m')
        wind_speed = current_data.get('wind_speed_10m')
        pressure = current_data.get('surface_pressure')
        cloud_coverage = current_data.get('cloud_cover')
        rain = current_data.get('rain')

        return cls(temperature, humidity, wind_speed, pressure, cloud_coverage, rain)

    def __str__(self):
        return (f"Температура: {self.temperature:.2f}°C, \n"
                f"Влажность: {self.humidity}%, \n"
                f"Скорость ветра: {self.wind_speed} км/ч, \n"
                f"Атмосферное давление: {self.pressure} гПа, \n"
                f"Облачность: {self.cloud_coverage}%, \n"
                f"Дождь за последний час: {self.rain} мм")

    def to_json(self):
        return json.dumps({
            'temperature': self.temperature,
            'humidity': self.humidity,
            'wind_speed': self.wind_speed,
            'pressure': self.pressure,
            'cloud_coverage': self.cloud_coverage,
            'rain': self.rain
        })