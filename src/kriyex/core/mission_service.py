from datetime import datetime

from kriyex.domain.models import Mission, MissionStatus
from kriyex.infrastructure.database import Database


class MissionService:
    def __init__(self, database: Database) -> None:
        self._database = database

    def create(self, goal: str) -> Mission:
        title = " ".join(goal.split())[:60]
        with self._database.connection() as connection:
            cursor = connection.execute("INSERT INTO missions(title, goal) VALUES (?, ?)", (title, goal))
            row = connection.execute("SELECT * FROM missions WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return self._to_mission(row)

    def list_missions(self) -> list[Mission]:
        with self._database.connection() as connection:
            rows = connection.execute("SELECT * FROM missions ORDER BY updated_at DESC, id DESC").fetchall()
        return [self._to_mission(row) for row in rows]

    def set_status(self, mission_id: int, status: MissionStatus) -> None:
        with self._database.connection() as connection:
            connection.execute("UPDATE missions SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (status.value, mission_id))

    @staticmethod
    def _to_mission(row: object) -> Mission:
        return Mission(row["id"], row["title"], row["goal"], MissionStatus(row["status"]), datetime.fromisoformat(row["created_at"]), datetime.fromisoformat(row["updated_at"]))
