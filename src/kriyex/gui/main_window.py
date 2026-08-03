"""
Main application window for KRIYEX.
"""

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QHBoxLayout,
    QInputDialog,
    QMessageBox,
    QMainWindow,
    QStackedWidget,
    QWidget,
)

from kriyex.app.bootstrap import ApplicationServices
from kriyex.config.settings import settings
from kriyex.core.providers import ProviderError, ProviderFactory
from kriyex.domain.models import PermissionDecision
from kriyex.gui.pages.chat_page import ChatPage
from kriyex.gui.pages.automation_page import AutomationPage
from kriyex.gui.pages.chats_page import ChatsPage
from kriyex.gui.pages.memory_page import MemoryPage
from kriyex.gui.pages.missions_page import MissionsPage
from kriyex.gui.pages.security_page import SecurityPage
from kriyex.gui.pages.tasks_page import TasksPage
from kriyex.gui.response_worker import ResponseWorker
from kriyex.gui.settings_dialog import SettingsDialog
from kriyex.gui.sidebar import Sidebar


class MainWindow(QMainWindow):
    """Main window of the KRIYEX desktop application."""

    def __init__(self, services: ApplicationServices) -> None:
        super().__init__()
        self._services = services
        self._current_chat_id: int | None = None
        self._response_worker: ResponseWorker | None = None

        self._configure_window()
        self._build_ui()

    def _configure_window(self) -> None:
        """Configure the main application window."""

        self.setWindowTitle(settings.app_name)
        self.resize(1200, 800)

    def _build_ui(self) -> None:
        """Build the main user interface."""

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main horizontal layout
        root_layout = QHBoxLayout(central_widget)

        # Left sidebar
        self.sidebar = Sidebar()
        self.sidebar.setMaximumWidth(220)

        # Main chat page
        self.chat_page = ChatPage()
        self.chats_page = ChatsPage(self._services.chat)
        self.tasks_page = TasksPage(self._services.tasks)
        self.memory_page = MemoryPage(self._services.memory)
        self.missions_page = MissionsPage(self._services.missions)
        self.automation_page = AutomationPage(self._services.executor)
        self.security_page = SecurityPage(self._services.permissions, self._services.audit)
        self.pages = QStackedWidget()
        self.pages.addWidget(self.chat_page)
        self.pages.addWidget(self.chats_page)
        self.pages.addWidget(self.tasks_page)
        self.pages.addWidget(self.memory_page)
        self.pages.addWidget(self.missions_page)
        self.pages.addWidget(self.automation_page)
        self.pages.addWidget(self.security_page)

        # Add widgets to layout
        root_layout.addWidget(self.sidebar)
        root_layout.addWidget(self.pages)

        # Status bar
        self.statusBar().showMessage("Ready")
        self.chat_page.message_submitted.connect(self._send_message)
        self.chats_page.chat_selected.connect(self._open_chat)
        self.tasks_page.approval_requested.connect(self._review_permission)
        self.sidebar.itemClicked.connect(
            lambda item: self._navigate(self.sidebar.row(item))
        )
        self._load_latest_chat()

    def _new_chat(self) -> None:
        chat = self._services.chat.create_chat()
        self._current_chat_id = chat.id
        self.chat_page.chat_panel.clear()
        self.pages.setCurrentWidget(self.chat_page)
        self.statusBar().showMessage("New local conversation started")

    def _load_latest_chat(self) -> None:
        chats = self._services.chat.list_chats()
        if chats:
            self._open_chat(chats[0].id)
        else:
            self._new_chat()

    def _open_chat(self, chat_id: int) -> None:
        self._current_chat_id = chat_id
        self.chat_page.chat_panel.show_messages(self._services.chat.messages(chat_id))
        self.pages.setCurrentWidget(self.chat_page)
        self.statusBar().showMessage("Loaded local conversation")

    def _send_message(self, content: str) -> None:
        if self._response_worker is not None and self._response_worker.isRunning():
            self.statusBar().showMessage("KRIYEX is still responding")
            return
        if self._current_chat_id is None:
            self._new_chat()
        assert self._current_chat_id is not None
        if content.lower().startswith("/plan "):
            goal = content[6:].strip()
            if not goal:
                self.statusBar().showMessage("Add a goal after /plan")
                return
            self._create_plan(goal, content)
            return
        if self._is_history_question(content):
            self._answer_history_question(content)
            return
        browser_url = self._browser_url(content)
        if browser_url:
            self._open_browser(browser_url, content)
            return
        messages = self._services.chat.start_turn(self._current_chat_id, content)
        self.chat_page.chat_panel.show_messages(messages)
        self.chat_page.chat_panel.begin_streaming_response()
        self.chat_page.input_panel.setEnabled(False)
        try:
            memories = () if self._services.settings.private_mode() else tuple(
                memory.content for memory in self._services.memory.relevant_to(content)
            )
            provider = ProviderFactory().create(
                self._services.settings.provider_config(), memories
            )
        except ProviderError as error:
            self._finish_response(str(error))
            return
        self._response_worker = ResponseWorker(self._services.chat, provider, self._current_chat_id, self)
        self._response_worker.chunk_received.connect(self.chat_page.chat_panel.append_stream_chunk)
        self._response_worker.response_failed.connect(self._show_provider_error)
        self._response_worker.finished.connect(self._finish_response)
        self._response_worker.start()

    def _create_plan(self, goal: str, command: str) -> None:
        assert self._current_chat_id is not None
        tasks = self._services.tasks.create_plan(goal)
        self._services.chat.start_turn(self._current_chat_id, command)
        summary = "Plan created:\n" + "\n".join(
            f"{task.position}. {task.title}{' (approval required)' if task.requires_approval else ''}"
            for task in tasks
        )
        self._services.chat.complete_turn(self._current_chat_id, summary)
        self.chat_page.chat_panel.show_messages(self._services.chat.messages(self._current_chat_id))
        self.tasks_page.refresh()
        self.statusBar().showMessage("Plan saved locally. Review approval-required steps before execution.")

    @staticmethod
    def _is_history_question(content: str) -> bool:
        normalized = " ".join(content.lower().split())
        return normalized in {
            "what is my last chat",
            "what was my last chat",
            "what is my last message",
            "what was my last message",
        }

    def _answer_history_question(self, question: str) -> None:
        assert self._current_chat_id is not None
        self._services.chat.start_turn(self._current_chat_id, question)
        previous = self._services.chat.previous_user_message(self._current_chat_id)
        if previous is None:
            response = "There is no earlier message in this conversation yet."
        else:
            response = f'Your previous message in this conversation was: “{previous.content}”'
        self._services.chat.complete_turn(self._current_chat_id, response)
        self.chat_page.chat_panel.show_messages(self._services.chat.messages(self._current_chat_id))
        self.statusBar().showMessage("Answered from local conversation history")

    @staticmethod
    def _browser_url(content: str) -> str | None:
        normalized = content.strip().lower()
        if normalized in {"open google", "open google.com"}:
            return "https://www.google.com"
        if normalized.startswith("open http://") or normalized.startswith("open https://"):
            return content.strip()[5:].strip()
        return None

    def _open_browser(self, url: str, request: str) -> None:
        answer = QMessageBox.question(
            self,
            "Internet permission required",
            f"Open this website in your default browser?\n\n{url}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        allowed = answer == QMessageBox.StandardButton.Yes
        self._services.audit.record("open_browser", url, "approved" if allowed else "denied")
        if allowed and QDesktopServices.openUrl(QUrl(url)):
            response = f"Opened {url} in your default browser."
        elif allowed:
            response = f"KRIYEX could not open {url} in the default browser."
        else:
            response = "Browser request cancelled."
        assert self._current_chat_id is not None
        self._services.chat.start_turn(self._current_chat_id, request)
        self._services.chat.complete_turn(self._current_chat_id, response)
        self.chat_page.chat_panel.show_messages(self._services.chat.messages(self._current_chat_id))

    def _show_provider_error(self, error: str) -> None:
        self.statusBar().showMessage(error)

    def _finish_response(self, _error: str = "") -> None:
        self.chat_page.chat_panel.end_streaming_response()
        if self._current_chat_id is not None:
            self.chat_page.chat_panel.show_messages(
                self._services.chat.messages(self._current_chat_id)
            )
        self.chat_page.input_panel.setEnabled(True)
        self.chat_page.input_panel.setFocus()
        self.statusBar().showMessage("Response saved locally")
        self._response_worker = None

    def _navigate(self, row: int) -> None:
        if row == 0:
            self._new_chat()
        elif row == 1:
            self.chats_page.refresh()
            self.pages.setCurrentWidget(self.chats_page)
            self.statusBar().showMessage("Browse conversations stored only on this device.")
        elif row == 2:
            self.missions_page.refresh()
            self.pages.setCurrentWidget(self.missions_page)
            self.statusBar().showMessage("Manage persistent goals and their lifecycle.")
        elif row == 3:
            self.tasks_page.refresh()
            self.pages.setCurrentWidget(self.tasks_page)
            self.statusBar().showMessage("Plans are local and require approval before sensitive execution.")
        elif row == 4:
            self.memory_page.refresh()
            self.pages.setCurrentWidget(self.memory_page)
            self.statusBar().showMessage("Memory is local and only saved when you add it.")
        elif row == 5:
            self.pages.setCurrentWidget(self.automation_page)
            self.statusBar().showMessage("Automation requests are previewed before approval.")
        elif row == 7:
            self.security_page.refresh()
            self.pages.setCurrentWidget(self.security_page)
            self.statusBar().showMessage("Review every saved permission and recent tool request.")
        elif row == 8:
            SettingsDialog(self._services.settings, self).exec()
            self._services.chat.set_private_mode(self._services.settings.private_mode())
            self._services.audit.set_private_mode(self._services.settings.private_mode())
            if self._services.settings.private_mode():
                self._new_chat()
            self.statusBar().showMessage("Model settings saved locally")
        elif row >= 1:
            self.statusBar().showMessage(
                f"{self.sidebar.item(row).text()} is planned for the next module."
            )

    def _review_permission(self, capability: str) -> None:
        choices = ["Allow once", "Always allow", "Deny", "Always deny"]
        choice, accepted = QInputDialog.getItem(
            self,
            "Permission required",
            f"Allow KRIYEX to use {capability} for this task?",
            choices,
            0,
            False,
        )
        if not accepted:
            return
        decision = {
            "Allow once": PermissionDecision.ALLOW_ONCE,
            "Always allow": PermissionDecision.ALWAYS_ALLOW,
            "Deny": PermissionDecision.DENY,
            "Always deny": PermissionDecision.ALWAYS_DENY,
        }[choice]
        self._services.permissions.set_decision(capability, decision)
        self._services.audit.record("permission_decision", capability, decision.value)
        self.security_page.refresh()
        self.statusBar().showMessage(f"{capability} permission: {choice.lower()}.")
