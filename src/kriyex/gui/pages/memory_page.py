"""Explicit user controls for local long-term memory."""

import json
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from kriyex.core.memory_service import MemoryService


class MemoryPage(QWidget):
    """Manage only memories deliberately added by the user."""

    def __init__(self, memory_service: MemoryService) -> None:
        super().__init__()
        self._memory_service = memory_service
        self._editing_id: int | None = None
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Long-term memory (saved only when you add it here)"))
        self.memory_list = QListWidget()
        layout.addWidget(self.memory_list)
        self.category = QComboBox()
        self.category.addItems(MemoryService.categories)
        layout.addWidget(self.category)
        self.content = QTextEdit()
        self.content.setPlaceholderText("Example: I prefer Python type hints and Ruff for linting.")
        self.content.setFixedHeight(90)
        layout.addWidget(self.content)
        actions = QHBoxLayout()
        self.save_button = QPushButton("Add memory")
        self.toggle_button = QPushButton("Enable / disable")
        self.delete_button = QPushButton("Delete")
        self.export_button = QPushButton("Export")
        for button in (self.save_button, self.toggle_button, self.delete_button, self.export_button):
            actions.addWidget(button)
        layout.addLayout(actions)
        self.memory_list.itemClicked.connect(self._select)
        self.save_button.clicked.connect(self._save)
        self.toggle_button.clicked.connect(self._toggle)
        self.delete_button.clicked.connect(self._delete)
        self.export_button.clicked.connect(self._export)

    def refresh(self) -> None:
        self.memory_list.clear()
        for memory in self._memory_service.list_memories():
            state = "enabled" if memory.enabled else "disabled"
            item = QListWidgetItem(f"[{memory.category} • {state}] {memory.content}")
            item.setData(Qt.ItemDataRole.UserRole, memory.id)
            item.setData(Qt.ItemDataRole.UserRole + 1, memory.enabled)
            self.memory_list.addItem(item)

    def _select(self, item: QListWidgetItem) -> None:
        self._editing_id = item.data(Qt.ItemDataRole.UserRole)
        display = item.text()
        category = display.split(" • ", 1)[0].removeprefix("[")
        index = self.category.findText(category)
        if index >= 0:
            self.category.setCurrentIndex(index)
        self.content.setPlainText(display.split("] ", 1)[1])
        self.save_button.setText("Update memory")

    def _save(self) -> None:
        try:
            if self._editing_id is None:
                self._memory_service.add(self.category.currentText(), self.content.toPlainText())
            else:
                self._memory_service.update(
                    self._editing_id, self.category.currentText(), self.content.toPlainText()
                )
        except ValueError as error:
            QMessageBox.warning(self, "Memory", str(error))
            return
        self.content.clear()
        self._editing_id = None
        self.save_button.setText("Add memory")
        self.refresh()

    def _toggle(self) -> None:
        item = self.memory_list.currentItem()
        if item:
            self._memory_service.set_enabled(
                item.data(Qt.ItemDataRole.UserRole),
                not item.data(Qt.ItemDataRole.UserRole + 1),
            )
            self.refresh()

    def _delete(self) -> None:
        item = self.memory_list.currentItem()
        if item and QMessageBox.question(self, "Delete memory", "Delete this memory permanently?") == QMessageBox.StandardButton.Yes:
            self._memory_service.delete(item.data(Qt.ItemDataRole.UserRole))
            self.content.clear()
            self._editing_id = None
            self.save_button.setText("Add memory")
            self.refresh()

    def _export(self) -> None:
        filename, _ = QFileDialog.getSaveFileName(self, "Export memories", "kriyex-memories.json", "JSON (*.json)")
        if not filename:
            return
        data = [
            {"category": memory.category, "content": memory.content, "enabled": memory.enabled}
            for memory in self._memory_service.list_memories()
        ]
        Path(filename).write_text(json.dumps(data, indent=2), encoding="utf-8")
