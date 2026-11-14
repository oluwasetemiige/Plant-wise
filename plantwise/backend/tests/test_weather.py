from app import weather


def test_condition_words():
    assert weather.condition(0) == "Clear sky"
    assert weather.condition(63) == "Rain"
    assert weather.condition(95) == "Thunderstorm"
    assert weather.condition(None) == "Cloudy"


def test_get_weather_shape(monkeypatch):
    payload = {
        "current": {"temperature_2m": 29.4, "relative_humidity_2m": 70, "wind_speed_10m": 8.2, "weather_code": 2},
        "daily": {
            "weather_code": [63] * 7,
            "precipitation_sum": [5, None, 0, 0, 1, 2, 3],
            "precipitation_probability_max": [60] * 7,
            "temperature_2m_max": [31] * 7,
            "temperature_2m_min": [22] * 7,
        },
    }

    class Resp:
        def raise_for_status(self):
            pass

        def json(self):
            return payload

    monkeypatch.setattr(weather.httpx, "get", lambda *a, **k: Resp())
    weather._WX_CACHE.clear()
    w = weather.get_weather("Lagos")
    assert w["current"]["label"] == "Partly cloudy"
    assert w["daily"]["rain"][1] == 0 and len(w["daily"]["label"]) == 7
