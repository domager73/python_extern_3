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


def test_get_weather_by_coords(client):
    response = client.post('/weather/by-coordinates', data=json.dumps({
        'lat': 55.7558,
        'lon': 37.6173
    }), content_type='application/json')

