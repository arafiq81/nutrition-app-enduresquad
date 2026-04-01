#!/usr/bin/env bash
# scripts/clean_database.sh
# ─────────────────────────────────────────────────────────────────────────────
# Reset all training and nutrition data for a user (keeps the user account).
# Usage: bash scripts/clean_database.sh [user_id]
# Default user_id: 1
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
source venv/bin/activate 2>/dev/null || true

USER_ID="${1:-1}"

echo "WARNING: This will delete all training sessions and nutrition data for user $USER_ID."
read -rp "Continue? [y/N] " confirm
[[ "${confirm,,}" == "y" ]] || { echo "Aborted."; exit 0; }

python3 - <<EOF
from app import create_app, db
from app.models import TrainingSession, DailyNutrition

app = create_app()
with app.app_context():
    t = TrainingSession.query.filter_by(user_id=$USER_ID).delete()
    n = DailyNutrition.query.filter_by(user_id=$USER_ID).delete()
    db.session.commit()
    print(f"✓ Deleted {t} training sessions")
    print(f"✓ Deleted {n} daily nutrition records")
    print("Database is clean and ready for fresh data.")
EOF
