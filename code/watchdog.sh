#!/bin/bash
# Server-side watchdog: keeps each stage alive, restarts stalls, logs everything.
# Only touches $HOME/sy/F2.
set -u
F2="$HOME/sy/F2"
PY="$HOME/sy/F1/t1/venv/bin/python"
LOG="$F2/logs/watchdog.log"
STALL=900          # 15 min without log growth = stalled
INTERVAL=300

say() { echo "[$(date '+%m-%d %H:%M:%S')] $*" >> "$LOG"; }

# stage:name|marker|logfile|pattern|cmd
STAGES=(
  "chips2|$F2/data/chips2/summary.json|$F2/logs/chips2.log|build_chips2.py|$PY $F2/code/build_chips2.py"
)

say "watchdog start (pid $$)"
while true; do
  for s in "${STAGES[@]}"; do
    IFS='|' read -r name marker logf pattern cmd <<< "$s"
    [ -f "$marker" ] && continue
    pid=$(pgrep -f "$pattern" | head -1)
    if [ -z "$pid" ]; then
      say "$name: not running -> restart"
      cd "$F2/code" && nohup $cmd >> "$logf" 2>&1 &
      continue
    fi
    if [ -f "$logf" ]; then
      age=$(( $(date +%s) - $(stat -c %Y "$logf") ))
      if [ "$age" -gt "$STALL" ]; then
        say "$name: stalled ${age}s -> kill $pid and restart"
        kill "$pid" 2>/dev/null
        sleep 5
        cd "$F2/code" && nohup $cmd >> "$logf" 2>&1 &
      fi
    fi
  done
  sleep "$INTERVAL"
done
