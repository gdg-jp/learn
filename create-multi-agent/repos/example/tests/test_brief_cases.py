from __future__ import annotations

from acmedesk_support.brief import build_escalation_brief

REQUIRED_SECTIONS = [
    "## Case Summary",
    "## Customer Account Context",
    "## Similar Historical Tickets",
    "## Relevant Knowledge Base / Runbook References",
    "## Incident Correlation",
    "## Severity Recommendation",
    "## Escalation Decision",
    "## Draft Customer Response",
    "## Internal Escalation Note",
]


def test_case_a_sso_outage_brief() -> None:
    brief = build_escalation_brief(
        "Contoso administrator reports that all employees cannot log in with SAML SSO. "
        "They updated the IdP certificate yesterday. This is a Premier support customer."
    )

    for section in REQUIRED_SECTIONS:
        assert section in brief
    assert "Contoso" in brief
    assert "TCK-1276" in brief
    assert "Identity Platform" in brief
    assert "Recommended severity: SEV2" in brief
    assert "INC-2026-0507-SAML-METADATA" in brief


def test_case_b_billing_discrepancy_brief() -> None:
    brief = build_escalation_brief(
        "Globex says this month's invoice is higher than the contract amount. "
        "They increased seat count last month but cannot understand the invoice line items."
    )

    assert "Globex" in brief
    assert "TCK-1188" in brief
    assert "Billing Operations" in brief
    assert "Recommended severity: SEV3" in brief
    assert "seat-change audit" in brief


def test_case_c_webhook_delay_brief() -> None:
    brief = build_escalation_brief(
        "Initech reports that CRM webhook delivery is delayed by more than 30 minutes. "
        "There is business impact and they need to know if this is a known incident."
    )

    assert "Initech" in brief
    assert "TCK-1403" in brief
    assert "Integrations Platform" in brief
    assert "Recommended severity: SEV2" in brief
    assert "INC-2026-0521-WEBHOOK-LATENCY" in brief
