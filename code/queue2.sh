#!/bin/bash
set -u
PY="$HOME/sy/F1/t1/venv/bin/python"
cd "$HOME/sy/F2/code" || exit 1

run() {
  arch="$1"; fold="$2"
  log="$HOME/sy/F2/runs/train_${arch}_f${fold}.log"
  echo "[$(date '+%H:%M')] start $arch f$fold" >> "$HOME/sy/F2/logs/queue2.log"
  CUDA_VISIBLE_DEVICES=5 nice -n 15 "$PY" train_baselines.py --arch "$arch" \
      --folds "$fold" --epochs 20 >> "$log" 2>&1
  echo "[$(date '+%H:%M')] end $arch f$fold" >> "$HOME/sy/F2/logs/queue2.log"
}
export -f run
export PY

{
  for f in 0 1 2 3 4; do echo "unetpp $f"; done
  for f in 0 1 2 3 4; do echo "deeplab $f"; done
} | xargs -P 3 -L 1 bash -c 'run "$@"' _
echo "queue2 done" >> "$HOME/sy/F2/logs/queue2.log"
