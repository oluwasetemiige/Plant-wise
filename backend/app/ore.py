"""Ore, the farmer-facing assistant.

ORE_BRAIN=own     (default) her own built-in brain, see brain.py. No API key, no cost.
ORE_BRAIN=claude  use Claude (needs ANTHROPIC_API_KEY). If Claude fails, the own brain answers.
"""
import logging

from .brain import ask_brain
from .config import CLAUDE_MODEL, ORE_BRAIN
from .data import CROPS
from .rules import judge

SYSTEM = (
    "You are Ore, a friendly farming assistant inside PlantWise, a free weather advice service "
    "for smallholder farmers in Nigeria. Reply in the language the farmer writes in (English, "
    "Nigerian Pidgin, Yorùbá, Hausa or Igbo). Use short, simple sentences (4 at most), no jargon "
    "and no markdown. Base planting, irrigation and harvest timing advice on the forecast context "
    "given. Never invent weather numbers. For pesticides, chemicals or health questions, tell the "
    "farmer to speak to their local agricultural extension officer. If a question is not about "
    "farming or weather, say kindly that you can only help with farming. If unsure, say so."
)

_client = None


def _get_client():
    global _client
    if _client is None:
        from anthropic import Anthropic  # only needed in claude mode

        _client = Anthropic()  # reads ANTHROPIC_API_KEY from the environment
    return _client


def forecast_context(city: str, crop_key: str, fc: dict) -> str:
    crop = CROPS[crop_key]
    j = judge(fc, crop)
    return (
        f"Farmer location: {city}, Nigeria. Crop: {crop['name']}. 7-day forecast starting today. "
        f"Rain mm: {', '.join(str(round(x)) for x in fc['rain'])}. "
        f"Chance of rain %: {', '.join(str(x) for x in fc['pop'])}. "
        f"High C: {', '.join(str(round(x)) for x in fc['hi'])}. "
        f"PlantWise rules say: {j['k'].upper()}. {j['why']}"
    )


def _clean(history: list[dict], message: str) -> list[dict]:
    """Claude needs alternating roles that start with a user turn."""
    msgs: list[dict] = []
    for m in [*history[-8:], {"role": "user", "content": message}]:
        role = "assistant" if m.get("role") == "assistant" else "user"
        if msgs and msgs[-1]["role"] == role:
            msgs[-1]["content"] += "\n" + m["content"]
        else:
            msgs.append({"role": role, "content": m["content"]})
    while msgs and msgs[0]["role"] != "user":
        msgs.pop(0)
    return msgs


def _ask_claude(message: str, history: list[dict], city: str, crop_key: str, forecast: dict) -> str:
    r = _get_client().messages.create(
        model=CLAUDE_MODEL,
        max_tokens=300,
        system=SYSTEM + "\n\nContext: " + forecast_context(city, crop_key, forecast),
        messages=_clean(history, message),
    )
    return "".join(b.text for b in r.content if b.type == "text").strip()


def ask_ore(message: str, history: list[dict], city: str, crop_key: str, forecast: dict, lang: str = "en") -> str:
    if ORE_BRAIN == "claude":
        try:
            return _ask_claude(message, history, city, crop_key, forecast)
        except Exception:
            logging.getLogger("uvicorn.error").exception("Claude failed, using Ore's own brain")
    return ask_brain(message, history, city, crop_key, forecast, lang)
