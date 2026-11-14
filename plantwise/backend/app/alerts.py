"""Daily alerts: send every subscribed farmer today's advice on WhatsApp.

Run from cron:  python -m app.alerts      (e.g. every day at 06:00)
or over HTTP:   POST /api/alerts/run with header X-Admin-Token
"""
import logging

from . import db
from .rules import advice
from .weather import get_forecast
from .whatsapp import send

log = logging.getLogger(__name__)


def run_daily() -> dict:
    sent = failed = 0
    for f in db.list_subscribed():
        try:
            message = advice(f["city"], f["crop"], f["lang"], get_forecast(f["city"]))["message"]
            send(f["phone"], message, template=True)
            sent += 1
        except Exception:
            log.exception("Alert failed for farmer %s", f["phone"][-4:])
            failed += 1
    return {"sent": sent, "failed": failed}


if __name__ == "__main__":
    db.init()
    print(run_daily())
