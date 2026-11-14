"""Ore's own brain: no outside AI, no API key, no cost.

It reads the farmer's message, works out what they want (intent), spots the crop
and city they mention, then answers from the live forecast and the PlantWise rules.
Works in English, Nigerian Pidgin, Yorùbá and Hausa. Add knowledge by editing the
keyword lists, TEXT and TIPS below.
"""
import re
import unicodedata

from .data import CITIES, CROPS
from .rules import alerts, judge
from .weather import get_forecast

# ---------------------------------------------------------------- language
LANG_HINTS = {
    "pcm": {"abeg", "wetin", "dey", "wey", "suppose", "wahala", "sabi", "una", "oga", "abi", "how far"},
    "yo": {"bawo", "kaaro", "kaasan", "kaale", "ese", "gbin", "gbigbin", "oko", "agbado", "iresi", "bomi",
           "kini", "nje", "ejowo", "ikore", "ojo", "ooru", "ola", "oni", "pele"},
    "ha": {"sannu", "kwana", "barka", "ruwa", "shuka", "gona", "nagode", "zafi", "girbi", "kwari", "taki",
           "yau", "gobe", "yaushe", "zai", "sama", "shayar", "dasa"},
}

# ---------------------------------------------------------------- keywords
# word = whole word, "word*" = starts with, "two words" = phrase
INTENTS = {
    "pest": ["pest", "pests", "disease*", "insect*", "worm*", "armyworm", "spray*", "chemical*", "pesticide*",
             "herbicide*", "fertili*", "blight", "fungus", "kwari", "taki", "ajile", "kokoro", "arun", "cuta", "magani"],
    "tips": ["how to", "how do", "how long", "how many days", "spacing", "apart", "how deep", "depth",
             "seed rate", "guide", "tips", "tell me about"],
    "harvest": ["harvest*", "ikore", "kore", "girbi", "mature", "ready"],
    "plant": ["plant*", "sow*", "gbin", "gbigbin", "shuka", "dasa"],
    "alerts": ["alert*", "warning*", "flood*", "storm*", "drought*", "dry spell", "ikilo", "gargadi", "danger"],
    "water": ["water*", "irrigat*", "bomi", "shayar*", "ban ruwa"],
    "rain": ["rain", "rains", "raining", "rainfall", "ojo", "ruwan sama", "sama", "ruwa", "shower*", "drizzle"],
    "heat": ["hot", "heat", "temperature", "temp", "sun", "sunny", "ooru", "gbona", "zafi"],
}
GREET = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening", "how far", "wetin dey",
         "bawo", "kaaro", "kaasan", "kaale", "sannu", "ina kwana", "barka", "pele"]
THANKS = ["thank*", "thanks", "ese", "nagode", "na gode", "gode"]
HELP = ["help", "what can you do", "menu"]
CROP_WORDS = {
    "maize": ["maize", "corn", "agbado", "masara"],
    "cassava": ["cassava", "gbaguda", "rogo"],
    "rice": ["rice", "iresi", "shinkafa"],
    "tomato": ["tomato", "tomatoes", "tomati", "tumatir"],
}

# ---------------------------------------------------------------- knowledge
# General guidelines. Local varieties differ: confirm with your extension officer.
TIPS = {
    "maize": "Maize: plant 1 to 2 seeds per hole, about 3 to 5 cm deep, with rows roughly 75 cm apart and 25 cm between plants. Weed early.",
    "cassava": "Cassava: plant healthy stem cuttings about 20 to 25 cm long, roughly 1 m apart in rows 1 m apart, pressed slanted or flat into loose soil. Weed in the first 3 months.",
    "rice": "Rice: upland rice is usually sown in rows about 20 to 25 cm apart. Lowland rice is often transplanted from a nursery after 3 to 4 weeks. Keep the field weeded and manage the water carefully.",
    "tomato": "Tomato: raise seedlings in a nursery for about 3 to 4 weeks, then transplant with about 60 cm between rows and 45 cm between plants. Stake the plants and avoid wetting the leaves.",
}
MATURITY = {
    "maize": "Most maize varieties are ready to harvest in about 90 to 120 days (early varieties about 80 to 90).",
    "cassava": "Cassava roots are usually ready in about 9 to 12 months.",
    "rice": "Most rice varieties mature in about 100 to 130 days.",
    "tomato": "Tomato harvest starts about 60 to 90 days after transplanting.",
}
CONFIRM = " Local varieties differ, so confirm with your extension officer."

