from PySide6.QtCore import Signal
from PySide6.QtWidgets import QVBoxLayout, QWidget

from kriyex.gui.chat_panel import ChatPanel
from kriyex.gui.input_panel import InputPanel


class ChatPage(QWidget):
    """Main chat page."""

    message_submitted = Signal(str)

    def __init__(self) -> None:
        super().__init__()

        layout = QVBoxLayout(self)

        self.chat_panel = ChatPanel()
        self.input_panel = InputPanel()

        layout.addWidget(self.chat_panel)
        layout.addWidget(self.input_panel)
        self.input_panel.returnPressed.connect(self._submit)

    def _submit(self) -> None:
        message = self.input_panel.text().strip()
        if message:
            self.input_panel.clear()
            self.message_submitted.emit(message)
