"""Simple auth with hashed passwords."""

import hashlib
import secrets
from app.db import get_db


def _hash(password: str) -> str:
    salt = secrets.token_hex(8)
    h = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    return f"{salt}${h}"


def _verify(password: str, stored: str) -> bool:
    salt, h = stored.split("$")
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest() == h


def create_user(email: str, password: str, name: str = "") -> dict:
    conn = get_db()
    try:
        cursor = conn.execute(
            "INSERT INTO users (email, password_hash, name) VALUES (?, ?, ?)",
            (email.lower().strip(), _hash(password), name),
        )
        conn.commit()
        return {"id": cursor.lastrowid, "email": email, "plan": "free"}
    except Exception:
        return None
    finally:
        conn.close()


def verify_user(email: str, password: str) -> dict | None:
    conn = get_db()
    row = conn.execute(
        "SELECT id, email, password_hash, name, plan, free_generations_left FROM users WHERE email = ?",
        (email.lower().strip(),),
    ).fetchone()
    conn.close()

    if row and _verify(password, row["password_hash"]):
        return dict(row)
    return None


def get_user(user_id: int) -> dict | None:
    conn = get_db()
    row = conn.execute(
        "SELECT id, email, name, plan, free_generations_left, lemon_squeezy_subscription_id FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def decrement_free_generations(user_id: int) -> bool:
    """Return True if generation was allowed."""
    conn = get_db()
    row = conn.execute(
        "SELECT plan, free_generations_left FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    if not row:
        conn.close()
        return False

    if row["plan"] != "free":
        conn.close()
        return True  # paid users have unlimited

    if row["free_generations_left"] <= 0:
        conn.close()
        return False

    conn.execute(
        "UPDATE users SET free_generations_left = free_generations_left - 1 WHERE id = ?",
        (user_id,),
    )
    conn.commit()
    conn.close()
    return True


def save_listing(user_id: int, product_name: str, product_specs: str, language: str, result_json: str) -> int:
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO listings (user_id, product_name, product_specs, language, result_json) VALUES (?, ?, ?, ?, ?)",
        (user_id, product_name, product_specs, language, result_json),
    )
    conn.commit()
    lid = cursor.lastrowid
    conn.close()
    return lid


def get_user_listings(user_id: int, limit: int = 20) -> list:
    conn = get_db()
    rows = conn.execute(
        "SELECT id, product_name, language, created_at FROM listings WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
        (user_id, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_listing(listing_id: int, user_id: int) -> dict | None:
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM listings WHERE id = ? AND user_id = ?",
        (listing_id, user_id),
    ).fetchone()
    conn.close()
    return dict(row) if row else None
