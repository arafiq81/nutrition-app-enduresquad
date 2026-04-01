# Changelog

All notable changes to Ironman Nutrition Bot are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). This project uses [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### Planned
- Streaming Claude responses via Server-Sent Events
- Multi-turn chat history (last 5 exchanges as context)
- PostgreSQL support for cloud deployments
- Strava webhook integration for automatic session import
- Role-based access control (replace `user.id == 1` admin check)

---

## [1.3.0] — 2026-04-01

### Added
- AI nutrition coaching chatbot powered by Anthropic Claude (`claude-sonnet-4-20250514`)
- `chat_messages` table for usage tracking and rate limiting
- Daily message limit (3 messages/user/day) with database-backed enforcement
- Chat history view (last 5 exchanges)

### Changed
- System prompt now injects live training load and TDEE targets for context-aware advice

---

## [1.2.0] — 2026-03-01

### Added
- Admin approval workflow — new registrations require approval before access
- `approved`, `approved_at`, `approved_by` columns on `users` table
- Admin dashboard at `/admin/pending-users`
- Approve / reject actions with audit timestamps

### Migration
- Run `scripts/migrations/add_approval_column.py` on existing databases

---

## [1.1.0] — 2026-02-01

### Added
- Multi-session logging route (`/training/log-multi`) — log a full training day in one form
- Strength training sports: `strength_core`, `strength_functional`, `strength_power`, `strength_mobility`, `strength_heavy`
- Zone-specific energy rates for all new sport types

### Fixed
- Zone distribution percentage validation in `NutritionCalculator`

---

## [1.0.0] — 2026-01-01

### Added
- User authentication (Flask-Login, bcrypt password hashing)
- Athlete profile setup (age, sex, weight, height, body fat, HR zones, training phase)
- Single training session logging with heart-rate zone breakdown
- Power-based cycling energy calculation (FTP/watts)
- RMR calculation: Cunningham (with body fat %) or Mifflin-St Jeor
- NEAT, TEF, and TDEE calculations
- Dynamic carbohydrate periodization based on training load score
- Hydration targets (sweat rate estimation per sport × zone intensity)
- Daily nutrition summary with macro breakdown
- Training history and nutrition history views
- SQLite database with application factory pattern

---

[Unreleased]: https://github.com/your-org/nutrition-app/compare/v1.3.0...HEAD
[1.3.0]: https://github.com/your-org/nutrition-app/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/your-org/nutrition-app/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/your-org/nutrition-app/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/your-org/nutrition-app/releases/tag/v1.0.0
