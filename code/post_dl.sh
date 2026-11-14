#!/bin/bash
set -u
F2="$HOME/sy/F2"
PY="$HOME/sy/F1/t1/venv/bin/python"
LOG="$F2/logs/post_dl.log"
say() { echo "[$(date '+%H:%M:%S')] $*" >> "$LOG"; }

say "waiting for dl3"
for i in $(seq 1 300); do
  pgrep -f "dl3.py" > /dev/null || break
  sleep 60
done
say "dl3 finished"

if [ ! -f "$F2/data/src.7z" ]; then say "FAILED: no src.7z"; exit 1; fi
MD5=$(md5sum "$F2/data/src.7z" | awk '{print $1}')
say "md5=$MD5 (zenodo aec0fd95fbc27b98dbbe7861b5dc7359)"

say "extracting"
$PY "$F2/code/extract_inspect.py" >> "$LOG" 2>&1
say "extract exit=$?"

say "summary"
$PY "$F2/code/summarize.py" >> "$LOG" 2>&1
say "done"
