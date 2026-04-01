#!/usr/bin/env python3
"""
scripts/migrations/20260401_add_chat_table.py
─────────────────────────────────────────────
Creates the chat_messages table for AI coaching history.

Run once:
    python scripts/migrations/20260401_add_chat_table.py
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "nutrition.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    cursor.execute("""
        CREATE TABLE chat_messages (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL REFERENCES users(id),
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            user_message TEXT NOT NULL,
            bot_response TEXT NOT NULL,
            tokens_used INTEGER DEFAULT 0
        )
    """)
    cursor.execute("CREATE INDEX ix_chat_messages_created_at ON chat_messages(created_at)")
    print("✓ Created chat_messages table")
except sqlite3.OperationalError as e:
    print(f"  Table may already exist: {e}")

conn.commit()
conn.close()
print("\nMigration complete.")
