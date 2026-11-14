#!/bin/bash
# Poll the server every 5 min; exit (and notify) on milestone / error / stall.
SSH="C:/Windows/System32/OpenSSH/ssh.exe -o BatchMode=yes -o ConnectTimeout=15"
HOST="daxiniu12@192.168.20.12"
LOG="D:/F2/logs/watch.log"
mkdir -p D:/F2/logs
prev_sig=""
same=0
for i in $(seq 1 48); do
  out=$($SSH $HOST "bash ~/sy/F2/code/status.sh" 2>&1)
  ts=$(date '+%H:%M:%S')
  echo "===== $ts =====" >> "$LOG"
  echo "$out" >> "$LOG"
  pct=$(echo "$out" | grep -oE '[0-9]+\.[0-9]%' | head -1)
  ms=$(echo "$out" | grep -E 'assembled|extract done|wrote screen|candidates|pre-pull|chain2 end|chain1 finished|FAILED|Traceback' | tail -1 | sed 's/^ *//')
  sig="$pct|$ms"
  if echo "$out" | grep -qE 'FAILED|Traceback'; then
    echo "EXIT reason=error" >> "$LOG"; echo "$out"; exit 2
  fi
  if [ -n "$ms" ] && [ "$ms" != "$prev_sig" ] && [ -n "$prev_sig" ]; then
    echo "EXIT reason=milestone" >> "$LOG"; echo "$out"; exit 0
  fi
  if [ "$sig" = "$prev_sig" ]; then same=$((same+1)); else same=0; fi
  if [ $same -ge 3 ]; then
    echo "EXIT reason=stall" >> "$LOG"; echo "$out"; exit 3
  fi
  prev_sig="$sig"
  sleep 300
done
echo "EXIT reason=timeout" >> "$LOG"
echo "watch window finished"
