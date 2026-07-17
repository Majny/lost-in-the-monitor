#!/usr/bin/env python3
"""Build per-language transcript dirs (en/cs/sw) from the staged sources + faithful translations,
so both the strong (Gemini, local) and weak (gpt-oss, cluster) monitors can score each arm with
the same monitor_vllm.py / scripts-07 machinery.

Reads data/xlingual_scaled/src/<key>.json (group/variant/effort + English cot) and the workflow's
<key>.cs.txt / <key>.sw.txt, writes data/xlingual_scaled/arm_{en,cs,sw}/<key>.json with a
raw_thinking field in that language and policy/main_ok/side_ok set so group_of accepts them
(only VALID transcripts were staged: attacks main_ok&side_ok, honest_hard non-leaking).

Run:  uv run scripts/13_stage_xlingual.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "data" / "xlingual_scaled"
SRC = BASE / "src"


def main() -> None:
    arms = {a: (BASE / f"arm_{a}") for a in ("en", "cs", "sw")}
    for p in arms.values():
        p.mkdir(parents=True, exist_ok=True)
    n = {"en": 0, "cs": 0, "sw": 0}
    missing = []
    for sf in sorted(SRC.glob("*.json")):
        key = sf.stem
        src = json.loads(sf.read_text())
        is_attack = src["group"] == "attack"
        base = {"policy": src["group"], "variant": src["variant"],
                "reasoning_effort": src.get("effort"),
                "main_ok": True, "side_ok": bool(is_attack)}  # staged set is valid by construction
        texts = {"en": src["cot"]}
        cs = BASE / f"{key}.cs.txt"
        sw = BASE / f"{key}.sw.txt"
        texts["cs"] = cs.read_text().strip() if cs.exists() else ""
        texts["sw"] = sw.read_text().strip() if sw.exists() else ""
        for a in ("en", "cs", "sw"):
            if not texts[a].strip():
                if a != "en":
                    missing.append(f"{key}.{a}")
                continue
            (arms[a] / f"{key}.json").write_text(json.dumps({**base, "raw_thinking": texts[a]}, ensure_ascii=False))
            n[a] += 1
    print(f"staged arms: en={n['en']} cs={n['cs']} sw={n['sw']}")
    if missing:
        print(f"[!] missing {len(missing)} translations: {', '.join(missing[:12])}{' …' if len(missing) > 12 else ''}")


if __name__ == "__main__":
    main()