WHEN = {
    "en": ("today", "tomorrow", "in {n} days"),
    "pcm": ("today", "tomorrow", "for {n} days time"),
    "yo": ("lónìí", "ní ọ̀la", "lẹ́yìn ọjọ́ {n}"),
    "ha": ("yau", "gobe", "nan da kwana {n}"),
}

TEXT = {
    "en": {
        "greet": "Hello! I’m Ore. Ask me if you should plant, when it will rain, whether to water your {crop}, or about the heat.",
        "thanks": "You’re welcome! Ask me anything about your farm.",
        "rain": "In {city}: {pop0}% chance of rain today and {pop1}% tomorrow. About {total} mm is expected this week, with the most rain {wet} ({mx} mm).",
        "rain_none": "No real rain is forecast in {city} this week.",
        "water_yes": "Rain is coming ({mm3} mm in the next 3 days), so you may not need to water your {crop} now.",
        "water_no": "Little rain is expected ({mm3} mm in the next 3 days). Water your {crop} early in the morning or late in the evening.",
        "heat_hot": "The high today is {hi}°C. That is very hot. Water early in the morning and shade young plants if you can.",
        "heat_ok": "The high today is {hi}°C. That is fine for most crops.",
        "harvest_window": "Good dry days for harvesting start {when}.",
        "harvest_wet": "Rain is forecast on most days this week, so harvest early if the crop is ready and dry it well.",
        "no_alerts": "No weather alerts this week.",
        "pest": "I can’t safely advise on pesticides, chemicals or fertilizer amounts. Please speak to your local agricultural extension officer.",
        "unknown": "I’m not sure about that yet. I can help with planting time, rain, watering, heat and harvest. Try: “Should I plant {crop} today?”",
    },
    "pcm": {
        "greet": "Hello! Na Ore be this. Ask me if you suppose plant, when rain go fall, if you go water your {crop}, or about the heat.",
        "thanks": "You are welcome! Ask me anything about your farm.",
        "rain": "For {city}: {pop0}% chance say rain go fall today and {pop1}% tomorrow. About {total} mm go fall this week, and the most rain go fall {wet} ({mx} mm).",
        "rain_none": "No real rain dey for {city} this week.",
        "water_yes": "Rain dey come ({mm3} mm for the next 3 days), so you no need water your {crop} now.",
        "water_no": "Rain small ({mm3} mm for the next 3 days). Water your {crop} early morning or late evening.",
        "heat_hot": "Today the sun go reach {hi}°C. E hot well well. Water your farm early morning and cover small plants if you fit.",
        "heat_ok": "Today the sun go reach {hi}°C. E good for most crops.",
        "harvest_window": "Dry days wey good to harvest start {when}.",
        "harvest_wet": "Rain go fall most days this week, so harvest early if the crop don ready and dry am well.",
        "no_alerts": "No weather alert dey this week.",
        "pest": "I no fit safely advise on pesticide, chemical or fertilizer quantity. Abeg talk to your local agric extension officer.",
        "unknown": "I never sabi that one yet. I fit help with when to plant, rain, water, heat and harvest. Try ask: “Make I plant {crop} today?”",
    },
    "yo": {
        "greet": "Pẹlẹ o! Ore ni mí. Ẹ bi mí bóyá kí ẹ gbin, ìgbà tí òjò yóò rọ̀, bóyá kí ẹ bomi rin {crop} yín, tàbí nípa ooru.",
        "thanks": "Ẹ ṣé! Ẹ bi mí ohunkóhun nípa oko yín.",
        "rain": "Ní {city}: ìṣeéṣe òjò jẹ́ {pop0}% lónìí àti {pop1}% ní ọ̀la. Nǹkan bí {total} mm ni a retí ní ọ̀sẹ̀ yìí, òjò tó pọ̀ jù yóò rọ̀ {wet} ({mx} mm).",
        "rain_none": "A kò retí òjò gidi ní {city} ní ọ̀sẹ̀ yìí.",
        "water_yes": "Òjò ń bọ̀ ({mm3} mm ní ọjọ́ mẹ́ta tó ń bọ̀), nítorí náà ẹ kò nílò láti bomi rin {crop} báyìí.",
        "water_no": "Òjò kò pọ̀ ({mm3} mm ní ọjọ́ mẹ́ta tó ń bọ̀). Ẹ bomi rin {crop} yín ní àárọ̀ kùtù tàbí ní ìrọ̀lẹ́.",
        "heat_hot": "Ooru lónìí yóò dé {hi}°C. Ó gbóná gan-an. Ẹ bomi rin oko yín ní àárọ̀ kùtù, kí ẹ sì bò àwọn ewéko kékeré tí ẹ bá lè.",
        "heat_ok": "Ooru lónìí yóò dé {hi}°C. Ó dára fún ọ̀pọ̀ ohun ọ̀gbìn.",
        "harvest_window": "Àwọn ọjọ́ gbígbẹ tó dára fún ìkórè bẹ̀rẹ̀ {when}.",
        "harvest_wet": "Òjò yóò rọ̀ ní ọ̀pọ̀ ọjọ́ ní ọ̀sẹ̀ yìí, nítorí náà ẹ kórè ní kùtù tí ohun ọ̀gbìn bá ti pọ́n, kí ẹ sì gbẹ ẹ́ dáadáa.",
        "no_alerts": "Kò sí ìkìlọ̀ ojú ọjọ́ ní ọ̀sẹ̀ yìí.",
        "pest": "Mi ò lè gba yín nímọ̀ràn láìfọkàn balẹ̀ lórí oògùn kòkòrò, kẹ́míkà tàbí iye ajílẹ̀. Ẹ jọ̀wọ́ ẹ bá ọ̀gá ìgbìmọ̀ àgbẹ̀ àdúgbò yín sọ̀rọ̀.",
        "unknown": "Mi ò tíì mọ̀ nípa ìyẹn. Mo lè ràn yín lọ́wọ́ lórí ìgbà tí a ó gbin, òjò, bí a ṣe ń bomi rin, ooru àti ìkórè. Ẹ gbìyànjú: “Ṣé kí n gbin {crop} lónìí?”",
    },
    "ha": {
        "greet": "Sannu! Ni ce Ore. Ku tambaye ni ko ya kamata ku shuka, lokacin da ruwan sama zai sauka, ko ku shayar da {crop}, ko game da zafi.",
        "thanks": "Ba komai! Ku tambaye ni duk abin da ya shafi gonarku.",
        "rain": "A {city}: akwai damar ruwan sama kashi {pop0}% yau da kashi {pop1}% gobe. Ana sa ran kusan {total} mm a wannan mako, mafi yawan ruwan zai sauka {wet} ({mx} mm).",
        "rain_none": "Ba a sa ran ruwan sama sosai a {city} a wannan mako.",
        "water_yes": "Ruwan sama na zuwa ({mm3} mm cikin kwanaki 3 masu zuwa), don haka ba ku bukatar shayar da {crop} yanzu.",
        "water_no": "Ruwan sama kadan ne ({mm3} mm cikin kwanaki 3 masu zuwa). Ku shayar da {crop} da sassafe ko da yamma.",
        "heat_hot": "Zafin yau zai kai {hi}°C. Yana da zafi sosai. Ku shayar da gonarku da sassafe, kuma ku rufe kananan shuke-shuke idan za ku iya.",
        "heat_ok": "Zafin yau zai kai {hi}°C. Ya dace da yawancin amfanin gona.",
        "harvest_window": "Kwanakin bushewa masu kyau don girbi sun fara {when}.",
        "harvest_wet": "Ruwan sama zai sauka a yawancin kwanaki a wannan mako, don haka ku girbe da wuri idan amfanin ya nuna, ku bushe shi sosai.",
        "no_alerts": "Babu gargadin yanayi a wannan mako.",
        "pest": "Ba zan iya ba da shawara lafiya kan magungunan kwari, sinadarai ko adadin taki ba. Don Allah ku tuntubi jami’in noma na yankinku.",
        "unknown": "Ban san wannan ba tukuna. Zan iya taimaka muku da lokacin shuka, ruwan sama, shayarwa, zafi da girbi. Ku gwada tambaya: “Shin in shuka {crop} yau?”",
    },
}


