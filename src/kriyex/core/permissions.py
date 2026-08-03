"""Centralized capability checks for high-impact operations."""

from kriyex.domain.models import PermissionDecision
from kriyex.infrastructure.database import Database


class PermissionManager:
    def __init__(self, database: Database) -> None:
        self._database = database

    def decision_for(self, capability: str) -> PermissionDecision | None:
        with self._database.connection() as connection:
            row = connection.execute(
                "SELECT decision FROM permissions WHERE capability = ?", (capability,)
            ).fetchone()
        return PermissionDecision(row["decision"]) if row else None

    def set_decision(self, capability: str, decision: PermissionDecision) -> None:
        with self._database.connection() as connection:
            connection.execute(
                """INSERT INTO permissions(capability, decision, updated_at)
                   VALUES (?, ?, CURRENT_TIMESTAMP)
                   ON CONFLICT(capability) DO UPDATE SET decision = excluded.decision,
                   updated_at = CURRENT_TIMESTAMP""",
                (capability, decision.value),
            )

    def is_allowed(self, capability: str) -> bool:
        return self.decision_for(capability) == PermissionDecision.ALWAYS_ALLOW

    def consume_allow_once(self, capability: str) -> bool:
        if self.decision_for(capability) != PermissionDecision.ALLOW_ONCE:
            return False
        with self._database.connection() as connection:
            connection.execute("DELETE FROM permissions WHERE capability = ?", (capability,))
        return True

    def all_decisions(self) -> list[tuple[str, PermissionDecision]]:
        with self._database.connection() as connection:
            rows = connection.execute("SELECT capability, decision FROM permissions ORDER BY capability").fetchall()
        return [(row["capability"], PermissionDecision(row["decision"])) for row in rows]
