# -*- coding: utf-8 -*-
"""Pre-pull S2 crops for the best dates (20 m, lake bbox), under a size budget."""
import csv
import os

import numpy as np
import rasterio
from rasterio.warp import transform_bounds
from rasterio.windows import from_bounds

F2 = os.path.expanduser("~/sy/F2")
OUT = os.path.join(F2, "data", "s2raw")
os.makedirs(OUT, exist_ok=True)
BASE = ("https://sentinel-cogs.s3.us-west-2.amazonaws.com/"
        "sentinel-s2-l2a-cogs/50/R/%s/%s/%s/%s")
BBOX = (115.85, 28.85, 116.45, 29.60)
BANDS = ["B03", "B08", "B11", "SCL"]
MAXDATES = 10
BUDGET = 2.0e9


def pick_dates():
    rows = list(csv.DictReader(open(os.path.join(F2, "data", "screen.csv"))))
    for r in rows:
        r["cmax"] = float(r["cloud_max_pct"])
        r["wm"] = float(r["water_mean_pct"])
    good = [r for r in rows if r["cmax"] < 25 and r["wm"] > 2]
    if len(good) < 6:
        good = [r for r in rows if r["cmax"] < 40 and r["wm"] > 1]
    good.sort(key=lambda r: -r["wm"])
    return [r["date"] for r in good[:MAXDATES]]


def main():
    inv = list(csv.DictReader(open(os.path.join(F2, "data", "s2_inventory.csv"))))
    by_date = {}
    for r in inv:
        by_date.setdefault(r["date"], []).append(r)
    dates = pick_dates()
    print("selected dates:", dates, flush=True)
    used = 0.0
    for d in dates:
        for r in by_date[d]:
            path = os.path.join(OUT, "%s_%s.npz" % (d, r["tile"]))
            if os.path.exists(path):
                used += os.path.getsize(path)
                continue
            if used > BUDGET:
                print("budget reached %.2f GB" % (used / 1e9), flush=True)
                return
            base = BASE % (r["tile"], r["year"], r["month"], r["scene"])
            try:
                with rasterio.open(base + "/B02.tif") as ds:
                    tb = transform_bounds("EPSG:4326", ds.crs, *BBOX)
                    win = from_bounds(*tb, transform=ds.transform).round_offsets()
                    win = win.round_lengths()
                    h, w = int(win.height // 2), int(win.width // 2)
                    if h < 50 or w < 50:
                        continue
                    cubes = {}
                    for b in BANDS:
                        with rasterio.open(base + "/%s.tif" % b) as bs:
                            cubes[b] = bs.read(1, window=win, out_shape=(h, w))
                    tr = ds.window_transform(win) * rasterio.Affine.scale(2, 2)
                    np.savez_compressed(path, transform=np.array(tr)[:6],
                                        crs=ds.crs.to_string(), **cubes)
            except Exception as exc:     # noqa: BLE001
                print("fail %s %s %s" % (d, r["tile"], exc), flush=True)
                continue
            size = os.path.getsize(path)
            used += size
            print("%s %s %.1f MB  total %.2f GB" % (d, r["tile"], size / 1e6, used / 1e9),
                  flush=True)


if __name__ == "__main__":
    main()
