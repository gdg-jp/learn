from __future__ import annotations

from google.adk.agents import Agent

from acmedesk_support.policy import recommend_escalation
from agents._common import build_a2a_app, model_name


def evaluate_escalation_policy(inquiry: str) -> dict:
    """Return severity, SLA, escalation decision, owner team, and customer-safe constraints."""
    return recommend_escalation(inquiry)


root_agent = Agent(
    name="escalation_policy_agent",
    model=model_name(),
    description="Applies AcmeDesk severity, escalation, SLA, and communication policies.",
    instruction=(
        "You are the Escalation Policy Agent. "
        "Use evaluate_escalation_policy for every request. Return recommended severity, "
        "reasoning, SLA response deadline, escalation decision, target team, required attachments, "
        "missing information, and customer communication constraints."
    ),
    tools=[evaluate_escalation_policy],
)

app = build_a2a_app(root_agent, default_port=8105)
