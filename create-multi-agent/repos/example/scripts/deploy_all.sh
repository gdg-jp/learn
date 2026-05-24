#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${GOOGLE_CLOUD_PROJECT:-}" ]]; then
  echo "GOOGLE_CLOUD_PROJECT is required" >&2
  exit 2
fi

REGION="${GOOGLE_CLOUD_LOCATION:-us-central1}"
UV_BIN="${UV_BIN:-uv}"
REQ_FILE=".agent-engine-temp/requirements.txt"

mkdir -p .agent-engine-temp
"${UV_BIN}" export \
  --format requirements.txt \
  --no-dev \
  --no-hashes \
  --no-emit-project \
  --output-file "${REQ_FILE}"

deploy_agent() {
  local name="$1"
  local app_path="$2"
  local description="$3"

  echo "Deploying ${name} to Agent Runtime..."
  "${UV_BIN}" run adk deploy agent_engine . \
    --project "${GOOGLE_CLOUD_PROJECT}" \
    --region "${REGION}" \
    --display_name "AcmeDesk ${name}" \
    --description "${description}" \
    --adk_app "${app_path}" \
    --adk_app_object root_agent \
    --requirements_file "${REQ_FILE}" \
    --temp_folder ".agent-engine-temp/${name}"
}

deploy_agent "Ticket History Agent" \
  "agents/ticket_history/agent.py" \
  "Searches historical AcmeDesk support tickets over A2A."

deploy_agent "Knowledge Base Agent" \
  "agents/knowledge_base/agent.py" \
  "Searches AcmeDesk FAQ, troubleshooting, runbooks, policies, and known issues over A2A."

deploy_agent "Account Context Agent" \
  "agents/account_context/agent.py" \
  "Looks up customer account, contract, entitlement, SLA, contact, and health context over A2A."

deploy_agent "Incident Status Agent" \
  "agents/incident_status/agent.py" \
  "Correlates support cases with active and historical incidents over A2A."

deploy_agent "Escalation Policy Agent" \
  "agents/escalation_policy/agent.py" \
  "Applies AcmeDesk severity, SLA, escalation, and customer-communication policies over A2A."

deploy_agent "Support Coordinator Agent" \
  "agents/coordinator/agent.py" \
  "Coordinates specialist A2A agents and produces Customer Support Escalation Briefs."

echo "Deployment commands completed."
echo "Update coordinator A2A endpoint environment variables with the deployed specialist agent cards."
