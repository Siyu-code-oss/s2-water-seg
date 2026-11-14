# -*- coding: utf-8 -*-
"""Fetch S2 stacks over Poyang Lake (20 m, common grid), bands in parallel."""
import csv
import os
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import rasterio
from rasterio.warp import Resampling, reproject, transform_bounds
from rasterio.windows import from_bounds

F2 = os.path.expanduser("~/sy/F2")
OUT = os.path.join(F2, "data", "poyang")
os.makedirs(OUT, exist_ok=True)
BASE = ("https://sentinel-cogs.s3.us-west-2.amazonaws.com/"
        "sentinel-s2-l2a-cogs/50/R/%s/%s/%s/%s")
BBOX = (115.90, 28.90, 116.45, 29.60)
BANDS = ["B01", "B02", "B03", "B04", "B05", "B06", "B07", "B08", "B8A",
         "B09", "B10", "B11", "B12"]
CRS = "EPSG:32650"
RES = 20.0
MAX_DATES = 6
WORKERS = 8

left, bottom, right, top = transform_bounds("EPSG:4326", CRS, *BBOX)
W = int((right - left) / RES)
H = int((top - bottom) / RES)
TR = rasterio.transform.from_origin(left, top, RES, RES)


def read_grid(url, dtype):
    with rasterio.open(url) as ds:
        win = from_bounds(left, bottom, right, top, transform=ds.transform)
        win = win.round_offsets().round_lengths()
        h = max(1, int(win.height * ds.res[0] / RES))
        w = max(1, int(win.width * ds.res[1] / RES))
        arr = ds.read(1, window=win, out_shape=(h, w))
        src_tr = ds.window_transform(win) * rasterio.Affine.scale(
            win.width / w, win.height / h)
        tmp = np.zeros((H, W), dtype)
        reproject(arr, tmp, src_transform=src_tr, src_crs=ds.crs,
                  dst_transform=TR, dst_crs=CRS, resampling=Resampling.nearest)
        return tmp


def grab(job):
    date, tiles, i, b = job
    out = np.zeros((H, W), "uint16")
    for r in tiles:
        url = (BASE % (r["tile"], r["year"], r["month"], r["scene"])) + "/%s.tif" % b
        try:
            a = read_grid(url, "uint16")
            out = np.where(a > 0, a, out)
        except Exception:      # noqa: BLE001
            continue
    return i, out


def select_dates():
    rows = [r for r in csv.DictReader(open(os.path.join(F2, "data", "poyang_screen.csv")))
            if float(r["cloud_min_pct"]) < 10]
    rows.sort(key=lambda r: (r["date"][:4], -float(r["water_mean_pct"])))
    seen, out = {}, []
    for r in rows:
        y = r["date"][:4]
        if seen.get(y, 0) >= 1:
            continue
        seen[y] = seen.get(y, 0) + 1
        out.append(r["date"])
    return out[:MAX_DATES]


def main():
    print("grid %dx%d" % (H, W), flush=True)
    inv = list(csv.DictReader(open(os.path.join(F2, "data", "s2_inventory.csv"))))
    by = {}
    for r in inv:
        by.setdefault(r["date"], []).append(r)
    dates = select_dates()
    print("dates:", dates, flush=True)
    for date in dates:
        dst = os.path.join(OUT, "%s.npz" % date)
        if os.path.exists(dst):
            print("skip", date, flush=True)
            continue
        tiles = by[date][:2]
        stack = np.zeros((16, H, W), "uint16")
        jobs = [(date, tiles, i, b) for i, b in enumerate(BANDS)]
        with ThreadPoolExecutor(max_workers=WORKERS) as ex:
            for i, arr in ex.map(grab, jobs):
                stack[i] = arr
        try:
            scl = np.zeros((H, W), "uint8")
            for r in tiles:
                url = (BASE % (r["tile"], r["year"], r["month"],
                               r["scene"])) + "/SCL.tif"
                a = read_grid(url, "uint8")
                scl = np.where(a > 0, a, scl)
        except Exception:      # noqa: BLE001
            scl = np.zeros((H, W), "uint8")
        np.savez_compressed(dst, img=stack, scl=scl)
        print("ok %s %.1f MB valid=%.1f%%" % (
            date, os.path.getsize(dst) / 1e6, 100 * float((stack[3] > 0).mean())),
            flush=True)


if __name__ == "__main__":
    main()
