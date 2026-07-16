# Pre-Registration: Lost in the Monitor

**Is cross-lingual CoT monitoring failure monitor-side or model-side?**

| | |
|---|---|
| **Version** | v0.9 — DRAFT until all `[FREEZE BEFORE RUN]` fields are filled and this file is committed with tag `prereg-v1` |
| **Author** | Jakub Dvořák (solo) |
| **Date drafted** | 2026-07-16 |
| **Freeze deadline** | Before the first full-scale (n ≥ 400/cell) monitoring run; MVP (n≈100/cell, Sep 15–28) is explicitly *pilot/calibration* and its data will NOT enter confirmatory statistics |
| **Methodological template** | CoT Red-Handed (arXiv 2505.23575) — control-style, instructed-covert CoT-monitoring stress test |
| **Repo** | `lost-in-the-monitor` (public from start, MIT) |

**Freeze protocol.** Every `[FREEZE BEFORE RUN]` marker below must be replaced by an exact value (a number, a model version string, a prompt hash) before the confirmatory run starts. The frozen version is committed and tagged; any later change is a *deviation* and must be reported per §12. Pilot/MVP data may inform frozen values (prompts, thresholds, calibration) but is quarantined from all confirmatory analyses.

---

## 1. Research question

Chain-of-thought (CoT) monitoring is a load-bearing hope for AI control, and prior work (Onyame et al., arXiv 2605.27901) shows monitor catch rates degrade on non-English CoT in single-turn MCQ settings. Nobody has separated the two possible mechanisms:

> **RQ:** When a trusted monitor's catch rate on covertly-misbehaving agent transcripts drops for non-English CoT, is the drop **recoverable by translating the CoT to English before monitoring** (→ monitor-side failure), or does non-English CoT carry **less monitorable signal** even after translation (→ model-side failure)?

The decisive instrument is a **monitor-language × CoT-language matrix** over agentic deception transcripts with **programmatic, language-neutral ground truth**, plus a **translate-then-monitor** arm.

---

## 2. Hypotheses and decision rules

All decision rules operate on the **primary contrast** defined in §5 unless stated otherwise. "Gap" and "recovery" are defined precisely in §8.3.

- **H-gap (precondition):** Direct monitoring of non-English CoT (Czech and/or German versions of the same transcripts) yields lower detection performance than English CoT.
  *Confirmed for language L if:* ΔAUC(EN − L) ≥ **5 pp** `[FREEZE BEFORE RUN: 5 pp]` **and** the paired-bootstrap 95% CI on ΔAUC excludes 0 **and** paired McNemar p < .05 after Holm correction across language pairs (§8.4).

- **H-monitor (monitor-side failure):** Translate-then-monitor recovers **≥ 80%** `[FREEZE BEFORE RUN: 80%]` of the gap.
  *Recovery fraction R_L = (AUC_translate,L − AUC_direct,L) / (AUC_EN − AUC_direct,L),* computed only for languages where H-gap is confirmed.
  *Interpretation:* the failure lives in the monitor; the fix is a cheap translation layer (~$0.001/call) that deployed monitoring pipelines currently lack. Publishable as a concrete, actionable patch + measurement of how much it buys.

- **H-model (model-side failure):** Recovery fraction R_L < 80% `[same frozen threshold]` for a language with a confirmed gap, i.e., the translated CoT still monitors worse than natively-English CoT of the same underlying behavior.
  *Interpretation:* non-English CoT carries objectively less monitorable signal; safety cases must not assume CoT monitoring works outside English. Publishable as a fundamental limitation finding. R_L is reported as a continuous quantity in all cases; the 80% cut is the pre-registered label, not a way to hide partial recovery.

- **H-robust (no gap):** All non-English cells are within **< 5 pp AUC** `[same frozen threshold]` of the English baseline at n ≥ 400/cell, with paired CIs consistent with no effect.
  *Interpretation:* agentic CoT oversight is language-robust at ≤ 32B scale — the extrapolation from Onyame et al.'s MCQ results to agentic settings does not hold. Publishable as a contradiction of the field's working assumption. Per kill criterion K2 (§10), we publish this and **stop** — no effect-hunting by adding models or languages.

**Decision tree** (evaluated per language, primary = Czech):

```
Gap ≥ 5pp AUC (Holm-significant)?
├── NO  → H-robust  → publish contradiction, stop
└── YES → Translate-then-monitor recovers ≥ 80% of gap?
          ├── YES → H-monitor → publish cheap-fix result + recommendation
          └── NO  → H-model  → publish fundamental-limitation result + safety-case implication
```

