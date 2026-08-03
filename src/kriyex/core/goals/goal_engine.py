"""
Goal Understanding Engine.

Determines the user's primary goal from a message.
"""

from __future__ import annotations

from kriyex.core.goals.goal_type import GoalType


class GoalEngine:
    """Determines the user's primary goal."""

    def detect_goal(self, message: str) -> GoalType:
        text = message.lower()

        # -------------------------------------------------
        # Learning
        # -------------------------------------------------

        if any(word in text for word in (
            "teach",
            "learn",
            "explain",
            "understand",
        )):
            return GoalType.LEARN

        # -------------------------------------------------
        # Software Development
        # -------------------------------------------------

        if any(word in text for word in (
            "build",
            "create",
            "develop",
            "application",
            "app",
            "software",
        )):
            return GoalType.BUILD_SOFTWARE

        # -------------------------------------------------
        # Coding
        # -------------------------------------------------

        if any(word in text for word in (
            "code",
            "python",
            "java",
            "bug",
            "error",
            "debug",
        )):
            return GoalType.CODE

        # -------------------------------------------------
        # Planning
        # -------------------------------------------------

        if any(word in text for word in (
            "plan",
            "roadmap",
            "steps",
        )):
            return GoalType.PLAN

        # -------------------------------------------------
        # Research
        # -------------------------------------------------

        if any(word in text for word in (
            "research",
            "compare",
            "difference",
        )):
            return GoalType.RESEARCH

        # -------------------------------------------------
        # Current Information
        # -------------------------------------------------

        if any(word in text for word in (
            "today",
            "latest",
            "news",
            "current",
            "president",
            "weather",
        )):
            return GoalType.CURRENT_INFORMATION

        # -------------------------------------------------
        # Automation
        # -------------------------------------------------

        if any(word in text for word in (
            "automate",
            "automation",
        )):
            return GoalType.AUTOMATE

        # -------------------------------------------------
        # Search
        # -------------------------------------------------

        if any(word in text for word in (
            "search",
            "find",
            "locate",
        )):
            return GoalType.SEARCH

        return GoalType.CHAT