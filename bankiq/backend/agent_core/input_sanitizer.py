"""Prompt-injection and oversized-input guard for RM queries."""

import re
from dataclasses import dataclass
from typing import Optional

MAX_CHARS = 4000

_INJECTION_PATTERNS: list[re.Pattern[str]] = [
    re.compile(p, re.IGNORECASE)
    for p in [
        r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
        r"disregard\s+(your\s+)?(system\s+)?prompt",
        r"you\s+are\s+now\s+(a|an)\s+",
        r"<\s*/?\s*system\s*>",
        r"```\s*system",
        r"jailbreak",
        r"DAN\s+mode",
        r"reveal\s+(your\s+)?(system\s+)?prompt",
        r"override\s+(safety|compliance|guard)",
        r"bypass\s+(pipeline|guard|compliance)",
    ]
]


@dataclass(frozen=True)
class SanitizeResult:
    """Outcome of input sanitization."""

    ok: bool
    text: str
    error: Optional[str] = None


class InputSanitizer:
    """Sanitize RM natural-language queries before they enter the agent loop."""

    def sanitize(self, raw: str) -> SanitizeResult:
        """
        Validate and normalize raw RM query text.

        Parameters:
            raw: Unsanitized query string from the RM.

        Returns:
            SanitizeResult with ok=True and cleaned text, or ok=False with generic error.
        """
        if not raw or not raw.strip():
            return SanitizeResult(ok=False, text="", error="Query cannot be empty.")

        if len(raw) > MAX_CHARS:
            return SanitizeResult(
                ok=False,
                text="",
                error=f"Query exceeds maximum length of {MAX_CHARS} characters.",
            )

        for pattern in _INJECTION_PATTERNS:
            if pattern.search(raw):
                return SanitizeResult(
                    ok=False,
                    text="",
                    error="Query contains disallowed content and was rejected.",
                )

        return SanitizeResult(ok=True, text=raw.strip())
