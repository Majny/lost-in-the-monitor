#!/usr/bin/env python3
"""Build the review doc: English CoT next to my faithful Czech, for Jakub to verify.

Reads the same valid transcripts as the pack (medium attacks + honest) and the Czech I
produced in data/xlingual/<id>.human_cs.txt, and writes notes/translation_review_cs.md with
EN and CS adjacent per transcript. Jakub reviews the CS as a native speaker: the ONE thing
to check is that it stayed as messy/fragmentary as the English (not polished), kept every
clause, and left code/paths in English. Edit the CS inline; then re-run scripts/09_sync_review
to push edits back into the .human_cs.txt files that the comparison reads.

Run:  uv run scripts/08_build_review.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRANSCRIPTS = ROOT / "data" / "transcripts" / "pilot"
CACHE = ROOT / "data" / "xlingual"
OUT = ROOT / "notes" / "translation_review_cs.md"
N_ATTACK, N_HONEST = 15, 10

MARK_BEGIN = "<!-- CS:{tid} -->"
MARK_END = "<!-- /CS:{tid} -->"


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
        "# Překlad ke kontrole — CS (rodilý mluvčí verifikuje)",
        "",
        "Přeložil jsem 17 CoT věrně a **záměrně rozklizeně**. Tvoje jediná úloha jako rodilého",
        "mluvčího: ověř, že čeština zůstala **stejně útržkovitá / neučesaná jako angličtina** (ne",
        "uhlazená!), že nic nechybí a že kód/cesty (`safe/`, `base_dir`, `os.path`, `/etc/passwd`)",
        "zůstaly anglicky. Uprav CS přímo mezi značkami `<!-- CS:id -->` … `<!-- /CS:id -->`.",
        "Až budeš hotový, spustím `scripts/09_sync_review.py`, který tvé úpravy vezme zpět do",
        "souborů, ze kterých počítám výsledek.",
        "",
        f"*{len(picked)} transcriptů ({len(attacks[:N_ATTACK])} útoků + {len(honest[:N_HONEST])} honest).*",
        "",
        "---",
        "",
    ]
    n_missing = 0
    for i, (tid, grp, cot) in enumerate(picked, 1):
        cs_path = CACHE / f"{tid}.human_cs.txt"
        cs = cs_path.read_text().strip() if cs_path.exists() else ""
        if not cs:
            n_missing += 1
            cs = "_(překlad chybí — subagent selhal, doplním)_"
        lines += [
            f"## {i}. `{tid}`  ({grp})",
            "",
            "**EN:**",
            "```",
            cot,
            "```",
            "",
            "**CS (můj překlad — zkontroluj a případně uprav):**",
            "",
            MARK_BEGIN.format(tid=tid),
            "```",
            cs,
            "```",
            MARK_END.format(tid=tid),
            "",
            "---",
            "",
        ]
    OUT.write_text("\n".join(lines))
    msg = f"wrote {OUT}  ({len(picked)} transcripts"
    msg += f", {n_missing} missing CS)" if n_missing else ")"
    print(msg)


if __name__ == "__main__":
    main()
