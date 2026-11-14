#!/bin/bash
# Compact status report for the F2 pipeline.
F2="$HOME/sy/F2"
echo "== $(date '+%H:%M:%S') =="
echo "-- running:"
pgrep -af 'dl2.py|overnight.sh|chain2.sh|grab_aux.py|grab_s2.py|screen.py|extract_inspect.py' 2>/dev/null | awk '{print "   ", $1, $NF}' | head -8
echo "-- download:"
tail -1 "$F2/logs/dl32.log" 2>/dev/null | sed 's/^/   /'
echo "-- chain1:"
tail -2 "$F2/logs/overnight.log" 2>/dev/null | sed 's/^/   /'
echo "-- chain2:"
tail -2 "$F2/logs/chain2.log" 2>/dev/null | sed 's/^/   /'
echo "-- data:"
du -sh "$F2/data" 2>/dev/null | sed 's/^/   /'
ls "$F2/data/src.7z" "$F2/data/screen.csv" 2>/dev/null | sed 's/^/   /'
echo "-- errors:"
grep -h "FAILED\|Traceback" "$F2/logs/"*.log 2>/dev/null | tail -3 | sed 's/^/   /'
