"""
Maps detected goals to conversation strategies.
"""

from __future__ import annotations

from kriyex.core.goals.conversation_strategy import ConversationStrategy
from kriyex.core.goals.goal_type import GoalType


class StrategySelector:
    """Selects the best strategy for a detected goal."""

    def select(self, goal: GoalType) -> ConversationStrategy:

        strategy_map = {
            GoalType.CHAT: ConversationStrategy.NATURAL_CHAT,

            GoalType.LEARN: ConversationStrategy.TEACH_STEP_BY_STEP,

            GoalType.BUILD_SOFTWARE: ConversationStrategy.ASK_CLARIFYING_QUESTIONS,

            GoalType.CODE: ConversationStrategy.DIRECT_RESPONSE,

            GoalType.PLAN: ConversationStrategy.CREATE_PLAN,

            GoalType.AUTOMATE: ConversationStrategy.CREATE_PLAN,

            GoalType.RESEARCH: ConversationStrategy.DIRECT_RESPONSE,

            GoalType.SEARCH: ConversationStrategy.EXECUTE_TOOL,

            GoalType.CURRENT_INFORMATION: ConversationStrategy.SEARCH_WEB,

            GoalType.FILE_OPERATION: ConversationStrategy.EXECUTE_TOOL,

            GoalType.SYSTEM_OPERATION: ConversationStrategy.EXECUTE_TOOL,

            GoalType.UNKNOWN: ConversationStrategy.DIRECT_RESPONSE,
        }

        return strategy_map.get(
            goal,
            ConversationStrategy.DIRECT_RESPONSE,
        )