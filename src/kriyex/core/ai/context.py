"""
Shared AI context object.

Every AI subsystem reads from and writes to this object.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AIContext:
    """
    Shared context flowing through the complete AI pipeline.
    """

    # ---------------------------------------------------------
    # User Request
    # ---------------------------------------------------------

    user_message: str

    # ---------------------------------------------------------
    # Goal Understanding
    # ---------------------------------------------------------

    goal: str = "unknown"

    strategy: str = "direct_response"

    # ---------------------------------------------------------
    # Current System Context
    # ---------------------------------------------------------

    current_date: str = ""

    current_time: str = ""

    operating_system: str = ""

    python_version: str = ""

    architecture: str = ""

    processor: str = ""

    # ---------------------------------------------------------
    # Conversation Context
    # ---------------------------------------------------------

    chat_id: int | None = None

    private_mode: bool = False

    # ---------------------------------------------------------
    # AI Memory
    # ---------------------------------------------------------

    memories: list[str] = field(default_factory=list)

    # ---------------------------------------------------------
    # Planning
    # ---------------------------------------------------------

    plan: str = ""

    # ---------------------------------------------------------
    # Future
    # ---------------------------------------------------------

    provider: str = ""

    model: str = ""

    permissions: list[str] = field(default_factory=list)

    tools: list[str] = field(default_factory=list)

    metadata: dict[str, str] = field(default_factory=dict)