from PySide6.QtWidgets import QLineEdit


class InputPanel(QLineEdit):
    """Message input."""

    def __init__(self) -> None:
        super().__init__()

        self.setPlaceholderText("Ask KRIYEX anything...")
        self.setClearButtonEnabled(True)
