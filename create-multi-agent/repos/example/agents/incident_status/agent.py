from __future__ import annotations

from google.adk.agents import Agent

from acmedesk_support.incidents import correlate_incidents
from agents._common import build_a2a_app, model_name


def check_incident_status(inquiry: str) -> dict:
    """Correlate the inquiry with active and historical AcmeDesk incidents."""
    return correlate_incidents(inquiry)


root_agent = Agent(
    name="incident_status_agent",
    model=model_name(),
    description="Checks active and historical incidents and public status updates.",
    instruction=(
        "You are the Incident Status Agent. "
        "Use check_incident_status for every request. Return active incident correlation, "
        "historical incident similarities, known-vs-customer-specific assessment, "
        "and customer-shareable status updates. "
        "Do not expose internal incident timeline details in customer-safe text."
    ),
    tools=[check_incident_status],
)

app = build_a2a_app(root_agent, default_port=8104)
