# -*- coding: utf-8 -*-
"""P1.1 COG windowed-read verification ."""
import os
import time

os.environ.setdefault("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")
os.environ.setdefault("CPL_VSIL_CURL_ALLOWED_EXTENSIONS", ".tif")

import rasterio
from rasterio.windows import Window

BASE = ("https://sentinel-cogs.s3.us-west-2.amazonaws.com/"
        "sentinel-s2-l2a-cogs/50/R/KV/2020/7/S2A_50RKV_20200701_0_L2A")

for band in ("B04", "SCL"):
    url = "%s/%s.tif" % (BASE, band)
    t0 = time.time()
    with rasterio.open(url) as ds:
        print("%s: size=%s crs=%s res=%s blocks=%s" % (
            band, (ds.height, ds.width), ds.crs, ds.res, ds.block_shapes[0]))
        print("   bounds(WGS84):", ds.bounds)
        win = Window(ds.width // 2, ds.height // 2, 512, 512)
        arr = ds.read(1, window=win)
    print("   window read %s dtype=%s min=%s max=%s  %.1f s"
          % (arr.shape, arr.dtype, arr.min(), arr.max(), time.time() - t0))
