#!/usr/bin/env python3
"""
scripts/migrations/20260101_add_auth_columns.py
────────────────────────────────────────────────
Adds authentication and profile-completion columns to the users table.

Run once against an existing pre-auth database:
    python scripts/migrations/20260101_add_auth_columns.py
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "nutrition.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

migrations = [
    ("email",            "ALTER TABLE users ADD COLUMN email VARCHAR(120)"),
    ("password_hash",    "ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)"),
    ("name",             "ALTER TABLE users ADD COLUMN name VARCHAR(100)"),
    ("profile_complete", "ALTER TABLE users ADD COLUMN profile_complete BOOLEAN DEFAULT 0"),
]

for column_name, sql in migrations:
    try:
        cursor.execute(sql)
        print(f"✓ Added column: {column_name}")
    except sqlite3.OperationalError:
        print(f"  Column already exists: {column_name}")

conn.commit()
conn.close()
print("\nMigration complete.")
