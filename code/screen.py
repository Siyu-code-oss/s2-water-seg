# -*- coding: utf-8 -*-
"""Coarse screening of S2 dates: cloud fraction and water fraction on overviews."""
import concurrent.futures as cf
import csv
import os
import time

import numpy as np
import rasterio
from rasterio.warp import transform_bounds

F2 = os.path.expanduser(os.environ.get("F2_ROOT","~/F2"))
BASE = ("https://sentinel-cogs.s3.us-west-2.amazonaws.com/"
        "sentinel-s2-l2a-cogs/50/R/%s/%d/%d/%s")
BBOX = (115.90, 28.80, 116.70, 29.80)   # lon0, lat0, lon1, lat1
PIX = 384                                # decimated read size


def load():
    rows = list(csv.DictReader(open(os.path.join(F2, "data", "s2_inventory.csv"))))
    by_date = {}
    for r in rows:
        by_date.setdefault(r["date"], []).append(r)
    return by_date


def read_overview(url, bounds):
    with rasterio.open(url) as ds:
        tb = transform_bounds("EPSG:4326", ds.crs, *bounds)
        win = rasterio.windows.from_bounds(*tb, transform=ds.transform)
        win = win.round_offsets().round_lengths()
        win = rasterio.windows.Window(
            max(0, win.col_off), max(0, win.row_off),
            min(win.width, ds.width - win.col_off),
            min(win.height, ds.height - win.row_off))
        h = max(8, int(PIX * win.height / max(win.width, 1)))
        return ds.read(1, window=win, out_shape=(h, PIX))


def one(item):
    date, rows = item
    clouds, waters, used = [], [], 0
    for r in rows:
        url = BASE % (r["tile"], int(r["year"]), int(r["month"]), r["scene"])
        try:
            scl = read_overview(url + "/SCL.tif", BBOX)
            b03 = read_overview(url + "/B03.tif", BBOX).astype("float32")
            b08 = read_overview(url + "/B08.tif", BBOX).astype("float32")
        except Exception as exc:      # noqa: BLE001
            continue
        valid = (scl != 0) & (scl < 250)
        if valid.sum() < 50:
            continue
        cloud = np.isin(scl, [3, 8, 9, 10]) & valid
        clouds.append(100.0 * cloud.sum() / valid.sum())
        ok = valid & ~cloud
        ndwi = (b03 - b08) / (b03 + b08 + 1e-6)
        waters.append(100.0 * (ndwi[ok] > 0).sum() / max(ok.sum(), 1))
        used += 1
    if not used:
        return None
    return (date, used, float(np.mean(clouds)), float(np.max(clouds)),
            float(np.mean(waters)))


def main():
    by_date = load()
    print("dates:", len(by_date), flush=True)
    out = []
    t0 = time.time()
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        for i, res in enumerate(ex.map(one, sorted(by_date.items())), 1):
            if res:
                out.append(res)
            if i % 20 == 0:
                print("  %d/%d  %.1f min" % (i, len(by_date), (time.time() - t0) / 60),
                      flush=True)
    with open(os.path.join(F2, "data", "screen.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "tiles", "cloud_mean_pct", "cloud_max_pct", "water_mean_pct"])
        w.writerows(out)
    print("wrote screen.csv rows=", len(out), flush=True)
    good = [r for r in out if r[3] < 20 and r[4] > 3]
    print("candidates (cloud<20%% and water>3%%):", len(good), flush=True)
    for r in sorted(good, key=lambda x: -x[4])[:15]:
        print("  %s tiles=%d cloud=%.1f%% water=%.1f%%" % (r[0], r[1], r[3], r[4]),
              flush=True)


if __name__ == "__main__":
    main()
