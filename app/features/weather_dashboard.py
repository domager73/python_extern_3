from dash import Dash, dcc, html, dash
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from app.service.remote.api.accu_weather_api import WeatherAPI


def init_dash_graphics_app(flask_app):
    dash_app = Dash(__name__, server=flask_app, url_base_pathname='/dashboard/')

    dash_app.layout = html.Div([
        dcc.Location(id='url', refresh=True),
        html.H1("Оценка погоды с Dashboard", style={'textAlign': 'center', 'marginBottom': '20px'}),
        html.Div([
            dcc.Input(
                id='city-input',
                type='text',
                placeholder="Enter a city",
                style={
                    'width': '300px',
                    'height': '40px',
                    'fontSize': '18px',
                    'marginBottom': '20px'
                },
                value='Йошкар-Ола'
            ),
            dcc.Dropdown(
                id='forecast-dropdown',
                options=[
                    {'label': '1-Day Forecast', 'value': 1},
                    {'label': '3-Day Forecast', 'value': 3},
                    {'label': '7-Day Forecast', 'value': 7},
                ],
                value=3,
                style={'marginBottom': '20px'}
            ),
            dcc.Dropdown(
                id='weather-parameter-dropdown',
                options=[
                    {'label': 'Температура (°C)', 'value': 'temperature_2m'},
                    {'label': 'Влажность (%)', 'value': 'relative_humidity_2m'},
                    {'label': 'Дождь (мм)', 'value': 'rain'},
                    {'label': 'Облачность (%)', 'value': 'cloud_cover'},
                    {'label': 'Атмосферное давление (гПа)', 'value': 'surface_pressure'},
                    {'label': 'Скорость ветра (м/с)', 'value': 'wind_speed_10m'}
                ],
                value='temperature_2m',
                style={'marginBottom': '20px'}
            ),
        ], style={'margin': '20px'}),
        dcc.Graph(id='temp-graph', style={'marginBottom': '20px'}),
        html.Button("Вернуться на главную", id="back-button", n_clicks=0,
                    style={
                        'fontSize': '18px',
                        'padding': '10px 20px',
                        'margin': '10px',
                        'backgroundColor': '#007bff',
                        'color': 'white',
                    }),
    ], style={'padding': '20px'})

    @dash_app.callback(
        Output('temp-graph', 'figure'),
        Input('city-input', 'value'),
        Input('forecast-dropdown', 'value'),
        Input('weather-parameter-dropdown', 'value'),
    )
    def update_graph(selected_city, forecast_days, weather_parameter):
        if selected_city and forecast_days and weather_parameter:
            try:
                coordinates = WeatherAPI.get_coordinates_by_city(selected_city)
                variable_by_time = WeatherAPI.get_weather_variables_by_time(
                    coordinates.lat, coordinates.lon,
                    weather_parameter, forecast_days
                )
                figure = go.Figure([
                    go.Scatter(x=variable_by_time.times, y=variable_by_time.variable, mode='lines',
                               name=weather_parameter)
                ])

                figure.update_layout(title=f"{forecast_days}-Day Forecast in {selected_city}")
                return figure
            except Exception as e:
                print(e)
        return go.Figure()

    @dash_app.callback(
        Output('url', 'pathname'),
        Input('back-button', 'n_clicks')
    )
    def go_back(n_clicks):
        if n_clicks > 0:
            return '/'
        return dash.no_update

    return dash_app
