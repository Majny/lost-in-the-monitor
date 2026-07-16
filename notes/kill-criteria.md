# Kill criteria (mirror of project spec — freeze before full run)

1. **Language drift:** <40 % language-compliant transcripts after one week of
   prompt engineering (stretch arm) → drop live non-EN generation, run the
   translation-matrix core only. Still a full paper.
2. **No gap:** all non-EN cells within 5 pp AUC of EN at n=400 → publish the
   robustness result ("language-robust at ≤32B — extrapolation from MCQ
   fragility does not hold for agents") and stop. No hunting for effects.
3. **Scooped:** weekly arXiv check (Saturdays). If the monitor-language ×
   CoT-language matrix appears elsewhere → pivot remaining effort to the
   code-switching project (vault: 07_ZASOBNIK #3), reusing this pipeline.
4. **Monitor broken:** EN-EN AUC < 0.65 after prompt tuning during MVP →
   simplify the scenario until the baseline works; if not fixed within a
   week → switch to the insurance project (AF census).

Decision log for any change to these criteria goes here, with date.
