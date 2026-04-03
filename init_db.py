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

    # Seed admin user on first deploy only.
    # Reads credentials from env vars — never hardcoded.
    # Skipped entirely if ADMIN_EMAIL is not set or admin already exists.
    admin_email = os.getenv("ADMIN_EMAIL", "").strip().lower()
    admin_password = os.getenv("ADMIN_PASSWORD", "").strip()

    if admin_email and admin_password:
        from app.models import User
        if not User.query.filter_by(email=admin_email).first():
            if len(admin_password) < 12:
                print("✗ ADMIN_PASSWORD must be at least 12 characters — skipping admin seed", file=sys.stderr)
            else:
                admin = User(
                    name="Admin",
                    email=admin_email,
                    profile_complete=False,
                    approved=True,   # admin is pre-approved
                )
                admin.set_password(admin_password)
                db.session.add(admin)
                db.session.commit()
                print(f"✓ Admin user created: {admin_email} (id={admin.id})")
        else:
            print(f"✓ Admin user already exists: {admin_email} — skipped")
