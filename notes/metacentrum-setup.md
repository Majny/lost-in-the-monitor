# MetaCentrum setup — offloading generation from the Mac

*Status 2026-07-17: access confirmed; the GPU inference stack is NOT yet set up. The
first real cluster run should be done interactively — first-time serving setups always
need debugging, so it is deliberately not attempted unattended.*

## Access (confirmed, works)
- SSH key: `Host metacentrum` → skirit.metacentrum.cz, key `~/.ssh/for_metacentrum/id_ed25519`,
  no passphrase. No Kerberos needed for SSH.
- Username on the grid: **dvorak2810**. Frontend: skirit.grid.cesnet.cz, PBS (`qsub`) available.
- Home storage: `/storage/brno11-elixir/home/dvorak2810` (+ brno12-cerit, brno2) — ample quota.

## What's missing to generate gpt-oss-20b transcripts there
- No `ollama` module; `apptainer` not on the login-node PATH (usually `module add` on a
  compute node).
- The subject model must be served on a GPU node. Two workable routes:
  1. **vLLM** in a Python venv on an A100/H100 node (serves an OpenAI-compatible endpoint),
     model pulled from Hugging Face to `$SCRATCHDIR`.
  2. **apptainer** ollama image on a GPU node, model pulled to scratch.
- PBS GPU request is resource-based, e.g.:
  `qsub -I -l select=1:ncpus=8:ngpus=1:mem=64gb:scratch_local=60gb -l walltime=4:00:00`

## Code change needed first
`scripts/01_pilot_cot_capture.py` currently talks to a local Ollama server. To use a
remote vLLM endpoint it needs a configurable backend (base_url + OpenAI-compatible client);
the CoT lands in `reasoning`/`<think>` depending on the server. Small refactor, do it
before the cluster run.

## Plan (interactive, together)
1. Interactive GPU job → validate serving (vLLM + gpt-oss-20b answers one prompt, CoT visible).
2. Point `scripts/01` at that endpoint; confirm capture works on the cluster.
3. Batch-submit generation for the big run (n≥400/cell, add Qwen3-32B).

## Why not tonight
The small pilot generation is already done on the Mac; everything left tonight is Gemini
API (monitoring, translation) which uses no GPU at all. MetaCentrum matters for the *big*
confirmatory run, not this pilot.