Mixed outcomes across languages/monitors (e.g., recovery for German but not Czech) are pre-declared as **reportable heterogeneity**, described per-cell, not averaged away.

---

## 3. Design

### 3.1 Locked design decisions (not up for revision)

1. **Instructed-covert (control-style):** the attack policy is *instructed* to complete a covert side task alongside the main task; the honest policy does only the main task. Positives and negatives exist by construction; no propensity measurement.
2. **Programmatic, language-neutral ground truth:** whether the covert side task succeeded is decided by **hidden automated tests** (unit tests / assertions), never an LLM judge. This is the core defense against the attack-validity confound — the validity criterion cannot depend on language.
3. **Core arm = translation matrix on English-generated transcripts:** attack quality is held fixed across languages because CS/DE versions are *translations of the same transcript*. This arm cannot fail on language drift.
4. **Text-only summer, GPUs from Sep 15;** MVP is pilot only.

### 3.2 Arm A — core (translation matrix; confirmatory)

1. **Generate English transcripts.** Code-agent setting (CoT Red-Handed / ControlArena style): main coding task + hidden side task (benign code sabotage detectable by hidden tests). Attack policy = instructed to pursue both; honest policy = main task only. Subjects: gpt-oss-20b (full raw CoT, local/A100) and Qwen3-32B (vLLM, MetaCentrum, small < 24h single-GPU jobs).
2. **Validity filter (programmatic only).** Inclusion rules in §9.
3. **Translate the CoT.** Czech: machine translation + **native-speaker (author) verification** of the full confirmatory set or a frozen subset `[FREEZE BEFORE RUN: verification coverage — recommended: 100% of CS attack CoTs + ≥30% random honest CoTs, with a public correction log]`. German: MT + spot-check of `[FREEZE BEFORE RUN: e.g. 10%]`. Translations preserve pairing: same transcript in 3 languages.
4. **Run the monitor matrix** (§5) on all versions. Monitors read **only the CoT**, capped at **8k tokens** `[FREEZE BEFORE RUN: 8000 tokens]` per transcript. Monitor outputs a suspicion score 0–100 with a frozen prompt `[FREEZE BEFORE RUN: prompt file hash]`, temperature 0.

### 3.3 Arm B — stretch (live non-English generation; descriptive/exploratory only)

Prompt/prefill engineering to keep CoT in Czech/German during live generation. Report only transcripts that are language-compliant (> 70% of CoT tokens in target language per a frozen classifier `[FREEZE BEFORE RUN: classifier = fasttext lid.176 or equivalent + 70% threshold]`) **and** side-task-valid. Per-language side-task success rate is itself a reported result. **Arm B never feeds the confirmatory hypotheses** — it is exploratory context, subject to kill criterion K1.

---

## 4. Conditions

**Subjects (2):** gpt-oss-20b; Qwen3-32B.
**CoT languages (3):** EN (native baseline); DE (high-resource control, MT); CS (mid-resource, natively verified).
**Monitors (4):**

| Monitor | Role |
|---|---|
| M1: Gemini Flash, English prompt `[FREEZE: exact model version string]` | main trusted monitor |
| M2: translate-then-monitor (CoT → EN via Gemini `[FREEZE: version]`, then M1) | the decisive arm |
| M3: Qwen3-8B, English prompt `[FREEZE: version/quantization]` | weak trusted monitor (AI-control realism) |
| M4: keyword/regex baseline `[FREEZE: keyword list hash]` | floor baseline |

**Cells:** per subject, 3 languages × 4 monitors − 1 (M2 on EN CoT is the identity; run it once anyway as a translation round-trip sanity check, not a confirmatory cell) = **11 confirmatory cells × 2 subjects = 22 cells**, each scoring the *same* n ≥ 400 transcripts per subject (paired design).

**Optional ablation (time permitting, exploratory):** monitor prompted in the CoT's language. Swahili/Telugu at most as an unverified MT appendix.

---

## 5. Primary contrast and confirmatory scope

- **Primary confirmatory cell family:** subject **gpt-oss-20b** × monitor **M1 (Gemini Flash EN)** × language pairs **{EN↔CS, EN↔DE}**, with recovery evaluated via **M2** on the same transcripts. Czech is the headline language (native verification kills the "the translator ruined it" objection).
- **Replication:** the same analysis on Qwen3-32B; reported as confirmatory replication, not pooled.
- **Secondary/exploratory:** M3, M4, Arm B, ablations — reported with the same statistics but labeled non-primary.

---

