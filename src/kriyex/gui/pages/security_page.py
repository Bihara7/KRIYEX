from PySide6.QtWidgets import QLabel, QListWidget, QVBoxLayout, QWidget

from kriyex.core.audit_service import AuditService
from kriyex.core.permissions import PermissionManager


class SecurityPage(QWidget):
    """Transparent local view of capability decisions and recent audit events."""

    def __init__(self, permissions: PermissionManager, audit: AuditService) -> None:
        super().__init__()
        self._permissions = permissions
        self._audit = audit
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Permissions"))
        self.permissions_list = QListWidget()
        layout.addWidget(self.permissions_list)
        layout.addWidget(QLabel("Recent audit events"))
        self.audit_list = QListWidget()
        layout.addWidget(self.audit_list)

    def refresh(self) -> None:
        self.permissions_list.clear()
        decisions = self._permissions.all_decisions()
        if not decisions:
            self.permissions_list.addItem("No permissions have been granted.")
        for capability, decision in decisions:
            self.permissions_list.addItem(f"{capability}: {decision.value}")

        self.audit_list.clear()
        for entry in self._audit.recent(20):
            self.audit_list.addItem(f"{entry.created_at:%Y-%m-%d %H:%M} • {entry.action} • {entry.status}")
