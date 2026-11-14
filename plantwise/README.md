# PlantWise

Hyperlocal planting, irrigation and harvest advice for smallholder farmers in Nigeria,
with **Ore**, a Claude-powered assistant farmers can chat with on the web or WhatsApp.

agritech climate-tech smallholder-farmers nigeria weather whatsapp fastapi python javascript open-meteo sustainability hackathon

Smallholder farmers still decide when to plant by guesswork, and a wrong planting date can wipe out a whole season. PlantWise reads the forecast for the farmer’s town and tells them in simple words when to plant, wait, or irrigate. Farmers just enter their WhatsApp number and get the advice every morning, with no app to open. They can also chat with Ore to ask about rain, watering, heat, and harvest.

## How it all connects

```
Open-Meteo ──► weather.py ──► rules.py ──► /api/advice ──► web app (Today, This week)
                                 │
                                 ├──► ore.py -> brain.py ──► /api/ore ──► web app (Ask Ore)
                                 │                     └─► WhatsApp chat (whatsapp.py)
                                 └──► alerts.py ──► WhatsApp daily alerts
web sign-up (Settings) ──► /api/farmers ──► SQLite (db.py) ──► alerts.py
```

The weather icon (top right of the app) opens a panel where you pick any listed Nigerian city and see its current weather and 7-day outlook. Add more cities in `backend/app/data.py` and `frontend/js/app.js`.

One service runs everything: the backend serves the web app and the API on the same address.

```
plantwise/
├── backend/
│   ├── app/
│   │   ├── main.py        API routes + serves the web app
│   │   ├── rules.py       rules engine: forecast -> verdict, alerts, farmer message
│   │   ├── weather.py     Open-Meteo forecast (free, cached 30 min)
│   │   ├── brain.py       Ore's own brain (intents, forecast answers, 4 languages)
│   │   ├── ore.py        picks the brain: own (default) or Claude
│   │   ├── whatsapp.py    WhatsApp webhook (chat) and send helper
│   │   ├── alerts.py      daily WhatsApp alerts to subscribed farmers
│   │   ├── db.py          SQLite: farmers, subscriptions, chat history
│   │   ├── messages.py    EN / Pidgin / Yorùbá / Hausa templates
│   │   ├── data.py        cities and crop thresholds
│   │   ├── utils.py       phone number cleanup
│   │   └── config.py      environment settings
│   ├── tests/             rules + database tests
│   └── requirements.txt
├── frontend/              mobile-first web app, no build step
│   ├── index.html
│   ├── css/style.css
│   └── js/{config.js, app.js}
├── .env.example
└── README.md
```

## Run it

```bash
cd backend
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env                                # Ore works with no API key
uvicorn app.main:app --reload
```

Open http://localhost:8000 for the app and http://localhost:8000/docs for the API.
Run `pytest` in `backend/` to check the rules and database.

## Ore's brain

Ore answers with her own built-in brain (`backend/app/brain.py`): no API key and no cost. She understands
questions about planting, rain, watering, heat, harvest and weather alerts in English, Pidgin, Yorùbá and Hausa, picks out the
crop and city a farmer mentions, and answers from the live forecast and the PlantWise rules. Pesticide and fertilizer
questions go to the local extension officer. To teach her more, edit the keyword lists, `TEXT` and `TIPS` in `brain.py`.
To use Claude instead, set `ORE_BRAIN=claude` and `ANTHROPIC_API_KEY` in `.env`.

## API

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/advice?city=Kano&crop=maize&lang=ha` | verdict, reason, alerts, farmer message |
| GET | `/api/forecast?city=Kano` | 7-day rain, rain chance, high/low |
| GET | `/api/weather?city=Lagos` | current conditions + 7-day outlook (weather panel) |
| POST | `/api/ore` | `{message, history, city, crop}` -> `{reply}` |
| POST | `/api/farmers` | `{phone, city, crop, lang}` subscribe to daily alerts |
| POST | `/api/alerts/run` | send daily alerts now (header `X-Admin-Token`) |
| GET | `/api/options` | cities, crops, languages |
| GET/POST | `/webhook/whatsapp` | WhatsApp Cloud API webhook |

## WhatsApp setup (Meta Cloud API)

1. Create an app at developers.facebook.com and add the WhatsApp product.
2. Put the access token and phone number ID in `.env`, and pick a `WA_VERIFY_TOKEN`.
3. Deploy the backend over HTTPS (or use `ngrok http 8000` while testing).
4. In the WhatsApp config, set the webhook to `https://YOUR-URL/webhook/whatsapp`, enter your verify token, and subscribe to `messages`.
5. Farmers message the number: `city Kano`, `crop rice`, `lang ha`, `today`, `stop`, `start`, or any question for Ore.

## Daily alerts

Farmers subscribe in the app (Settings) or by sending `START` on WhatsApp. Send the alerts with:

```bash
python -m app.alerts                       # run from cron, e.g. 0 6 * * *
curl -X POST https://YOUR-URL/api/alerts/run -H "X-Admin-Token: $ADMIN_TOKEN"
```

WhatsApp only allows free-form messages within 24 hours of the farmer's last message.
For daily alerts to everyone else, create a message template in Meta Business Manager
with one variable (body: `{{1}}`), get it approved, and set `WA_TEMPLATE_NAME` in `.env`.

## Deploy

Any host that runs Python works (Render, Railway, a Vultr VPS). Start command:
`uvicorn app.main:app --host 0.0.0.0 --port $PORT`. Set the `.env` values as environment
variables, and keep `DB_PATH` on a persistent disk (or move to Postgres for scale).

## Next steps

- Add SMS (Africa's Talking or Termii) beside WhatsApp.
- Give Ore a knowledge base of local crop calendars and extension-service advice.
- Tune the crop thresholds in `data.py` with local agro-meteorology data.
- Have native speakers review `messages.py` and Ore's replies in each language.
