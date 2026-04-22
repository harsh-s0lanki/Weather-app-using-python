# ⟡ Zephyr — Weather App

A beautiful, full-featured weather web application built with Python (Flask) and the OpenWeatherMap API.

## Features
- 🌡 Current temperature with feels-like, min/max
- 💨 Wind speed & direction, humidity, pressure, visibility, cloud cover
- 🌅 Sunrise & sunset times with live local clock
- 📅 5-day forecast
- 🔍 City autocomplete search
- 📍 Geolocation (use my location)
- 🌡 °C / °F toggle
- 🗺 Map link for the searched location

## Setup

### 1. Get an API Key
Sign up at [openweathermap.org](https://openweathermap.org/api) (free tier works fine).

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set your API key
**Option A — Environment variable (recommended):**
```bash
export OPENWEATHER_API_KEY=your_key_here
python app.py
```

**Option B — Edit app.py directly:**
Open `app.py` and replace `YOUR_API_KEY_HERE` on line 9 with your key.

### 4. Run
```bash
python app.py
```

Open your browser at **http://localhost:5000**

## Project Structure
```
weather_app/
├── app.py              # Flask backend
├── requirements.txt    # Python dependencies
└── templates/
    └── index.html      # Frontend (HTML/CSS/JS)
```

## API Endpoints
| Endpoint | Params | Description |
|---|---|---|
| `GET /api/weather` | `city` or `lat`+`lon`, `unit` | Current weather + 5-day forecast |
| `GET /api/autocomplete` | `q` | City name suggestions |
