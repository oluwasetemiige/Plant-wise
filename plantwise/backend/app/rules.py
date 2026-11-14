"""The PlantWise rules engine: forecast in, verdict + alerts + farmer message out."""
from datetime import date, timedelta

from .data import CROPS
from .messages import MSG


def day_label(i: int) -> str:
    if i == 0:
        return "today"
    if i == 1:
        return "tomorrow"
    return (date.today() + timedelta(days=i)).strftime("%A")


def judge(d: dict, crop: dict) -> dict:
    """Return {"k": plant|wait|dry, "n": days to wait, "why": plain-English reason}."""
    total = sum(d["rain"])
    heavy = next((i for i, r in enumerate(d["rain"][:3]) if r >= crop["over"]), None)
    if heavy is not None:
        n = heavy + 1
        while n < 7 and d["rain"][n] >= crop["over"] / 2:
            n += 1
        why = f"Heavy rain of {round(d['rain'][heavy])} mm is forecast {day_label(heavy)}. It could wash the seeds away."
        return {"k": "wait", "n": n, "why": why}
    if total < crop["need"]:
        why = f"Only {round(total)} mm of rain is forecast this week. {crop['name']} needs about {crop['need']} mm."
        return {"k": "dry", "n": 0, "why": why}
    why = f"{round(total)} mm of steady rain is forecast this week, with no flood-level downpour."
    return {"k": "plant", "n": 0, "why": why}


def alerts(d: dict) -> list[str]:
    out = [f"Flood risk: {round(r)} mm of rain {day_label(i)}." for i, r in enumerate(d["rain"]) if r >= 40]
    run = longest = 0
    for r in d["rain"]:
        run = run + 1 if r < 1 else 0
        longest = max(longest, run)
    if longest >= 4:
        out.append(f"Dry spell: {longest} days in a row with almost no rain.")
    if max(d["hi"]) >= 36:
        out.append(f"Heat: up to {round(max(d['hi']))}°C. Water crops early in the morning.")
    return out


def farmer_message(city: str, crop_key: str, lang: str, verdict: dict) -> str:
    crop = CROPS[crop_key]
    name = {"yo": crop["yo"], "ha": crop["ha"]}.get(lang, crop["name"].lower())
    text = MSG.get(lang, MSG["en"])[verdict["k"]].format(c=name, n=verdict["n"])
    return f"PlantWise {city}: {text}"


def advice(city: str, crop_key: str, lang: str, forecast: dict) -> dict:
    verdict = judge(forecast, CROPS[crop_key])
    return {
        "verdict": verdict["k"],
        "days_to_wait": verdict["n"],
        "reason": verdict["why"],
        "alerts": alerts(forecast),
        "message": farmer_message(city, crop_key, lang, verdict),
    }
