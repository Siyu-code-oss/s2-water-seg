# -*- coding: utf-8 -*-
"""Build the 1 km analysis table: flood frequency, land cover, terrain."""
import gzip
import json
import os
import shutil

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.warp import reproject, transform_bounds

F2 = os.path.expanduser(os.environ.get("F2_ROOT","~/F2"))
AUX = os.path.join(F2, "data", "aux")
OUT = os.path.join(F2, "runs", "p4")
os.makedirs(OUT, exist_ok=True)

CRS = "EPSG:32650"
BLK = 50          # 50 x 20 m = 1 km
BBOX = (115.90, 28.90, 116.45, 29.60)
WC_CLASSES = {10: "tree", 20: "shrub", 30: "grass", 40: "crop", 50: "built",
              60: "bare", 80: "water", 90: "wetland", 95: "mangrove"}
CN = {"tree": 60, "shrub": 65, "grass": 70, "crop": 78, "built": 92,
      "bare": 85, "water": 100, "wetland": 85, "mangrove": 80}


def main():
    freq = np.load(os.path.join(F2, "runs", "poyang", "freq.npy"))
    H, W = freq.shape
    left, bottom, right, top = transform_bounds("EPSG:4326", CRS, *BBOX)
    tr20 = rasterio.transform.from_origin(left, top, 20.0, 20.0)

    # land cover -> 20 m grid
    lc = np.zeros((H, W), "uint8")
    with rasterio.open(os.path.join(AUX, "landcover_n27.tif")) as ds:
        print("wc crs", ds.crs, "bounds", ds.bounds, "res", ds.res, flush=True)
        reproject(rasterio.band(ds, 1), lc, src_transform=ds.transform,
                  src_crs=ds.crs, dst_transform=tr20, dst_crs=CRS,
                  resampling=Resampling.nearest)
    print("landcover done", np.unique(lc)[:10], flush=True)

    # DEM -> 20 m grid
    hgt = []
    for n in ["N28E115", "N28E116", "N29E115", "N29E116"]:
        src = os.path.join(AUX, n + ".hgt.gz")
        dst = os.path.join(AUX, n + ".hgt")
        if not os.path.exists(dst):
            with gzip.open(src, "rb") as fi, open(dst, "wb") as fo:
                shutil.copyfileobj(fi, fo)
        hgt.append(dst)
    dem = np.full((H, W), np.nan, "float32")
    for p in hgt:
        try:
            with rasterio.open(p) as ds:
                tmp = np.full((H, W), np.nan, "float32")
                reproject(rasterio.band(ds, 1), tmp, dst_transform=tr20, dst_crs=CRS,
                          resampling=Resampling.bilinear, src_nodata=-32768,
                          dst_nodata=np.nan)
                dem = np.where(np.isnan(dem), tmp, dem)
        except Exception as exc:      # noqa: BLE001
            print("dem fail", p, exc, flush=True)
    print("dem done nan%%=%.1f" % (100 * np.isnan(dem).mean()), flush=True)

    gy, gx = H // BLK, W // BLK
    rows = []
    for i in range(gy):
        for j in range(gx):
            f = freq[i * BLK:(i + 1) * BLK, j * BLK:(j + 1) * BLK]
            ok = np.isfinite(f)
            if ok.mean() < 0.5:
                continue
            d = dem[i * BLK:(i + 1) * BLK, j * BLK:(j + 1) * BLK]
            l = lc[i * BLK:(i + 1) * BLK, j * BLK:(j + 1) * BLK]
            vals, cnts = np.unique(l, return_counts=True)
            frac = {WC_CLASSES[int(v)]: float(c) / l.size for v, c in zip(vals, cnts)
                    if int(v) in WC_CLASSES}
            if not frac:
                continue
            gx_m = left + (j + 0.5) * BLK * 20
            gy_m = top - (i + 0.5) * BLK * 20
            cn = sum(CN[k] * v for k, v in frac.items())
            rows.append(dict(
                i=i, j=j, x=gx_m, y=gy_m,
                freq=float(np.nanmean(f)),
                elev=float(np.nanmean(d)) if np.isfinite(d).any() else 0.0,
                slope=0.0, cn=cn,
                **{("f_" + k): frac.get(k, 0.0) for k in CN}))
    with open(os.path.join(OUT, "cells.json"), "w") as f:
        json.dump(rows, f)
    print("cells:", len(rows), flush=True)
    if rows:
        print("freq mean %.3f  cn mean %.1f" % (
            np.mean([r["freq"] for r in rows]), np.mean([r["cn"] for r in rows])),
            flush=True)


if __name__ == "__main__":
    main()
