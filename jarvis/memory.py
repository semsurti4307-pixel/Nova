from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict, List
import time


class ConversationMemory:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(db_path))
        self._init_schema()

    def _init_schema(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                ts REAL NOT NULL
            )
            """
        )
        self.conn.commit()

    def append(self, session: str, role: str, content: str) -> None:
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO messages (session, role, content, ts) VALUES (?, ?, ?, ?)",
            (session, role, content, time.time()),
        )
        self.conn.commit()

    def recent(self, session: str, limit: int = 30) -> List[Dict[str, str]]:
        cur = self.conn.cursor()
        cur.execute(
            "SELECT role, content FROM messages WHERE session = ? ORDER BY id DESC LIMIT ?",
            (session, limit),
        )
        rows = list(cur.fetchall())[::-1]
        return [{"role": r, "content": c} for (r, c) in rows]

    def clear(self, session: str) -> None:
        cur = self.conn.cursor()
        cur.execute("DELETE FROM messages WHERE session = ?", (session,))
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()
