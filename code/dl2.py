# -*- coding: utf-8 -*-
"""Multi-connection resumable downloader v2 (auto-reconnect per range)."""
import hashlib
import json
import os
import threading
import time
import urllib.request

RECORD = "8039317"
OUT = os.path.expanduser(os.environ.get("DL_OUT", "~/sy/F2/data/src.7z"))
PARTS = int(os.environ.get("DL_PARTS", "16"))
RETRY = 500


def api():
    with urllib.request.urlopen(
            "https://zenodo.org/api/records/%s" % RECORD, timeout=60) as r:
        d = json.load(r)
    f = max(d["files"], key=lambda x: x["size"])
    return f["links"]["self"], f["size"], f["checksum"].split(":")[-1], f["key"]


def worker(url, start, end, path, stat):
    expect = end - start + 1
    fails = 0
    while True:
        have = os.path.getsize(path) if os.path.exists(path) else 0
        if have >= expect:
            stat["finished"] += 1
            return
        pos = start + have
        try:
            req = urllib.request.Request(
                url, headers={"Range": "bytes=%d-%d" % (pos, end)})
            with urllib.request.urlopen(req, timeout=60) as r:
                if r.status != 206:
                    raise RuntimeError("server ignored range: %s" % r.status)
                with open(path, "ab") as fp:
                    while pos <= end:
                        chunk = r.read(1 << 20)
                        if not chunk:
                            raise RuntimeError("short read")
                        room = expect - have
                        if len(chunk) > room:
                            chunk = chunk[:room]
                        fp.write(chunk)
                        have += len(chunk)
                        pos += len(chunk)
                        stat["done"] += len(chunk)
                        if have >= expect:
                            break
            fails = 0
        except Exception:
            fails += 1
            stat["err"] += 1
            if fails > RETRY:
                raise
            time.sleep(min(30, 2 + fails))


def main():
    url, size, md5, name = api()
    print("file=%s size=%.2f GB md5=%s" % (name, size / 1e9, md5), flush=True)
    step = size // PARTS + 1
    stat = {"done": 0, "finished": 0, "err": 0}
    paths, ths = [], []
    for i in range(PARTS):
        s = i * step
        e = min(size - 1, s + step - 1)
        p = "%s.part%02d" % (OUT, i)
        paths.append(p)
        t = threading.Thread(target=worker, args=(url, s, e, p, stat), daemon=True)
        t.start()
        ths.append(t)
    t0 = time.time()
    last = 0
    while any(t.is_alive() for t in ths):
        time.sleep(60)
        el = time.time() - t0
        sp = (stat["done"] - last) / 60.0
        last = stat["done"]
        print("%5.1f%%  %.1f MB  now %.0f KB/s  elapsed %.0f min  done %d/%d  retries %d"
              % (100.0 * stat["done"] / size, stat["done"] / 1e6, sp / 1024, el / 60,
                 stat["finished"], PARTS, stat["err"]), flush=True)
    print("assembling...", flush=True)
    with open(OUT, "wb") as out:
        for p in paths:
            with open(p, "rb") as fp:
                for b in iter(lambda: fp.read(1 << 22), b""):
                    out.write(b)
    h = hashlib.md5()
    with open(OUT, "rb") as fp:
        for b in iter(lambda: fp.read(1 << 22), b""):
            h.update(b)
    ok = h.hexdigest() == md5
    print("assembled %.2f GB md5=%s %s" % (os.path.getsize(OUT) / 1e9,
                                           h.hexdigest(), "OK" if ok else "MISMATCH"),
          flush=True)
    if ok:
        for p in paths:
            os.remove(p)


if __name__ == "__main__":
    main()
