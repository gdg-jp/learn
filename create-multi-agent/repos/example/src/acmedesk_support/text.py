from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any

TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9-]+", re.IGNORECASE)

SYNONYMS = {
    "sso": {"saml", "idp", "identity", "authentication", "login", "certificate", "metadata"},
    "saml": {"sso", "idp", "identity", "authentication", "login", "certificate", "metadata"},
    "login": {"sso", "saml", "authentication", "identity"},
    "certificate": {"saml", "idp", "metadata", "thumbprint"},
    "billing": {"invoice", "seat", "true-up", "contract", "finance", "proration"},
    "invoice": {"billing", "seat", "true-up", "contract", "finance", "proration"},
    "seat": {"billing", "invoice", "true-up", "proration"},
    "webhook": {"integration", "integrations", "crm", "salesforce", "queue", "delay", "latency"},
    "crm": {"webhook", "integration", "integrations", "salesforce", "queue", "delay"},
    "delay": {"latency", "queue", "webhook", "slow"},
}


def tokens(text: str) -> set[str]:
    normalized = text.lower().replace("全社員", " all employees ")
    result = {match.group(0) for match in TOKEN_RE.finditer(normalized)}
    for key, values in SYNONYMS.items():
        if key in result:
            result.update(values)
    return result


def text_from_record(record: dict[str, Any]) -> str:
    parts: list[str] = []
    for value in record.values():
        if isinstance(value, list):
            parts.extend(str(item) for item in value)
        elif isinstance(value, dict):
            parts.append(text_from_record(value))
        else:
            parts.append(str(value))
    return " ".join(parts)


def score_text(query: str, text: str, boosts: Iterable[str] = ()) -> int:
    query_tokens = tokens(query)
    document = text.lower()
    document_tokens = tokens(document)
    score = 0
    for token in query_tokens:
        if token in document_tokens:
            score += 3
        elif token in document:
            score += 1
    for boost in boosts:
        if boost and boost.lower() in document:
            score += 8
    return score


def compact(text: str, max_chars: int = 280) -> str:
    one_line = re.sub(r"\s+", " ", text).strip()
    if len(one_line) <= max_chars:
        return one_line
    return one_line[: max_chars - 3].rstrip() + "..."
