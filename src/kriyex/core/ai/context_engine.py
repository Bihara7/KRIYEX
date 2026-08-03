"""
Context Engine.

Collects all information required by the AI before
prompt generation.
"""

from __future__ import annotations

from datetime import datetime

from kriyex.core.ai.context import AIContext
from kriyex.core.system.system_info import system_info


class ContextEngine:
    """
    Builds an AIContext for the current request.
    """

    def build(
        self,
        user_message: str,
        chat_id: int | None = None,
        private_mode: bool = False,
    ) -> AIContext:

        now = datetime.now()

        context = AIContext(
            user_message=user_message,
            chat_id=chat_id,
            private_mode=private_mode,
        )

        context.current_date = now.strftime("%Y-%m-%d")
        context.current_time = now.strftime("%H:%M")

        context.operating_system = system_info.operating_system
        context.python_version = system_info.python_version
        context.architecture = system_info.machine
        context.processor = system_info.processor

        return context