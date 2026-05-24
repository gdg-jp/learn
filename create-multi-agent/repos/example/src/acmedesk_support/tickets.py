from __future__ import annotations

from typing import Any

from acmedesk_support.intake import parse_case
from acmedesk_support.loaders import load_jsonl
from acmedesk_support.paths import DATA_DIR
from acmedesk_support.text import score_text, text_from_record


def search_ticket_history(query: str, limit: int = 4) -> list[dict[str, Any]]:
    intake = parse_case(query)
    records = _load_ticket_records()
    scored: list[tuple[int, dict[str, Any]]] = []
    for record in records:
        boosts = [intake.category]
        if intake.customer_id:
            boosts.append(intake.customer_id)
        score = score_text(query, text_from_record(record), boosts=boosts)
        if record.get("category") == intake.category:
            score += 5
        if intake.customer_id and record.get("customer_id") == intake.customer_id:
            score += 8
        if score > 0:
            scored.append((score, record))

    ranked = sorted(scored, key=lambda item: item[0], reverse=True)[:limit]
    return [_enrich_ticket(record, score) for score, record in ranked]


def _load_ticket_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted((DATA_DIR / "tickets").glob("20*.jsonl")):
        for record in load_jsonl(str(path.relative_to(DATA_DIR))):
            records.append(record)
    return records


def _enrich_ticket(record: dict[str, Any], score: int) -> dict[str, Any]:
    ticket_id = record["ticket_id"]
    comments_path = DATA_DIR / "tickets" / "ticket_comments" / f"{ticket_id}-comments.jsonl"
    comments: list[dict[str, Any]] = []
    if comments_path.exists():
        comments = load_jsonl(str(comments_path.relative_to(DATA_DIR)))
    return {
        **record,
        "match_score": score,
        "comments": comments,
        "applicable_insight": _insight(record),
    }


def _insight(record: dict[str, Any]) -> str:
    category = record.get("category")
    if category == "authentication":
        return (
            "Prior SAML cases show certificate metadata freshness and fingerprint checks "
            "are the fastest path."
        )
    if category == "billing":
        return (
            "Prior billing cases show seat-change audit exports make prorated true-up "
            "charges explainable."
        )
    if category == "integrations":
        return (
            "Prior webhook cases show queue age, retry count, endpoint responses, "
            "and replay need to be checked together."
        )
    return (
        "Use the prior cause and resolution as comparison points, "
        "but confirm current incident status."
    )
