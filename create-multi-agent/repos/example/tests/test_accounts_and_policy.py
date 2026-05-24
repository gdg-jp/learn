from __future__ import annotations

from acmedesk_support.accounts import get_account_context
from acmedesk_support.policy import recommend_escalation


def test_contoso_account_context_includes_premier_sla() -> None:
    context = get_account_context("Contoso has an SSO outage for all employees.")

    assert context["found"] is True
    assert context["account"]["customer_name"] == "Contoso"
    assert context["contract"]["support_tier"] == "Premier"
    assert any(row["severity"] == "SEV2" for row in context["sla"])


def test_case_a_policy_escalates_to_identity_platform() -> None:
    recommendation = recommend_escalation(
        "Contoso all employees cannot log in with SAML SSO after an IdP certificate "
        "rotation. Premier support."
    )

    assert recommendation["severity"] == "SEV2"
    assert recommendation["should_escalate"] is True
    assert recommendation["team"] == "Identity Platform"
    assert recommendation["sla"]["first_response"] == "30 minutes"


def test_case_b_policy_uses_billing_operations() -> None:
    recommendation = recommend_escalation(
        "Globex invoice is higher than the contract amount after seat count increased last month."
    )

    assert recommendation["severity"] == "SEV3"
    assert recommendation["team"] == "Billing Operations"
    assert "Invoice number" in recommendation["additional_info_needed"]
