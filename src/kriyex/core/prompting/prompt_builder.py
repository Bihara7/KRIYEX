"""
Prompt Builder for KRIYEX.

Responsible for assembling the complete system prompt from
multiple independent components.
"""

from __future__ import annotations

from datetime import datetime

from kriyex.core.conversation.conversation import Conversation
from kriyex.core.identity.identity import Identity
from kriyex.core.personality.personality import Personality
from kriyex.core.system.system_info import system_info


class PromptBuilder:
    """Builds the complete system prompt for KRIYEX."""

    def build(self, memories: tuple[str, ...] = ()) -> str:
        now = datetime.now()

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
        # Conversation Engine
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
        # Current Context
        # ==========================================================

        sections.append(
            f"""
Current Context

Today's Date:
{now.strftime("%Y-%m-%d")}

Current Time:
{now.strftime("%H:%M")}

Operating System:
{system_info.operating_system}

Python Version:
{system_info.python_version}

Architecture:
{system_info.machine}

Processor:
{system_info.processor}

Application:
KRIYEX Desktop
""".strip()
        )

        # ==========================================================
        # Memory
        # ==========================================================

        if memories:
            memory_text = "\n".join(f"- {memory}" for memory in memories)
        else:
            memory_text = "- None"

        sections.append(
            f"""
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
- Never introduce yourself as Qwen, Llama, Gemma, Mistral, DeepSeek, or any other model unless the user explicitly asks about the underlying model.
- Never pretend to execute an action.
- Never claim to have opened files, websites, applications, or tools unless KRIYEX confirms completion.
- Never invent facts.
- Use the provided current date and time instead of your training cutoff.
- If you do not know something, say so honestly.
- Always prioritize user privacy.
- Ask for permission before any sensitive or destructive action.
- Think step by step before answering complex requests.
- Focus on helping the user accomplish real work instead of only answering questions.
- Prefer planning before execution.
- Explain your reasoning when appropriate.
- Keep answers concise unless the user asks for more detail.
""".strip()
        )

        return "\n\n".join(sections)