# Lost in the Monitor

**When chain-of-thought oversight of a reasoning model fails outside English,
is it the *monitor* or the *model* that fails?**

A control-style deception evaluation on open-weight reasoning models that
decomposes cross-lingual chain-of-thought (CoT) monitoring failure into a
*monitor-side* effect (recoverable by translating the CoT to English before
monitoring) and a *model-side* effect (non-English CoT genuinely carries less
monitorable signal). The two answers imply opposite safety policies — a cheap
translation layer versus a fundamental limit of CoT monitoring.

> **Status:** in preparation (design + native-Czech translation packs + harness).
> Not yet runnable end-to-end. First public research note planned for
> October 2026; full write-up with open code and all transcripts by end of
> November 2026. This repository is public as a timestamped, pre-registered
> record of the work as it is built.

## The question

Reading a reasoning model's visible chain of thought to catch misbehaviour
before it acts is one of the few oversight levers AI safety currently has, and
recent work shows it is fragile: outside English, monitors miss deceptive
reasoning almost entirely. What has **not** been established is *why*. If the
monitor is at fault, translating the CoT to English before monitoring should
recover the lost catch-rate — a cheap fix. If non-English reasoning carries
less monitorable signal even to a competent reader, no translation helps, and
CoT-based safety cases cannot rely on monitoring outside English.

## Relation to prior work

Onyame et al., *The Fragility of Chain-of-Thought Monitoring Across
Typologically Diverse Languages* ([arXiv:2605.27901](https://arxiv.org/abs/2605.27901),
May 2026), established that CoT monitoring degrades sharply in lower-resource
languages — on single-turn multiple-choice tasks, judged by a single
English-prompted LLM judge, with no translation ablation and no variation of
the monitor's language. This project takes that as its motivating result and
asks the question that setup cannot: on **agentic** transcripts with
programmatic ground truth, is the degradation **monitor-side or model-side**,
measured across a monitor-language × CoT-language matrix with a
translate-then-monitor arm? To our knowledge (2026-07) that decomposition is
open. Methodological template: *CoT Red-Handed*
([arXiv:2505.23575](https://arxiv.org/abs/2505.23575)).

## Design (one paragraph)

Control-style / instructed-covert: an attack policy is *instructed* to insert a
covert code sabotage (a directory-traversal backdoor keyed to a sentinel
prefix), an honest policy solves the same task cleanly. Whether the sabotage
succeeded is decided by **hidden automated tests** — programmatic,
language-neutral ground truth that never depends on an LLM judge, which removes
the attack-validity confound that would otherwise contaminate cross-lingual
comparisons. English transcripts are translated into Czech (human-verified by a
native speaker — the data layer most labs cannot produce in-house) and German
(machine translation with spot checks); a family of monitors (an English-prompted
LLM judge, a translate-then-monitor pipeline, a weak trusted model, and a
keyword baseline) reads only the CoT and scores suspicion. Primary metric is
AUC with bootstrap confidence intervals; paired McNemar tests compare language
versions of the same transcript. Every outcome branch is publishable — a
recoverable gap, an unrecoverable gap, or no gap at all.

> Early informal observation (day 0): instructed in Czech to reason in Czech,
> gpt-oss-20b acknowledged the instruction *in English* and kept reasoning in
> English — which is why live non-English generation is a stretch arm and the
> core of the study runs on translated English transcripts.

## Pre-registration

Hypotheses, sample sizes, metrics, statistical tests, and kill criteria are in
[`notes/pre-registration.md`](notes/pre-registration.md) (frozen before the
full run) and [`notes/kill-criteria.md`](notes/kill-criteria.md). The v0 design
review and its open fixes are in [`notes/v0-review.md`](notes/v0-review.md).

## Stack

Subjects: `gpt-oss-20b` (full raw CoT, local via Ollama) and `Qwen3-32B` (vLLM).
Harness: [Inspect](https://inspect.aisi.org.uk/) (Task / Solver / Scorer).
Judge & translator: Gemini Flash (used **only** as a monitor/translator, never
as a CoT subject, since it exposes thought summaries rather than raw CoT).
Analysis: bootstrap CIs, paired McNemar, Holm correction.

## Repository layout

```
scripts/    one-off & sandbox scripts (00_sandbox.py = CoT-capture spike)
src/        scenarios · solvers · translate · monitors · analysis
data/       transcripts (all published) · translations_verified (+ correction log)
notes/      pre-registration · kill criteria · v0 design review · daily log
results/    tables & figures
```

## Method & authorship

Research direction, experimental design decisions, and the native-Czech
verification are the author's. Engineering is done in the open with heavy
AI-assisted coding (Claude Code) — the author steers and reviews every design
choice. This is stated plainly because honest provenance is the point of an
open, pre-registered safety project.

## License

MIT (code). Prompt packs and transcripts released with the write-up.

---

*Jakub Dvořák · [kubadvorak.com](https://kubadvorak.com) · started July 2026.*
