# Architecture

This document describes the system design, data flows, and key design decisions for Ironman Nutrition Bot.

---

## Overview

Ironman Nutrition Bot is a monolithic [Flask](https://flask.palletsprojects.com/) web application following the **application factory** pattern. It is designed to run on a single host (originally a Raspberry Pi) and can be migrated to a cloud platform without code changes by swapping the database connection string and adjusting the deployment method.

---

## Component Map

```
Browser
  │
  │  HTTP (Jinja2 rendered HTML)
  ▼
┌─────────────────────────────────────────────────────────┐
│                     Flask App                           │
│                                                         │
│  routes.py (Blueprint "main")                           │
│    ├── Authentication   /login /register /logout        │
│    ├── Profile          /profile /setup-profile         │
│    ├── Training         /training/log  /training/log-multi
│    ├── Nutrition        /nutrition/calculate             │
│    ├── History          /history/training /history/nutrition
│    ├── Admin            /admin/pending-users             │
│    └── Chat             (via chat.py)                   │
│                                                         │
│  calculations.py (NutritionCalculator)                  │
│    RMR → NEAT → Training Energy → TEF → TDEE → Macros   │
│    Hydration                                            │
│                                                         │
│  chat.py (NutritionChatBot)                             │
│    Rate limit check → Build system prompt → Claude API  │
│                                                         │
│  models/                                                │
│    User  TrainingSession  MealLog  DailyNutrition  ChatMessage
└───────────────────────────┬─────────────────────────────┘
                            │  SQLAlchemy ORM
                            ▼
                     SQLite / PostgreSQL

                            │  Anthropic SDK
                            ▼
                     Claude API (cloud)
```

---

## Data Models

### `users`

Stores athlete credentials, physical metrics, and HR zone thresholds. The first registered user (`id=1`) acts as admin. A `profile_complete` flag gates access to the dashboard until the athlete setup form is submitted.

**Known limitation:** Admin detection via `id == 1` is a workaround — a future `is_admin` boolean column should replace it (tracked in Unreleased section of CHANGELOG).

### `training_sessions`

One row per training session. Zone percentages (1–5) are stored as floats summing to ~100%. Energy expenditure and training load are calculated at write time by `NutritionCalculator` and stored as denormalised values for fast dashboard reads.

### `daily_nutrition`

One row per athlete per date. Stores both calculated targets and (optionally) consumed values. The `recalculated_count` field tracks how many times TDEE was recomputed on a given day.

**Bug note:** The `date` column currently has `unique=True`, which limits the table to one row per date globally across all users. The correct constraint should be `UniqueConstraint('user_id', 'date')`. See `scripts/migrations/` for the fix.

### `meal_logs`

Optional individual meal entries. The UI for this model exists at the model layer but the routing/templates are not yet complete.

### `chat_messages`

Persists every Claude exchange for rate limiting and usage auditing. Indexed on `(user_id, created_at)` to make the daily count query efficient.

---

## Nutrition Calculation Pipeline

```
User profile (weight, sex, age, body fat, activity level)
         │
         ▼
    calculate_rmr()          Cunningham or Mifflin-St Jeor
         │
         ▼
    calculate_neat(rmr)      rmr × activity_level_multiplier
         │
         ▼
    calculate_training_energy()   zone-based kcal/min × weight adjustment
    (per TrainingSession)         OR power-based for cycling
         │
         ▼
    calculate_tef(baseline + training)   10% of total intake estimate
         │
         ▼
    TDEE = RMR + NEAT + ΣTraining + TEF
         │
         ▼
    calculate_daily_macros(load, tdee)   carb-periodised macro split
         │
         ▼
    calculate_hydration_needs(sessions)  sweat rate × sport × zone intensity
```

### Carbohydrate Periodisation

Carbohydrate targets are dynamically adjusted based on the day's `training_load_score`:

| Load Score | Carb Target |
|-----------|-------------|
| < 50 (rest / easy) | 3–4 g/kg |
| 50–100 (moderate) | 5–6 g/kg |
| 100–150 (high)    | 6–8 g/kg |
| > 150 (very high) | 8–10 g/kg |

See `calculations.py → calculate_daily_macros()` for the exact thresholds.

---

## Authentication & Authorisation

- Passwords are hashed with **Werkzeug's `generate_password_hash`** (pbkdf2:sha256).
- Sessions are managed by **Flask-Login** with a signed cookie (`SECRET_KEY`).
- The `@login_required` decorator protects all routes except `/login` and `/register`.
- Admin routes perform `if user.id != 1` guard — replace with a proper role column before adding more admin users.

---

## Configuration Hierarchy

```
Config (base)
├── DevelopmentConfig   DEBUG=True
├── ProductionConfig    DEBUG=False
└── TestingConfig       in-memory SQLite, TESTING=True
```

`create_app()` selects the config class based on the `FLASK_ENV` environment variable (default: `DevelopmentConfig`).

---

## Technology Choices

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Web framework | Flask 3.0 | Lightweight, minimal footprint for single-host Pi deployment |
| ORM | SQLAlchemy 2.0 | Seamless SQLite→PostgreSQL swap |
| Auth | Flask-Login + Werkzeug | Minimal, no external auth service dependency |
| AI | Anthropic Claude API | Best-in-class instruction-following for nutrition coaching |
| Template engine | Jinja2 (bundled with Flask) | Server-side rendering, no JS build toolchain needed |
| Database | SQLite (dev/Pi), PostgreSQL (cloud) | Zero-config for on-prem; scalable for cloud |
