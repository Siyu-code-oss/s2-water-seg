# -*- coding: utf-8 -*-
"""S2 scene inventory over the study area (metadata only)."""
import concurrent.futures as cf
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

BUCKET = "https://sentinel-cogs.s3.us-west-2.amazonaws.com/"
TILES = ["LT", "LU", "MT", "MU"]
YEARS = range(2015, 2025)
MONTHS = range(6, 10)


def _get(url):
    for _ in range(4):
        try:
            with urllib.request.urlopen(url, timeout=45) as r:
                return r.read().decode()
        except Exception:
            continue
    return ""


def list_prefixes(tile, year, month):
    prefix = "sentinel-s2-l2a-cogs/50/R/%s/%d/%d/" % (tile, year, month)
    out, token = [], None
    for _ in range(20):
        q = {"list-type": "2", "delimiter": "/", "prefix": prefix, "max-keys": "1000"}
        if token:
            q["continuation-token"] = token
        x = _get(BUCKET + "?" + urllib.parse.urlencode(q))
        if not x:
            break
        root = ET.fromstring(x)
        ns = {"s": "http://s3.amazonaws.com/doc/2006-03-01/"}
        for p in root.findall(".//s:CommonPrefixes/s:Prefix", ns):
            out.append(p.text)
        nt = root.find(".//s:NextContinuationToken", ns)
        token = nt.text if nt is not None else None
        if not token:
            break
    return [p.split("/")[-2] for p in out]


def job(args):
    t, y, m = args
    return t, y, m, list_prefixes(t, y, m)


def main():
    jobs = [(t, y, m) for t in TILES for y in YEARS for m in MONTHS]
    rows = []
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        for t, y, m, scenes in ex.map(job, jobs):
            for s in scenes:
                d = re.search(r"_(\d{8})_", s)
                rows.append((t, y, m, s, d.group(1) if d else ""))
    rows.sort(key=lambda r: (r[4], r[0]))
    with open("/home/daxiniu12/sy/F2/data/s2_inventory.csv", "w") as f:
        f.write("tile,year,month,scene,date\n")
        for r in rows:
            f.write("%s,%d,%d,%s,%s\n" % r)
    print("scenes:", len(rows))
    uniq = {}
    for t, y, m, s, d in rows:
        uniq.setdefault(d, set()).add(t)
    print("unique dates:", len(uniq))
    for y in YEARS:
        n = sum(1 for d in uniq if d[:4] == str(y))
        print("  %d: %d dates" % (y, n))
    json.dump(sorted(uniq), open("/home/daxiniu12/sy/F2/data/s2_dates.json", "w"))


if __name__ == "__main__":
    main()
