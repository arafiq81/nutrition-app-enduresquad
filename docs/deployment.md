# Deployment Guide

This guide covers running Ironman Nutrition Bot in production on both on-premises hardware and cloud platforms.

---

## On-Premises (Raspberry Pi / Linux Server)

### 1. Install system dependencies

```bash
sudo apt update && sudo apt install -y python3 python3-pip python3-venv git
```

### 2. Clone and configure

```bash
git clone <your-repo-url> /opt/nutrition-app
cd /opt/nutrition-app

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
nano .env          # Set SECRET_KEY and ANTHROPIC_API_KEY
```

### 3. Initialise the database

```bash
source venv/bin/activate
python init_db.py
```

### 4. Create a systemd service

```bash
sudo nano /etc/systemd/system/nutrition-bot.service
```

Paste the following (adjust paths as needed):

```ini
[Unit]
Description=Ironman Nutrition Bot
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/opt/nutrition-app
EnvironmentFile=/opt/nutrition-app/.env
ExecStart=/opt/nutrition-app/venv/bin/python run.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable nutrition-bot
sudo systemctl start nutrition-bot
sudo systemctl status nutrition-bot
```

### 5. View logs

```bash
sudo journalctl -u nutrition-bot -f
```

### 6. Remote access via Cloudflare Tunnel (optional)

Cloudflare Tunnel exposes the app to the internet without opening a firewall port:

```bash
# Install cloudflared
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64 -o /usr/local/bin/cloudflared
chmod +x /usr/local/bin/cloudflared

# Authenticate and create a named tunnel (requires Cloudflare account)
cloudflared tunnel login
cloudflared tunnel create nutrition-bot

# Or use a quick ephemeral tunnel for testing (no account needed)
cloudflared tunnel --url http://localhost:5000
```

For a persistent tunnel, create `/etc/cloudflared/config.yml` and a matching systemd service. See `cloudflare-tunnel-commands.txt` for operational commands.

---

## Cloud Deployment

### Requirements

- Replace SQLite with **PostgreSQL** (update `DATABASE_URL` in `.env`)
- Set `FLASK_ENV=production`
- Use a production WSGI server (Gunicorn)
- Set a cryptographically strong `SECRET_KEY`

Install Gunicorn:

```bash
pip install gunicorn
```

Start:

```bash
gunicorn -w 4 -b 0.0.0.0:8000 "run:app"
```

---

### Docker

A `Dockerfile` for containerised cloud deployment:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_ENV=production
EXPOSE 8000

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8000", "run:app"]
```

Build and run:

```bash
docker build -t nutrition-app .
docker run -p 8000:8000 \
  -e SECRET_KEY=<key> \
  -e ANTHROPIC_API_KEY=<key> \
  -e DATABASE_URL=postgresql://user:pass@host/db \
  nutrition-app
```

---

### Heroku

```bash
# Install Heroku CLI, then:
heroku create your-app-name
heroku config:set SECRET_KEY=<key> ANTHROPIC_API_KEY=<key> FLASK_ENV=production
heroku addons:create heroku-postgresql:mini

git push heroku main
heroku run python init_db.py
heroku open
```

Add a `Procfile` at the project root:

```
web: gunicorn "run:app"
```

---

### AWS / GCP / Azure

For container-based deployments (ECS, Cloud Run, App Service):

1. Push image to your registry (ECR / GCR / ACR)
2. Set all environment variables as platform secrets
3. Mount a persistent volume or use a managed PostgreSQL service for the database
4. Point a load balancer at port 8000

---

## Database: SQLite → PostgreSQL Migration

1. Update `.env`:
   ```
   DATABASE_URL=postgresql://user:password@host:5432/nutrition_db
   ```

2. Update `config.py` to read `DATABASE_URL`:
   ```python
   SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'sqlite:///{db_path}')
   ```

3. Export data from SQLite and import into PostgreSQL using `pgloader` or a custom script.

4. Run `python init_db.py` against the new database (creates tables without dropping data if tables already exist).

---

## Security Checklist for Production

- [ ] `SECRET_KEY` is a random 32+ byte hex string
- [ ] `DEBUG = False` (enforced by `ProductionConfig`)
- [ ] HTTPS is terminated at a reverse proxy (nginx, Cloudflare, or load balancer)
- [ ] `.env` file is **not** committed to the repository
- [ ] Database is not publicly accessible (bind to localhost or VPC only)
- [ ] `ANTHROPIC_API_KEY` is stored in a secrets manager, not a plain file
- [ ] Firewall only exposes port 80/443; internal Flask port (5000/8000) is not reachable externally
