from dash import Dash, dcc, html, Input, Output, State, dash
import dash_leaflet as dl
import dash_bootstrap_components as dbc
from app.service.remote.api.accu_weather_api import WeatherAPI
from dash.dependencies import ALL

from weather_model.weather_model import WeatherEvaluator


def init_dash_map_app(flask_app):
    dash_app = Dash(__name__, server=flask_app, url_base_pathname='/dashboard2/')

    # UI на странице
    dash_app.layout = html.Div([
        html.H1("Постройка пути + оценка погоды", style={'textAlign': 'center', 'marginBottom': '20px'}),
        html.H3("Введите город отправления", style={'textAlign': 'center', 'marginBottom': '20px'}),
        dcc.Input(
            id='departure-city',
            type='text',
            placeholder="Departure City",
            style={
                'width': '300px',
                'height': '40px',
                'fontSize': '18px',
                'marginBottom': '20px'
            },
            value='Казань'
        ),
        html.H3("Введите город прибытия", style={'textAlign': 'center', 'marginBottom': '20px'}),
        dcc.Input(
            id='destination-city',
            type='text',
            placeholder="Departure City",
            style={
                'width': '300px',
                'height': '40px',
                'fontSize': '18px',
                'marginBottom': '20px'
            },
            value='Москва'
        ),
        html.H3("Введите промежуточные точки", style={'textAlign': 'center', 'marginBottom': '20px'}),
        html.Button("Add Intermediate City", id="add-city-btn", n_clicks=0),
        html.Div(id="intermediate-cities-container"),
        dl.Map(id='map', center=[55.75, 37.62], zoom=5, style={'width': '100%', 'height': '500px'}),
        dcc.Store(id='intermediate-cities', data=[]),
        html.Div(id="legend", style={'padding': '10px', 'backgroundColor': 'white', 'maxWidth': '300px'}),
        html.Button("Вернуться на главную", id="back-button", n_clicks=0,
                    style={
                        'fontSize': '18px',
                        'padding': '10px 20px',
                        'margin': '10px',
                        'backgroundColor': '#007bff',
                        'color': 'white',
                    }),
    ])

    # Callback для добавления нового поля для промежуточного города
    @dash_app.callback(
        Output('intermediate-cities-container', 'children'),
        Output('intermediate-cities', 'data'),
        Input('add-city-btn', 'n_clicks'),
        State('intermediate-cities', 'data')
    )
    def add_city_input(n_clicks, cities):
        if n_clicks > len(cities):  # Если кликнули "Add", добавляем поле
            cities.append('')
        return [dcc.Input(id={'type': 'city-input', 'index': i}, type='text', placeholder=f'Intermediate City {i + 1}',
                          value=city)
                for i, city in enumerate(cities)], cities

    # Callback для обновления карты и легенды
    @dash_app.callback(
        Output('map', 'children'),
        Output('legend', 'children'),
        Input('departure-city', 'value'),
        Input('destination-city', 'value'),
        Input({'type': 'city-input', 'index': ALL}, 'value')
    )
    def update_map(departure_city, destination_city, intermediate_cities):
        try:
            # Получение координат для отправного и конечного пунктов
            departure_cor = WeatherAPI.get_coordinates_by_city(departure_city)
            destination_cor = WeatherAPI.get_coordinates_by_city(destination_city)

            # Проверка промежуточных точек
            intermediate_positions = []
            for city in intermediate_cities:
                if city:
                    cor = WeatherAPI.get_coordinates_by_city(city)
                    intermediate_positions.append([cor.lat, cor.lon])

            # Построение маршрута с промежуточными точками
            all_positions = [[departure_cor.lat, departure_cor.lon]] + intermediate_positions + [
                [destination_cor.lat, destination_cor.lon]]

            # Построение маршрута с промежуточными точками
            all_weather = []
            for i in all_positions:
                all_weather.append(WeatherAPI.get_weather_by_coordinates(i[0], i[1]))

            all_evaluate = []
            for i in all_weather:
                all_evaluate.append(WeatherEvaluator().evaluate(i))

            # Добавляем маркеры и маршрут
            markers = [
                dl.Marker(position=position, children=[dl.Tooltip(f"{city}: {evaluate}")])
                for position, evaluate, city in
                zip(all_positions, all_evaluate, [departure_city] + intermediate_cities + [destination_city])
            ]

            polyline = dl.Polyline(positions=all_positions, color='blue')

            # Создание легенды
            legend_content = html.Div([
                html.Div(
                    [
                        html.H1(
                            city + ': '
                        ),
                        html.Div(
                            str(weather),
                        ),
                    ],
                    style={'color': 'black', 'fontSize': '14px'})

                for weather, city in zip(all_weather, [departure_city] + intermediate_cities + [destination_city])
            ])

            return markers + [polyline], legend_content

        except Exception as e:
            return [dbc.Alert("Error: " + str(e), color="danger")], "Error: Could not load legend"

    @dash_app.callback(
        Output('url', 'pathname'),
        Input('back-button', 'n_clicks')
    )
    def go_back(n_clicks):
        if n_clicks > 0:
            return '/'
        return dash.no_update

    return dash_app
