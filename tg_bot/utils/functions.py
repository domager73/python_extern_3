import re

from tg_bot.utils.consts import Consts
from plotly import graph_objs as go

import numpy as np


class UtilFunctions:
    @staticmethod
    def key_to_label(label):
        return Consts.weather_variables.get(label)

    @staticmethod
    def label_to_key(key):
        for label, mapping_key in Consts.weather_variables.items():
            if mapping_key == key:
                return label
        return None

    @staticmethod
    def create_plot(departure_city, destination_city, start_weather, end_weather,hourly):
        fig = go.Figure()

        # Основные линии графика
        fig.add_trace(
            go.Scatter(x=start_weather.times, y=start_weather.variable, mode='lines+markers', name=departure_city))
        fig.add_trace(
            go.Scatter(x=end_weather.times, y=end_weather.variable, mode='lines+markers', name=destination_city))

        # Средние значения
        start_avg = np.mean(start_weather.variable)
        end_avg = np.mean(end_weather.variable)

        # Добавление горизонтальных линий для средних значений
        fig.add_trace(
            go.Scatter(x=start_weather.times, y=[start_avg] * len(start_weather.times),
                       mode='lines', name=f"Среднее ({departure_city})", line=dict(dash='dash'))
        )
        fig.add_trace(
            go.Scatter(x=end_weather.times, y=[end_avg] * len(end_weather.times),
                       mode='lines', name=f"Среднее ({destination_city})", line=dict(dash='dash'))
        )

        fig.update_layout(
            title='Прогноз погоды',
            xaxis_title='Дни',
            yaxis_title=hourly,
            legend=dict(x=0, y=1.0)
        )

        # Сохранение графика в файл
        fig.write_image("weather_plot.png")

    @staticmethod
    def is_number_colon_number(string):
        pattern = r"^\d+(\.\d+)?:\d+(\.\d+)?$"
        return bool(re.match(pattern, string))
