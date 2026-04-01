#!/usr/bin/env python3
"""
scripts/migrations/20260301_add_approval_columns.py
────────────────────────────────────────────────────
Adds the admin approval columns to the users table.

Run once against an existing database:
    python scripts/migrations/20260301_add_approval_columns.py
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "nutrition.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

migrations = [
    ("approved",    "ALTER TABLE users ADD COLUMN approved BOOLEAN DEFAULT 0"),
    ("approved_at", "ALTER TABLE users ADD COLUMN approved_at DATETIME"),
    ("approved_by", "ALTER TABLE users ADD COLUMN approved_by INTEGER"),
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
