#!/usr/bin/env bash
# scripts/lint.sh
# ─────────────────────────────────────────────────────────────────────────────
# Run all linters and formatters.
# Usage: bash scripts/lint.sh [--fix]
# Pass --fix to auto-format with black and isort.
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

FIX=false
for arg in "$@"; do
    [[ "$arg" == "--fix" ]] && FIX=true
done

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
source venv/bin/activate 2>/dev/null || true

echo "Running isort..."
if $FIX; then
    isort .
else
    isort --check-only --diff .
fi

echo "Running black..."
if $FIX; then
    black .
else
    black --check .
fi

echo "Running flake8..."
flake8 app/ config.py run.py --max-line-length=100 --extend-ignore=E501

echo "✓ All checks passed"
