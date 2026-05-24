from __future__ import annotations

from typing import Any

from acmedesk_support.accounts import get_account_context
from acmedesk_support.incidents import correlate_incidents
from acmedesk_support.intake import parse_case
from acmedesk_support.knowledge import search_knowledge_base
from acmedesk_support.policy import recommend_escalation
from acmedesk_support.redaction import redact_customer_text
from acmedesk_support.tickets import search_ticket_history


def build_escalation_brief(query: str) -> str:
    intake = parse_case(query)
    account = get_account_context(query)
    tickets = search_ticket_history(query, limit=3)
    knowledge = search_knowledge_base(query, limit=5)
    incidents = correlate_incidents(query, limit=3)
    recommendation = recommend_escalation(query)

    sections = [
        "# Customer Support Escalation Brief",
        _case_summary(query, intake),
        _account_context(account),
        _historical_tickets(tickets),
        _knowledge_refs(knowledge),
        _incident_correlation(incidents),
        _severity_recommendation(recommendation),
        _escalation_decision(recommendation),
        _draft_customer_response(intake, incidents, recommendation),
        _internal_escalation_note(intake, account, tickets, incidents, recommendation),
    ]
    return "\n\n".join(sections).strip() + "\n"


def _case_summary(query: str, intake: Any) -> str:
    signals = ", ".join(intake.key_signals) if intake.key_signals else "No special signals detected"
    return "\n".join(
        [
            "## Case Summary",
            f"- Inquiry summary: {query.strip()}",
            f"- Impact scope: {intake.impact_scope}",
            f"- Problem category: {intake.category}",
            f"- Initial urgency: {intake.initial_urgency}",
            f"- Key signals: {signals}",
        ]
    )


def _account_context(context: dict[str, Any]) -> str:
    if not context.get("found"):
        return "## Customer Account Context\n- No matching customer account found."
    account = context["account"]
    contract = context["contract"]
    health = context["health"]
    contact = next((row for row in context["contacts"] if row["emergency"] == "true"), None)
    emergency_contact = (
        f"- Emergency contact: {contact['name']} ({contact['role']})"
        if contact
        else "- Emergency contact: Not listed"
    )
    entitlements = ", ".join(
        row["feature"] for row in context["entitlements"] if row["entitled"] == "true"
    )
    return "\n".join(
        [
            "## Customer Account Context",
            f"- Customer name: {account['customer_name']}",
            f"- Contract plan: {contract['plan']}",
            f"- Support tier: {contract['support_tier']}",
            f"- SLA: {contract['support_tier']} matrix applies by severity",
            f"- CSM: {account['csm']}",
            "- Importance and health: "
            f"{account['segment']} segment, ARR ${contract['arr_usd']}, "
            f"health score {health['health_score']}",
            f"- Risk signals: {health['risk_signals']}",
            f"- Key entitlements: {entitlements}",
            emergency_contact,
        ]
    )


def _historical_tickets(tickets: list[dict[str, Any]]) -> str:
    lines = ["## Similar Historical Tickets"]
    if not tickets:
        lines.append("- No similar historical tickets found.")
        return "\n".join(lines)
    for ticket in tickets:
        tags = ", ".join(ticket.get("tags", []))
        lines.extend(
            [
                f"- {ticket['ticket_id']} - {ticket['subject']}",
                f"  - Similarities: category={ticket['category']}, tags={tags}",
                "  - Differences: "
                f"customer={ticket['customer_id']}, severity={ticket['severity']}, "
                f"status={ticket['status']}",
                f"  - Past cause: {ticket['cause']}",
                f"  - Resolution: {ticket['resolution']}",
                f"  - Applicable insight: {ticket['applicable_insight']}",
            ]
        )
    return "\n".join(lines)


def _knowledge_refs(refs: list[dict[str, Any]]) -> str:
    lines = ["## Relevant Knowledge Base / Runbook References"]
    for ref in refs:
        visibility = "customer-safe" if ref["customer_safe"] else "internal-only"
        lines.append(f"- {ref['title']} ({ref['path']}, {visibility}): {ref['summary']}")
    if not refs:
        lines.append("- No relevant references found.")
    return "\n".join(lines)


