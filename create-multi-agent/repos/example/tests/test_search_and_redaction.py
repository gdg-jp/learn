from __future__ import annotations

from acmedesk_support.incidents import correlate_incidents
from acmedesk_support.knowledge import search_knowledge_base
from acmedesk_support.redaction import redact_customer_text
from acmedesk_support.tickets import search_ticket_history


def test_ticket_search_prioritizes_customer_and_category() -> None:
    tickets = search_ticket_history("Contoso SAML SSO IdP certificate all employees", limit=2)

    assert tickets[0]["ticket_id"] == "TCK-1276"
    assert tickets[0]["category"] == "authentication"


def test_knowledge_search_returns_customer_safe_and_internal_refs() -> None:
    refs = search_knowledge_base("SAML SSO certificate rotation all users", limit=5)
    paths = {ref["path"] for ref in refs}

    assert "knowledge_base/faq/login-and-sso.md" in paths
    assert "knowledge_base/runbooks/auth-service-runbook.md" in paths
    assert any(ref["customer_safe"] is False for ref in refs)


def test_incident_correlation_finds_active_webhook_incident() -> None:
    incidents = correlate_incidents("Initech CRM webhook delay over 30 minutes in us-west1")

    assert incidents["likely_related"] is True
    assert incidents["active_matches"][0]["incident_id"] == "INC-2026-0521-WEBHOOK-LATENCY"


def test_redaction_removes_customer_unsafe_terms() -> None:
    text = "tenant_id: acme-123 has raw logs in the internal timeline from the backend service."

    redacted = redact_customer_text(text)

    assert "acme-123" not in redacted
    assert "raw logs" not in redacted
    assert "backend service" not in redacted
