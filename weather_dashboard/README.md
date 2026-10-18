# Weather Dashboard

This small Flask-based weather dashboard is adapted into the repository 103M_Testing_Malkin_DA.

It uses Nominatim (OpenStreetMap) for geocoding and Open‑Meteo for weather forecasts (no API keys required).

Run locally:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r weather_dashboard/requirements.txt
python weather_dashboard/app.py
```

Open http://localhost:5000/weather
