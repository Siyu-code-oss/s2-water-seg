# -*- coding: utf-8 -*-
"""Permanent-water vs ESA WorldCover water class agreement."""
import os

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.warp import reproject, transform_bounds

F2 = os.path.expanduser(os.environ.get("F2_ROOT","~/F2"))
freq = np.load(os.path.join(F2, "runs", "poyang", "freq.npy"))
H, W = freq.shape
BBOX = (115.90, 28.90, 116.45, 29.60)
CRS = "EPSG:32650"
left, bottom, right, top = transform_bounds("EPSG:4326", CRS, *BBOX)
tr = rasterio.transform.from_origin(left, top, (right - left) / W, (top - bottom) / H)

wc = np.zeros((H, W), "uint8")
with rasterio.open(os.path.join(F2, "data", "aux", "landcover_n27.tif")) as ds:
    reproject(rasterio.band(ds, 1), wc, src_transform=ds.transform, src_crs=ds.crs,
              dst_transform=tr, dst_crs=CRS, resampling=Resampling.nearest)

valid = np.isfinite(freq) & (wc > 0)
perm = valid & (freq >= 0.9)
wcw = valid & (wc == 80)

tp = int((perm & wcw).sum())
fp = int((perm & ~wcw).sum())
fn = int((~perm & wcw).sum())
tn = int((valid & ~perm & ~wcw).sum())
prec = 100 * tp / max(1, tp + fp)
rec = 100 * tp / max(1, tp + fn)
iou = 100 * tp / max(1, tp + fp + fn)
print("valid px %d  ours=%d  wc=%d" % (valid.sum(), perm.sum(), wcw.sum()))
print("precision %.1f%%  recall %.1f%%  IoU %.1f%%" % (prec, rec, iou))
