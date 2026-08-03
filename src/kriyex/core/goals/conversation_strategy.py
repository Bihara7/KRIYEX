"""
Conversation strategies used by KRIYEX.
"""

from enum import Enum


class ConversationStrategy(str, Enum):
    DIRECT_RESPONSE = "direct_response"

    ASK_CLARIFYING_QUESTIONS = "ask_clarifying_questions"

    TEACH_STEP_BY_STEP = "teach_step_by_step"

    CREATE_PLAN = "create_plan"

    EXECUTE_TOOL = "execute_tool"

    SEARCH_WEB = "search_web"

    NATURAL_CHAT = "natural_chat"