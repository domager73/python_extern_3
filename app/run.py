from dotenv import load_dotenv
from flask import jsonify, request

from app.features.geomap import init_dash_map_app
from app.features.weather_dashboard import init_dash_graphics_app
from app.utils.consts import Constants
from weather_model.weather_model import WeatherEvaluator

from flask import Flask, render_template
from app.service.remote.api.accu_weather_api import WeatherAPI

# понимаю что на git не надо комитить .env но вы бы их ни как не увидели и не запустили проект

load_dotenv()

app = Flask(__name__)

# иннициализация dash board
init_dash_graphics_app(app)
init_dash_map_app(app)


# иннициализация веб приложени
@app.route('/')
def index():
    return render_template('index.html', input_method="city")


# логика ux в вебе
# Роут для сайта
@app.route('/evaluate-weather', methods=['POST'])
def evaluate_weather():
    input_method = request.form.get('input_method', 'city')
    waypoints = []

    if input_method == 'city':
        # Извлечение промежуточных городов
        waypoint_index = 1
        while request.form.get(f'waypoint_city_{waypoint_index}'):
            waypoints.append(request.form.get(f'waypoint_city_{waypoint_index}'))
            waypoint_index += 1

        departure_city = request.form.get('departure_city')
        destination_city = request.form.get('destination_city')

        if not departure_city or not destination_city:
            return render_template('index.html',
                                   weather=Constants.REQUIRED_CITY_MESSAGE,
                                   departure_city=departure_city,
                                   destination_city=destination_city,
                                   input_method=input_method)

        try:
            weather_departure_coordinate = WeatherAPI.get_coordinates_by_city(departure_city)
            weather_departure = WeatherAPI.get_weather_by_coordinates(
                weather_departure_coordinate.lat, weather_departure_coordinate.lon)
        except Exception:
            return render_template('index.html',
                                   weather=Constants.DEPARTURE_CITY_NOT_FOUND,
                                   departure_city=departure_city,
                                   destination_city=destination_city,
                                   input_method=input_method)

        try:
            weather_destination_coordinate = WeatherAPI.get_coordinates_by_city(destination_city)
            weather_destination = WeatherAPI.get_weather_by_coordinates(
                weather_destination_coordinate.lat, weather_destination_coordinate.lon)
        except Exception:
            return render_template('index.html',
                                   weather=Constants.DESTINATION_CITY_NOT_FOUND,
                                   departure_city=departure_city,
                                   destination_city=destination_city,
                                   input_method=input_method)

    elif input_method == 'coordinates':
        # Извлечение промежуточных координат
        waypoint_index = 1
        while request.form.get(f'waypoint_lat_{waypoint_index}') and request.form.get(f'waypoint_lon_{waypoint_index}'):
            lat = request.form.get(f'waypoint_lat_{waypoint_index}')
            lon = request.form.get(f'waypoint_lon_{waypoint_index}')
            waypoints.append((lat, lon))
            waypoint_index += 1

        departure_lat = request.form.get('departure_lat')
        departure_lon = request.form.get('departure_lon')
        destination_lat = request.form.get('destination_lat')
        destination_lon = request.form.get('destination_lon')

        if not (departure_lat and departure_lon and destination_lat and destination_lon):
            return render_template('index.html',
                                   weather=Constants.REQUIRED_COORDINATES_MESSAGE,
                                   departure_lat=departure_lat,
                                   departure_lon=departure_lon,
                                   destination_lat=destination_lat,
                                   destination_lon=destination_lon,
                                   input_method=input_method)

        try:
            weather_departure = WeatherAPI.get_weather_by_coordinates(departure_lat, departure_lon)
        except Exception:
            return render_template('index.html',
                                   weather=Constants.DEPARTURE_LOCATION_NOT_FOUND,
                                   departure_lat=departure_lat,
                                   departure_lon=departure_lon,
                                   destination_lat=destination_lat,
                                   destination_lon=destination_lon,
                                   input_method=input_method)

        try:
            weather_destination = WeatherAPI.get_weather_by_coordinates(destination_lat, destination_lon)
        except Exception:
            return render_template('index.html',
                                   weather=Constants.DESTINATION_LOCATION_NOT_FOUND,
                                   departure_lat=departure_lat,
                                   departure_lon=departure_lon,
                                   destination_lat=destination_lat,
                                   destination_lon=destination_lon,
                                   input_method=input_method)

    evaluator = WeatherEvaluator()

    # Обработка оценок погоды
    evaluations = {}
    if weather_departure:
        evaluations['departure'] = evaluator.evaluate(weather_departure)

    if weather_destination:
        evaluations['destination'] = evaluator.evaluate(weather_destination)

    # Обработка промежуточных точек
    waypoint_evaluations = {}
    for waypoint in waypoints:
        if input_method == 'city':
            # Получаем погоду для промежуточных городов
            try:
                waypoint_weather = WeatherAPI.get_weather_by_coordinates(
                    WeatherAPI.get_coordinates_by_city(waypoint).lat,
                    WeatherAPI.get_coordinates_by_city(waypoint).lon
                )
                waypoint_evaluations[waypoint] = evaluator.evaluate(waypoint_weather)
            except Exception:
                waypoint_evaluations[waypoint] = Constants.WEATHER_NOT_AVAILABLE
        else:
            # Получаем погоду для промежуточных координат
            lat, lon = waypoint
            try:
                waypoint_weather = WeatherAPI.get_weather_by_coordinates(lat, lon)
                waypoint_evaluations[f"{lat}, {lon}"] = evaluator.evaluate(waypoint_weather)
            except Exception:
                waypoint_evaluations[f"{lat}, {lon}"] = Constants.WEATHER_NOT_AVAILABLE

    return render_template('index.html',
                           departure_weather=evaluations.get('departure'),
                           destination_weather=evaluations.get('destination'),
                           waypoint_evaluations=waypoint_evaluations,
                           departure_city=departure_city if input_method == 'city' else None,
                           destination_city=destination_city if input_method == 'city' else None,
                           departure_lat=departure_lat if input_method == 'coordinates' else None,
                           departure_lon=departure_lon if input_method == 'coordinates' else None,
                           destination_lat=destination_lat if input_method == 'coordinates' else None,
                           destination_lon=destination_lon if input_method == 'coordinates' else None,
                           waypoints=waypoints,
                           input_method=input_method)


