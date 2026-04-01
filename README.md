# Ironman Nutrition Bot

A personalized nutrition tracking and AI coaching web application for Ironman triathlon athletes. Calculates daily energy needs (RMR, NEAT, TDEE), macro targets, and hydration requirements based on actual training load — powered by the Anthropic Claude API for on-demand nutrition coaching.

## Features

- **Precision Nutrition Calculations** — Mifflin-St Jeor / Cunningham RMR, NEAT, TEF, and zone-based training energy expenditure
- **Multi-sport Training Logging** — Swim, bike, run, and strength sessions with heart-rate zone breakdown or power data
- **Dynamic Macro Periodisation** — Carbohydrate targets adjust automatically based on daily training load
- **AI Nutrition Coach** — Chat with Claude for instant, context-aware advice (3 messages/day per user)
- **Admin Approval Workflow** — New accounts require admin sign-off before access is granted
- **On-prem / Cloud Flexible** — SQLite for Raspberry Pi; swap to PostgreSQL for cloud deployment

---

## Quick Start

### Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.10+ |
| pip | 23+ |

### 1. Clone & configure environment

```bash
git clone <your-repo-url>
cd nutrition-app

cp .env.example .env
# Edit .env and set SECRET_KEY and ANTHROPIC_API_KEY
```

### 2. Install dependencies

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Initialise the database

```bash
python init_db.py
```

### 4. Run the development server

```bash
python run.py
```

Open [http://localhost:5000](http://localhost:5000)

> **First login:** The user created during `init_db.py` is automatically set as admin (user ID 1). All subsequent registrations require admin approval via `/admin/pending-users`.

---

## Deployment

### On-premises (Raspberry Pi / Linux server)

See [docs/deployment.md](docs/deployment.md#on-premises) for the full systemd service setup and optional Cloudflare Tunnel for remote access.

### Cloud (AWS / GCP / Azure / Heroku)

See [docs/deployment.md](docs/deployment.md#cloud) for containerised deployment with PostgreSQL.

---

## Usage Examples

### Log a training day and get nutrition targets

1. Navigate to **Log Training** → enter swim/bike/run details with heart-rate zone percentages
2. The app automatically calculates energy expenditure and saves to the database
3. View daily **Nutrition Results** for TDEE breakdown, macro targets (carbs/protein/fat), and hydration goal

### Use the AI coach

1. Visit the **Chat** page
2. Ask anything: _"What should I eat 2 hours before my long ride?"_
3. Claude receives your profile + today's training load as context and replies with personalised advice

### API / CLI access

See [examples/](examples/) for scripted training log submissions and nutrition calculation demos.

---

## Project Structure

```
nutrition-app/
├── app/                    # Flask application package
│   ├── __init__.py         # App factory (create_app)
│   ├── calculations.py     # Nutrition engine (RMR/NEAT/TDEE/macros)
│   ├── chat.py             # Claude AI chatbot integration
│   ├── routes.py           # All HTTP routes (Blueprint)
│   ├── models/             # SQLAlchemy data models
│   └── templates/          # Jinja2 HTML templates
├── docs/                   # Extended documentation
│   ├── architecture.md     # System design & data flow
│   ├── deployment.md       # On-prem & cloud deployment guides
│   ├── api.md              # Route reference
│   └── prompt-library.md   # Claude prompt design notes
├── examples/               # Runnable usage examples
├── tests/                  # pytest test suite
├── scripts/                # Operational & migration scripts
│   └── migrations/         # Database schema migration scripts
├── config.py               # Flask configuration classes
├── run.py                  # Development server entry point
├── init_db.py              # Database initialisation script
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development/test dependencies
├── .env.example            # Environment variable template
└── .gitignore
```

---

## Configuration

All configuration is via environment variables. See `.env.example` for the full list. Key variables:

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | **Yes** | Flask session signing key |
| `ANTHROPIC_API_KEY` | **Yes** | Anthropic Claude API key |
| `DATABASE_URL` | No | Override default SQLite path |
| `FLASK_ENV` | No | `development` \| `production` |

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for code style, branching strategy, and pull-request guidelines.

---

## License

MIT — see [LICENSE](LICENSE).
