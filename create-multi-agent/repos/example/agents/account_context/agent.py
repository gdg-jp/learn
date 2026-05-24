from __future__ import annotations

from google.adk.agents import Agent

from acmedesk_support.accounts import get_account_context
from agents._common import build_a2a_app, model_name


def lookup_account_context(inquiry: str) -> dict:
    """Return account, contract, entitlement, contact, health, and SLA context."""
    return get_account_context(inquiry)


root_agent = Agent(
    name="account_context_agent",
    model=model_name(),
    description=(
        "Looks up AcmeDesk customer account, contract, support tier, SLA, "
        "contacts, and health."
    ),
    instruction=(
        "You are the Account Context Agent for AcmeDesk support. "
        "Use lookup_account_context for every request. Return customer name, plan, support tier, "
        "SLA rows, CSM, contacts, entitlements, health score, and risk signals. "
        "If the customer is unknown, say what identifier is missing."
    ),
    tools=[lookup_account_context],
)

app = build_a2a_app(root_agent, default_port=8103)
