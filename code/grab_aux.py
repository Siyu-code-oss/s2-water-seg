# -*- coding: utf-8 -*-
"""Download auxiliary layers: SRTM DEM tiles and ESA WorldCover."""
import os
import urllib.request

F2 = os.path.expanduser("~/sy/F2")
AUX = os.path.join(F2, "data", "aux")
os.makedirs(AUX, exist_ok=True)

SRTM = "https://elevation-tiles-prod.s3.amazonaws.com/skadi/%s/%s.hgt.gz"
WC = ("https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/"
      "ESA_WorldCover_10m_2021_v200_%s_Map.tif")

JOBS = [("N28E115", SRTM % ("N28", "N28E115")), ("N28E116", SRTM % ("N28", "N28E116")),
        ("N29E115", SRTM % ("N29", "N29E115")), ("N29E116", SRTM % ("N29", "N29E116")),
        ("landcover", WC % "N30E114")]


def get(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 1e6:
        print("skip", path, flush=True)
        return
    tmp = path + ".part"
    for attempt in range(6):
        try:
            with urllib.request.urlopen(url, timeout=120) as r, open(tmp, "wb") as f:
                while True:
                    b = r.read(1 << 20)
                    if not b:
                        break
                    f.write(b)
            os.replace(tmp, path)
            print("ok %s %.1f MB" % (os.path.basename(path),
                                     os.path.getsize(path) / 1e6), flush=True)
            return
        except Exception as exc:   # noqa: BLE001
            print("retry", path, exc, flush=True)
    print("FAILED", path, flush=True)


for name, url in JOBS:
    ext = ".hgt.gz" if "skadi" in url else ".tif"
    get(url, os.path.join(AUX, name + ext))
