from __future__ import annotations

import argparse
import json
from pathlib import Path

ENV_NAMES = {
    "ticket_history": "TICKET_HISTORY_A2A_URL",
    "knowledge_base": "KNOWLEDGE_BASE_A2A_URL",
    "account_context": "ACCOUNT_CONTEXT_A2A_URL",
    "incident_status": "INCIDENT_STATUS_A2A_URL",
    "escalation_policy": "ESCALATION_POLICY_A2A_URL",
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create coordinator A2A endpoint env vars from a JSON resource map."
    )
    parser.add_argument("resource_map", help="JSON file with agent key to A2A base URL mappings.")
    parser.add_argument("--output", default=".env.runtime")
    args = parser.parse_args()

    data = json.loads(Path(args.resource_map).read_text(encoding="utf-8"))
    lines = []
    for key, env_name in ENV_NAMES.items():
        if key in data:
            lines.append(f"{env_name}={str(data[key]).rstrip('/')}")
    Path(args.output).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
