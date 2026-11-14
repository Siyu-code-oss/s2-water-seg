#!/bin/bash
# Run ablation folds with 3 concurrent processes on GPU 5.
set -u
PY="$HOME/sy/F1/t1/venv/bin/python"
cd "$HOME/sy/F2/code" || exit 1

run() {
  tag="$1"; fold="$2"; extra="$3"
  log="$HOME/sy/F2/runs/train_${tag}_f${fold}.log"
  echo "[$(date '+%H:%M')] start $tag f$fold $extra" >> "$HOME/sy/F2/logs/queue.log"
  CUDA_VISIBLE_DEVICES=5 nice -n 15 "$PY" train_usgs.py --epochs 60 \
      --folds "$fold" --tag "$tag" $extra >> "$log" 2>&1
  echo "[$(date '+%H:%M')] end $tag f$fold" >> "$HOME/sy/F2/logs/queue.log"
}
export -f run
export PY

{
  for f in 0 1 2 3 4; do echo "std $f --ds=0"; done
  for f in 0 1 2 3 4; do echo "b4 $f --nbands=4"; done
} | xargs -P 3 -L 1 bash -c 'run "$@"' _
echo "queue done" >> "$HOME/sy/F2/logs/queue.log"
