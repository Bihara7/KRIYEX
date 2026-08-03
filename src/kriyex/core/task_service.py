"""Persistence and lifecycle operations for user-visible plans."""

from datetime import datetime

from kriyex.core.planner import Planner
from kriyex.domain.models import Task, TaskStatus
from kriyex.infrastructure.database import Database


class TaskService:
    def __init__(self, database: Database, planner: Planner) -> None:
        self._database = database
        self._planner = planner

    def create_plan(self, goal: str) -> list[Task]:
        steps = self._planner.create_plan(goal)
        with self._database.connection() as connection:
            connection.executemany(
                """INSERT INTO tasks(goal, title, position, status, requires_approval, capability)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                [
                    (
                        goal,
                        step.title,
                        position,
                        TaskStatus.PENDING.value,
                        step.requires_approval,
                        step.capability,
                    )
                    for position, step in enumerate(steps, start=1)
                ],
            )
        return self.for_goal(goal)

    def for_goal(self, goal: str) -> list[Task]:
        with self._database.connection() as connection:
            rows = connection.execute(
                "SELECT * FROM tasks WHERE goal = ? ORDER BY position", (goal,)
            ).fetchall()
        return [self._to_task(row) for row in rows]

    def recent(self, limit: int = 30) -> list[Task]:
        with self._database.connection() as connection:
            rows = connection.execute(
                "SELECT * FROM tasks ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        return [self._to_task(row) for row in reversed(rows)]

    @staticmethod
    def _to_task(row: object) -> Task:
        return Task(
            id=row["id"],
            goal=row["goal"],
            title=row["title"],
            position=row["position"],
            status=TaskStatus(row["status"]),
            requires_approval=bool(row["requires_approval"]),
            capability=row["capability"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )
