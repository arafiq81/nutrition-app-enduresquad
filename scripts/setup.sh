#!/usr/bin/env bash
# scripts/setup.sh
# ─────────────────────────────────────────────────────────────────────────────
# Bootstrap a fresh development environment.
# Usage: bash scripts/setup.sh
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "───────────────────────────────────────────────"
echo "  Ironman Nutrition Bot — Development Setup"
echo "───────────────────────────────────────────────"

# Python version check
PYTHON=$(command -v python3 || command -v python)
PY_VERSION=$("$PYTHON" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
REQUIRED="3.10"

python3 -c "
import sys
v = sys.version_info
if (v.major, v.minor) < (3, 10):
    print(f'ERROR: Python 3.10+ required, found {v.major}.{v.minor}')
    sys.exit(1)
" || exit 1

echo "✓ Python $PY_VERSION"

# Virtual environment
if [[ ! -d venv ]]; then
    echo "Creating virtual environment..."
    "$PYTHON" -m venv venv
fi
source venv/bin/activate
echo "✓ Virtual environment activated"

# Dependencies
echo "Installing production dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

echo "Installing dev dependencies..."
pip install --quiet -r requirements-dev.txt
echo "✓ Dependencies installed"

# Environment file
if [[ ! -f .env ]]; then
    cp .env.example .env
    echo ""
    echo "⚠  Created .env from .env.example"
    echo "   Edit .env and set SECRET_KEY and ANTHROPIC_API_KEY before running."
else
    echo "✓ .env already exists"
fi

# Database
echo "Initialising database..."
if [[ -f data/nutrition.db ]]; then
    echo "  Database already exists — skipping init_db.py"
    echo "  Delete data/nutrition.db and re-run to start fresh."
else
    python init_db.py
fi

echo ""
echo "───────────────────────────────────────────────"
echo "  Setup complete! Start the app with:"
echo "    source venv/bin/activate && python run.py"
echo "───────────────────────────────────────────────"
