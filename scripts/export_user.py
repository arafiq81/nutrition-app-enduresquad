#!/usr/bin/env python3
"""
scripts/export_user.py
──────────────────────
Export an athlete's profile to JSON for backup or migration.

Usage:
    python scripts/export_user.py [user_id]  [output_file]
    python scripts/export_user.py            # exports user 1 → user_backup.json
    python scripts/export_user.py 2 user2.json
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import create_app
from app.models import User

USER_ID   = int(sys.argv[1]) if len(sys.argv) > 1 else 1
OUT_FILE  = sys.argv[2]       if len(sys.argv) > 2 else "user_backup.json"

app = create_app()
with app.app_context():
    user = User.query.get(USER_ID)
    if not user:
        print(f"User {USER_ID} not found.")
        sys.exit(1)

    data = {
        "name": user.name,
        "email": user.email,
        "age": user.age,
        "sex": user.sex,
        "weight_kg": user.weight_kg,
        "height_cm": user.height_cm,
        "body_fat_percentage": user.body_fat_percentage,
        "activity_level": user.activity_level,
        "training_phase": user.training_phase,
        "hr_max": user.hr_max,
        "hr_zone1_max": user.hr_zone1_max,
        "hr_zone2_max": user.hr_zone2_max,
        "hr_zone3_max": user.hr_zone3_max,
        "hr_zone4_max": user.hr_zone4_max,
        "ftp_watts": user.ftp_watts,
    }

    with open(OUT_FILE, "w") as f:
        json.dump(data, f, indent=2)

    print(f"✓ User '{user.name}' exported to {OUT_FILE}")
