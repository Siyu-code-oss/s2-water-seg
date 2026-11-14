# -*- coding: utf-8 -*-
"""Chunked verified downloader for a named Zenodo file."""
import hashlib
import json
import os
import threading
import time
import urllib.request

RECORD = os.environ["REC"]
KEYSUB = os.environ["KEYSUB"]
OUT = os.path.expanduser(os.environ["OUT"])
CHUNK = 16 << 20
WORKERS = int(os.environ.get("WORKERS", "64"))


def api():
    with urllib.request.urlopen(
            "https://zenodo.org/api/records/%s" % RECORD, timeout=60) as r:
        d = json.load(r)
    f = next(x for x in d["files"] if KEYSUB in x["key"])
    return f["links"]["self"], f["size"], f["checksum"].split(":")[-1], f["key"]


def fetch(url, start, end, path):
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
        except Exception:      # noqa: BLE001
            fails += 1
            if fails > 400:
                return False
            time.sleep(min(20, 1 + fails))


def main():
    url, size, md5, name = api()
    print("file=%s size=%.2f GB" % (name, size / 1e9), flush=True)
    n = (size + CHUNK - 1) // CHUNK
    idx = list(range(n))
    lock = threading.Lock()
    st = {"done": 0, "bytes": 0, "bad": 0}

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
                        st["bad"] += 1
                    continue
            with lock:
                st["done"] += 1
                st["bytes"] += e - s + 1

    ths = [threading.Thread(target=worker, daemon=True) for _ in range(WORKERS)]
    t0 = time.time()
    for t in ths:
        t.start()
    last = 0
    while any(t.is_alive() for t in ths):
        time.sleep(60)
        with lock:
            b, d = st["bytes"], st["done"]
        print("%5.1f%%  %.1f MB  %.0f KB/s  chunks %d/%d bad %d  %.0f min" % (
            100.0 * b / size, b / 1e6, (b - last) / 60 / 1024, d, n, st["bad"],
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
    print("md5 %s %s" % (h.hexdigest(), "OK" if h.hexdigest() == md5 else "MISMATCH"),
          flush=True)
    if h.hexdigest() == md5:
        for i in range(n):
            os.remove("%s.c%04d" % (OUT, i))


if __name__ == "__main__":
    main()
