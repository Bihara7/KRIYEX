"""
Prompt Builder for KRIYEX.

Responsible for assembling the complete system prompt from
multiple independent AI subsystems.
"""

from __future__ import annotations

from kriyex.core.ai.context import AIContext
from kriyex.core.ai.strategy_prompt import StrategyPrompt
from kriyex.core.conversation.conversation import Conversation
from kriyex.core.identity.identity import Identity
from kriyex.core.personality.personality import Personality


class PromptBuilder:
    """
    Builds the complete system prompt for KRIYEX.
    """

    def build(
        self,
        context: AIContext,
        memories: tuple[str, ...] = (),
    ) -> str:

        sections: list[str] = []

        # ==========================================================
        # Identity
        # ==========================================================

        sections.append(
            f"""
You are {Identity.NAME}.

Title:
{Identity.TITLE}

{Identity.DESCRIPTION}
""".strip()
        )

        # ==========================================================
        # Product Principles
        # ==========================================================

        principles = "\n".join(
            f"- {principle}" for principle in Identity.PRODUCT_PRINCIPLES
        )

        sections.append(
            f"""
Product Principles

{principles}
""".strip()
        )

        # ==========================================================
        # Personality
        # ==========================================================

        sections.append(
            f"""
Personality

{Personality.STYLE}

Teaching Style

{Personality.TEACHING}

Coding Standards

{Personality.CODING}

Conversation Style

{Personality.CONVERSATION}
""".strip()
        )

        # ==========================================================
        # Conversation
        # ==========================================================

        sections.append(
            f"""
Conversation Guidelines

{Conversation.GENERAL}

{Conversation.TEACHING}

{Conversation.CODING}

{Conversation.CASUAL}

{Conversation.PROBLEM_SOLVING}

{Conversation.SAFETY}
""".strip()
        )

        # ==========================================================
        # Goal & Strategy
        # ==========================================================

        sections.append(
            f"""
Current Goal

{context.goal}

Conversation Strategy

{context.strategy}

Strategy Instructions

{StrategyPrompt.build(context.strategy)}
""".strip()
        )

        # ==========================================================
        # System Context
        # ==========================================================

        sections.append(
            f"""
Current Context

Today's Date:
{context.current_date}

Current Time:
{context.current_time}

Operating System:
{context.operating_system}

Python Version:
{context.python_version}

Architecture:
{context.architecture}

Processor:
{context.processor}
""".strip()
        )

        # ==========================================================
        # Conversation Context
        # ==========================================================

        if memories:
            memory_text = "\n".join(
                f"- {memory}" for memory in memories
            )
        else:
            memory_text = "- None"

        sections.append(
            f"""
Conversation Context

User Message

{context.user_message}

Relevant Memories

{memory_text}
""".strip()
        )

        # ==========================================================
        # Core Rules
        # ==========================================================

        sections.append(
            """
Core Rules

- You are KRIYEX, not the underlying language model.
- Never introduce yourself as Qwen, Llama, Gemma, Mistral, DeepSeek, or any other model unless the user explicitly asks.
- Never pretend an action has been completed.
- Never claim to have opened files, applications, websites, or tools unless KRIYEX has actually confirmed completion.
- Never invent facts.
- Use the provided context instead of relying on outdated knowledge.
- If you do not know something, say so honestly.
- Prioritize user privacy.
- Ask permission before sensitive or destructive actions.
- Think before answering.
- Understand the user's goal before proposing a solution.
- Ask clarifying questions when requirements are incomplete.
- Prefer planning before implementation.
- Keep responses concise unless the user requests more detail.
""".strip()
        )

        return "\n\n".join(sections)