from __future__ import annotations

from typing import Any

from acmedesk_support.intake import parse_case
from acmedesk_support.loaders import load_csv


def get_account_context(query: str) -> dict[str, Any]:
    intake = parse_case(query)
    if not intake.customer_id:
        return {"found": False, "message": "No matching customer account found."}

    customer_id = intake.customer_id
    account = _one("accounts/accounts.csv", customer_id)
    contract = _one("accounts/contracts.csv", customer_id)
    health = _one("accounts/account_health_scores.csv", customer_id)
    contacts = [
        row
        for row in load_csv("accounts/customer_contacts.csv")
        if row["customer_id"] == customer_id
    ]
    entitlements = [
        row for row in load_csv("accounts/entitlements.csv") if row["customer_id"] == customer_id
    ]
    sla = [
        row
        for row in load_csv("accounts/sla_matrix.csv")
        if row["support_tier"] == contract["support_tier"]
    ]

    return {
        "found": True,
        "account": account,
        "contract": contract,
        "health": health,
        "contacts": contacts,
        "entitlements": entitlements,
        "sla": sla,
    }


def get_sla_for(query: str, severity: str) -> dict[str, str] | None:
    context = get_account_context(query)
    if not context.get("found"):
        return None
    support_tier = context["contract"]["support_tier"]
    for row in load_csv("accounts/sla_matrix.csv"):
        if row["support_tier"] == support_tier and row["severity"] == severity:
            return row
    return None


def _one(relative_path: str, customer_id: str) -> dict[str, str]:
    for row in load_csv(relative_path):
        if row["customer_id"] == customer_id:
            return row
    raise LookupError(f"No row for {customer_id} in {relative_path}")
