from __future__ import annotations

from typing import Any

from acmedesk_support.intake import parse_case
from acmedesk_support.loaders import iter_markdown
from acmedesk_support.text import compact, score_text


def search_knowledge_base(query: str, limit: int = 6) -> list[dict[str, Any]]:
    intake = parse_case(query)
    docs = (
        iter_markdown("knowledge_base")
        + iter_markdown("policies")
        + iter_markdown("product/known_issues")
        + iter_markdown("product/release_notes")
    )
    scored: list[tuple[int, dict[str, str]]] = []
    for doc in docs:
        searchable = f"{doc['title']} {doc['path']} {doc['content']}"
        score = score_text(query, searchable, boosts=[intake.category])
        if score > 0:
            scored.append((score, doc))

    ranked = sorted(scored, key=lambda item: item[0], reverse=True)[:limit]
    return [
        {
            "path": doc["path"],
            "title": doc["title"],
            "match_score": score,
            "summary": compact(doc["content"], 360),
            "customer_safe": "runbooks" not in doc["path"] and "policies" not in doc["path"],
        }
        for score, doc in ranked
    ]
