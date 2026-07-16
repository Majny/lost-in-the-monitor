#!/usr/bin/env python3
"""Sync Jakub's edited Czech from notes/translation_review_cs.md back to the .txt files.

The comparison (scripts/07) reads faithful Czech from data/xlingual/<id>.human_cs.txt.
After Jakub edits the review doc, this pulls each CS block (between the <!-- CS:id --> …
<!-- /CS:id --> markers, inside the ``` fence) back into that file, so the human-verified
version is what gets scored.

Run:  uv run scripts/09_sync_review.py
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REVIEW = ROOT / "notes" / "translation_review_cs.md"
CACHE = ROOT / "data" / "xlingual"


def main() -> None:
    if not REVIEW.exists():
        raise SystemExit(f"no review doc at {REVIEW} — run scripts/08_build_review.py first")
    text = REVIEW.read_text()
    # Grab everything between the per-id markers, then strip the code fence inside.
    blocks = re.findall(r"<!-- CS:(?P<tid>[^ ]+?) -->\n(?P<body>.*?)\n<!-- /CS:(?P=tid) -->",
                        text, flags=re.DOTALL)
    if not blocks:
        raise SystemExit("no <!-- CS:id --> markers found — is this the right file?")
    CACHE.mkdir(parents=True, exist_ok=True)
    written = 0
    for tid, body in blocks:
        m = re.search(r"```[a-z]*\n(?P<cs>.*?)\n```", body, flags=re.DOTALL)
        cs = (m.group("cs") if m else body).strip()
        if not cs or cs.startswith("_(překlad chybí"):
            print(f"  skip {tid} (empty/placeholder)")
            continue
        (CACHE / f"{tid}.human_cs.txt").write_text(cs + "\n")
        written += 1
    print(f"synced {written} human-CS translation(s) from review doc")


if __name__ == "__main__":
    main()
