# -*- coding: utf-8 -*-
"""Chunked parallel download of an arbitrary URL (resume inside chunks)."""
import os
import sys
import threading
import time
import urllib.request

URL = sys.argv[1]
OUT = os.path.expanduser(sys.argv[2])
WORKERS = int(sys.argv[3]) if len(sys.argv) > 3 else 24
CHUNK = 8 << 20

req = urllib.request.Request(URL, method="HEAD")
with urllib.request.urlopen(req, timeout=60) as r:
    SIZE = int(r.headers["Content-Length"])
print("size %.1f MB" % (SIZE / 1e6), flush=True)


def fetch(start, end, path):
    expect = end - start + 1
    tmp = path + ".tmp"
    fails = 0
    while True:
        have = os.path.getsize(tmp) if os.path.exists(tmp) else 0
        if have >= expect:
            os.replace(tmp, path)
            return True
        try:
            q = urllib.request.Request(URL, headers={
                "Range": "bytes=%d-%d" % (start + have, end)})
            with urllib.request.urlopen(q, timeout=60) as r:
                if r.status != 206:
                    raise RuntimeError("status %s" % r.status)
                with open(tmp, "ab") as f:
                    while have < expect:
                        b = r.read(1 << 20)
                        if not b:
                            break
                        b = b[:expect - have]
                        f.write(b)
                        have += len(b)
            fails = 0
        except Exception:      # noqa: BLE001
            fails += 1
            if fails > 200:
                return False
            time.sleep(2)


n = (SIZE + CHUNK - 1) // CHUNK
idx = list(range(n))
lock = threading.Lock()
done = [0]


def worker():
    while True:
        with lock:
            if not idx:
                return
            i = idx.pop(0)
        s = i * CHUNK
        e = min(SIZE - 1, s + CHUNK - 1)
        p = "%s.c%04d" % (OUT, i)
        if not (os.path.exists(p) and os.path.getsize(p) == e - s + 1):
            fetch(s, e, p)
        with lock:
            done[0] += 1


ths = [threading.Thread(target=worker, daemon=True) for _ in range(WORKERS)]
t0 = time.time()
for t in ths:
    t.start()
while any(t.is_alive() for t in ths):
    time.sleep(20)
    cur = sum(os.path.getsize("%s.c%04d" % (OUT, i)) for i in range(n)
              if os.path.exists("%s.c%04d" % (OUT, i)))
    print("%.1f%% %.1f MB %.0f KB/s chunks %d/%d" % (
        100 * cur / SIZE, cur / 1e6, cur / 1e3 / max(1, time.time() - t0), done[0], n),
        flush=True)
with open(OUT, "wb") as out:
    for i in range(n):
        with open("%s.c%04d" % (OUT, i), "rb") as f:
            for b in iter(lambda: f.read(1 << 22), b""):
                out.write(b)
for i in range(n):
    os.remove("%s.c%04d" % (OUT, i))
print("done %.1f MB" % (os.path.getsize(OUT) / 1e6), flush=True)
