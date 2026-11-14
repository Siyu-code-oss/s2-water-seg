# -*- coding: utf-8 -*-
"""Multi-connection resumable downloader (server side)."""
import hashlib
import json
import os
import sys
import threading
import time
import urllib.request

RECORD = "8039317"
OUT = os.path.expanduser("~/sy/F2/data/src.7z")
PARTS = 16


def api():
    with urllib.request.urlopen(
            "https://zenodo.org/api/records/%s" % RECORD, timeout=60) as r:
        d = json.load(r)
    f = max(d["files"], key=lambda x: x["size"])
    return f["links"]["self"], f["size"], f["checksum"].split(":")[-1], f["key"]


def worker(url, start, end, path, done, idx, total):
    if os.path.exists(path) and os.path.getsize(path) == end - start + 1:
        done["done"] += end - start + 1
        return
    pos = start + (os.path.getsize(path) if os.path.exists(path) else 0)
    req = urllib.request.Request(url, headers={"Range": "bytes=%d-%d" % (pos, end)})
    with urllib.request.urlopen(req, timeout=120) as r, open(path, "ab") as fp:
        while True:
            chunk = r.read(1 << 20)
            if not chunk:
                break
            fp.write(chunk)
            pos += len(chunk)
            done["done"] += len(chunk)
            if pos > end:
                break
    done["finished"] += 1


def main():
    url, size, md5, name = api()
    print("file=%s size=%.2f GB md5=%s" % (name, size / 1e9, md5), flush=True)
    step = size // PARTS + 1
    done = {"done": 0, "finished": 0}
    paths = []
    ths = []
    for i in range(PARTS):
        s = i * step
        e = min(size - 1, s + step - 1)
        p = "%s.part%02d" % (OUT, i)
        paths.append(p)
        t = threading.Thread(target=worker, args=(url, s, e, p, done, i, size), daemon=True)
        t.start()
        ths.append(t)
    t0 = time.time()
    last = 0
    while any(t.is_alive() for t in ths):
        time.sleep(30)
        el = time.time() - t0
        sp = (done["done"] - last) / 30.0
        last = done["done"]
        pct = 100.0 * done["done"] / size
        print("%5.1f%%  %.1f/%.1f MB  now %.0f KB/s  elapsed %.0f min  finished %d/%d"
              % (pct, done["done"] / 1e6, size / 1e6, sp / 1024, el / 60,
                 done["finished"], PARTS), flush=True)
    print("assembling...", flush=True)
    with open(OUT, "wb") as out:
        for p in paths:
            with open(p, "rb") as fp:
                while True:
                    b = fp.read(1 << 22)
                    if not b:
                        break
                    out.write(b)
    h = hashlib.md5()
    with open(OUT, "rb") as fp:
        for b in iter(lambda: fp.read(1 << 22), b""):
            h.update(b)
    print("assembled %.2f GB md5=%s %s" % (os.path.getsize(OUT) / 1e9, h.hexdigest(),
                                           "OK" if h.hexdigest() == md5 else "MISMATCH"),
          flush=True)
    if h.hexdigest() == md5:
        for p in paths:
            os.remove(p)


if __name__ == "__main__":
    main()
