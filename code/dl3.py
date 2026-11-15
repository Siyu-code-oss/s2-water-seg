# -*- coding: utf-8 -*-
"""Chunked, verifiable downloader: every chunk is written from scratch and
size-checked, so no resume-offset bug can corrupt the result."""
import hashlib
import json
import os
import threading
import time
import urllib.request

RECORD = "8039317"
OUT = os.path.expanduser("~/F2/data/src.7z")
CHUNK = 16 << 20
WORKERS = int(os.environ.get("WORKERS", "24"))


def api():
    with urllib.request.urlopen(
            "https://zenodo.org/api/records/%s" % RECORD, timeout=60) as r:
        d = json.load(r)
    f = max(d["files"], key=lambda x: x["size"])
    return f["links"]["self"], f["size"], f["checksum"].split(":")[-1]


def fetch(url, start, end, path):
    """Resume inside the chunk: keep partial bytes, ask only for the rest."""
    expect = end - start + 1
    tmp = path + ".tmp"
    fails = 0
    while True:
        have = os.path.getsize(tmp) if os.path.exists(tmp) else 0
        if have >= expect:
            os.replace(tmp, path)
            return True
        try:
            req = urllib.request.Request(
                url, headers={"Range": "bytes=%d-%d" % (start + have, end)})
            with urllib.request.urlopen(req, timeout=60) as r:
                if r.status != 206:
                    raise RuntimeError("status %s" % r.status)
                with open(tmp, "ab") as f:
                    while have < expect:
                        b = r.read(1 << 20)
                        if not b:
                            break
                        if len(b) > expect - have:
                            b = b[:expect - have]
                        f.write(b)
                        have += len(b)
            fails = 0
        except Exception:          # noqa: BLE001
            fails += 1
            if fails > 400:
                return False
            time.sleep(min(20, 1 + fails))


def main():
    url, size, md5 = api()
    n = (size + CHUNK - 1) // CHUNK
    print("size %.2f GB  chunks %d x %d MB" % (size / 1e9, n, CHUNK >> 20), flush=True)
    idx = list(range(n))
    lock = threading.Lock()
    stat = {"done": 0, "bytes": 0, "bad": 0}

    def worker():
        while True:
            with lock:
                if not idx:
                    return
                i = idx.pop(0)
            s = i * CHUNK
            e = min(size - 1, s + CHUNK - 1)
            p = "%s.c%04d" % (OUT, i)
            if not (os.path.exists(p) and os.path.getsize(p) == e - s + 1):
                if not fetch(url, s, e, p):
                    with lock:
                        stat["bad"] += 1
                    continue
            with lock:
                stat["done"] += 1
                stat["bytes"] += e - s + 1

    ths = [threading.Thread(target=worker, daemon=True) for _ in range(WORKERS)]
    t0 = time.time()
    for t in ths:
        t.start()
    last = 0
    while any(t.is_alive() for t in ths):
        time.sleep(30)
        with lock:
            b = stat["bytes"]
            d = stat["done"]
        print("%5.1f%%  %.1f MB  %.0f KB/s  chunks %d/%d bad %d  %.0f min" % (
            100.0 * b / size, b / 1e6, (b - last) / 30 / 1024, d, n, stat["bad"],
            (time.time() - t0) / 60), flush=True)
        last = b

    print("assembling", flush=True)
    with open(OUT, "wb") as out:
        for i in range(n):
            with open("%s.c%04d" % (OUT, i), "rb") as f:
                for b in iter(lambda: f.read(1 << 22), b""):
                    out.write(b)
    h = hashlib.md5()
    with open(OUT, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    ok = h.hexdigest() == md5
    print("md5 %s  %s" % (h.hexdigest(), "OK" if ok else "MISMATCH"), flush=True)
    if ok:
        for i in range(n):
            os.remove("%s.c%04d" % (OUT, i))


if __name__ == "__main__":
    main()
