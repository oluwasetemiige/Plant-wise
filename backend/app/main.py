"""PlantWise: API + web app in one service.

Run:  uvicorn app.main:app --reload   ->  http://localhost:8000  (app)  /docs  (API)
"""
import hmac
import logging
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import alerts, db, whatsapp
from .config import ADMIN_TOKEN, ALLOWED_ORIGINS
from .data import CITIES, CROPS, LANGUAGES
from .ore import ask_ore
from .rules import advice
from .utils import normalize_phone
from .weather import get_forecast, get_weather

log = logging.getLogger("uvicorn.error")
db.init()
app = FastAPI(title="PlantWise")
app.add_middleware(CORSMiddleware, allow_origins=ALLOWED_ORIGINS, allow_methods=["*"], allow_headers=["*"])
app.include_router(whatsapp.router)


def _check(city: str, crop: str, lang: str = "en") -> None:
    if city not in CITIES or crop not in CROPS or lang not in LANGUAGES:
        raise HTTPException(status_code=422, detail="Unknown city, crop or language")


def _forecast(city: str) -> dict:
    try:
        return get_forecast(city)
    except Exception:
        raise HTTPException(status_code=502, detail="Weather service unavailable")


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/options")
def options():
    return {"cities": list(CITIES), "crops": {k: v["name"] for k, v in CROPS.items()}, "languages": LANGUAGES}


@app.get("/api/forecast")
def forecast(city: str = "Ibadan"):
    _check(city, "maize")
    return _forecast(city)


@app.get("/api/weather")
def weather(city: str = "Ibadan"):
    """Current conditions and 7-day outlook for the weather panel."""
    _check(city, "maize")
    try:
        return get_weather(city)
    except Exception:
        raise HTTPException(status_code=502, detail="Weather service unavailable")


@app.get("/api/advice")
def get_advice(city: str = "Ibadan", crop: str = "maize", lang: str = "en"):
    _check(city, crop, lang)
    return advice(city, crop, lang, _forecast(city))


class OreRequest(BaseModel):
    message: str
    history: list[dict] = []
    city: str = "Ibadan"
    crop: str = "maize"
    lang: str = "en"


@app.post("/api/ore")
def ore(req: OreRequest):
    _check(req.city, req.crop)
    forecast_data = _forecast(req.city)
    try:
        reply = ask_ore(req.message[:1000], req.history, req.city, req.crop, forecast_data, req.lang)
    except Exception:
        log.exception("Ore failed")  # shows the real reason in your terminal
        raise HTTPException(status_code=502, detail="Ore is unavailable")
    return {"reply": reply}


class FarmerIn(BaseModel):
    phone: str
    city: str = "Ibadan"
    crop: str = "maize"
    lang: str = "en"


@app.post("/api/farmers")
def register_farmer(f: FarmerIn):
    """Web sign-up: subscribe a WhatsApp number to daily alerts."""
    _check(f.city, f.crop, f.lang)
    phone = normalize_phone(f.phone)
    if not 10 <= len(phone) <= 15:
        raise HTTPException(status_code=422, detail="Enter a full phone number with country code")
    db.save_farmer(phone, city=f.city, crop=f.crop, lang=f.lang, subscribed=1)
    return {"ok": True}


@app.post("/api/alerts/run")
def run_alerts(x_admin_token: str = Header(default="")):
    if not ADMIN_TOKEN or not hmac.compare_digest(x_admin_token, ADMIN_TOKEN):
        raise HTTPException(status_code=403)
    return alerts.run_daily()


# Serve the web app from the same service (must stay last so /api routes win)
FRONTEND = Path(__file__).resolve().parents[2] / "frontend"
if FRONTEND.is_dir():
    app.mount("/", StaticFiles(directory=FRONTEND, html=True), name="web")
