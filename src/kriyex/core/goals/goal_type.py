"""
Supported user goal types.
"""

from enum import Enum


class GoalType(str, Enum):
    UNKNOWN = "unknown"

    CHAT = "chat"

    LEARN = "learn"

    BUILD_SOFTWARE = "build_software"

    CODE = "code"

    PLAN = "plan"

    AUTOMATE = "automate"

    RESEARCH = "research"

    WRITE = "write"

    SEARCH = "search"

    CURRENT_INFORMATION = "current_information"

    FILE_OPERATION = "file_operation"

    SYSTEM_OPERATION = "system_operation"