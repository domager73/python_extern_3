from app.models.weather import WeatherData

#Модель оценивания погоды
class WeatherEvaluator:
    #дефолтные параметры для модели но ты модешь задать свои
    def __init__(self, temp_min=278, temp_max=303, wind_speed_max=10, humidity_max=75, visibility_min=1000,
                 pressure_min=980, pressure_max=1040, cloud_coverage_max=50, rain_max=0.2):
        self.temp_min = temp_min
        self.temp_max = temp_max
        self.wind_speed_max = wind_speed_max
        self.humidity_max = humidity_max
        self.visibility_min = visibility_min
        self.pressure_min = pressure_min
        self.pressure_max = pressure_max
        self.cloud_coverage_max = cloud_coverage_max
        self.rain_max = rain_max

    def is_bad_weather(self, weather_data: WeatherData):
        if weather_data.temperature < self.temp_min or weather_data.temperature > self.temp_max:
            return True
        if weather_data.wind_speed > self.wind_speed_max:
            return True
        if weather_data.humidity > self.humidity_max:
            return True
        if weather_data.visibility < self.visibility_min:
            return True
        if weather_data.pressure < self.pressure_min or weather_data.pressure > self.pressure_max:
            return True
        if weather_data.cloud_coverage > self.cloud_coverage_max:
            return True
        if weather_data.rain > self.rain_max:
            return True

        return False

    def evaluate(self, weather_data):
        if self.is_bad_weather(weather_data):
            return "Неблагоприятные условия"
        else:
            return "Хорошие условия"
