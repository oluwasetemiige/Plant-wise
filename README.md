# 🌱 PlantWise

**Smarter planting decisions. Better harvests.**

PlantWise is a climate-smart agricultural assistant designed to help smallholder farmers make better farming decisions using local weather forecasts, crop information, and practical agricultural advice.

It helps farmers understand when to plant, when to wait, when to irrigate, and how changing weather conditions may affect their crops.

Farmers can also interact with **Ore**, PlantWise's built-in farming assistant, through the web application or WhatsApp integration.

---

## 1. What PlantWise Does

PlantWise provides:

- **Weather Forecasts:** Current weather conditions and seven-day forecasts for supported Nigerian cities.
- **Planting Advice:** Recommendations based on weather conditions and crop requirements.
- **Irrigation Guidance:** Advice on when crops may need watering.
- **Ore AI Assistant:** Answers farming and weather-related questions.
- **WhatsApp Integration:** Allows farmers to interact with PlantWise through WhatsApp.
- **Daily Weather Alerts:** Sends weather-related farming advice to subscribed farmers.
- **Multiple Languages:** Supports English, Nigerian Pidgin, Yorùbá, and Hausa through Ore's built-in brain.

## 2. How PlantWise Works

PlantWise connects weather information, a farming rules engine, a database, and a web interface.

### System architecture

```text
              FARMER
                 |
                 v
          PLANTWISE WEB APP
                 |
                 v
          FASTAPI BACKEND
                 |
       +---------+---------+
       |         |         |
       v         v         v
    WEATHER    RULES      ORE
    SERVICE    ENGINE   ASSISTANT
       |         |         |
       v         v         v
   OPEN-METEO  FARMING   ANSWERS
              ADVICE
                 |
                 v
             SQLITE DB
                 |
                 v
           WHATSAPP ALERTS
```

### How the process works

1. A farmer opens PlantWise and selects a city and crop.
2. The backend requests weather information from Open-Meteo.
3. The rules engine evaluates the forecast against crop-related thresholds.
4. PlantWise generates practical farming recommendations.
5. The frontend displays the results.
6. Farmers can also ask Ore questions or subscribe to WhatsApp alerts.

## 3. Technology Stack

| Component | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, FastAPI |
| Weather data | Open-Meteo |
| Database | SQLite |
| AI assistant | Ore built-in brain |
| Optional AI provider | Anthropic Claude |
| Messaging | WhatsApp Cloud API |
| Web server | Nginx |
| Application server | Uvicorn |
| Hosting | Vultr VPS |
| Operating system | Ubuntu 24.04 |

## 4. Project Structure

```text
Plant-wise/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── rules.py
│   │   ├── weather.py
│   │   ├── brain.py
│   │   ├── ore.py
│   │   ├── whatsapp.py
│   │   ├── alerts.py
│   │   ├── db.py
│   │   ├── messages.py
│   │   ├── data.py
│   │   ├── utils.py
│   │   └── config.py
│   │
│   ├── tests/
│   └── requirements.txt
│
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── config.js
│       └── app.js
│
├── .env.example
└── README.md
```

## 5. Running PlantWise Locally

### Requirements

- Python 3.10 or newer
- Git
- Internet connection for live weather data

### Installation

Clone the repository:

```bash
git clone https://github.com/oluwasetemiige/Plant-wise.git
```

Enter the backend directory:

