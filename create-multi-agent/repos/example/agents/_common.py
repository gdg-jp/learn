from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"


def ensure_src_path() -> None:
    src = str(SRC_DIR)
    if src not in sys.path:
        sys.path.insert(0, src)


ensure_src_path()
load_dotenv(REPO_ROOT / ".env")


def model_name() -> str:
    return os.getenv("ADK_MODEL", "gemini-2.5-flash")


def specialist_card_url(env_name: str, default_base_url: str) -> str:
    base_url = os.getenv(env_name, default_base_url).rstrip("/")
    if base_url.endswith("/.well-known/agent-card.json"):
        return base_url
    return f"{base_url}/.well-known/agent-card.json"


def build_a2a_app(agent, default_port: int):
    from google.adk.a2a.utils.agent_to_a2a import to_a2a

    host = os.getenv("A2A_HOST", "localhost")
    protocol = os.getenv("A2A_PROTOCOL", "http")
    port = int(os.getenv("PORT", str(default_port)))
    return to_a2a(agent, host=host, port=port, protocol=protocol)
