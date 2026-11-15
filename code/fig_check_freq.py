# -*- coding: utf-8 -*-
"""Check whether the white/grey patch inside the lake is NaN (no valid obs) or freq=0."""
import os

import numpy as np
import rasterio
from rasterio.warp import transform_bounds

F2 = os.path.expanduser("~/F2")
freq = np.load(os.path.join(F2, "runs", "poyang", "freq.npy"))
BBOX = (115.90, 28.90, 116.45, 29.60)
CRS = "EPSG:32650"
left, bottom, right, top = transform_bounds("EPSG:4326", CRS, *BBOX)
ny, nx = freq.shape
print("grid", freq.shape, "extent", left, right, bottom, top)


def rc(lon, lat):
    x, y = "", ""
    from rasterio.warp import transform
    xs, ys = transform("EPSG:4326", CRS, [lon], [lat])
    x, y = xs[0], ys[0]
    c = int((x - left) / (right - left) * nx)
    r = int((top - y) / (top - bottom) * ny)
    return r, c


def box_stats(lon0, lat0, lon1, lat1, tag):
    r0, c0 = rc(lon0, lat1)
    r1, c1 = rc(lon1, lat0)
    sub = freq[max(0, r0):r1, max(0, c0):c1]
    n = sub.size
    nan = int(np.isnan(sub).sum())
    zero = int((sub == 0).sum())
    print("%s: cells=%d, NaN=%d (%.1f%%), exact 0=%d (%.1f%%), valid mean=%.3f"
          % (tag, n, nan, 100 * nan / n, zero, 100 * zero / n,
             np.nanmean(sub) if nan < n else float("nan")))


box_stats(116.00, 29.30, 116.30, 29.45, "lake centre")
box_stats(116.10, 29.05, 116.25, 29.15, "south lake")
box_stats(115.95, 29.35, 116.10, 29.50, "west lake")
print("total NaN fraction: %.1f%%" % (100 * np.isnan(freq).mean()))
