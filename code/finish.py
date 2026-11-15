# -*- coding: utf-8 -*-
"""Finish an almost-complete multi-part download: split the remaining bytes
across many connections, then assemble and verify."""
import hashlib
import json
import os
import threading
import time
import urllib.request

RECORD = "8039317"
OUT = os.path.expanduser("~/F2/data/src.7z")
PARTS = 32
SUB = 16          # connections per unfinished part


def api():
    with urllib.request.urlopen(
            "https://zenodo.org/api/records/%s" % RECORD, timeout=60) as r:
        d = json.load(r)
    f = max(d["files"], key=lambda x: x["size"])
    return f["links"]["self"], f["size"], f["checksum"].split(":")[-1]


def get_range(url, start, end, path, stat):
    done = os.path.getsize(path) if os.path.exists(path) else 0
    expect = end - start + 1
    fails = 0
    while done < expect:
        pos = start + done
        try:
            req = urllib.request.Request(url, headers={"Range": "bytes=%d-%d" % (pos, end)})
            with urllib.request.urlopen(req, timeout=60) as r:
                if r.status != 206:
                    raise RuntimeError("no range")
                with open(path, "ab") as f:
                    while done < expect:
                        b = r.read(1 << 20)
                        if not b:
                            raise RuntimeError("short")
                        if len(b) > expect - done:
                            b = b[:expect - done]
                        f.write(b)
                        done += len(b)
                        stat["n"] += len(b)
            fails = 0
        except Exception:      # noqa: BLE001
            fails += 1
            if fails > 200:
                raise
            time.sleep(2)


def main():
    url, size, md5 = api()
    step = size // PARTS + 1
    todo = []
    for i in range(PARTS):
        s = i * step
        e = min(size - 1, s + step - 1)
        p = "%s.part%02d" % (OUT, i)
        have = os.path.getsize(p) if os.path.exists(p) else 0
        exp = e - s + 1
        if have < exp:
            todo.append((i, s, e, p, have, exp))
    print("unfinished parts:", [(t[0], t[5] - t[4]) for t in todo], flush=True)

    for i, s, e, p, have, exp in todo:
        start = s + have
        remain = exp - have
        n = min(SUB, max(1, remain // (2 << 20)))
        chunk = remain // n + 1
        stat = {"n": 0}
        ths = []
        tmps = []
        for j in range(n):
            a = start + j * chunk
            b = min(e, a + chunk - 1)
            if a > b:
                break
            tmp = "%s.sub%02d" % (p, j)
            tmps.append((tmp, a, b))
            t = threading.Thread(target=get_range, args=(url, a, b, tmp, stat), daemon=True)
            t.start()
            ths.append(t)
        t0 = time.time()
        while any(t.is_alive() for t in ths):
            time.sleep(20)
            print("  part%02d %.1f/%.1f MB %.0f KB/s" % (
                i, stat["n"] / 1e6, remain / 1e6,
                stat["n"] / 1e3 / max(1, time.time() - t0)), flush=True)
        with open(p, "ab") as f:
            for tmp, a, b in tmps:
                with open(tmp, "rb") as g:
                    for b_ in iter(lambda: g.read(1 << 22), b""):
                        f.write(b_)
                os.remove(tmp)
        print("  part%02d complete %d/%d" % (i, os.path.getsize(p), exp), flush=True)

    print("assembling", flush=True)
    with open(OUT, "wb") as out:
        for i in range(PARTS):
            with open("%s.part%02d" % (OUT, i), "rb") as f:
                for b in iter(lambda: f.read(1 << 22), b""):
                    out.write(b)
    h = hashlib.md5()
    with open(OUT, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    ok = h.hexdigest() == md5
    print("md5 %s %s" % (h.hexdigest(), "OK" if ok else "MISMATCH"), flush=True)
    if ok:
        for i in range(PARTS):
            os.remove("%s.part%02d" % (OUT, i))


if __name__ == "__main__":
    main()
