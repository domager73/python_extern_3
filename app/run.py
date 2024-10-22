from dotenv import load_dotenv
from flask import Flask, jsonify, request, render_template
import os

from app.utils.consts import Constants
from app.service.remote.api.accu_weather_api import WeatherAPI
from weather_model.weather_model import WeatherEvaluator

load_dotenv()

weather_api = WeatherAPI(os.getenv('WEATHER_API_KEY'))

app = Flask(__name__)


#иннициализация веб приложени
@app.route('/')
def index():
    return render_template('index.html')


#логика ux в вебе
# Роут для сайта
@app.route('/evaluate-weather', methods=['POST'])
def evaluate_weather():
    input_method = request.form.get('input_method')

    if input_method == 'city':
        departure_city = request.form.get('departure_city')
        destination_city = request.form.get('destination_city')

        if not departure_city or not destination_city:
            return render_template('index.html',
                                   weather=Constants.REQUIRED_CITY_MESSAGE,
                                   departure_city=departure_city,
                                   destination_city=destination_city,
                                   input_method=input_method)

        try:
            weather_departure = weather_api.get_weather_by_city(departure_city)
        except Exception as e:
            return render_template('index.html',
                                   weather=Constants.DEPARTURE_CITY_NOT_FOUND,
                                   departure_city=departure_city,
                                   destination_city=destination_city,
                                   input_method=input_method)

        try:
            weather_destination = weather_api.get_weather_by_city(destination_city)
        except Exception as e:
            return render_template('index.html',
                                   weather=Constants.DESTINATION_CITY_NOT_FOUND,
                                   departure_city=departure_city,
                                   destination_city=destination_city,
                                   input_method=input_method)

    elif input_method == 'coordinates':
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
            weather_departure = weather_api.get_weather_by_coordinates(departure_lat, departure_lon)
        except Exception as e:
            return render_template('index.html',
                                   weather=Constants.DEPARTURE_LOCATION_NOT_FOUND,
                                   departure_lat=departure_lat,
                                   departure_lon=departure_lon,
                                   destination_lat=destination_lat,
                                   destination_lon=destination_lon,
                                   input_method=input_method)

        try:
            weather_destination = weather_api.get_weather_by_coordinates(destination_lat, destination_lon)
        except Exception as e:
            return render_template('index.html',
                                   weather=Constants.DESTINATION_LOCATION_NOT_FOUND,
                                   departure_lat=departure_lat,
                                   departure_lon=departure_lon,
                                   destination_lat=destination_lat,
                                   destination_lon=destination_lon,
                                   input_method=input_method)

    evaluator = WeatherEvaluator()

    if weather_departure and weather_destination:
        departure_evaluation = evaluator.evaluate(weather_departure)
        destination_evaluation = evaluator.evaluate(weather_destination)

        return render_template('index.html',
                               departure_weather=departure_evaluation,
                               destination_weather=destination_evaluation,
                               departure_city=departure_city if input_method == 'city' else None,
                               destination_city=destination_city if input_method == 'city' else None,
                               departure_lat=departure_lat if input_method == 'coordinates' else None,
                               departure_lon=departure_lon if input_method == 'coordinates' else None,
                               destination_lat=destination_lat if input_method == 'coordinates' else None,
                               destination_lon=destination_lon if input_method == 'coordinates' else None,
                               input_method=input_method)
    else:
        return render_template('index.html',
                               weather=Constants.WEATHER_NOT_AVAILABLE,
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
        weather_data = weather_api.get_weather_by_coordinates(latitude, longitude)
    except Exception as e:
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
        weather_data = weather_api.get_weather_by_city(city)
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
        weather_data = weather_api.get_weather_by_city(city)
    except Exception as e:
        return jsonify({"error": Constants.CITY_NOT_FOUND}), 400

    if weather_data:
        evaluator = WeatherEvaluator()
        weather_evaluation = evaluator.evaluate(weather_data)
        return jsonify({"evaluation": weather_evaluation})
    else:
        return jsonify({"error": Constants.WEATHER_NOT_AVAILABLE}), 500

#запуск
app.run(debug=True)
