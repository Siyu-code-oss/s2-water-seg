#!/bin/bash
set -u
PY="$HOME/sy/F1/t1/venv/bin/python"
cd "$HOME/sy/F2/code" || exit 1
LOG="$HOME/sy/F2/logs/queue3.log"
say() { echo "[$(date '+%H:%M')] $*" >> "$LOG"; }

say "waiting for queue2"
for i in $(seq 1 600); do
  pgrep -f queue2.sh > /dev/null || break
  sleep 60
done
say "queue2 finished, start NDWI folds"

run() {
  fold="$1"
  log="$HOME/sy/F2/runs/train_ndwi_f${fold}.log"
  say "start ndwi f$fold"
  CUDA_VISIBLE_DEVICES=5 nice -n 15 "$PY" train_usgs.py --epochs 60 \
      --folds "$fold" --tag ndwi --ch 17 --chipdir "$HOME/sy/F2/data/chips17" >> "$log" 2>&1
  say "end ndwi f$fold"
}
export -f run
export PY

seq 0 4 | xargs -P 3 -L 1 bash -c 'run "$@"' _
say "queue3 done"
