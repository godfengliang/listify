"""Simple SQLite database for users and listings."""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "listify.db")


def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT DEFAULT '',
            plan TEXT DEFAULT 'free',
            lemon_squeezy_customer_id TEXT,
            lemon_squeezy_subscription_id TEXT,
            free_generations_left INTEGER DEFAULT 3,
            referral_code TEXT UNIQUE,
            referred_by INTEGER,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            product_specs TEXT,
            language TEXT DEFAULT 'English',
            result_json TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE INDEX IF NOT EXISTS idx_listings_user ON listings(user_id);
        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
    """)
    # Add columns that might be missing from older DBs
    _migrate(conn)
    conn.commit()
    conn.close()


def _migrate(conn):
    """Add missing columns to existing tables."""
    existing_cols = [r[1] for r in conn.execute("PRAGMA table_info(users)").fetchall()]
    if "referral_code" not in existing_cols:
        conn.execute("ALTER TABLE users ADD COLUMN referral_code TEXT")
    if "referred_by" not in existing_cols:
        conn.execute("ALTER TABLE users ADD COLUMN referred_by INTEGER")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_users_referral ON users(referral_code)")


init_db()