# Роуты для web api
@app.route('/weather/by-coordinates', methods=['POST'])
def get_weather_by_coords():
    data = request.get_json()
    latitude = data.get('lat')
    longitude = data.get('lon')

    if latitude is None or longitude is None:
        return jsonify({"error": Constants.LAT_LONG_REQUIRED}), 400

    try:
        weather_data = WeatherAPI.get_weather_by_coordinates(latitude, longitude)
    except:
        return jsonify({"error": Constants.CITY_NOT_FOUND}), 400

    if weather_data:
        return weather_data.to_json()
    else:
        return jsonify({"error": Constants.WEATHER_NOT_AVAILABLE}), 500


@app.route('/weather/by-city', methods=['POST'])
def get_weather_by_city():
    data = request.get_json()
    city = data.get('city')

    if not city:
        return jsonify({"error": "Необходимо указать название города"}), 400

    try:
        coordinates = WeatherAPI.get_coordinates_by_city(city)

        weather_data = WeatherAPI.get_weather_by_coordinates(coordinates.lat, coordinates.lon)
    except Exception as e:
        return jsonify({"error": Constants.CITY_NOT_FOUND}), 400

    if weather_data:
        return weather_data.to_json()
    else:
        return jsonify({"error": Constants.WEATHER_NOT_AVAILABLE}), 500


@app.route('/weather/evaluation', methods=['POST'])
def get_weather_evaluation():
    data = request.get_json()
    city = data.get('city')

    if not city:
        return jsonify({"error": Constants.LAT_LONG_REQUIRED}), 400

    try:
        coordinates = WeatherAPI.get_coordinates_by_city(city)

        weather_data = WeatherAPI.get_weather_by_coordinates(coordinates.lat, coordinates.lon)
    except Exception as e:
        return jsonify({"error": Constants.CITY_NOT_FOUND}), 400

    if weather_data:
        evaluator = WeatherEvaluator()
        weather_evaluation = evaluator.evaluate(weather_data)
        return jsonify({"evaluation": weather_evaluation})
    else:
        return jsonify({"error": Constants.WEATHER_NOT_AVAILABLE}), 500

# запуск
app.run(port=5001)
