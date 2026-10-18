from flask import Flask, render_template, request, jsonify, url_for
import requests
from urllib.parse import urlencode

app = Flask(__name__, template_folder="templates", static_folder="static")

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

USER_AGENT = "103M_Testing_Malkin_DA-weather/1.0 (github:Agrahm13)"

WEATHERCODE = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Drizzle: Light",
    53: "Drizzle: Moderate",
    55: "Drizzle: Dense",
    61: "Rain: Slight",
    63: "Rain: Moderate",
    65: "Rain: Heavy",
    71: "Snow: Slight",
    73: "Snow: Moderate",
    75: "Snow: Heavy",
    95: "Thunderstorm",
}


def geocode(query, limit=6):
    params = {"q": query, "format": "json", "limit": limit}
    headers = {"User-Agent": USER_AGENT}
    r = requests.get(NOMINATIM_URL, params=params, headers=headers, timeout=10)
    r.raise_for_status()
    return r.json()


def fetch_weather(lat, lon):
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": "true",
        "daily": "temperature_2m_max,temperature_2m_min,weathercode",
        "timezone": "auto",
    }
    r = requests.get(WEATHER_URL, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()

    current = data.get("current_weather")
    daily = data.get("daily")

    result = {
        "current": {
            "temperature": current.get("temperature"),
            "windspeed": current.get("windspeed"),
            "winddirection": current.get("winddirection"),
            "weathercode": current.get("weathercode"),
            "description": WEATHERCODE.get(current.get("weathercode"), "Unknown"),
            "time": current.get("time"),
        },
        "daily": {
            "time": daily.get("time"),
            "max": daily.get("temperature_2m_max"),
            "min": daily.get("temperature_2m_min"),
            "codes": daily.get("weathercode"),
        },
    }
    return result


@app.route("/weather", methods=["GET", "POST"])
def weather():
    query = ""
    places = []
    selected = None
    forecast = None
    error = None

    if request.method == "POST":
        query = request.form.get("query", "").strip()
        if not query:
            error = "Введите город или место"
        else:
            try:
                places = geocode(query)
            except Exception as e:
                error = f"Ошибка геокодирования: {e}"

            if places:
                # If user selected a specific place (lat/lon), prefer that
                sel_index = request.form.get("place_index")
                try:
                    if sel_index is not None and sel_index != "":
                        sel_index = int(sel_index)
                        selected = places[sel_index]
                    else:
                        selected = places[0]

                    lat = float(selected["lat"])
                    lon = float(selected["lon"])
                    forecast = fetch_weather(lat, lon)
                except Exception as e:
                    error = f"Не удалось получить погоду: {e}"

    return render_template(
        "weather_index.html",
        query=query,
        places=places,
        selected=selected,
        forecast=forecast,
        error=error,
    )


@app.route("/api/weather")
def api_weather():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    if not lat or not lon:
        return jsonify({"error": "lat and lon required"}), 400
    try:
        forecast = fetch_weather(float(lat), float(lon))
        return jsonify(forecast)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/")
def index_redirect():
    # Keep the repository's existing README and landing structure in mind;
    # expose the dashboard at /weather and link from root README.
    return ("<html><body><h2>Weather dashboard</h2>"
            "<p>Go to <a href=\"/weather\">/weather</a> to open the dashboard.</p>"
            "</body></html>")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
