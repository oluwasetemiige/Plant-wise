"""WhatsApp Cloud API (Meta): webhook for incoming chat, plus the send helper.

Farmer commands: "city Kano", "crop rice", "lang ha", "today", "stop", "start".
Anything else goes to Ore. Preferences and history are stored in SQLite (db.py).
"""
import logging

import httpx
from fastapi import APIRouter, Body, HTTPException, Request, Response

from . import db
from .config import WA_ACCESS_TOKEN, WA_PHONE_NUMBER_ID, WA_TEMPLATE_LANG, WA_TEMPLATE_NAME, WA_VERIFY_TOKEN
from .data import CITIES, CROPS, LANGUAGES
from .ore import ask_ore
from .rules import advice
from .weather import get_forecast

log = logging.getLogger(__name__)
router = APIRouter(prefix="/webhook")


@router.get("/whatsapp")
def verify(request: Request):
    q = request.query_params
    if WA_VERIFY_TOKEN and q.get("hub.mode") == "subscribe" and q.get("hub.verify_token") == WA_VERIFY_TOKEN:
        return Response(q.get("hub.challenge", ""), media_type="text/plain")
    raise HTTPException(status_code=403)


@router.post("/whatsapp")
def incoming(payload: dict = Body(...)):
    try:
        msg = payload["entry"][0]["changes"][0]["value"]["messages"][0]
    except (KeyError, IndexError):
        return {"ok": True}  # delivery receipts etc.
    if msg.get("type") == "text":
        sender = msg["from"]
        try:
            send(sender, handle(sender, msg["text"]["body"].strip()))
        except Exception:
            log.exception("WhatsApp handling failed")
    return {"ok": True}


def handle(sender: str, text: str) -> str:
    farmer = db.get_farmer(sender) or {**db.DEFAULT_PREFS}
    word, _, arg = text.partition(" ")
    word, arg = word.lower(), arg.strip().lower()
    options = {"city": {c.lower(): c for c in CITIES}, "crop": {c: c for c in CROPS}, "lang": {k: k for k in LANGUAGES}}

    if word == "stop":
        db.save_farmer(sender, subscribed=0)
        return "You will not get daily alerts any more. Send START to turn them back on, or just ask me a question."
    if word == "start":
        db.save_farmer(sender, subscribed=1)
        return "Daily alerts are on. Send STOP any time to turn them off."
    if word in options:
        if arg in options[word]:
            db.save_farmer(sender, **{word: options[word][arg]})
            return f"Saved. {word.capitalize()}: {options[word][arg]}."
        return f"Options for {word}: " + ", ".join(options[word].values())

    forecast = get_forecast(farmer["city"])
    if text.lower() in ("today", "advice"):
        return advice(farmer["city"], farmer["crop"], farmer["lang"], forecast)["message"]
    reply = ask_ore(text, db.recent_messages(sender), farmer["city"], farmer["crop"], forecast, farmer["lang"])
    db.add_message(sender, "user", text)
    db.add_message(sender, "assistant", reply)
    return reply


def send(to: str, body: str, template: bool = False) -> None:
    """Send a WhatsApp message. template=True uses the approved template (needed to
    message a farmer who has not written to you in the last 24 hours)."""
    if template and WA_TEMPLATE_NAME:
        message = {
            "type": "template",
            "template": {
                "name": WA_TEMPLATE_NAME,
                "language": {"code": WA_TEMPLATE_LANG},
                "components": [{"type": "body", "parameters": [{"type": "text", "text": body}]}],
            },
        }
    else:
        message = {"type": "text", "text": {"body": body}}
    r = httpx.post(
        f"https://graph.facebook.com/v20.0/{WA_PHONE_NUMBER_ID}/messages",
        headers={"Authorization": f"Bearer {WA_ACCESS_TOKEN}"},
        json={"messaging_product": "whatsapp", "to": to, **message},
        timeout=10,
    )
    r.raise_for_status()
