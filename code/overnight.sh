#!/bin/bash
# Unattended chain: wait for download -> verify -> extract -> inspect -> screen
set -u
F2="$HOME/sy/F2"
PY="$HOME/sy/F1/t1/venv/bin/python"
LOG="$F2/logs/overnight.log"
MD5="aec0fd95fbc27b98dbbe7861b5dc7359"
say() { echo "[$(date '+%H:%M:%S')] $*" >> "$LOG"; }

say "chain start"

# 1) wait for download to finish (dl2.py exits after assembly)
for i in $(seq 1 240); do
  if ! pgrep -f "dl2.py" > /dev/null; then break; fi
  sleep 60
done
say "downloader no longer running"

if [ ! -f "$F2/data/src.7z" ]; then
  say "FAILED: src.7z missing"; exit 1
fi

# 2) verify md5
H=$(md5sum "$F2/data/src.7z" | awk '{print $1}')
say "md5=$H"
if [ "$H" != "$MD5" ]; then say "FAILED: md5 mismatch"; exit 1; fi

# 3) extract + inspect
say "extracting"
$PY "$F2/code/extract_inspect.py" >> "$LOG" 2>&1 || { say "FAILED: extract"; exit 1; }
say "extract done"

# 4) coarse screening of S2 dates (cloud + water on overviews)
say "screening"
$PY "$F2/code/screen.py" >> "$LOG" 2>&1 || say "FAILED: screen"
say "chain end"
