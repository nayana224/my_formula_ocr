from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class HistoryEntry:
    id: int
    latex: str
    created_at: str


class HistoryDatabase:
    """OCR 결과를 작은 SQLite 데이터베이스에 저장한다."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def add(self, latex: str) -> None:
        clean = latex.strip()
        if not clean:
            return
        created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with sqlite3.connect(self._path) as connection:
            connection.execute(
                "INSERT INTO history(latex, created_at) VALUES (?, ?)",
                (clean, created_at),
            )
            connection.execute(
                "DELETE FROM history WHERE id NOT IN "
                "(SELECT id FROM history ORDER BY id DESC LIMIT 100)"
            )

    def recent(self, limit: int = 30) -> list[HistoryEntry]:
        with sqlite3.connect(self._path) as connection:
            rows = connection.execute(
                "SELECT id, latex, created_at FROM history ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [HistoryEntry(*row) for row in rows]

    def clear(self) -> None:
        with sqlite3.connect(self._path) as connection:
            connection.execute("DELETE FROM history")

    def _initialize(self) -> None:
        with sqlite3.connect(self._path) as connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS history ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "latex TEXT NOT NULL, "
                "created_at TEXT NOT NULL"
                ")"
            )
