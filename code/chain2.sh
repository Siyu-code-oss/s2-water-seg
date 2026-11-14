#!/bin/bash
# Second unattended stage: aux layers + S2 pre-pull, after chain 1 ends.
set -u
F2="$HOME/sy/F2"
PY="$HOME/sy/F1/t1/venv/bin/python"
LOG="$F2/logs/chain2.log"
say() { echo "[$(date '+%H:%M:%S')] $*" >> "$LOG"; }

say "chain2 start (waiting for chain1)"
for i in $(seq 1 240); do
  if ! pgrep -f "overnight.sh" > /dev/null; then break; fi
  sleep 60
done
say "chain1 finished"

say "aux download"
$PY "$F2/code/grab_aux.py" >> "$LOG" 2>&1 || say "FAILED: aux"

if [ -f "$F2/data/screen.csv" ]; then
  say "s2 pre-pull"
  $PY "$F2/code/grab_s2.py" >> "$LOG" 2>&1 || say "FAILED: s2 pull"
else
  say "no screen.csv, skip s2 pull"
fi

say "chain2 end"
