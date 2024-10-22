import json

#Модель погоды
class WeatherData:
    def __init__(self, temperature=None, humidity=None, wind_speed=None, pressure=None, visibility=None,
                 cloud_coverage=None, rain=None):
        self.temperature = temperature
        self.humidity = humidity
        self.wind_speed = wind_speed
        self.pressure = pressure
        self.visibility = visibility
        self.cloud_coverage = cloud_coverage
        self.rain = rain

    @classmethod
    def from_json(cls, json_data):
        temperature = json_data['main'].get('temp')
        humidity = json_data['main'].get('humidity')
        wind_speed = json_data['wind'].get('speed')
        pressure = json_data['main'].get('pressure')
        visibility = json_data.get('visibility')
        cloud_coverage = json_data['clouds'].get('all')
        rain = json_data.get('rain', {}).get('1h', 0)

        return cls(temperature, humidity, wind_speed, pressure, visibility, cloud_coverage, rain)

    def __str__(self):
        return (f"Температура: {self.temperature - 273.15:.2f}°C, "
                f"Влажность: {self.humidity}%, "
                f"Скорость ветра: {self.wind_speed} м/с, "
                f"Атмосферное давление: {self.pressure} гПа, "
                f"Видимость: {self.visibility} м, "
                f"Облачность: {self.cloud_coverage}%, "
                f"Дождь за последний час: {self.rain} мм")

    def to_json(self):
        return json.dumps({
            'temperature': self.temperature,
            'humidity': self.humidity,
            'wind_speed': self.wind_speed,
            'pressure': self.pressure,
            'visibility': self.visibility,
            'cloud_coverage': self.cloud_coverage,
            'rain': self.rain
        })
