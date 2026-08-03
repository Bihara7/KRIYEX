"""
AI Service.

Coordinates the complete AI workflow for KRIYEX.
"""

from __future__ import annotations

from kriyex.core.ai.context import AIContext
from kriyex.core.ai.pipeline import AIPipeline
from kriyex.core.memory.memory_detector import MemoryDetector
from kriyex.core.prompting.prompt_builder import PromptBuilder


class AIService:
    """
    Central AI coordinator.

    Responsible for:
    - Building AI context
    - Building system prompts
    - Detecting long-term memories
    """

    def __init__(self) -> None:
        self._pipeline = AIPipeline()
        self._prompt_builder = PromptBuilder()
        self._memory_detector = MemoryDetector()

        # Injected later by the ApplicationContainer
        self.memory_service = None

    def analyze(
        self,
        user_message: str,
        chat_id: int | None = None,
        private_mode: bool = False,
    ) -> AIContext:
        """
        Analyze a user request and build the AI context.
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

    def should_remember(self, message: str) -> bool:
        """
        Determine whether the user's message is worth
        saving as long-term memory.
        """
        return self._memory_detector.should_remember(message)

    def learn(self, message: str) -> None:
        """
        Automatically store important user information.
        """

        if self.memory_service is None:
            return

        if not self.should_remember(message):
            return

        try:
            self.memory_service.add(
                "Personal",
                message,
            )
        except Exception:
            # Ignore duplicate or invalid memories for now.
            pass