"""
Memory Detector.

Detects information that is worth remembering.
"""

from __future__ import annotations

import re


class MemoryDetector:
    """
    Detects long-term memories from user messages.
    """

    PATTERNS = [
        r"\bmy name is\b",
        r"\bi am\b",
        r"\bi'm\b",
        r"\bmy favorite\b",
        r"\bi like\b",
        r"\bi love\b",
        r"\bi prefer\b",
        r"\bi use\b",
        r"\bi work\b",
        r"\bi study\b",
        r"\bi live\b",
        r"\bremember that\b",
        r"\bnever forget\b",
    ]

    def should_remember(self, message: str) -> bool:
        text = message.lower()

        return any(
            re.search(pattern, text)
            for pattern in self.PATTERNS
        )