# ---------------------------------------------------------------- helpers
def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(ch for ch in s if not unicodedata.combining(ch))


def _has(words: list[str], toks: list[str], text: str) -> bool:
    for w in words:
        if " " in w:
            if w in text:
                return True
        elif w.endswith("*"):
            if any(t.startswith(w[:-1]) for t in toks):
                return True
        elif w in toks:
            return True
    return False


def detect_language(message: str, default: str = "en") -> str:
    text = _norm(message)
    toks = set(re.findall(r"[a-z0-9]+", text))
    scores = {lang: sum(1 for h in hints if (h in text if " " in h else h in toks)) for lang, hints in LANG_HINTS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] >= 1 else default


def detect_intent(message: str) -> str:
    text = _norm(message)
    toks = re.findall(r"[a-z0-9]+", text)
    short = len(toks) <= 4
    if short and _has(GREET, toks, text):
        return "greet"
    if short and _has(THANKS, toks, text):
        return "thanks"
    if _has(HELP, toks, text):
        return "greet"
    for name, words in INTENTS.items():
        if _has(words, toks, text):
            return name
    if _has(GREET, toks, text):
        return "greet"
    if _has(THANKS, toks, text):
        return "thanks"
    return "unknown"


def _mentioned(message: str, default_crop: str, default_city: str) -> tuple[str, str]:
    text = _norm(message)
    toks = re.findall(r"[a-z0-9]+", text)
    crop = next((k for k, ws in CROP_WORDS.items() if _has(ws, toks, text)), default_crop)
    city = next((c for c in CITIES if _norm(c) in text), default_city)
    return crop, city


