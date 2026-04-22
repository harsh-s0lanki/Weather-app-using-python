from flask import Flask, render_template, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

# OpenWeatherMap API configuration
API_KEY = os.environ.get("OPENWEATHER_API_KEY", "YOUR_API_KEY_HERE")
BASE_URL = "https://api.openweathermap.org/data/2.5"
GEO_URL = "https://api.openweathermap.org/geo/1.0"


def kelvin_to_celsius(k):
    return round(k - 273.15, 1)


def kelvin_to_fahrenheit(k):
    return round((k - 273.15) * 9/5 + 32, 1)


def get_wind_direction(degrees):
    dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
            "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    ix = round(degrees / (360 / len(dirs))) % len(dirs)
    return dirs[ix]


def format_weather(data, unit="metric"):
    temp_k = data["main"]["temp"]
    feels_k = data["main"]["feels_like"]
    min_k = data["main"]["temp_min"]
    max_k = data["main"]["temp_max"]

    if unit == "metric":
        temp = kelvin_to_celsius(temp_k)
        feels = kelvin_to_celsius(feels_k)
        temp_min = kelvin_to_celsius(min_k)
        temp_max = kelvin_to_celsius(max_k)
        unit_sym = "°C"
        speed_unit = "m/s"
        wind_speed = round(data["wind"]["speed"], 1)
    else:
        temp = kelvin_to_fahrenheit(temp_k)
        feels = kelvin_to_fahrenheit(feels_k)
        temp_min = kelvin_to_fahrenheit(min_k)
        temp_max = kelvin_to_fahrenheit(max_k)
        unit_sym = "°F"
        speed_unit = "mph"
        wind_speed = round(data["wind"]["speed"] * 2.237, 1)

    sunrise = datetime.fromtimestamp(data["sys"]["sunrise"]).strftime("%H:%M")
    sunset = datetime.fromtimestamp(data["sys"]["sunset"]).strftime("%H:%M")

    return {
        "city": data["name"],
        "country": data["sys"]["country"],
        "temp": temp,
        "feels_like": feels,
        "temp_min": temp_min,
        "temp_max": temp_max,
        "unit": unit_sym,
        "description": data["weather"][0]["description"].title(),
        "icon": data["weather"][0]["icon"],
        "icon_id": data["weather"][0]["id"],
        "humidity": data["main"]["humidity"],
        "pressure": data["main"]["pressure"],
        "visibility": round(data.get("visibility", 0) / 1000, 1),
        "wind_speed": wind_speed,
        "wind_unit": speed_unit,
        "wind_dir": get_wind_direction(data["wind"].get("deg", 0)),
        "clouds": data["clouds"]["all"],
        "sunrise": sunrise,
        "sunset": sunset,
        "timezone": data["timezone"],
        "lat": data["coord"]["lat"],
        "lon": data["coord"]["lon"],
    }


def format_forecast(data, unit="metric"):
    daily = {}
    for item in data["list"]:
        date = datetime.fromtimestamp(item["dt"]).strftime("%Y-%m-%d")
        day_name = datetime.fromtimestamp(item["dt"]).strftime("%A")
        if date not in daily:
            daily[date] = {
                "day": day_name,
                "date": datetime.fromtimestamp(item["dt"]).strftime("%b %d"),
                "temps": [],
                "icons": [],
                "descriptions": [],
            }
        temp_k = item["main"]["temp"]
        temp = kelvin_to_celsius(temp_k) if unit == "metric" else kelvin_to_fahrenheit(temp_k)
        daily[date]["temps"].append(temp)
        daily[date]["icons"].append(item["weather"][0]["icon"])
        daily[date]["descriptions"].append(item["weather"][0]["description"])

    result = []
    for date, d in list(daily.items())[:5]:
        result.append({
            "day": d["day"],
            "date": d["date"],
            "temp_max": max(d["temps"]),
            "temp_min": min(d["temps"]),
            "icon": d["icons"][len(d["icons"])//2],
            "description": d["descriptions"][len(d["descriptions"])//2].title(),
        })
    return result


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/weather")
def weather():
    city = request.args.get("city", "")
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    unit = request.args.get("unit", "metric")

    if not city and not (lat and lon):
        return jsonify({"error": "City or coordinates required"}), 400

    try:
        if lat and lon:
            params = {"lat": lat, "lon": lon, "appid": API_KEY}
        else:
            params = {"q": city, "appid": API_KEY}

        r = requests.get(f"{BASE_URL}/weather", params=params, timeout=10)
        if r.status_code == 404:
            return jsonify({"error": "City not found. Please check the name and try again."}), 404
        if r.status_code == 401:
            return jsonify({"error": "Invalid API key. Please check your OpenWeatherMap API key."}), 401
        r.raise_for_status()
        weather_data = format_weather(r.json(), unit)

        # Fetch 5-day forecast
        fc_r = requests.get(f"{BASE_URL}/forecast", params=params | {"appid": API_KEY}, timeout=10)
        fc_r.raise_for_status()
        forecast = format_forecast(fc_r.json(), unit)
        weather_data["forecast"] = forecast

        return jsonify(weather_data)
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Network error. Please check your connection."}), 503
    except requests.exceptions.Timeout:
        return jsonify({"error": "Request timed out. Please try again."}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/autocomplete")
def autocomplete():
    q = request.args.get("q", "")
    if len(q) < 2:
        return jsonify([])
    try:
        r = requests.get(f"{GEO_URL}/direct", params={"q": q, "limit": 5, "appid": API_KEY}, timeout=5)
        r.raise_for_status()
        results = [
            {"name": c["name"], "country": c["country"], "state": c.get("state", ""),
             "lat": c["lat"], "lon": c["lon"]}
            for c in r.json()
        ]
        return jsonify(results)
    except:
        return jsonify([])


if __name__ == "__main__":
    app.run(debug=True, port=5000)
