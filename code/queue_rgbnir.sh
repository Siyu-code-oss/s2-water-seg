#!/bin/bash
# Launch the remaining RGB+NIR folds, one per free GPU, waiting when none is free.
set -u
F2="$HOME/sy/F2"
PY="$HOME/sy/F1/t1/venv/bin/python"
LOG="$F2/logs/queue_rgbnir.log"
say() { echo "[$(date '+%m-%d %H:%M')] $*" >> "$LOG"; }

for f in 1 2 3 4; do
  [ -f "$F2/runs/f${f}_rgbnir.done" ] && continue
  for i in $(seq 1 240); do
    g=""
    for k in 0 1 2 3 4 5; do
      u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $k)
      if [ "$u" -lt 2000 ]; then g=$k; break; fi
    done
    if [ -n "$g" ]; then
      say "fold$f -> GPU$g"
      (cd "$F2/code" && CUDA_VISIBLE_DEVICES=$g nice -n 15 nohup $PY train_usgs.py \
        --epochs 60 --folds $f --tag rgbnir --bands 1,2,3,7 \
        > "$F2/runs/train_rgbnir_f${f}.log" 2>&1 &)
      sleep 45
      break
    fi
    sleep 120
  done
done
say "rgbnir queue done"
