"""
Database initialisation — safe to run on every deploy.

Uses db.create_all() which is idempotent: it only creates tables that do not
yet exist and never drops or modifies tables that already have data.  All
existing rows are always preserved.
"""
import os
import sys

from app import create_app, db

app = create_app()

with app.app_context():
    db_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")

    # Mask credentials in log output
    log_uri = db_uri.split("@")[-1] if "@" in db_uri else db_uri
    print(f"  Database: {log_uri}")

    try:
        db.create_all()
        print("✓ Database tables verified / created")
    except Exception as exc:
        print(f"✗ Database initialisation failed: {exc}", file=sys.stderr)
        sys.exit(1)
