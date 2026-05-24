from __future__ import annotations

import re

REDACTIONS = [
    (re.compile(r"\btenant[_ -]?id[:=]?\s*[a-z0-9-]+", re.IGNORECASE), "tenant identifier"),
    (re.compile(r"\bqueue[_ -]?id[:=]?\s*[a-z0-9-]+", re.IGNORECASE), "queue identifier"),
    (re.compile(r"\bbackend service\b", re.IGNORECASE), "service"),
    (re.compile(r"\binternal timeline\b", re.IGNORECASE), "investigation timeline"),
    (re.compile(r"\braw logs?\b", re.IGNORECASE), "diagnostic details"),
]


def redact_customer_text(text: str) -> str:
    result = text
    for pattern, replacement in REDACTIONS:
        result = pattern.sub(replacement, result)
    return result
