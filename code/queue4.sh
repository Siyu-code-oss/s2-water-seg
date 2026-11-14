#!/bin/bash
set -u
PY="$HOME/sy/F1/t1/venv/bin/python"
cd "$HOME/sy/F2/code" || exit 1
LOG="$HOME/sy/F2/logs/queue4.log"
say() { echo "[$(date '+%H:%M')] $*" >> "$LOG"; }

say "queue4 start"

run() {
  tag="$1"; fold="$2"; extra="$3"
  log="$HOME/sy/F2/runs/train_${tag}_f${fold}.log"
  say "start $tag f$fold"
  CUDA_VISIBLE_DEVICES=5 nice -n 15 "$PY" train_usgs.py --epochs 60 \
      --folds "$fold" --tag "$tag" $extra >> "$log" 2>&1
  say "end $tag f$fold"
}
export -f run
export PY

{
  for f in 0 1 2 3 4; do echo "bce $f --loss=bce"; done
  for f in 0 1 2 3 4; do echo "focal $f --loss=focal"; done

} | xargs -P 3 -L 1 bash -c 'run "$@"' _
say "queue4 done"
