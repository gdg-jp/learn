UV ?= uv
UV_RUN := $(UV) run

.PHONY: setup lock lint test run-specialists run-coordinator case-a case-b case-c deploy-all clean

setup:
	$(UV) sync --extra dev

lock:
	$(UV) lock

lint:
	$(UV_RUN) --extra dev ruff check .

test:
	$(UV_RUN) --extra dev pytest

run-specialists:
	@set -e; \
	trap 'kill 0' INT TERM EXIT; \
	PYTHONPATH=src $(UV_RUN) uvicorn agents.ticket_history.agent:app --host 0.0.0.0 --port 8101 & \
	PYTHONPATH=src $(UV_RUN) uvicorn agents.knowledge_base.agent:app --host 0.0.0.0 --port 8102 & \
	PYTHONPATH=src $(UV_RUN) uvicorn agents.account_context.agent:app --host 0.0.0.0 --port 8103 & \
	PYTHONPATH=src $(UV_RUN) uvicorn agents.incident_status.agent:app --host 0.0.0.0 --port 8104 & \
	PYTHONPATH=src $(UV_RUN) uvicorn agents.escalation_policy.agent:app --host 0.0.0.0 --port 8105 & \
	echo "Specialist A2A agents are running on ports 8101-8105."; \
	wait

run-coordinator:
	PYTHONPATH=src $(UV_RUN) uvicorn agents.coordinator.agent:app --host 0.0.0.0 --port 8100

case-a:
	PYTHONPATH=src $(UV_RUN) python scripts/run_case.py case-a

case-b:
	PYTHONPATH=src $(UV_RUN) python scripts/run_case.py case-b

case-c:
	PYTHONPATH=src $(UV_RUN) python scripts/run_case.py case-c

deploy-all:
	./scripts/deploy_all.sh

web:
	PYTHONPATH=src $(UV_RUN) adk web agents --port 8000

clean:
	rm -rf .venv .pytest_cache .ruff_cache .agent-engine-temp build dist *.egg-info
