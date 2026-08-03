"""
AI Service.

Coordinates the complete AI workflow for KRIYEX.
"""

from __future__ import annotations

from kriyex.core.ai.context import AIContext
from kriyex.core.ai.pipeline import AIPipeline
from kriyex.core.prompting.prompt_builder import PromptBuilder


class AIService:
    """
    Central AI coordinator.
    """

    def __init__(self) -> None:
        self._pipeline = AIPipeline()
        self._prompt_builder = PromptBuilder()

    def analyze(
        self,
        user_message: str,
        chat_id: int | None = None,
        private_mode: bool = False,
    ) -> AIContext:
        """
        Build the AI context.
        """
        return self._pipeline.analyze(
            user_message=user_message,
            chat_id=chat_id,
            private_mode=private_mode,
        )

    def build_system_prompt(
        self,
        context: AIContext,
        memories: tuple[str, ...] = (),
    ) -> str:
        """
        Build the complete system prompt.
        """
        return self._prompt_builder.build(
            context=context,
            memories=memories,
        )