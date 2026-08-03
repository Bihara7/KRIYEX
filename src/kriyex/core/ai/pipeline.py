"""
AI Pipeline.

Coordinates the reasoning process before sending a request
to the language model.
"""

from __future__ import annotations

from kriyex.core.ai.context import AIContext
from kriyex.core.ai.context_engine import ContextEngine
from kriyex.core.goals.goal_engine import GoalEngine
from kriyex.core.goals.strategy_selector import StrategySelector


class AIPipeline:
    """
    Coordinates the AI reasoning pipeline.
    """

    def __init__(self) -> None:
        self._context_engine = ContextEngine()
        self._goal_engine = GoalEngine()
        self._strategy_selector = StrategySelector()

    def analyze(
        self,
        user_message: str,
        chat_id: int | None = None,
        private_mode: bool = False,
    ) -> AIContext:
        """
        Build the AI context and enrich it with
        goal and conversation strategy.
        """

        context = self._context_engine.build(
            user_message=user_message,
            chat_id=chat_id,
            private_mode=private_mode,
        )

        goal = self._goal_engine.detect_goal(user_message)
        context.goal = goal.value

        strategy = self._strategy_selector.select(goal)
        context.strategy = strategy.value

        return context