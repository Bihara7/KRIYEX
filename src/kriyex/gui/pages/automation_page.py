from PySide6.QtWidgets import QLabel, QPushButton, QTextEdit, QVBoxLayout, QWidget

from kriyex.core.executor import ToolExecutor


class AutomationPage(QWidget):
    """Preview-only entry point for approval-gated automation."""

    def __init__(self, executor: ToolExecutor) -> None:
        super().__init__()
        self._executor = executor
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Desktop Automation — actions require explicit approval"))
        self.request = QTextEdit()
        self.request.setPlaceholderText("Describe a terminal or filesystem action to review…")
        layout.addWidget(self.request)
        self.review = QPushButton("Review terminal request")
        self.result = QLabel("No action has been requested.")
        layout.addWidget(self.review)
        layout.addWidget(self.result)
        self.review.clicked.connect(self._review)

    def _review(self) -> None:
        decision = self._executor.request("run_command", self.request.toPlainText().strip() or "Terminal action")
        self.result.setText(decision.explanation + " No command has been executed.")
