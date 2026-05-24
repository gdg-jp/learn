# AcmeDesk Customer Support Escalation Agent

This is the completed repository for the hands-on lab "ADK x A2A x Agent Runtime Customer Support Escalation Agent".

The app models a B2B SaaS support workflow for AcmeDesk. A Support Coordinator Agent receives a customer support inquiry, delegates research to five specialist agents over A2A, and produces a Customer Support Escalation Brief for support operators.

## Architecture

```text
Support Coordinator Agent
  |- Ticket History Agent       (A2A, port 8101)
  |- Knowledge Base Agent       (A2A, port 8102)
  |- Account Context Agent      (A2A, port 8103)
  |- Incident Status Agent      (A2A, port 8104)
  `- Escalation Policy Agent    (A2A, port 8105)
```

Each specialist is an ADK agent exposed as an A2A Starlette app with `to_a2a()`. The coordinator consumes the specialists through `RemoteA2aAgent(use_legacy=False)` wrapped in `AgentTool`, so specialist findings return to the coordinator as tool results. The specialists are intentionally not registered as `sub_agents`, because `sub_agents` enables `transfer_to_agent(...)` and can hand the conversation off to a single specialist instead of aggregating all findings. The coordinator also has no local "build full brief" shortcut tool, so ADK Web is forced to call the five A2A specialist tools before synthesizing the final brief.

For deterministic workshop checks, the shared `acmedesk_support` package also exposes local search and brief-building functions. The CLI sample cases use those functions so they can run without calling an LLM. That deterministic path is not registered as a coordinator ADK tool.

## Setup

Install [uv](https://docs.astral.sh/uv/) if it is not already available.

```bash
make setup
cp .env.example .env
```

Set either `GOOGLE_API_KEY` for Google AI Studio or Vertex AI environment variables in `.env`.

Important dependency note: ADK 2.1 requires `a2a-sdk>=0.3,<0.4` for the current A2A helper modules. This repo pins `a2a-sdk[http-server]==0.3.26` so the Starlette A2A server can serve agent cards and JSON-RPC routes.

Dependencies are managed with `uv` from `pyproject.toml` and `uv.lock`. Do not install them with `pip`; use `make setup` or `uv sync --extra dev`.

## Run locally

Start the five specialist A2A services:

```bash
make run-specialists
```

In another terminal, start the coordinator A2A service:

```bash
make run-coordinator
```

The agent cards are available at:

```text
http://localhost:8101/.well-known/agent-card.json
http://localhost:8102/.well-known/agent-card.json
http://localhost:8103/.well-known/agent-card.json
http://localhost:8104/.well-known/agent-card.json
http://localhost:8105/.well-known/agent-card.json
http://localhost:8100/.well-known/agent-card.json
```

## Run sample cases without an LLM

```bash
make case-a
make case-b
make case-c
```

These commands generate the same Customer Support Escalation Brief shape expected from the coordinator:

- Case A: Contoso SAML SSO outage after IdP certificate rotation
- Case B: Globex billing discrepancy after seat increase
- Case C: Initech CRM webhook delivery delay

## Test and lint

```bash
make lint
make test
```

## Deploy to Agent Runtime

Authenticate with Google Cloud first:

```bash
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

Then set the required environment variables:

```bash
export GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
export GOOGLE_CLOUD_LOCATION=us-central1
export GOOGLE_GENAI_USE_VERTEXAI=true
```

Deploy every agent:

```bash
make deploy-all
```

The script deploys each specialist and the coordinator with:

```bash
uv export --format requirements.txt --no-dev --no-hashes --no-emit-project \
  --output-file .agent-engine-temp/requirements.txt

uv run adk deploy agent_engine . \
  --project "$GOOGLE_CLOUD_PROJECT" \
  --region "$GOOGLE_CLOUD_LOCATION" \
  --adk_app agents/<agent_name>/agent.py \
  --adk_app_object root_agent \
  --requirements_file .agent-engine-temp/requirements.txt
```

The temporary requirements file is exported from the uv lockfile because the ADK Agent Runtime deploy command accepts a requirements file.

After the specialist Agent Runtime resources are created, expose or connect them as A2A endpoints following the Agent2Agent Runtime documentation, then update the coordinator environment variables to point to those endpoint agent-card URLs.

Agent2Agent on Agent Runtime is currently a preview workflow. Keep local A2A URLs for workshop development and use runtime endpoints for the deployment exercise.

## Repository layout

```text
agents/                  ADK agent entrypoints
data/                    Fictional AcmeDesk support corpus
scripts/                 CLI runners and deployment helpers
src/acmedesk_support/    Deterministic data search and brief logic
tests/                   Unit and sample-case tests
```