def _when(i: int, lang: str) -> str:
    today, tomorrow, later = WHEN[lang]
    return today if i == 0 else tomorrow if i == 1 else later.format(n=i)


# ---------------------------------------------------------------- the brain
def ask_brain(message: str, history: list[dict], city: str, crop_key: str, forecast: dict, lang: str = "en") -> str:
    lang = detect_language(message, lang if lang in TEXT else "en")
    intent = detect_intent(message)
    crop_key, new_city = _mentioned(message, crop_key, city)
    if new_city != city:  # the farmer asked about another city
        try:
            forecast, city = get_forecast(new_city), new_city
        except Exception:
            pass
    crop = CROPS[crop_key]
    name = {"yo": crop["yo"], "ha": crop["ha"]}.get(lang, crop["name"].lower())
    t = TEXT[lang]
    rain = forecast["rain"]

    if intent == "greet":
        return t["greet"].format(crop=name)
    if intent == "thanks":
        return t["thanks"]
    if intent == "pest":
        return t["pest"]
    if intent == "tips":
        return TIPS[crop_key] + " " + MATURITY[crop_key] + CONFIRM
    if intent == "harvest":
        dry = [i for i in range(7) if rain[i] < 1]
        start = next((i for i in dry if i + 1 < 7 and rain[i + 1] < 1), dry[0] if dry else None)
        window = t["harvest_window"].format(when=_when(start, lang)) if start is not None else t["harvest_wet"]
        return window + " " + MATURITY[crop_key]
    if intent == "plant":
        from .messages import MSG

        j = judge(forecast, crop)
        text = MSG[lang][j["k"]].format(c=name, n=j["n"])
        return text + (" " + j["why"] if lang == "en" else "")
    if intent == "alerts":
        found = alerts(forecast)
        return " ".join(found) if found else t["no_alerts"]
    if intent == "water":
        mm3 = round(sum(rain[:3]))
        return t["water_yes" if mm3 >= 10 else "water_no"].format(mm3=mm3, crop=name)
    if intent == "rain":
        total = round(sum(rain))
        if total < 1:
            return t["rain_none"].format(city=city)
        wet = max(range(7), key=lambda i: rain[i])
        return t["rain"].format(city=city, pop0=forecast["pop"][0], pop1=forecast["pop"][1], total=total,
                                wet=_when(wet, lang), mx=round(rain[wet]))
    if intent == "heat":
        hi = round(forecast["hi"][0])
        return t["heat_hot" if hi >= 36 else "heat_ok"].format(hi=hi)
    return t["unknown"].format(crop=name)
