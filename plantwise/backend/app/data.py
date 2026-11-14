"""Static reference data: Nigerian cities and crop thresholds.

Thresholds are starting points. Tune them with local agro-meteorology data.
need = minimum rain (mm) over the next 7 days for planting
over = single-day rain (mm) that risks washing seeds away
"""
CITIES = {
    "Ibadan": (7.38, 3.95),
    "Kano": (12.00, 8.52),
    "Kaduna": (10.52, 7.44),
    "Abuja": (9.06, 7.49),
    "Enugu": (6.46, 7.55),
    "Makurdi": (7.73, 8.52),
    "Ilorin": (8.50, 4.55),
    "Lagos": (6.52, 3.38),
    "Port Harcourt": (4.82, 7.05),
    "Benin City": (6.34, 5.63),
    "Abeokuta": (7.16, 3.35),
    "Akure": (7.25, 5.19),
    "Osogbo": (7.77, 4.56),
    "Owerri": (5.48, 7.03),
    "Calabar": (4.95, 8.33),
    "Minna": (9.61, 6.55),
    "Jos": (9.90, 8.86),
    "Yola": (9.20, 12.48),
    "Maiduguri": (11.85, 13.16),
    "Sokoto": (13.06, 5.24),
}

CROPS = {
    "maize": {"name": "Maize", "need": 25, "over": 45, "yo": "àgbàdo", "ha": "masara"},
    "cassava": {"name": "Cassava", "need": 15, "over": 50, "yo": "gbágùdá", "ha": "rogo"},
    "rice": {"name": "Rice", "need": 45, "over": 80, "yo": "ìrẹsì", "ha": "shinkafa"},
    "tomato": {"name": "Tomato", "need": 20, "over": 35, "yo": "tòmátò", "ha": "tumatir"},
}

LANGUAGES = {"en": "English", "pcm": "Nigerian Pidgin", "yo": "Yorùbá", "ha": "Hausa"}

DEFAULT_PREFS = {"city": "Ibadan", "crop": "maize", "lang": "en"}