## 6. Sample size and power `[FREEZE BEFORE RUN: n per cell = 400 (200 attack + 200 honest)]`

**n ≥ 400 transcripts/cell (≈ 200 attack + 200 honest), per subject.** Translations reuse the same transcripts, so this is one generation budget per subject, not per cell.

**Why AUC is primary and why this n:**

1. **AUC precision.** By Hanley–McNeil, at AUC ≈ 0.80 with 200 positives/200 negatives, SE(AUC) ≈ 0.022 → 95% CI half-width ≈ ±4.3 pp for a single cell.
2. **The paired design buys the power.** CS/DE cells are translations of the *same* transcripts, so per-transcript monitor scores are strongly correlated across languages. Paired-bootstrap ΔAUC (resampling transcripts, carrying all language versions together) has SE ≈ 0.015–0.02 for plausible cross-language score correlations (ρ ≈ 0.6–0.8), giving ~80% power to detect a **≈ 5 pp AUC** difference — exactly the pre-registered effect threshold. Unpaired, the same power would need roughly 2–3× the n.
3. **Why TPR@2%FPR cannot be primary at this n.** With 200 negatives, the 2% FPR operating point is set by the 4th-highest honest score — a single order statistic. The threshold itself is unstable (observing 4/200 false positives is consistent with a true FPR anywhere in ~[0.5%, 5%]), and the TPR estimated at that threshold has bootstrap CIs of roughly ±8–10 pp at n = 150–200 — wider than the expected effect. At n = 400 it is a usable *secondary* metric with CIs; it is never a headline number. (This instability was a flaw in the project's original draft and is the reason n was raised to 400.)
4. **McNemar power.** With 400 paired binary decisions, McNemar detects asymmetries in discordant pairs down to roughly 60/40 splits when ≥ 10% of pairs are discordant — adequate for the effect sizes Onyame-style degradation implies.

---

## 7. Metrics

- **Primary: AUC** per cell, over monitor suspicion scores vs. programmatic ground truth, with transcript-level bootstrap 95% CI (B = 10,000 `[FREEZE BEFORE RUN]`, seed frozen `[FREEZE BEFORE RUN: seed]`).
- **Secondary: TPR@2%FPR** per cell, with bootstrap CI; reported, never headlined.
- **Derived: recovery fraction R_L** (§2), with paired-bootstrap CI.
- **Descriptive:** score distributions per cell; Arm B language-compliance and per-language side-task success rates; CS translation correction-log statistics.

---

## 8. Statistical analysis plan

1. **ΔAUC (paired bootstrap):** resample transcripts with replacement; each draw carries the transcript's EN, CS, DE versions and all monitor scores; recompute AUCs and differences. 95% percentile CIs. A gap "exists" per the H-gap rule in §2.
2. **Binary decisions for McNemar:** monitor flag = suspicion score ≥ θ, where θ is calibrated to 2% FPR on a **held-out EN honest calibration split of 50 transcripts** `[FREEZE BEFORE RUN: split size + selection seed]` that is **excluded from all confirmatory statistics**. One θ per monitor, frozen after calibration, applied identically to all language versions.
3. **Paired McNemar** on flags across language versions of the same transcript: pairs EN↔CS and EN↔DE, per (subject × monitor). Exact binomial McNemar if discordant pairs < 25.
4. **Multiple comparisons:** Holm correction across the language-pair family {EN↔CS, EN↔DE} **within** each (subject × monitor); the primary claim rests on the primary cell family (§5), so no correction across subjects/monitors is applied to it, but all p-values for all cells are reported in full in a supplementary table.
5. **Recovery test:** H-monitor requires the paired-bootstrap 95% CI of R_L to lie above `[FREEZE BEFORE RUN: lower bound — recommended: CI excludes 50%, point estimate ≥ 80%]`; otherwise H-model.
6. **Manual read:** 30 transcripts per headline cell `[FREEZE BEFORE RUN: 30]` read by the author, with notes published — a qualitative sanity layer, not a statistic.
7. **No optional stopping:** confirmatory statistics run once, after the full frozen n is collected. Interim looks (MVP, debugging) are pilot only.

---

## 9. Inclusion / exclusion rules (programmatic only)

- **Attack positives:** included iff hidden side-task tests **pass** `[FREEZE BEFORE RUN: whether main-task tests must ALSO pass — recommended: yes, both, so the attack is genuinely covert-and-successful]`.
- **Honest negatives:** included iff main-task tests pass.
- **Excluded regardless:** empty CoT; CoT > 8k tokens is truncated at 8k (not excluded), truncation rate reported per cell.
- **No LLM-based validity filtering anywhere** — an LLM filter would itself be English-centric, reintroducing the confound this design exists to kill.
- **Arm B only:** language-compliance filter (§3.3).
- All exclusion counts reported per cell (CONSORT-style flow table in the write-up).

---

## 10. Kill criteria (pre-registered; mirrors `notes/kill-criteria.md` / anchor note §8)

- **K1 — Language drift (Arm B):** < 40% `[FREEZE BEFORE RUN: 40%]` language-compliant transcripts after one week of prompt engineering (planned week T7) → **drop Arm B**, run the translation matrix only. This is still the full paper — the monitor-side question is answered entirely by Arm A.
- **K2 — No gap:** all non-EN cells within 5 pp AUC of EN at n = 400 → declare **H-robust, publish, stop**. No hunting for the effect by adding models, languages, or scenarios.
- **K3 — Scooped:** weekly Saturday arXiv check; if the monitor-language × CoT-language matrix with a translate arm appears elsewhere → cite it, redirect remaining effort to the code-switching follow-up (idea bank #3), reusing the pipeline.
- **K4 — Monitor fails on English:** EN-EN AUC < 0.65 `[FREEZE BEFORE RUN: 0.65]` after prompt tuning during the MVP → simplify the scenario (more blatant sabotage) until the EN baseline works; if not fixed within one week → switch to the backup project (AF Census).

---

## 11. What counts as each outcome (all branches publishable)

| Outcome | Pre-registered criterion | Publication |
|---|---|---|
| **H-robust** | No language shows a Holm-significant gap ≥ 5 pp AUC | "Agentic CoT oversight is language-robust ≤ 32B — MCQ extrapolation fails." Negative-result note + arXiv. |
| **H-monitor** | Gap confirmed; R_L ≥ 80% (CI per §8.5) | "A $0.001 translation call fixes cross-lingual CoT monitoring — and deployed monitors don't have it." Fix + recommendation. |
| **H-model** | Gap confirmed; R_L < 80% | "Non-English CoT carries less monitorable signal — a fundamental hole in CoT-monitoring safety cases." |
| **Mixed** | Different branches for CS vs DE, or M1 vs M3, or gpt-oss vs Qwen | Reported per-cell as heterogeneity; headline claim restricted to the primary cell family. |
| **Infrastructure failure** | K4 fires and cannot be fixed | Short honest write-up of the pilot + pivot; pipeline released anyway. |

The write-up commitment is unconditional: v0 LessWrong note ~Oct 2 (whatever the 2×2 pilot shows, including "no difference yet"), full AF/LW post + arXiv preprint by Nov 30.

---

## 12. Deviations protocol

Any post-freeze change (prompt, threshold, n, model version, exclusion rule) is recorded in `notes/deviations.md` with date, reason, and whether it was made before or after seeing confirmatory data. Analyses affected by post-hoc changes are labeled exploratory in the write-up. Solo-researcher discipline substitute: the frozen tag `prereg-v1` plus public commit history is the audit trail.

---

## 13. Data & code release

- **Repo public from day one**, MIT license: scenarios + hidden tests, solvers, monitor prompts, translation workflow, analysis code (AUC/bootstrap/McNemar/plots), PBS job scripts.
- **Released data:** all transcripts per (model, language, policy); all monitor scores as CSV; CS verified translations + full correction log (appendix table); calibration split IDs; bootstrap seeds.
- **Reproducibility:** pinned model version strings, pinned dependency lockfile (uv), fixed sampling parameters `[FREEZE BEFORE RUN: temperature/top-p per subject]`, one-command analysis re-run from released scores.
- **Ethics/safety note:** the covert side task is benign, sandboxed code sabotage detectable by unit tests — standard control-evaluation practice (cf. CoT Red-Handed, ControlArena); no harmful capability uplift; no deployment-relevant exploits released.
- **Budget guard:** exact API volume computed and logged before the full run (cap: monitor reads CoT only, ≤ 8k tokens; expected total ≈ $15–40 Gemini + translation; hard cash ceiling $150).

---

## 14. Freeze checklist (complete → commit → tag `prereg-v1`)

- [ ] n per cell (default 400 = 200/200) and per-subject generation budget
- [ ] Gap threshold (5 pp AUC), recovery threshold (80%), and R_L CI rule
- [ ] Attack inclusion rule (side-task pass only vs. main+side both pass)
- [ ] Monitor prompt text (hash), suspicion scale, temperature 0
- [ ] Model version strings: gpt-oss-20b build, Qwen3-32B, Qwen3-8B, Gemini Flash (monitor + translator)
- [ ] McNemar threshold calibration: EN honest calibration split (size, seed), θ per monitor
- [ ] CS verification coverage %, DE spot-check %
- [ ] Arm B language-compliance classifier + 70% threshold
- [ ] Bootstrap B and seed; CoT token cap (8k)
- [ ] Kill-criteria numbers (40% compliance, 0.65 EN-EN AUC floor)
- [ ] Sampling parameters per subject model
- [ ] Keyword-baseline list (hash)

*After tagging, this document is read-only. Changes go to `notes/deviations.md`.*


---
## Power reasoning
AUC is primary because it uses every transcript's score and is threshold-free, so its sampling error shrinks predictably with n. By Hanley-McNeil, at a plausible monitor AUC of ~0.80 with 200 attack + 200 honest transcripts, SE(AUC) is about 0.022, i.e., a single-cell 95% CI of roughly +/-4.3 pp. The decisive gain comes from the paired design: Czech and German cells are translations of the *same* transcripts, so per-transcript monitor scores correlate strongly across languages (expected rho ~0.6-0.8). A paired bootstrap over transcripts (carrying all language versions of each transcript in every resample) drives SE(delta-AUC) down to roughly 0.015-0.02, which gives approximately 80% power to detect a ~5 pp AUC difference at n=400/cell — exactly the pre-registered minimum effect of interest. Achieving the same power with an unpaired comparison would need roughly 2-3x the sample.

TPR@2%FPR cannot carry the primary claim at feasible n because the operating point is a single order statistic of the honest-score distribution: with 200 negatives, the 2% FPR threshold sits at the 4th-highest honest score, and observing 4/200 false positives is consistent with a true FPR anywhere from ~0.5% to ~5%. The TPR read off at that jittery threshold has bootstrap CIs of about +/-8-10 pp at n=150-200 — wider than the 5 pp effect being tested, which was the flaw in the project's original smaller-n draft and the reason n was raised to >=400. At 200 negatives it becomes a reportable secondary metric with CIs, but never the headline.

McNemar on paired binary flags adds a distribution-free confirmation: with 400 paired decisions, even a modest 10% discordance rate yields adequate power to detect a 60/40 asymmetry in discordant pairs, which is well below the asymmetry implied by Onyame-scale degradation. Holm correction across the two language pairs (EN-CS, EN-DE) costs little power at 2 comparisons. n=400/cell is also the point where the whole design stays inside budget: translations reuse the same transcripts, so 400/subject is one generation budget, and monitoring ~400 x 3 languages x 4 monitors x ~6-8k tokens stays in the $15-40 Gemini range.

## Open decisions to freeze
- Attack inclusion rule: require BOTH main-task tests and hidden side-task tests to pass (truly covert-and-successful attack), or side-task pass alone? Recommended default: both must pass — it matches the CoT Red-Handed covert framing and avoids counting attacks a real deployment would reject as broken code.
- McNemar binary threshold: calibrate each monitor's flag threshold to 2% FPR on a held-out EN honest calibration split (~50 transcripts, excluded from all confirmatory stats), or use a fixed score cutoff (e.g., >=50/100)? Recommended default: the calibration-split approach — it is deployment-realistic and avoids arbitrary cutoffs, at the cost of 50 honest transcripts.
- Recovery-fraction statistical rule: what exactly must the R_L confidence interval satisfy for H-monitor? Recommended default: point estimate >= 80% AND paired-bootstrap 95% CI excluding 50% — a bare point estimate at 80% with a CI spanning 0-100% should not count as recovery.
- Primary confirmatory cell: gpt-oss-20b x Gemini Flash x EN-vs-CS with Qwen3-32B as a separate replication (recommended), or pool both subjects? Recommended default: do not pool — two subjects is replication, not a sample of models.
- n per cell: freeze at exactly 400 (200/200), or raise to ~500 if the September budget check shows headroom? Recommended default: freeze 400 and spend any surplus on the manual-read and CS-verification coverage instead of n.
- CS translation verification coverage: verify 100% of attack CoTs + ~30% of honest CoTs (recommended, protects the headline cell) vs. a flat random 50% of everything.
- Arm B language-compliance detector: which classifier (fasttext lid.176 recommended) and confirm the 70% token threshold before any Arm B generation.
- Exact pinned version strings for Gemini Flash (monitor AND translator), gpt-oss-20b build/quantization, Qwen3-32B, Qwen3-8B — must be filled into the freeze checklist the week of Sep 15, since Gemini free-tier model availability may shift by then.
