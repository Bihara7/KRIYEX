"""Local audit trail for security-relevant decisions and actions."""

from datetime import datetime

from kriyex.domain.models import AuditEntry
from kriyex.infrastructure.database import Database


class AuditService:
    def __init__(self, database: Database) -> None:
        self._database = database
        self._private_mode = False

    def set_private_mode(self, enabled: bool) -> None:
        self._private_mode = enabled

    def record(self, action: str, detail: str, status: str) -> None:
        if self._private_mode:
            return
        with self._database.connection() as connection:
            connection.execute(
                "INSERT INTO audit_log(action, detail, status) VALUES (?, ?, ?)",
                (action, detail, status),
            )

    def recent(self, limit: int = 100) -> list[AuditEntry]:
        with self._database.connection() as connection:
            rows = connection.execute(
                "SELECT * FROM audit_log ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        return [
            AuditEntry(
                id=row["id"],
                action=row["action"],
                detail=row["detail"],
                status=row["status"],
                created_at=datetime.fromisoformat(row["created_at"]),
            )
            for row in rows
        ]
