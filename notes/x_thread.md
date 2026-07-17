# X thread — "Lost in the Monitor" negative-result autopsy

How X threads work (do this):
- **MAIN post = the hook only** (1/ below). It's what gets reshared and what strangers judge.
  **No external link in the main post** — X throttles the reach of posts with links. Attach ONE
  figure here (see below); media lifts reach a lot.
- **Replies 2/–9/ = the thread**, each posted as a self-reply to the previous. Write each so it
  reads on its own (people see one reply out of context).
- **Put the repo link in the LAST reply** (10/), after they're convinced. Then pin the thread.
- Post it when you're around to reply (first ~30 min of engagement matters).

Suggested figure for the main post: a two-bar/line "pilot +0.24 → scaled −0.07 / −0.00 / +0.01",
or a screenshot of the EN/CS/SW detection table from the README. (Ask me and I'll generate a clean
PNG.)

---

## MAIN POST (the hook)

I spent weeks testing an AI-safety hypothesis I was sure was true: a model can hide misbehaviour
from a monitor by "thinking" in a non-English language. I scaled it up. It's dead. Here's the
autopsy — and the 3 things that survived. 🧵

## Replies (the thread)

**2/** The test: a model is told to plant a hidden backdoor in code. A separate "monitor" model
sees ONLY its chain-of-thought and rates how likely it's up to something. Ground truth = a hidden
unit test that actually runs the backdoor. No LLM-judge circularity.

**3/** The pilot (n=11) looked great. Machine-translating the chain-of-thought to Czech *inflated*
the monitor's catch rate by +0.24 — exactly the kind of "your cross-lingual eval is confounded by
the translator" result you can publish. I got excited.

**4/** Then I scaled to ~65 attacks across 3 conditions. The +0.24 became −0.07, −0.00, +0.01.
Gone. In hindsight the pilot never cleared significance — the confidence interval straddled zero
the whole time. Lesson 1: your exciting pilot is noise until it survives scale.

**5/** The core hypothesis — monitors degrade on non-English reasoning — was also null. Strong
monitor: 0.96 / 0.98 / 1.00 across English / Czech / Swahili. Even a cheap monitor didn't degrade;
Czech actually *helped* it. The effect I built the project on doesn't exist here.

**6/** Two confounds I only caught by running an adversarial review (independent agents told to
refute my findings): the incriminating code tokens (safe/, base_dir) are identical across every
language arm — so "language robustness" may be token-matching, not comprehension. Humbling.

**7/** What survived, and is real: monitors are *bimodal* at temperature 0. The same reasoning
scores ~90 on one call and ~15 on the next. Single-call monitor scores are coin flips on hard
cases — you must sample K times and report a detection *rate*. Most eval code doesn't.

**8/** Also real (if less novel): cheap monitors are near-blind to *subtle* sabotage. A weak
monitor caught 6% of subtly-framed backdoors that a frontier monitor caught 80% of. If your safety
plan leans on a cheap "trusted monitor," subtlety is its blind spot.

**9/** So what do you do when the research doesn't pan out? You write the autopsy. A cleanly-killed
hypothesis + transferable method lessons beats a p-hacked positive, and killing your own headline
is a skill worth practising. On to the next one. 🫡

**10/** Full code, data, and a day-by-day lab log with every wrong turn:
github.com/Majny/lost-in-the-monitor

---

Notes on tone/positioning:
- Honest, specific, not self-flagellating and not falsely upbeat — matches "engineer moving into
  safety research, anti-overclaiming."
- Don't tag labs/people to farm attention; if it's good, the right people find it.
- Optional pinned follow-up after it lands: "Next: does a linear probe on the model's *activations*
  catch the subtle backdoors the text monitor missed?" — teases the mech-interp pivot.
