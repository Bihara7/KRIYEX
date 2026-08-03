from datetime import UTC, datetime
from pathlib import Path
from typing import Self

from kriyex.core.audit_service import AuditService
from kriyex.core.chat_service import ChatService
from kriyex.core.executor import ToolExecutor
from kriyex.core.memory_service import MemoryService
from kriyex.core.mission_service import MissionService
from kriyex.core.permissions import PermissionManager
from kriyex.core.planner import Planner
from kriyex.core.providers import OllamaProvider
from kriyex.core.settings_service import SettingsService
from kriyex.core.task_service import TaskService
from kriyex.core.tools import create_default_registry
from kriyex.domain.models import (
    Message,
    MessageRole,
    PermissionDecision,
    ProviderConfig,
)
from kriyex.infrastructure.database import Database


def test_chat_is_persisted(tmp_path: Path) -> None:
    database = Database(tmp_path / "kriyex.db")
    database.initialize()
    service = ChatService(database)
    chat = service.create_chat("Test")
    service.add_message(chat.id, MessageRole.USER, "Hello")

    assert service.list_chats()[0].title == "Test"
    assert service.messages(chat.id)[0].content == "Hello"


def test_previous_user_message_ignores_the_current_question(tmp_path: Path) -> None:
    database = Database(tmp_path / "kriyex.db")
    database.initialize()
    service = ChatService(database)
    chat = service.create_chat()
    service.add_message(chat.id, MessageRole.USER, "First request")
    service.add_message(chat.id, MessageRole.ASSISTANT, "First answer")
    service.add_message(chat.id, MessageRole.USER, "What was my last message?")

    previous = service.previous_user_message(chat.id)

    assert previous is not None
    assert previous.content == "First request"


def test_chats_can_be_renamed_pinned_and_deleted(tmp_path: Path) -> None:
    database = Database(tmp_path / "kriyex.db")
    database.initialize()
    service = ChatService(database)
    chat = service.create_chat()
    service.rename_chat(chat.id, "Project notes")
    service.set_pinned(chat.id, True)

    assert service.list_chats()[0].title == "Project notes"
    assert service.list_chats()[0].pinned

    service.delete_chat(chat.id)
    assert service.list_chats() == []


def test_permissions_are_persisted(tmp_path: Path) -> None:
    database = Database(tmp_path / "kriyex.db")
    database.initialize()
    manager = PermissionManager(database)
    manager.set_decision("terminal", PermissionDecision.ALWAYS_ALLOW)

    assert manager.is_allowed("terminal")


def test_default_tools_are_unique() -> None:
    tools = create_default_registry().list_tools()
    assert {tool.name for tool in tools} == {"calculator", "read_file", "run_command"}


def test_provider_settings_are_persisted(tmp_path: Path) -> None:
    database = Database(tmp_path / "kriyex.db")
    database.initialize()
    service = SettingsService(database)
    service.save_provider_config(ProviderConfig(endpoint="http://localhost:11434/", model="qwen3"))

    assert service.provider_config() == ProviderConfig(endpoint="http://localhost:11434", model="qwen3")


def test_ollama_provider_streams_chunks() -> None:
    requests = []

    class FakeResponse:
        def __enter__(self) -> Self:
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def __iter__(self):
            return iter([b'{"message":{"content":"Hello"}}\n', b'{"message":{"content":" world"}}\n'])

    def opener(*args: object, **kwargs: object) -> FakeResponse:
        requests.append(args[0])
        return FakeResponse()

    provider = OllamaProvider(ProviderConfig(), opener=opener)
    messages = [Message(1, 1, MessageRole.USER, "Hi", datetime.now(UTC))]

    assert "".join(provider.stream(messages)) == "Hello world"
    assert b"You are KRIYEX" in requests[0].data


def test_plan_marks_file_changes_for_approval(tmp_path: Path) -> None:
    database = Database(tmp_path / "kriyex.db")
    database.initialize()
    tasks = TaskService(database, Planner()).create_plan("Create a portfolio site")

    assert any(task.requires_approval for task in tasks)
    assert any(task.capability == "filesystem" for task in tasks)


def test_terminal_tool_requires_approval(tmp_path: Path) -> None:
    database = Database(tmp_path / "kriyex.db")
    database.initialize()
    executor = ToolExecutor(
        create_default_registry(), PermissionManager(database), AuditService(database)
    )

    decision = executor.request("run_command", "Run project tests")

    assert not decision.allowed
    assert executor.request("calculator", "Add two values").allowed


def test_allow_once_is_consumed_after_a_tool_request(tmp_path: Path) -> None:
    database = Database(tmp_path / "kriyex.db")
    database.initialize()
    permissions = PermissionManager(database)
    permissions.set_decision("terminal", PermissionDecision.ALLOW_ONCE)
    executor = ToolExecutor(create_default_registry(), permissions, AuditService(database))

    assert executor.request("run_command", "Run a checked command").allowed
    assert not executor.request("run_command", "Run another command").allowed


def test_memories_are_explicitly_managed_and_relevant(tmp_path: Path) -> None:
    database = Database(tmp_path / "kriyex.db")
    database.initialize()
    service = MemoryService(database)
    memory = service.add("Development", "I prefer Python and Ruff for coding projects.")

    assert service.relevant_to("Help me with a Python project") == [memory]

    service.update(memory.id, "Development", "I prefer Rust for systems projects.")
    assert service.relevant_to("Help me with a Rust project")[0].content.startswith("I prefer Rust")

    service.set_enabled(memory.id, False)
    assert service.relevant_to("Help me with a Rust project") == []

    service.delete(memory.id)
    assert service.list_memories() == []


def test_private_chat_messages_are_not_persisted(tmp_path: Path) -> None:
    database = Database(tmp_path / "kriyex.db")
    database.initialize()
    service = ChatService(database)
    service.set_private_mode(True)
    chat = service.create_chat()
    service.add_message(chat.id, MessageRole.USER, "Private message")

    assert service.messages(chat.id)[0].content == "Private message"
    assert service.list_chats() == []


def test_mission_lifecycle_is_persisted(tmp_path: Path) -> None:
    database = Database(tmp_path / "kriyex.db")
    database.initialize()
    service = MissionService(database)
    service.create("Build my portfolio website")

    assert service.list_missions()[0].title == "Build my portfolio website"
