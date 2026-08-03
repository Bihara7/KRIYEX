"""Typed records shared between the UI, application services, and storage."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class PermissionDecision(StrEnum):
    ALLOW_ONCE = "allow_once"
    ALWAYS_ALLOW = "always_allow"
    DENY = "deny"
    ALWAYS_DENY = "always_deny"


class SafetyLevel(StrEnum):
    SAFE = "safe"
    CONFIRM = "confirm"
    RESTRICTED = "restricted"


@dataclass(frozen=True)
class ProviderConfig:
    provider: str = "ollama"
    endpoint: str = "http://127.0.0.1:11434"
    model: str = "llama3.2"


class TaskStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETE = "complete"
    BLOCKED = "blocked"


class MissionStatus(StrEnum):
    PLANNING = "planning"
    PAUSED = "paused"
    ACTIVE = "active"
    COMPLETE = "complete"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class Mission:
    id: int
    title: str
    goal: str
    status: MissionStatus
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class Task:
    id: int
    goal: str
    title: str
    position: int
    status: TaskStatus
    requires_approval: bool
    capability: str | None
    created_at: datetime


@dataclass(frozen=True)
class Memory:
    id: int
    category: str
    content: str
    enabled: bool
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class Chat:
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    pinned: bool = False


@dataclass(frozen=True)
class Message:
    id: int
    chat_id: int
    role: MessageRole
    content: str
    created_at: datetime


@dataclass(frozen=True)
class AuditEntry:
    id: int
    action: str
    detail: str
    status: str
    created_at: datetime
