from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QInputDialog,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from kriyex.core.chat_service import ChatService


class ChatsPage(QWidget):
    """Local conversation history and basic chat management."""

    chat_selected = Signal(int)

    def __init__(self, chat_service: ChatService) -> None:
        super().__init__()
        self._chat_service = chat_service
        layout = QVBoxLayout(self)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search chat titles...")
        layout.addWidget(self.search_input)
        self.chat_list = QListWidget()
        layout.addWidget(self.chat_list)
        actions = QHBoxLayout()
        self.pin_button = QPushButton("Pin / unpin")
        self.rename_button = QPushButton("Rename")
        self.delete_button = QPushButton("Delete")
        actions.addWidget(self.pin_button)
        actions.addWidget(self.rename_button)
        actions.addWidget(self.delete_button)
        layout.addLayout(actions)
        self.search_input.textChanged.connect(self.refresh)
        self.chat_list.itemActivated.connect(self._open_selected)
        self.pin_button.clicked.connect(self._toggle_pin)
        self.rename_button.clicked.connect(self._rename_selected)
        self.delete_button.clicked.connect(self._delete_selected)

    def refresh(self) -> None:
        selected_id = self._selected_id()
        self.chat_list.clear()
        for chat in self._chat_service.list_chats(self.search_input.text()):
            prefix = "★ " if chat.pinned else ""
            item = QListWidgetItem(f"{prefix}{chat.title}\n{chat.updated_at:%Y-%m-%d %H:%M}")
            item.setData(Qt.ItemDataRole.UserRole, chat.id)
            item.setData(Qt.ItemDataRole.UserRole + 1, chat.pinned)
            self.chat_list.addItem(item)
            if chat.id == selected_id:
                self.chat_list.setCurrentItem(item)

    def _selected_id(self) -> int | None:
        item = self.chat_list.currentItem()
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    def _open_selected(self, item: QListWidgetItem) -> None:
        self.chat_selected.emit(item.data(Qt.ItemDataRole.UserRole))

    def _toggle_pin(self) -> None:
        item = self.chat_list.currentItem()
        if item:
            self._chat_service.set_pinned(
                item.data(Qt.ItemDataRole.UserRole),
                not item.data(Qt.ItemDataRole.UserRole + 1),
            )
            self.refresh()

    def _rename_selected(self) -> None:
        chat_id = self._selected_id()
        item = self.chat_list.currentItem()
        if chat_id is None or item is None:
            return
        title, accepted = QInputDialog.getText(self, "Rename chat", "Title:", text=item.text().split("\n")[0].removeprefix("★ "))
        if accepted and title.strip():
            self._chat_service.rename_chat(chat_id, title)
            self.refresh()

    def _delete_selected(self) -> None:
        chat_id = self._selected_id()
        if chat_id is None:
            return
        answer = QMessageBox.question(self, "Delete chat", "Delete this local conversation and its messages?")
        if answer == QMessageBox.StandardButton.Yes:
            self._chat_service.delete_chat(chat_id)
            self.refresh()
