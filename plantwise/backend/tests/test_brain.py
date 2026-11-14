from app import brain

STEADY = {"rain": [8, 14, 6, 0, 12, 10, 5], "pop": [50, 70, 50, 20, 60, 55, 40], "hi": [31] * 7, "lo": [22] * 7}
HOT_DRY = {"rain": [0, 0, 0, 0, 2, 0, 0], "pop": [5] * 7, "hi": [38] * 7, "lo": [23] * 7}


def ask(msg, fc=STEADY, lang="en"):
    return brain.ask_brain(msg, [], "Ibadan", "maize", fc, lang)


def test_plant_advice_english():
    assert "Plant maize" in ask("Should I plant maize today?")


def test_pidgin_is_detected():
    assert "You fit plant" in ask("Abeg make I plant maize?")


def test_hausa_greeting():
    assert ask("Sannu").startswith("Sannu! Ni ce Ore")


def test_yoruba_question():
    assert "Òjò" in ask("Ṣé kí n gbin agbado?") or "gbin" in ask("Ṣé kí n gbin agbado?")


def test_rain_numbers():
    assert "mm" in ask("When will it rain?")


def test_water_dry_vs_wet():
    assert "may not need to water" in ask("Should I water my maize?")
    assert "Water your" in ask("Should I water my maize?", HOT_DRY)


def test_heat():
    assert "very hot" in ask("Is it too hot today?", HOT_DRY)


def test_pests_go_to_extension_officer():
    assert "extension officer" in ask("What pesticide should I spray on armyworm?")


def test_tips():
    assert "75 cm" in ask("How to plant maize?")


def test_harvest_window():
    assert "harvest" in ask("When should I harvest my rice?").lower()


def test_unknown():
    assert "not sure" in ask("What is the capital of France?")


def test_other_city(monkeypatch):
    monkeypatch.setattr(brain, "get_forecast", lambda c: HOT_DRY)
    assert "Kano" in ask("Will it rain in Kano?")
