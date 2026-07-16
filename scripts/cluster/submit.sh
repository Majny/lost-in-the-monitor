#!/bin/bash
# Run this in an AUTHENTICATED MetaCentrum session (i.e. after kinit succeeded, which
# happens when you ssh in interactively and type your password). Submits the CPU setup
# job and chains the GPU serve+generate job to run only if setup succeeds.
cd /storage/brno2/home/dvorak2810/litm || exit 1
SETUP=$(qsub setup.pbs) || { echo "setup qsub failed (Kerberos ticket? run: kinit)"; exit 1; }
echo "setup   job: $SETUP"
GEN=$(qsub -W depend=afterok:"$SETUP" serve_gen.pbs) || { echo "gen qsub failed"; exit 1; }
echo "gen     job: $GEN  (runs after setup succeeds)"
printf '%s\n%s\n' "$SETUP" "$GEN" > submitted.txt
echo "saved ids to submitted.txt — Claude reads job output from this dir via its ssh key."