def _incident_correlation(incidents: dict[str, Any]) -> str:
    lines = [
        "## Incident Correlation",
        f"- Current incident relationship: {incidents['assessment']}",
    ]
    if incidents["active_matches"]:
        for incident in incidents["active_matches"]:
            lines.append(
                "- Related active incident: "
                f"{incident['incident_id']} ({incident['status']}, "
                f"{incident['severity']}) - {incident['customer_summary']}"
            )
    else:
        lines.append("- Related active incident: None found.")
    if incidents["historical_matches"]:
        historical = ", ".join(item["incident_id"] for item in incidents["historical_matches"])
        lines.append(f"- Similar historical incidents: {historical}")
    if incidents["status_updates"]:
        latest = incidents["status_updates"][-1]
        lines.append(f"- Customer-shareable status update: {latest['message']}")
    else:
        lines.append("- Customer-shareable status update: No public status update found.")
    return "\n".join(lines)


def _severity_recommendation(recommendation: dict[str, Any]) -> str:
    sla = recommendation["sla"] or {}
    return "\n".join(
        [
            "## Severity Recommendation",
            f"- Recommended severity: {recommendation['severity']}",
            f"- Reasoning: {recommendation['severity_reason']}",
            f"- SLA response deadline: {sla.get('first_response', 'Unknown')}",
            f"- SLA update frequency: {sla.get('update_frequency', 'Unknown')}",
            "- Additional information needed: "
            f"{', '.join(recommendation['additional_info_needed'])}",
        ]
    )


def _escalation_decision(recommendation: dict[str, Any]) -> str:
    return "\n".join(
        [
            "## Escalation Decision",
            f"- Escalate: {'Yes' if recommendation['should_escalate'] else 'No'}",
            f"- Recommended team: {recommendation['team']}",
            f"- Escalation reason: {recommendation['reason']}",
            f"- Attach: {', '.join(recommendation['attach'])}",
        ]
    )


def _draft_customer_response(
    intake: Any, incidents: dict[str, Any], recommendation: dict[str, Any]
) -> str:
    next_update = (recommendation["sla"] or {}).get(
        "update_frequency", "the next agreed update window"
    )
    incident_sentence = (
        "We are also checking whether this is related to an active AcmeDesk service issue."
        if incidents["likely_related"]
        else "We are checking both customer-specific configuration and AcmeDesk service health."
    )
    response = "\n".join(
        [
            "## Draft Customer Response",
            "Hello,",
            "",
            f"Thank you for reporting this. We understand the impact as: {intake.impact_scope}",
            incident_sentence,
            "We are treating this as "
            f"{recommendation['severity']} while we complete the initial investigation.",
            f"Could you share: {', '.join(recommendation['additional_info_needed'])}?",
            f"We will follow up within {next_update} or sooner if we confirm a mitigation.",
        ]
    )
    return redact_customer_text(response)


def _internal_escalation_note(
    intake: Any,
    account: dict[str, Any],
    tickets: list[dict[str, Any]],
    incidents: dict[str, Any],
    recommendation: dict[str, Any],
) -> str:
    customer = account.get("account", {}).get("customer_name", intake.customer_name or "Unknown")
    ticket_ids = ", ".join(ticket["ticket_id"] for ticket in tickets) or "None"
    active_ids = ", ".join(item["incident_id"] for item in incidents["active_matches"]) or "None"
    return "\n".join(
        [
            "## Internal Escalation Note",
            f"- Customer impact: {customer}; {intake.impact_scope}",
            f"- Relevant tickets: {ticket_ids}",
            f"- Related incidents: {active_ids}",
            "- Request to owner team: "
            f"Validate {intake.category} diagnosis, confirm incident/customer-specific "
            "status, and advise mitigation.",
            f"- Attachments to include: {', '.join(recommendation['attach'])}",
            "- Internal handling: keep raw logs, tenant identifiers, and internal incident "
            "details out of customer-facing text.",
        ]
    )
