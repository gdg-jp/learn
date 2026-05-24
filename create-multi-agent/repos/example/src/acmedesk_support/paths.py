from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = Path(os.getenv("ACMEDESK_DATA_DIR") or REPO_ROOT / "data")
