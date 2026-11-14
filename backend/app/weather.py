"""Weather source: Open-Meteo (free, no API key). Results cached for 30 minutes."""
import time

import httpx

from .data import CITIES

_CACHE: dict[str, tuple[float, dict]] = {}
TTL = 30 * 60
URL = "https://api.open-meteo.com/v1/forecast"


def get_forecast(city: str) -> dict:
    """Return 7-day lists: rain (mm), pop (rain chance %), hi and lo (deg C)."""
    hit = _CACHE.get(city)
    if hit and time.time() - hit[0] < TTL:
        return hit[1]
    lat, lon = CITIES[city]
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "precipitation_sum,precipitation_probability_max,temperature_2m_max,temperature_2m_min",
        "timezone": "Africa/Lagos",
    }
    r = httpx.get(URL, params=params, timeout=10)
    r.raise_for_status()
    d = r.json()["daily"]
    data = {
        "rain": [v or 0 for v in d["precipitation_sum"]],
        "pop": [v or 0 for v in d["precipitation_probability_max"]],
        "hi": d["temperature_2m_max"],
        "lo": d["temperature_2m_min"],
    }
    _CACHE[city] = (time.time(), data)
    return data


# ---- Full weather (current conditions + 7-day outlook) for the weather panel
_WX_CACHE: dict[str, tuple[float, dict]] = {}


def condition(code) -> str:
    """Turn an Open-Meteo weather code into plain words."""
    if code is None:
        return "Cloudy"
    names = {0: "Clear sky", 1: "Mostly clear", 2: "Partly cloudy", 3: "Overcast", 45: "Fog", 48: "Fog"}
    if code in names:
        return names[code]
    if 51 <= code <= 57:
        return "Drizzle"
    if code in (61, 66):
        return "Light rain"
    if code in (63, 67):
        return "Rain"
    if code == 65:
        return "Heavy rain"
    if code in (80, 81):
        return "Showers"
    if code == 82:
        return "Heavy showers"
    if code >= 95:
        return "Thunderstorm"
    return "Cloudy"


def get_weather(city: str) -> dict:
    """Current conditions plus a 7-day outlook with a plain-words label per day."""
    hit = _WX_CACHE.get(city)
    if hit and time.time() - hit[0] < TTL:
        return hit[1]
    lat, lon = CITIES[city]
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
        "daily": "weather_code,precipitation_sum,precipitation_probability_max,temperature_2m_max,temperature_2m_min",
        "timezone": "Africa/Lagos",
    }
    r = httpx.get(URL, params=params, timeout=10)
    r.raise_for_status()
    j = r.json()
    cur, d = j["current"], j["daily"]
    data = {
        "current": {
            "temp": cur["temperature_2m"],
            "humidity": cur["relative_humidity_2m"],
            "wind": cur["wind_speed_10m"],
            "label": condition(cur["weather_code"]),
        },
        "daily": {
            "rain": [v or 0 for v in d["precipitation_sum"]],
            "pop": [v or 0 for v in d["precipitation_probability_max"]],
            "hi": d["temperature_2m_max"],
            "lo": d["temperature_2m_min"],
            "label": [condition(c) for c in d["weather_code"]],
        },
    }
    _WX_CACHE[city] = (time.time(), data)
    return data
