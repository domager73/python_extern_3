import pytest
import json
from app.run import app

# иннициализация проекта
@pytest.fixture()
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# Проверка работоспособности сайта
def test_index(client):
    response = client.get('/')
    assert response.status_code == 200

# Далее идут просто тесты на то что функции отрабатывают правильно и выдают корректные значения при разных входных
def test_get_weather_by_coords(client):
    response = client.post('/weather/by-coordinates', data=json.dumps({
        'lat': 55.7558,
        'lon': 37.6173
    }), content_type='application/json')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'humidity' in data
    assert type(data['temperature']) == float

def test_get_error_weather_by_coords(client):
    response = client.post('/weather/by-coordinates', data=json.dumps({
        'lat': 55.7558,
        'lon': 'a12.1231'
    }), content_type='application/json')

    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_get_weather_by_city(client):
    response = client.post('/weather/by-city', data=json.dumps({
        'city': 'Йошкар-Ола'
    }), content_type='application/json')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'humidity' in data
    assert type(data['temperature']) == float

def test_get_error_weather_by_city(client):
    response = client.post('/weather/by-city', data=json.dumps({
        'city': 'asdfasdfa'
    }), content_type='application/json')

    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_get_weather_evaluation(client):
    response = client.post('/weather/evaluation', data=json.dumps({
        'city': 'Казань'
    }), content_type='application/json')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['evaluation'] in ['Неблагоприятные условия', 'Благоприятные условия']

def test_get_error_weather_evaluation(client):
    response = client.post('/weather/evaluation', data=json.dumps({
        'caty': 'Казань'
    }), content_type='application/json')

    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
