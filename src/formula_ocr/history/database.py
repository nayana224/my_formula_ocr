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
    favorite: bool


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
                "INSERT INTO history(latex, created_at, favorite) VALUES (?, ?, 0)",
                (clean, created_at),
            )
            connection.execute(
                "DELETE FROM history WHERE favorite = 0 AND id NOT IN "
                "(SELECT id FROM history WHERE favorite = 0 ORDER BY id DESC LIMIT 100)"
            )

    def recent(self, limit: int = 30, query: str = "") -> list[HistoryEntry]:
        clean_query = query.strip()
        with sqlite3.connect(self._path) as connection:
            if clean_query:
                rows = connection.execute(
                    "SELECT id, latex, created_at, favorite FROM history "
                    "WHERE latex LIKE ? ORDER BY favorite DESC, id DESC LIMIT ?",
                    (f"%{clean_query}%", limit),
                ).fetchall()
            else:
                rows = connection.execute(
                    "SELECT id, latex, created_at, favorite FROM history "
                    "ORDER BY favorite DESC, id DESC LIMIT ?",
                    (limit,),
                ).fetchall()
        return [HistoryEntry(row[0], row[1], row[2], bool(row[3])) for row in rows]

    def set_favorite(self, entry_id: int, favorite: bool) -> None:
        with sqlite3.connect(self._path) as connection:
            connection.execute(
                "UPDATE history SET favorite = ? WHERE id = ?",
                (int(favorite), entry_id),
            )

    def delete(self, entry_id: int) -> None:
        with sqlite3.connect(self._path) as connection:
            connection.execute("DELETE FROM history WHERE id = ?", (entry_id,))

    def clear(self) -> None:
        with sqlite3.connect(self._path) as connection:
            connection.execute("DELETE FROM history")

    def _initialize(self) -> None:
        with sqlite3.connect(self._path) as connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS history ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "latex TEXT NOT NULL, "
                "created_at TEXT NOT NULL, "
                "favorite INTEGER NOT NULL DEFAULT 0"
                ")"
            )
            columns = {
                row[1]
                for row in connection.execute("PRAGMA table_info(history)").fetchall()
            }
            if "favorite" not in columns:
                connection.execute(
                    "ALTER TABLE history ADD COLUMN favorite INTEGER NOT NULL DEFAULT 0"
                )
