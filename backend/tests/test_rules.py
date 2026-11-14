from app.data import CROPS
from app.rules import advice, alerts, judge

HOT_DRY = {"rain": [0, 0, 0, 0, 2, 0, 0], "pop": [5] * 7, "hi": [37] * 7, "lo": [23] * 7}
STEADY = {"rain": [8, 14, 6, 0, 12, 10, 5], "pop": [50] * 7, "hi": [31] * 7, "lo": [22] * 7}
STORM = {"rain": [2, 64, 38, 22, 9, 5, 0], "pop": [90] * 7, "hi": [28] * 7, "lo": [22] * 7}


def test_plant_when_steady_rain():
    assert judge(STEADY, CROPS["maize"])["k"] == "plant"


def test_wait_when_heavy_rain_soon():
    j = judge(STORM, CROPS["maize"])
    assert j["k"] == "wait" and j["n"] >= 2


def test_dry_when_too_little_rain():
    assert judge(HOT_DRY, CROPS["maize"])["k"] == "dry"


def test_alerts_flag_dry_spell_and_heat():
    text = " ".join(alerts(HOT_DRY))
    assert "Dry spell" in text and "Heat" in text


def test_message_is_localised():
    assert "Ku shuka" in advice("Abuja", "maize", "ha", STEADY)["message"]
