#!/bin/bash
# GPU-aware dispatcher: never leave a free GPU idle while jobs are pending.
set -u
F2="$HOME/sy/F2"
PY="$HOME/sy/F1/t1/venv/bin/python"
JOBS="$F2/code/jobs.txt"
LOG="$F2/logs/sched.log"
MIN_FREE_MB=2000

say() { echo "[$(date '+%m-%d %H:%M')] $*" >> "$LOG"; }
say "scheduler start"

free_mb() { nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i "$1"; }

while true; do
  pending=0
  while IFS='|' read -r tag fold cmd || [ -n "$tag" ]; do
    [ -z "${tag:-}" ] && continue
    marker="$F2/runs/f${fold}_${tag}.done"
    [ -f "$marker" ] && continue
    pending=1
    if pgrep -f "$cmd" > /dev/null; then continue; fi
    for g in 0 1 2 3 4 5; do
      used=$(free_mb $g)
      if [ "$used" -lt "$MIN_FREE_MB" ]; then
        say "dispatch $tag f$fold -> GPU$g"
        (cd "$F2/code" && CUDA_VISIBLE_DEVICES=$g nice -n 15 nohup $PY $cmd \
          >> "$F2/runs/train_${tag}_f${fold}.log" 2>&1 &)
        sleep 8
        break
      fi
    done
  done < "$JOBS"
  [ "$pending" = "0" ] && { say "no pending jobs"; break; }
  sleep 120
done
say "scheduler done"
