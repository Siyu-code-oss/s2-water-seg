#!/bin/bash
# Watch the chunk download: alert on stall, exit on milestone/error.
SSH="C:/Windows/System32/OpenSSH/ssh.exe -o BatchMode=yes -o ConnectTimeout=15"
HOST="daxiniu12@192.168.20.12"
LOG="D:/F2/logs/watch2.log"
mkdir -p D:/F2/logs
prev=0
stall=0
for i in $(seq 1 48); do
  out=$($SSH $HOST "du -cb ~/sy/F2/data/src.7z.c* 2>/dev/null | tail -1 | cut -f1; tail -1 ~/sy/F2/logs/dl3.log; tail -1 ~/sy/F2/logs/post_dl.log 2>/dev/null" 2>&1)
  bytes=$(echo "$out" | head -1)
  bytes=${bytes:-0}
  { echo "===== $(date '+%H:%M:%S')  bytes=$bytes"; echo "$out"; } >> "$LOG"
  if echo "$out" | grep -qE "md5 |FAILED|done"; then
    echo "EXIT milestone" >> "$LOG"; echo "$out"; exit 0
  fi
  delta=$((bytes - prev))
  if [ $delta -lt 10000000 ]; then stall=$((stall+1)); else stall=0; fi
  if [ $stall -ge 2 ]; then
    echo "EXIT stall" >> "$LOG"; echo "$out"; exit 3
  fi
  prev=$bytes
  sleep 300
done
echo "watch2 window ended"
