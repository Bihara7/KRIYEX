"""User-approved, local-only long-term memory."""

import re
from datetime import datetime

from kriyex.domain.models import Memory
from kriyex.infrastructure.database import Database


class MemoryService:
    categories = ("Personal", "Work", "Development", "Applications", "Productivity", "Custom")

    def __init__(self, database: Database) -> None:
        self._database = database

    def add(self, category: str, content: str) -> Memory:
        self._validate(category, content)
        with self._database.connection() as connection:
            cursor = connection.execute(
                "INSERT INTO memories(category, content) VALUES (?, ?)",
                (category, content.strip()),
            )
            row = connection.execute("SELECT * FROM memories WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return self._to_memory(row)

    def update(self, memory_id: int, category: str, content: str) -> None:
        self._validate(category, content)
        with self._database.connection() as connection:
            connection.execute(
                """UPDATE memories SET category = ?, content = ?, updated_at = CURRENT_TIMESTAMP
                   WHERE id = ?""",
                (category, content.strip(), memory_id),
            )

    def list_memories(self) -> list[Memory]:
        with self._database.connection() as connection:
            rows = connection.execute("SELECT * FROM memories ORDER BY updated_at DESC, id DESC").fetchall()
        return [self._to_memory(row) for row in rows]

    def set_enabled(self, memory_id: int, enabled: bool) -> None:
        with self._database.connection() as connection:
            connection.execute(
                "UPDATE memories SET enabled = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (enabled, memory_id),
            )

    def delete(self, memory_id: int) -> None:
        with self._database.connection() as connection:
            connection.execute("DELETE FROM memories WHERE id = ?", (memory_id,))

    def relevant_to(self, prompt: str) -> list[Memory]:
        words = set(re.findall(r"[a-z0-9_]{3,}", prompt.lower()))
        matches = []
        for memory in self.list_memories():
            if memory.enabled and words.intersection(re.findall(r"[a-z0-9_]{3,}", memory.content.lower())):
                matches.append(memory)
        return matches

    @staticmethod
    def _validate(category: str, content: str) -> None:
        if category not in MemoryService.categories:
            raise ValueError("Unknown memory category.")
        if not content.strip():
            raise ValueError("Memory content is required.")

    @staticmethod
    def _to_memory(row: object) -> Memory:
        return Memory(
            id=row["id"],
            category=row["category"],
            content=row["content"],
            enabled=bool(row["enabled"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
