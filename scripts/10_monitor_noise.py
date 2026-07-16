#!/usr/bin/env python3
"""Quantify monitor non-determinism: score the SAME CoT K times and measure the spread.

The crux re-run showed the Gemini monitor gives wildly different suspicion scores to the
identical CoT across runs (e.g. 5 vs 95) even at temperature=0. If that is real, then every
single-call score in the pilot is dominated by monitor noise, and no per-transcript or
small-n AUC can be trusted. This measures the noise floor so we know how many samples K per
transcript are needed to average it out.

Run:  uv run scripts/10_monitor_noise.py
"""

from __future__ import annotations

import json
import os
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRANSCRIPTS = ROOT / "data" / "transcripts" / "pilot"
CACHE = ROOT / "data" / "xlingual"
K = 10

import importlib.util
spec = importlib.util.spec_from_file_location("crux", ROOT / "scripts" / "07_mt_vs_human.py")
crux = importlib.util.module_from_spec(spec)
spec.loader.exec_module(crux)


def cot_of(tid: str, arm: str) -> str:
    if arm == "EN":
        return json.loads((TRANSCRIPTS / f"{tid}.json").read_text()).get("raw_thinking", "").strip()
    if arm == "HUMAN-CS":
        return (CACHE / f"{tid}.human_cs.txt").read_text().strip()
    raise ValueError(arm)


def main() -> None:
    crux.load_dotenv()
    from google import genai
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    # a swingy attack (EN), the same attack's faithful CS, and a "stable" honest
    probes = [("attack-medium-7", "EN"), ("attack-medium-2", "HUMAN-CS"), ("honest-0", "EN")]
    print(f"K={K} repeated monitor calls on identical input (Gemini, temp=0)\n")
    for tid, arm in probes:
        cot = cot_of(tid, arm)
        scores = [crux.monitor(client, cot) for _ in range(K)]
        vals = [s for s in scores if s is not None]
        sd = statistics.pstdev(vals) if len(vals) > 1 else 0.0
        print(f"  {tid:18} [{arm:8}]  scores={vals}")
        print(f"  {'':18}            mean={statistics.mean(vals):.0f}  sd={sd:.0f}  min={min(vals)}  max={max(vals)}  range={max(vals)-min(vals)}\n")


if __name__ == "__main__":
    main()
