from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from kriyex.core.mission_service import MissionService
from kriyex.domain.models import MissionStatus


class MissionsPage(QWidget):
    def __init__(self, missions: MissionService) -> None:
        super().__init__()
        self._missions = missions
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Mission Control"))
        self.goal = QLineEdit()
        self.goal.setPlaceholderText("Create a persistent mission…")
        layout.addWidget(self.goal)
        self.create = QPushButton("Create mission")
        layout.addWidget(self.create)
        self.list = QListWidget()
        layout.addWidget(self.list)
        controls = QHBoxLayout()
        self.status = QComboBox()
        self.status.addItems([item.value for item in MissionStatus])
        self.apply = QPushButton("Update status")
        controls.addWidget(self.status)
        controls.addWidget(self.apply)
        layout.addLayout(controls)
        self.create.clicked.connect(self._create)
        self.apply.clicked.connect(self._apply)
        self.list.itemClicked.connect(self._select)

    def refresh(self) -> None:
        self.list.clear()
        for mission in self._missions.list_missions():
            item = QListWidgetItem(f"[{mission.status.value}] {mission.title}\n{mission.goal}")
            item.setData(Qt.ItemDataRole.UserRole, mission.id)
            item.setData(Qt.ItemDataRole.UserRole + 1, mission.status.value)
            self.list.addItem(item)

    def _create(self) -> None:
        goal = self.goal.text().strip()
        if goal:
            self._missions.create(goal)
            self.goal.clear()
            self.refresh()

    def _select(self, item: QListWidgetItem) -> None:
        self.status.setCurrentText(item.data(Qt.ItemDataRole.UserRole + 1))

    def _apply(self) -> None:
        item = self.list.currentItem()
        if item:
            self._missions.set_status(item.data(Qt.ItemDataRole.UserRole), MissionStatus(self.status.currentText()))
            self.refresh()
