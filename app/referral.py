"""Referral system — viral growth engine."""

import secrets
from app.db import get_db


def create_referral_code(user_id: int) -> str:
    """Generate a unique referral code for a user."""
    code = secrets.token_urlsafe(8)
    conn = get_db()
    conn.execute(
        "UPDATE users SET referral_code = ? WHERE id = ?",
        (code, user_id),
    )
    conn.commit()
    conn.close()
    return code


def get_referral_code(user_id: int) -> str:
    """Get user's referral code, creating one if needed."""
    conn = get_db()
    row = conn.execute(
        "SELECT referral_code FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    conn.close()
    if row and row["referral_code"]:
        return row["referral_code"]
    return create_referral_code(user_id)


def apply_referral(referral_code: str, new_user_id: int) -> bool:
    """Apply referral: give both users bonus generations."""
    conn = get_db()
    referrer = conn.execute(
        "SELECT id FROM users WHERE referral_code = ? AND id != ?",
        (referral_code, new_user_id),
    ).fetchone()
    if not referrer:
        conn.close()
        return False

    # Give referrer 3 bonus generations
    conn.execute(
        "UPDATE users SET free_generations_left = free_generations_left + 3 WHERE id = ?",
        (referrer["id"],),
    )
    # Give new user 3 bonus generations
    conn.execute(
        "UPDATE users SET free_generations_left = free_generations_left + 3, referred_by = ? WHERE id = ?",
        (referrer["id"], new_user_id),
    )
    conn.commit()
    conn.close()
    return True


def get_referral_stats(user_id: int) -> dict:
    """Get referral statistics for a user."""
    conn = get_db()
    row = conn.execute(
        "SELECT referral_code FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    count = conn.execute(
        "SELECT COUNT(*) as cnt FROM users WHERE referred_by = ?",
        (user_id,),
    ).fetchone()
    conn.close()

    code = row["referral_code"] if row and row["referral_code"] else get_referral_code(user_id)
    return {
        "referral_code": code,
        "referral_link": f"?ref={code}",
        "referrals_count": count["cnt"] if count else 0,
        "bonus_generations": (count["cnt"] if count else 0) * 3,
    }
