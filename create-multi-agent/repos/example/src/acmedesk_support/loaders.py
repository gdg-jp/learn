from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from acmedesk_support.paths import DATA_DIR


def load_csv(relative_path: str) -> list[dict[str, str]]:
    path = DATA_DIR / relative_path
    with path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def load_json(relative_path: str) -> Any:
    path = DATA_DIR / relative_path
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def load_jsonl(relative_path: str) -> list[dict[str, Any]]:
    path = DATA_DIR / relative_path
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def read_text(relative_path: str) -> str:
    return (DATA_DIR / relative_path).read_text(encoding="utf-8")


def iter_markdown(relative_dir: str) -> list[dict[str, str]]:
    root = DATA_DIR / relative_dir
    docs: list[dict[str, str]] = []
    for path in sorted(root.rglob("*.md")):
        docs.append(
            {
                "path": str(path.relative_to(DATA_DIR)),
                "title": _title_from_markdown(path),
                "content": path.read_text(encoding="utf-8"),
            }
        )
    return docs


def _title_from_markdown(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem.replace("-", " ").title()
