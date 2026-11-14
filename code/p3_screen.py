# -*- coding: utf-8 -*-
"""Screen Poyang Lake S2 dates: cloud fraction and water fraction on overviews."""
import concurrent.futures as cf
import csv
import os

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.warp import transform_bounds
from rasterio.windows import from_bounds

F2 = os.path.expanduser("~/sy/F2")
BASE = ("https://sentinel-cogs.s3.us-west-2.amazonaws.com/"
        "sentinel-s2-l2a-cogs/50/R/%s/%s/%s/%s")
BBOX = (115.90, 28.90, 116.45, 29.60)
PIX = 512


def read(url, bounds, shape=None):
    with rasterio.open(url) as ds:
        tb = transform_bounds("EPSG:4326", ds.crs, *bounds)
        win = from_bounds(*tb, transform=ds.transform).round_offsets().round_lengths()
        win = rasterio.windows.Window(max(0, win.col_off), max(0, win.row_off),
                                      min(win.width, ds.width - win.col_off),
                                      min(win.height, ds.height - win.row_off))
        if shape is None:
            h = max(8, int(PIX * win.height / max(1, win.width)))
            shape = (h, PIX)
        return ds.read(1, window=win, out_shape=shape, resampling=Resampling.nearest)


def one(item):
    date, rows = item
    cl, wa = [], []
    for r in rows[:2]:
        b = BASE % (r["tile"], r["year"], r["month"], r["scene"])
        try:
            scl = read(b + "/SCL.tif", BBOX)
            g = read(b + "/B03.tif", BBOX, scl.shape).astype("float32")
            n = read(b + "/B08.tif", BBOX, scl.shape).astype("float32")
        except Exception:       # noqa: BLE001
            continue
        valid = (scl != 0) & (scl < 250)
        if valid.sum() < 50:
            continue
        cloud = np.isin(scl, [3, 8, 9, 10]) & valid
        ok = valid & ~cloud
        cl.append(100.0 * cloud.sum() / valid.sum())
        ndwi = (g - n) / (g + n + 1e-6)
        wa.append(100.0 * (ndwi[ok] > 0).sum() / max(ok.sum(), 1))
    if not cl:
        return None
    return (date, float(np.min(cl)), float(np.mean(wa)))


def main():
    rows = list(csv.DictReader(open(os.path.join(F2, "data", "s2_inventory.csv"))))
    rows = [r for r in rows if int(r["year"]) >= 2019]
    by = {}
    for r in rows:
        by.setdefault(r["date"], []).append(r)
    print("dates:", len(by), flush=True)
    out = []
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        for res in ex.map(one, sorted(by.items())):
            if res:
                out.append(res)
    out.sort(key=lambda x: x[0])
    with open(os.path.join(F2, "data", "poyang_screen.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "cloud_min_pct", "water_mean_pct"])
        w.writerows(out)
    good = [r for r in out if r[1] < 15]
    print("dates scanned:", len(out), " clear(<15%%):", len(good), flush=True)
    for r in sorted(good, key=lambda x: -x[2])[:12]:
        print("  %s cloud=%.1f%% water=%.1f%%" % r, flush=True)


if __name__ == "__main__":
    main()
