from __future__ import annotations

from google.adk.agents import Agent

from acmedesk_support.tickets import search_ticket_history
from agents._common import build_a2a_app, model_name


def search_similar_tickets(inquiry: str) -> dict:
    """Search similar historical tickets and return causes, resolutions, and insights."""
    return {"similar_tickets": search_ticket_history(inquiry)}


root_agent = Agent(
    name="ticket_history_agent",
    model=model_name(),
    description="Searches AcmeDesk historical support tickets and escalation cases.",
    instruction=(
        "You are the Ticket History Agent. "
        "Use search_similar_tickets for every request. Return similar tickets, similarities, "
        "differences, past causes, resolutions, internal comments if useful, "
        "and applicable insights."
    ),
    tools=[search_similar_tickets],
)

app = build_a2a_app(root_agent, default_port=8101)
