# Contributing to Ironman Nutrition Bot

Thank you for contributing! Please follow these guidelines to keep the codebase consistent and maintainable.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Branching Strategy](#branching-strategy)
3. [Code Style](#code-style)
4. [Commit Messages](#commit-messages)
5. [Pull Requests](#pull-requests)
6. [Running Tests](#running-tests)
7. [Database Migrations](#database-migrations)

---

## Getting Started

```bash
# Fork & clone the repo
git clone <your-fork-url>
cd nutrition-app

# Set up the development environment
python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
pip install -r requirements-dev.txt

cp .env.example .env
# Fill in .env before running

python init_db.py
python run.py
```

---

## Branching Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Stable, always deployable |
| `develop` | Integration branch for feature work |
| `feature/<name>` | New features |
| `fix/<name>` | Bug fixes |
| `hotfix/<name>` | Urgent production fixes |

Always branch off `develop` for features/fixes. Merge back into `develop` via PR. `develop` is merged into `main` for releases.

---

## Code Style

This project follows [PEP 8](https://peps.python.org/pep-0008/) with the following additions:

- **Formatter:** `black` (line length 100)  
- **Import sorter:** `isort`  
- **Linter:** `flake8`

Run all three before committing:

```bash
black .
isort .
flake8 .
```

### Python conventions

- All functions and classes must have docstrings.
- Use type hints for function signatures in `calculations.py` and `chat.py`.
- Keep route handlers thin — business logic belongs in `calculations.py` or model methods.
- Validate all user input at the route layer; never trust `request.form` values without type-casting and bounds-checking.

### HTML / Jinja2 templates

- 2-space indentation in templates.
- Never bypass Jinja2 auto-escaping (`{{ value | safe }}` is prohibited unless explicitly reviewed).
- Keep templates logic-free — move any computation into route handlers or model properties.

### Database

- All schema changes must be accompanied by a migration script in `scripts/migrations/`.
- Never call `db.drop_all()` in production code.
- Use `db.session.add()` + `db.session.commit()` in route handlers; keep sessions short.

---

## Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <short description>

[optional body]
[optional footer]
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Examples:**

```
feat(chat): add streaming support for Claude responses
fix(models): remove unique constraint on DailyNutrition.date
docs(deployment): add AWS ECS deployment guide
test(calculations): add NEAT calculation edge-case tests
```

---

## Pull Requests

1. Open the PR against `develop` (not `main`).
2. Fill in the PR template:
   - **What changed** and why
   - **How to test** it manually
   - **Screenshots** if UI changed
3. All CI checks must pass before review.
4. At least one approving review is required before merge.
5. Squash-merge to keep `develop` history clean.

---

## Running Tests

```bash
# Run the full test suite
pytest

# With coverage report
pytest --cov=app --cov-report=term-missing

# Run a specific test file
pytest tests/test_calculations.py -v
```

Tests require a `testing` config — `TestingConfig` in `config.py` uses an in-memory SQLite database so tests never touch the development database.

---

## Database Migrations

This project does **not** use Alembic. Schema changes are managed via standalone migration scripts in `scripts/migrations/`.

When you add or modify a model:

1. Create `scripts/migrations/YYYYMMDD_<description>.py`
2. Use raw SQLite `ALTER TABLE` statements (see existing scripts as examples)
3. Document the migration in `CHANGELOG.md`
4. Test the migration on a copy of the database before opening a PR

---

## Reporting Bugs

Open a GitHub Issue with:
- Steps to reproduce
- Expected vs. actual behaviour
- Python version, OS, and Flask version (`pip show flask`)
- Relevant log output (`journalctl -u nutrition-bot -n 50`)
