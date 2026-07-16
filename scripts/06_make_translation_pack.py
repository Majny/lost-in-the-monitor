#!/usr/bin/env python3
"""Export a human-translation pack: English CoTs for a native speaker to translate faithfully.

This is the gold-standard control for the MT-confound result: the human translation must
preserve the English reasoning's *messiness* (fragments, run-ons, backtracking, "Wait…"),
NOT polish it — otherwise it becomes another normalization like the MT and the comparison
collapses. The instruction in the output file makes that explicit.

Selects valid medium attacks + honest and writes a fill-in Markdown pack.

Run:  uv run scripts/06_make_translation_pack.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRANSCRIPTS = ROOT / "data" / "transcripts" / "pilot"
OUT = ROOT / "notes" / "translation_pack_cs.md"
N_ATTACK, N_HONEST = 15, 10


def is_valid(rec: dict) -> str | None:
    if rec.get("policy") == "honest":
        return "honest" if rec.get("main_ok") else None
    if not (rec.get("main_ok") and rec.get("side_ok")):
        return None
    v = rec.get("variant") or ("medium" if "medium" in rec.get("run_id", "") else "")
    return "attack(medium)" if v == "medium" else None


def main() -> None:
    attacks, honest = [], []
    for f in sorted(TRANSCRIPTS.glob("*.json")):
        rec = json.loads(f.read_text())
        grp = is_valid(rec)
        cot = (rec.get("raw_thinking") or "").strip()
        if grp is None or not cot:
            continue
        (attacks if grp.startswith("attack") else honest).append((f.stem, grp, cot))
    picked = attacks[:N_ATTACK] + honest[:N_HONEST]

    lines = [
        "# Human translation pack — Czech (the gold-standard control)",
        "",
        "**Why this matters:** the whole cross-lingual result hinges on comparing a *faithful*",
        "human Czech translation against the machine one. Machine translation over-cleans the",
        "reasoning; your job is the opposite — **be faithful to the English's style, not polished**.",
        "",
        "**Rules:**",
        "- Translate meaning AND register: keep it as messy, fragmentary, and run-on as the English.",
        "- Preserve every clause, every 'Wait…', every backtrack and repetition. Do NOT tidy or shorten.",
        "- Leave code, identifiers, file paths, and string literals (e.g. `safe/`, `base_dir`, `os.path`) verbatim in English.",
        "- Do not add or explain anything. Match length roughly.",
        "",
        "Fill your translation under each `**CS:**` line. Save the file when done.",
        "",
        f"*{len(picked)} transcripts ({len(attacks[:N_ATTACK])} attacks + {len(honest[:N_HONEST])} honest).*",
        "",
        "---",
        "",
    ]
    for i, (tid, grp, cot) in enumerate(picked, 1):
        lines += [
            f"## {i}. `{tid}`  ({grp})",
            "",
            "**EN:**",
            "```",
            cot,
            "```",
            "",
            "**CS:**",
            "",
            "> _(tvůj věrný překlad sem — stejně rozklizeně jako EN)_",
            "",
            "---",
            "",
        ]
    OUT.write_text("\n".join(lines))
    print(f"wrote {OUT}  ({len(picked)} transcripts)")


if __name__ == "__main__":
    main()
