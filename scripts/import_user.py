#!/usr/bin/env python3
"""
scripts/import_user.py
──────────────────────
Import an athlete profile from a JSON backup.
Creates or updates the user. Sets `approved=True` and `profile_complete=True`.

Usage:
    python scripts/import_user.py [input_file]
    python scripts/import_user.py user_backup.json
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import create_app, db
from app.models import User

IN_FILE = sys.argv[1] if len(sys.argv) > 1 else "user_backup.json"

with open(IN_FILE) as f:
    data = json.load(f)

password = input(f"Set a password for {data['email']}: ").strip()
if len(password) < 8:
    print("Password must be at least 8 characters.")
    sys.exit(1)

app = create_app()
with app.app_context():
    user = User.query.filter_by(email=data["email"]).first()
    if user:
        print(f"User {data['email']} already exists — updating profile.")
    else:
        user = User(email=data["email"])
        db.session.add(user)

    user.name                = data.get("name", "")
    user.age                 = data.get("age")
    user.sex                 = data.get("sex")
    user.weight_kg           = data.get("weight_kg")
    user.height_cm           = data.get("height_cm")
    user.body_fat_percentage = data.get("body_fat_percentage")
    user.activity_level      = data.get("activity_level", "moderate")
    user.training_phase      = data.get("training_phase", "build")
    user.hr_max              = data.get("hr_max")
    user.hr_zone1_max        = data.get("hr_zone1_max")
    user.hr_zone2_max        = data.get("hr_zone2_max")
    user.hr_zone3_max        = data.get("hr_zone3_max")
    user.hr_zone4_max        = data.get("hr_zone4_max")
    user.ftp_watts           = data.get("ftp_watts")
    user.profile_complete    = True
    user.approved            = True
    user.set_password(password)

    db.session.commit()
    print(f"✓ User '{user.name}' imported (id={user.id})")
