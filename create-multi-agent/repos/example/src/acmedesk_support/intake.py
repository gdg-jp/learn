from __future__ import annotations

from dataclasses import dataclass

from acmedesk_support.loaders import load_csv


@dataclass(frozen=True)
class CaseIntake:
    customer_id: str | None
    customer_name: str | None
    category: str
    impact_scope: str
    initial_urgency: str
    key_signals: list[str]


def parse_case(query: str) -> CaseIntake:
    customer = _find_customer(query)
    category = _detect_category(query)
    signals = _signals(query)
    impact = _impact_scope(query, category)
    urgency = _initial_urgency(query, category, impact)
    return CaseIntake(
        customer_id=customer.get("customer_id") if customer else None,
        customer_name=customer.get("customer_name") if customer else None,
        category=category,
        impact_scope=impact,
        initial_urgency=urgency,
        key_signals=signals,
    )


def _find_customer(query: str) -> dict[str, str] | None:
    lowered = query.lower()
    for account in load_csv("accounts/accounts.csv"):
        if account["customer_name"].lower() in lowered or account["customer_id"].lower() in lowered:
            return account
    return None


def _detect_category(query: str) -> str:
    lowered = query.lower()
    if any(word in lowered for word in ["billing", "invoice", "seat", "請求", "契約"]):
        return "billing"
    if any(word in lowered for word in ["webhook", "crm", "integration", "連携", "遅延"]):
        return "integrations"
    if any(word in lowered for word in ["sso", "saml", "idp", "login", "ログイン", "証明書"]):
        return "authentication"
    if any(word in lowered for word in ["dashboard", "slow", "performance"]):
        return "performance"
    return "general"


def _signals(query: str) -> list[str]:
    lowered = query.lower()
    signals: list[str] = []
    checks = [
        ("all users affected", ["all employees", "all users", "全社員"]),
        ("IdP certificate rotation", ["certificate", "証明書", "idp"]),
        ("Premier support", ["premier"]),
        ("billing amount mismatch", ["higher", "invoice", "請求額", "契約より高い"]),
        ("seat count changed", ["seat", "seats", "seat 数"]),
        ("webhook delay over 30 minutes", ["30", "webhook", "遅延"]),
        ("business impact", ["business impact", "業務影響", "blocked"]),
    ]
    for label, needles in checks:
        if any(needle in lowered for needle in needles):
            signals.append(label)
    return signals


def _impact_scope(query: str, category: str) -> str:
    lowered = query.lower()
    if any(word in lowered for word in ["all employees", "all users", "全社員"]):
        return "All users for the customer are affected."
    if any(word in lowered for word in ["business impact", "業務影響", "blocked"]):
        return "A business-critical workflow is degraded."
    if category == "billing":
        return "Financial operations are affected; no production service outage is reported."
    return "Impact scope requires confirmation from the customer."


def _initial_urgency(query: str, category: str, impact: str) -> str:
    lowered = query.lower()
    all_user_impact = "all users" in impact.lower() or "all employees" in impact.lower()
    if "premier" in lowered and all_user_impact:
        return "High"
    integration_urgent = "30" in lowered or "business" in lowered or "業務影響" in lowered
    if category == "integrations" and integration_urgent:
        return "High"
    if category == "billing":
        return "Medium"
    return "Medium"
