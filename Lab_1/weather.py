import datetime as dt
import json

import requests
from flask import Flask, jsonify, request

# create your API token, and set it up in Postman collection as part of the Body section
API_TOKEN = "Mohyla"
# you can get API keys for free here - https://api-docs.pgamerx.com/
WEATHER_API_KEY = "1b1a01833275400e8bd155229231902"

app = Flask(__name__)


def getWeather(location: str, date: str):
    url_base = "http://api.weatherapi.com/v1/history.json"
    query_params = {
        "key": WEATHER_API_KEY,
        "q":location,
        "dt": date
    }
    url = f"{url_base}"
    payload = {}
    headers = {"Authorization": WEATHER_API_KEY}

    response = requests.request("GET", url, headers=headers, data=payload, params=query_params)
    return json.loads(response.text)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/")
def home_page():
    return "<p><h2>KMA L2: Python Saas.</h2></p>"


@app.route(
    "/content/api/v1/integration/generate",
    methods=["POST"],
)
def weather_endpoint():
    json_data = request.get_json()

    if json_data.get("token") is None:
        raise InvalidUsage("token is required", status_code=400)

    token = json_data.get("token")

    if token != API_TOKEN:
        raise InvalidUsage("wrong API token", status_code=403)

    weather = getWeather(json_data.get("location"), json_data.get("date"));
    result = {
        "requester_name": json_data.get('requester_name'),
        "timestamp": weather['location']['localtime'],
        "location": json_data['location'],
        "date": json_data['date'],
        "weather": {
            "temp_c": weather['forecast']['forecastday'][0]['day']['avgtemp_c'],
            "wind_kph": weather['forecast']['forecastday'][0]['day']['maxwind_mph'],
            "pressure_mb": weather['forecast']['forecastday'][0]['hour'][0]['pressure_mb'],
            "humidity": weather['forecast']['forecastday'][0]['day']['avghumidity']
        }
    }

    return result;