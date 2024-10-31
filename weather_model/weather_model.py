from app.models.weather import WeatherData

#Модель оценивания погоды
class WeatherEvaluator:
    #дефолтные параметры для модели но ты модешь задать свои
    def __init__(self, temp_min=5, temp_max=30, wind_speed_max=10, humidity_max=90,
                 pressure_min=980, pressure_max=1040, cloud_coverage_max=50, rain_max=0.2):
        self.temp_min = temp_min
        self.temp_max = temp_max
        self.wind_speed_max = wind_speed_max
        self.humidity_max = humidity_max
        self.pressure_min = pressure_min
        self.pressure_max = pressure_max
        self.cloud_coverage_max = cloud_coverage_max
        self.rain_max = rain_max

    def is_bad_weather(self, weather_data):
        if weather_data.temperature < self.temp_min or weather_data.temperature > self.temp_max:
            return 'Температура вне допустимых пределов.'
        if weather_data.wind_speed > self.wind_speed_max:
            return 'Сильная скорость ветра.'
        if weather_data.humidity > self.humidity_max:
            return 'Высокая влажность.'
        if weather_data.pressure < self.pressure_min or weather_data.pressure > self.pressure_max:
            return 'Атмосферное давление вне допустимых пределов.'
        if weather_data.cloud_coverage > self.cloud_coverage_max:
            return 'Высокая облачность.'
        if weather_data.rain > self.rain_max:
            return 'Возможен дождь'

        return False

    def evaluate(self, weather_data):
        is_bad = self.is_bad_weather(weather_data)

        if is_bad:
            return "Неблагоприятные условия: " + is_bad
        else:
            return "Хорошие условия"
