#!/usr/bin/env python3
"""Post-process generated Marp HTML files."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: fix-slide-html.py path/to/slide.html", file=sys.stderr)
        return 2

    html_path = Path(sys.argv[1])
    root = Path(__file__).resolve().parents[1]
    favicon = root / "assets" / "favicon.png"
    href = os.path.relpath(favicon, html_path.parent).replace(os.sep, "/")

    html = html_path.read_text(encoding="utf-8")
    link = f'<link rel="icon" type="image/png" href="{href}">'

    if re.search(r'<link\b[^>]*rel=["\'][^"\']*\bicon\b[^"\']*["\'][^>]*>', html):
        html = re.sub(
            r'<link\b[^>]*rel=["\'][^"\']*\bicon\b[^"\']*["\'][^>]*>',
            link,
            html,
            count=1,
        )
    elif "</head>" in html:
        html = html.replace("</head>", f"{link}</head>", 1)
    else:
        print(f"{html_path}: missing </head>", file=sys.stderr)
        return 1

    html_path.write_text(html, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
