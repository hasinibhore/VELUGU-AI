"""
database/db.py  —  SQLite setup for Velugu
Creates all tables and provides helper functions.
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "velugu.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create all tables if they don't exist and seed demo data."""
    conn = get_conn()
    c = conn.cursor()

    c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            age         INTEGER,
            phone       TEXT
        );

        CREATE TABLE IF NOT EXISTS medicines (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL DEFAULT 1,
            name        TEXT    NOT NULL,
            dosage      TEXT,
            time_label  TEXT,
            taken_today INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS emergency_contacts (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL DEFAULT 1,
            name        TEXT    NOT NULL,
            phone       TEXT    NOT NULL,
            relation    TEXT
        );

        CREATE TABLE IF NOT EXISTS interaction_logs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL DEFAULT 1,
            query       TEXT    NOT NULL,
            timestamp   TEXT    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS caregiver_alerts (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL DEFAULT 1,
            query       TEXT    NOT NULL,
            alert_time  TEXT    NOT NULL,
            resolved    INTEGER NOT NULL DEFAULT 0
        );
    """)

    # Seed demo user if not present
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        c.execute(
            "INSERT INTO users (name, age, phone) VALUES (?, ?, ?)",
            ("రామయ్య", 72, "+91 98765 43210"),
        )
        # Demo medicines
        c.executemany(
            "INSERT INTO medicines (name, dosage, time_label) VALUES (?, ?, ?)",
            [
                ("మెట్‌ఫార్మిన్", "500mg", "ఉదయం"),
                ("అమ్లోడిపైన్", "5mg", "రాత్రి"),
                ("విటమిన్ D3", "1 మాత్ర", "మధ్యాహ్నం"),
            ],
        )
        # Demo emergency contact
        c.execute(
            "INSERT INTO emergency_contacts (name, phone, relation) VALUES (?, ?, ?)",
            ("సురేష్ (కొడుకు)", "+91 99887 76655", "కొడుకు"),
        )

    conn.commit()
    conn.close()


# ── Medicine helpers ──────────────────────────────────────────────────────────

def get_medicines(user_id=1):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM medicines WHERE user_id = ?", (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_medicine(name, dosage, time_label, user_id=1):
    conn = get_conn()
    conn.execute(
        "INSERT INTO medicines (user_id, name, dosage, time_label) VALUES (?,?,?,?)",
        (user_id, name, dosage, time_label),
    )
    conn.commit()
    conn.close()


def mark_taken(med_id):
    conn = get_conn()
    conn.execute(
        "UPDATE medicines SET taken_today = 1 - taken_today WHERE id = ?",
        (med_id,),
    )
    conn.commit()
    conn.close()


def delete_medicine(med_id):
    conn = get_conn()
    conn.execute("DELETE FROM medicines WHERE id = ?", (med_id,))
    conn.commit()
    conn.close()


def reset_daily():
    """Reset taken_today — call at midnight or on each session start."""
    conn = get_conn()
    conn.execute("UPDATE medicines SET taken_today = 0")
    conn.commit()
    conn.close()


# ── Emergency contacts ────────────────────────────────────────────────────────

def get_emergency_contacts(user_id=1):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM emergency_contacts WHERE user_id = ?", (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_emergency_contact(name, phone, relation, user_id=1):
    conn = get_conn()
    conn.execute(
        "INSERT INTO emergency_contacts (user_id, name, phone, relation) VALUES (?,?,?,?)",
        (user_id, name, phone, relation),
    )
    conn.commit()
    conn.close()


# ── Interaction log & confusion detection ────────────────────────────────────

CONFUSION_WINDOW_SECONDS = 300   # 5 minutes
CONFUSION_THRESHOLD      = 3     # same query this many times → alert


def log_interaction(query: str, user_id: int = 1) -> bool:
    """
    Log a query.  Returns True if confusion is detected
    (same query ≥ CONFUSION_THRESHOLD times in the last 5 min).
    """
    now = datetime.now().isoformat()
    conn = get_conn()
    conn.execute(
        "INSERT INTO interaction_logs (user_id, query, timestamp) VALUES (?,?,?)",
        (user_id, query.strip(), now),
    )
    conn.commit()

    # Check for confusion: count similar queries in last 5 min
    cutoff = datetime.now().timestamp() - CONFUSION_WINDOW_SECONDS
    rows = conn.execute(
        "SELECT query, timestamp FROM interaction_logs WHERE user_id = ? ORDER BY id DESC LIMIT 20",
        (user_id,),
    ).fetchall()

    recent_similar = 0
    q_lower = query.strip().lower()
    for row in rows:
        ts = datetime.fromisoformat(row["timestamp"]).timestamp()
        if ts >= cutoff and row["query"].strip().lower() == q_lower:
            recent_similar += 1

    confused = recent_similar >= CONFUSION_THRESHOLD

    if confused:
        # Avoid duplicate alerts: check if an unresolved alert already exists
        existing = conn.execute(
            "SELECT id FROM caregiver_alerts WHERE user_id=? AND query=? AND resolved=0",
            (user_id, query.strip()),
        ).fetchone()
        if not existing:
            conn.execute(
                "INSERT INTO caregiver_alerts (user_id, query, alert_time) VALUES (?,?,?)",
                (user_id, query.strip(), now),
            )
            conn.commit()

    conn.close()
    return confused


def get_active_alerts(user_id: int = 1):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM caregiver_alerts WHERE user_id=? AND resolved=0 ORDER BY id DESC",
        (user_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def resolve_alert(alert_id: int):
    conn = get_conn()
    conn.execute(
        "UPDATE caregiver_alerts SET resolved=1 WHERE id=?", (alert_id,)
    )
    conn.commit()
    conn.close()