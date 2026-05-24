from __future__ import annotations

from typing import Any

from acmedesk_support.accounts import get_account_context, get_sla_for
from acmedesk_support.incidents import correlate_incidents
from acmedesk_support.intake import parse_case


def recommend_escalation(query: str) -> dict[str, Any]:
    intake = parse_case(query)
    account = get_account_context(query)
    incidents = correlate_incidents(query, limit=2)
    support_tier = account.get("contract", {}).get("support_tier", "Unknown")
    severity = _severity(query, intake.category, support_tier, incidents["likely_related"])
    team = _team(intake.category, query)
    should_escalate = severity in {"SEV1", "SEV2"} or (
        intake.category == "billing" and "invoice" in query.lower()
    )
    sla = get_sla_for(query, severity)

    return {
        "severity": severity,
        "severity_reason": _severity_reason(
            intake.category, support_tier, incidents["likely_related"], query
        ),
        "sla": sla,
        "should_escalate": should_escalate,
        "team": team if should_escalate else "Support owns initial response",
        "reason": _escalation_reason(intake.category, severity, incidents["likely_related"]),
        "attach": _attachments(intake.category),
        "additional_info_needed": _additional_info_needed(intake.category),
        "customer_safe_constraints": [
            "Do not include raw logs, tenant IDs, backend queue names, or internal timelines.",
            "Avoid definitive root-cause statements until the owner team confirms the finding.",
        ],
    }


def _severity(query: str, category: str, support_tier: str, likely_incident: bool) -> str:
    lowered = query.lower()
    if category == "authentication" and (
        "all employees" in lowered or "all users" in lowered or "全社員" in lowered
    ):
        return "SEV2"
    if category == "integrations" and (
        "30" in lowered or "business impact" in lowered or "業務影響" in lowered
    ):
        return "SEV2" if support_tier == "Premier" or likely_incident else "SEV3"
    if category == "billing":
        return "SEV3"
    if likely_incident:
        return "SEV2"
    return "SEV3"


def _team(category: str, query: str) -> str:
    lowered = query.lower()
    if category == "authentication":
        return "Identity Platform"
    if category == "integrations" or "webhook" in lowered:
        return "Integrations Platform"
    if category == "billing":
        return "Billing Operations"
    if category == "performance":
        return "Application Performance"
    return "Support Engineering"


def _severity_reason(category: str, support_tier: str, likely_incident: bool, query: str) -> str:
    if category == "authentication":
        return f"{support_tier} customer reports broad SSO login outage after IdP metadata change."
    if category == "integrations":
        incident_text = " with active incident correlation" if likely_incident else ""
        return f"Webhook delivery delay affects business workflow{incident_text}."
    if category == "billing":
        return "Billing discrepancy affects finance workflow but no production outage is reported."
    return "Severity is based on reported customer impact and current incident correlation."


def _escalation_reason(category: str, severity: str, likely_incident: bool) -> str:
    if category == "billing":
        return (
            "Billing Operations should validate proration, invoice line items, "
            "and contract terms."
        )
    if likely_incident:
        return (
            f"{severity} case may be tied to an active incident and needs "
            "owner-team confirmation."
        )
    return f"{severity} impact meets the escalation policy threshold."


def _attachments(category: str) -> list[str]:
    if category == "authentication":
        return [
            "Affected user count",
            "IdP provider and metadata URL",
            "Sanitized SAML error",
            "Certificate rotation time",
            "Relevant historical ticket IDs",
        ]
    if category == "billing":
        return [
            "Invoice number",
            "Billing period",
            "Seat-change dates and counts",
            "Contract plan and support tier",
            "Prior billing ticket IDs",
        ]
    if category == "integrations":
        return [
            "Affected webhook endpoint IDs",
            "Observed delay and queue age",
            "Recent endpoint response codes",
            "CRM import or rate-limit context",
            "Replay request details",
        ]
    return ["Customer impact summary", "Timeline", "Relevant logs or screenshots"]


def _additional_info_needed(category: str) -> list[str]:
    if category == "authentication":
        return [
            "Exact first failure time",
            "Whether password login still works",
            "Sanitized SAML trace",
        ]
    if category == "billing":
        return ["Invoice number", "Expected amount", "Seat addition date and count"]
    if category == "integrations":
        return ["Affected endpoints", "Example event IDs", "Current endpoint response codes"]
    return ["Affected users", "First observed time", "Screenshots or error messages"]
