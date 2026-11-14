#!/bin/bash
# Server-side watchdog v2: keeps the 5-fold training alive, max 3 concurrent.
set -u
F2="$HOME/sy/F2"
PY="$HOME/sy/F1/t1/venv/bin/python"
LOG="$F2/logs/watchdog.log"
LIMIT=3
STALL=1800
INTERVAL=300

say() { echo "[$(date '+%m-%d %H:%M:%S')] $*" >> "$LOG"; }
say "watchdog2 start (pid $$)"

while true; do
  # chips stage
  if [ ! -f "$F2/data/chips2/summary.json" ]; then
    if ! pgrep -f "build_chips2.py" > /dev/null; then
      say "chips2 missing -> restart"
      (cd "$F2/code" && nohup $PY build_chips2.py >> "$F2/logs/chips2.log" 2>&1 &)
    fi
  fi

  run=$(pgrep -fc "train_usgs.py --epochs" || true)
  run=${run:-0}
  for f in 0 1 2 3 4; do
    marker="$F2/runs/f${f}_base.done"
    [ -f "$marker" ] && continue
    if pgrep -f "train_usgs.py --epochs 60 --folds $f " > /dev/null; then
      # running: check progress
      logf="$F2/runs/train_f${f}.log"
      if [ -f "$logf" ]; then
        age=$(( $(date +%s) - $(stat -c %Y "$logf") ))
        if [ "$age" -gt "$STALL" ]; then
          pid=$(pgrep -f "train_usgs.py --epochs 60 --folds $f " | head -1)
          say "fold$f stalled ${age}s -> kill $pid"
          kill "$pid" 2>/dev/null
          sleep 3
          (cd "$F2/code" && CUDA_VISIBLE_DEVICES=5 nice -n 15 nohup $PY train_usgs.py \
             --epochs 60 --folds $f --tag base >> "$logf" 2>&1 &)
        fi
      fi
    else
      if [ "$run" -lt "$LIMIT" ]; then
        say "fold$f not running -> start (active=$run)"
        (cd "$F2/code" && CUDA_VISIBLE_DEVICES=5 nice -n 15 nohup $PY train_usgs.py \
           --epochs 60 --folds $f --tag base >> "$F2/runs/train_f${f}.log" 2>&1 &)
        run=$((run+1))
      fi
    fi
  done
  sleep "$INTERVAL"
done
