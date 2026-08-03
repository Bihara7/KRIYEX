from kriyex.config.settings import settings
from kriyex.core.ai_service import AIService
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


class ApplicationContainer:
    """
    Central container for all shared application services.
    """

    def __init__(self) -> None:
        # Database
        self.database = Database(settings.database_path)
        self.database.initialize()

        # Core Services
        self.chat = ChatService(self.database)
        self.permissions = PermissionManager(self.database)
        self.audit = AuditService(self.database)
        self.settings = SettingsService(self.database)
        self.memory = MemoryService(self.database)
        self.missions = MissionService(self.database)

        # AI
        self.ai = AIService()

        # Private Mode
        self.chat.set_private_mode(self.settings.private_mode())
        self.audit.set_private_mode(self.settings.private_mode())

        # Tools
        self.tools: ToolRegistry = create_default_registry()

        self.tasks = TaskService(
            self.database,
            Planner(),
        )

        self.executor = ToolExecutor(
            self.tools,
            self.permissions,
            self.audit,
        )