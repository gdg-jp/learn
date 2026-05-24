from __future__ import annotations

from google.adk.agents import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.tools.agent_tool import AgentTool

from agents._common import build_a2a_app, model_name, specialist_card_url

ticket_history_agent = RemoteA2aAgent(
    name="ticket_history_agent",
    agent_card=specialist_card_url("TICKET_HISTORY_A2A_URL", "http://localhost:8101"),
    description="Finds similar support tickets and historical resolutions.",
    use_legacy=False,
)
knowledge_base_agent = RemoteA2aAgent(
    name="knowledge_base_agent",
    agent_card=specialist_card_url("KNOWLEDGE_BASE_A2A_URL", "http://localhost:8102"),
    description="Finds FAQ, troubleshooting, runbook, product, and policy references.",
    use_legacy=False,
)
account_context_agent = RemoteA2aAgent(
    name="account_context_agent",
    agent_card=specialist_card_url("ACCOUNT_CONTEXT_A2A_URL", "http://localhost:8103"),
    description="Looks up customer account, contract, entitlement, SLA, and health context.",
    use_legacy=False,
)
incident_status_agent = RemoteA2aAgent(
    name="incident_status_agent",
    agent_card=specialist_card_url("INCIDENT_STATUS_A2A_URL", "http://localhost:8104"),
    description="Checks active and historical incidents for correlation.",
    use_legacy=False,
)
escalation_policy_agent = RemoteA2aAgent(
    name="escalation_policy_agent",
    agent_card=specialist_card_url("ESCALATION_POLICY_A2A_URL", "http://localhost:8105"),
    description="Recommends severity, SLA deadline, escalation target, and safe customer wording.",
    use_legacy=False,
)

root_agent = Agent(
    name="support_coordinator_agent",
    model=model_name(),
    description="Coordinates specialist A2A agents and creates Customer Support Escalation Briefs.",
    instruction=(
        "You are the Support Coordinator Agent for AcmeDesk. "
        "For every support inquiry, first structure the case, then delegate to all five "
        "specialist A2A agents before producing a final answer. "
        "You must consult ticket_history_agent, knowledge_base_agent, account_context_agent, "
        "incident_status_agent, and escalation_policy_agent. "
        "Do not produce the final brief until every specialist has returned its findings. "
        "Call the specialist agents as tools; do not transfer the conversation to them. "
        "After the specialist findings are available, synthesize a Customer Support "
        "Escalation Brief with these exact sections: "
        "Case Summary, Customer Account Context, Similar Historical Tickets, "
        "Relevant Knowledge Base / Runbook References, Incident Correlation, "
        "Severity Recommendation, Escalation Decision, Draft Customer Response, "
        "and Internal Escalation Note. "
        "Never include internal logs, raw identifiers, or internal incident timelines "
        "in the customer response."
    ),
    tools=[
        AgentTool(agent=ticket_history_agent),
        AgentTool(agent=knowledge_base_agent),
        AgentTool(agent=account_context_agent),
        AgentTool(agent=incident_status_agent),
        AgentTool(agent=escalation_policy_agent),
    ],
)

app = build_a2a_app(root_agent, default_port=8100)
