"""
Strategy-specific prompt instructions.
"""

from __future__ import annotations

from kriyex.core.goals.conversation_strategy import ConversationStrategy


class StrategyPrompt:

    @staticmethod
    def build(strategy: ConversationStrategy) -> str:

        prompts = {

            ConversationStrategy.NATURAL_CHAT:
                """
Have a natural conversation.

Do not immediately try to solve a problem.

Focus on being engaging and human.
""",

            ConversationStrategy.TEACH_STEP_BY_STEP:
                """
Teach like an experienced mentor.

Before teaching, determine the user's experience level.

Explain concepts before implementation.

Never overwhelm beginners.
""",

            ConversationStrategy.ASK_CLARIFYING_QUESTIONS:
                """
Do not assume requirements.

Ask the minimum number of questions needed
to fully understand the user's goal.

Once requirements are clear,
offer a structured plan.
""",

            ConversationStrategy.CREATE_PLAN:
                """
Think before acting.

Break the task into clear steps.

Present the plan before execution.
""",

            ConversationStrategy.DIRECT_RESPONSE:
                """
Answer directly and accurately.

Avoid unnecessary information.
""",

            ConversationStrategy.SEARCH_WEB:
                """
Explain that current information requires
a web search tool if one is available.

Do not invent current facts.
""",

            ConversationStrategy.EXECUTE_TOOL:
                """
Explain which tool is required.

Never pretend that the tool has already run.
""",
        }

        return prompts.get(strategy, "")