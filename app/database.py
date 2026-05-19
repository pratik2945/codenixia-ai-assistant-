import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from app.config import settings


def init_db() -> None:
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT,
                company TEXT,
                message TEXT,
                source TEXT DEFAULT 'web_form',
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS chat_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS automation_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                payload TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )


@contextmanager
def get_connection():
    conn = sqlite3.connect(settings.db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def insert_lead(
    name: str,
    email: str,
    phone: str | None = None,
    company: str | None = None,
    message: str | None = None,
    source: str = "web_form",
) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO leads (name, email, phone, company, message, source, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (name, email, phone, company, message, source, utc_now()),
        )
        return int(cursor.lastrowid)


def get_all_leads() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM leads ORDER BY created_at DESC"
        ).fetchall()
        return [dict(row) for row in rows]


def insert_chat_log(session_id: str, role: str, content: str) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO chat_logs (session_id, role, content, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (session_id, role, content, utc_now()),
        )


def get_chat_logs(limit: int = 100) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM chat_logs ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]


def insert_automation_log(event_type: str, payload: str, status: str) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO automation_logs (event_type, payload, status, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (event_type, payload, status, utc_now()),
        )


def get_automation_logs(limit: int = 50) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM automation_logs ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]


def export_leads_csv() -> Path:
    import csv

    leads = get_all_leads()
    export_path = settings.data_dir / "leads_export.csv"
    fieldnames = ["id", "name", "email", "phone", "company", "message", "source", "created_at"]

    with export_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for lead in leads:
            writer.writerow({k: lead.get(k, "") for k in fieldnames})

    return export_path
