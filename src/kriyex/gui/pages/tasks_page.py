from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QListWidget, QPushButton, QVBoxLayout, QWidget

from kriyex.core.task_service import TaskService


class TasksPage(QWidget):
    """Read-only view of plans created from chat goals."""

    approval_requested = Signal(str)

    def __init__(self, task_service: TaskService) -> None:
        super().__init__()
        self._task_service = task_service
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Plans and tasks"))
        self.task_list = QListWidget()
        layout.addWidget(self.task_list)
        self.approve_button = QPushButton("Review required permission")
        self.approve_button.setEnabled(False)
        layout.addWidget(self.approve_button)
        self._tasks = []
        self.task_list.currentRowChanged.connect(self._select_task)
        self.approve_button.clicked.connect(self._request_approval)

    def refresh(self) -> None:
        self.task_list.clear()
        self._tasks = self._task_service.recent()
        for task in self._tasks:
            approval = " • approval required" if task.requires_approval else ""
            self.task_list.addItem(f"{task.position}. {task.title}{approval}")

    def _select_task(self, row: int) -> None:
        task = self._tasks[row] if 0 <= row < len(self._tasks) else None
        self.approve_button.setEnabled(bool(task and task.capability))

    def _request_approval(self) -> None:
        row = self.task_list.currentRow()
        if 0 <= row < len(self._tasks):
            capability = self._tasks[row].capability
            if capability:
                self.approval_requested.emit(capability)
