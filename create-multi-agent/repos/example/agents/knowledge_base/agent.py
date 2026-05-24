from __future__ import annotations

from google.adk.agents import Agent

from acmedesk_support.knowledge import search_knowledge_base
from agents._common import build_a2a_app, model_name


def search_relevant_knowledge(inquiry: str) -> dict:
    """Search FAQ, troubleshooting, runbook, policy, release note, and known-issue docs."""
    return {"references": search_knowledge_base(inquiry)}


root_agent = Agent(
    name="knowledge_base_agent",
    model=model_name(),
    description="Searches AcmeDesk FAQ, troubleshooting, runbooks, policy, and product docs.",
    instruction=(
        "You are the Knowledge Base Agent. "
        "Use search_relevant_knowledge for every request. Separate customer-safe references "
        "from internal-only runbook and policy references. Include troubleshooting steps, "
        "workarounds, and internal checks when relevant."
    ),
    tools=[search_relevant_knowledge],
)

app = build_a2a_app(root_agent, default_port=8102)
