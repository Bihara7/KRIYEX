from PySide6.QtWidgets import QApplication

from kriyex.config.settings import settings
from kriyex.core.audit_service import AuditService
from kriyex.core.chat_service import ChatService
from kriyex.core.executor import ToolExecutor
from kriyex.core.memory_service import MemoryService
from kriyex.core.mission_service import MissionService
from kriyex.core.permissions import PermissionManager
from kriyex.core.planner import Planner
from kriyex.core.settings_service import SettingsService
from kriyex.core.task_service import TaskService
from kriyex.core.tools import ToolRegistry, create_default_registry
from kriyex.infrastructure.database import Database
from kriyex.shared.logging import configure_logging


def create_application() -> QApplication:
    configure_logging()

    app = QApplication([])
    app.setApplicationName(settings.app_name)
    app.setApplicationVersion(settings.version)
    app.setOrganizationName(settings.organization)

    return app


class ApplicationServices:
    def __init__(self) -> None:
        database = Database(settings.database_path)
        database.initialize()
        self.chat = ChatService(database)
        self.permissions = PermissionManager(database)
        self.audit = AuditService(database)
        self.settings = SettingsService(database)
        self.memory = MemoryService(database)
        self.missions = MissionService(database)
        self.chat.set_private_mode(self.settings.private_mode())
        self.audit.set_private_mode(self.settings.private_mode())
        self.tools: ToolRegistry = create_default_registry()
        self.tasks = TaskService(database, Planner())
        self.executor = ToolExecutor(self.tools, self.permissions, self.audit)


def create_services() -> ApplicationServices:
    return ApplicationServices()
