from PySide6.QtWidgets import QListWidget


class Sidebar(QListWidget):
    """Primary application navigation."""

    def __init__(self) -> None:
        super().__init__()
        self.addItems(["New Chat", "Chats", "Missions", "Tasks", "Memory", "Automation", "Tools", "Security", "Settings"])
