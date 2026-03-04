"""
DocQuery Query — Conversation Memory
SQLite-backed conversation history for multi-turn chat.
"""

import json
import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager

DB_PATH = os.getenv("DOCQUERY_MEMORY_DB", "./docquery_memory.db")


def init_memory_db():
    """Initialize the conversation memory database."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            sources TEXT,
            confidence TEXT,
            timestamp TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_session ON conversations(session_id)")
    conn.commit()
    conn.close()


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def add_message(session_id: str, role: str, content: str, sources: list | None = None, confidence: str | None = None):
    """Add a message to conversation history."""
    with get_db() as conn:
        conn.execute(
            "INSERT INTO conversations (session_id, role, content, sources, confidence) VALUES (?, ?, ?, ?, ?)",
            (session_id, role, content, json.dumps(sources) if sources else None, confidence),
        )
        conn.commit()


def get_history(session_id: str, limit: int = 20) -> list[dict]:
    """Get conversation history for a session."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT role, content, sources, confidence, timestamp FROM conversations WHERE session_id = ? ORDER BY id DESC LIMIT ?",
            (session_id, limit),
        ).fetchall()

    messages = []
    for row in reversed(rows):
        msg = {"role": row["role"], "content": row["content"]}
        if row["sources"]:
            msg["sources"] = json.loads(row["sources"])
        if row["confidence"]:
            msg["confidence"] = row["confidence"]
        messages.append(msg)

    return messages


def clear_history(session_id: str):
    """Clear conversation history for a session."""
    with get_db() as conn:
        conn.execute("DELETE FROM conversations WHERE session_id = ?", (session_id,))
        conn.commit()