```bash
cd Plant-wise/backend
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it:

**Windows:**

```bash
venv\Scripts\activate
```

**Linux/macOS:**

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the application:

```bash
uvicorn app.main:app --reload
```

Open the application:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

## 6. API Endpoints

PlantWise uses FastAPI to handle communication between the frontend and backend.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Checks backend availability |
| GET | `/api/options` | Returns supported cities, crops and languages |
| GET | `/api/forecast` | Returns a seven-day forecast |
| GET | `/api/weather` | Returns current weather and outlook |
| GET | `/api/advice` | Generates farming recommendations |
| POST | `/api/ore` | Sends a question to Ore |
| POST | `/api/farmers` | Registers a farmer for alerts |
| POST | `/api/alerts/run` | Runs daily alerts |
| GET/POST | `/webhook/whatsapp` | Handles WhatsApp webhook requests |

Interactive API documentation is available at `/docs`.

## 7. Ore — The Farming Assistant

Ore is the conversational assistant built into PlantWise.

By default, Ore uses its own built-in response engine, so it does not require an external AI API key.

Ore can help farmers with questions about:

- Planting periods
- Rainfall
- Irrigation
- Heat conditions
- Harvesting
- Weather alerts

It supports English, Nigerian Pidgin, Yorùbá, and Hausa.

An optional Claude integration is also available through environment configuration.

## 8. Database

PlantWise uses SQLite to store farmer information and chat history.

The database stores:

- Farmer phone numbers
- Selected cities
- Preferred crops
- Language preferences
- Alert subscription status
- Chat messages

The database is initialized automatically when the backend starts.

The default database path is `plantwise.db`, relative to the backend working directory.

For production, keep this file on persistent storage and back it up regularly.

## 9. Production Deployment — Vultr

PlantWise is deployed on a Vultr VPS running Ubuntu 24.04.

**Live application:**

http://139.84.250.6

### Deployment architecture

```text
             INTERNET
                 |
                 v
             VULTR VPS
                 |
                 v
               NGINX
                 |
                 v
          127.0.0.1:8000
                 |
                 v
            FASTAPI
             UVICORN
                 |
          +------+------+
          |             |
          v             v
       FRONTEND       API
          |             |
          +------+------+
                 |
                 v
              SQLITE
```

### Nginx

Nginx acts as a reverse proxy.

It receives requests on port 80 and forwards them internally to FastAPI on port 8000.

This allows visitors to access the application without specifying the backend port.

### Systemd

PlantWise runs as a Linux system service called `plantwise`.

Useful commands:

Check service status:

```bash
systemctl status plantwise
```

Restart PlantWise:

```bash
systemctl restart plantwise
```

Stop PlantWise:

```bash
systemctl stop plantwise
```

Start PlantWise:

```bash
systemctl start plantwise
```

View application logs:

```bash
journalctl -u plantwise -n 50 --no-pager
```

### Nginx commands

Check configuration:

```bash
nginx -t
```

Restart Nginx:

```bash
systemctl restart nginx
```

Check Nginx status:

```bash
systemctl status nginx
```

### Firewall

The Ubuntu firewall is configured to allow web traffic and SSH access.

The intended public access is:

| Port | Purpose |
|---|---|
| 22 | SSH administration |
| 80 | HTTP website |

Port 8000 is intended for internal communication between Nginx and FastAPI, not public access.

**Deployment note:** The current public address uses HTTP. HTTPS has not yet been configured because a domain name has not been connected.

## 10. Environment Configuration

PlantWise reads configuration from environment variables.

Important settings include:

| Variable | Purpose |
|---|---|
| `ORE_BRAIN` | Selects Ore's response engine |
| `ANTHROPIC_API_KEY` | Optional Claude API key |
| `CLAUDE_MODEL` | Claude model selection |
| `DB_PATH` | SQLite database location |
| `ADMIN_TOKEN` | Protects the daily alerts endpoint |
| `WA_VERIFY_TOKEN` | WhatsApp webhook verification |
| `WA_ACCESS_TOKEN` | WhatsApp API access |
| `WA_PHONE_NUMBER_ID` | WhatsApp phone number identifier |
| `WA_TEMPLATE_NAME` | Approved WhatsApp template |
| `WA_TEMPLATE_LANG` | WhatsApp template language |
| `ALLOWED_ORIGINS` | Allowed frontend origins |

Keep credentials and API tokens private. Never commit real secrets to GitHub.

## 11. Testing

Check the backend health endpoint:

```bash
curl http://127.0.0.1:8000/api/health
```

Expected response:

```json
{
  "status": "ok"
}
```

Run the project tests from the backend directory:

```bash
pytest
```

## 12. Future Improvements

Planned areas for improvement include:

- Custom domain and HTTPS configuration.
- Automated database backups.
- More Nigerian cities and crop varieties.
- Improved local agricultural recommendations.
- SMS notifications.
- More advanced AI assistance.
- Native mobile application.
- Expanded language support.
- Improved monitoring and uptime reporting.

---

## About PlantWise

PlantWise is built around one simple idea:

**Farmers should have access to useful weather information and practical farming advice before making decisions that affect their harvest.**

By combining climate information with accessible technology, PlantWise aims to make agricultural decision-making smarter, easier, and more accessible.

**PlantWise — Helping farmers grow with confidence.** 🌱
