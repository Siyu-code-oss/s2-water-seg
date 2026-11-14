# -*- coding: utf-8 -*-
"""Summarize extracted chips: per-event counts, raster shapes, label values."""
import collections
import os

import numpy as np
import rasterio

F2 = os.path.expanduser("~/sy/F2")
SRC = os.path.join(F2, "data", "src")

files = []
for root, _, fs in os.walk(SRC):
    for f in fs:
        if f.lower().endswith(".tif"):
            files.append(os.path.join(root, f))
print("tif files:", len(files))

kinds = collections.Counter()
events = collections.defaultdict(set)
for p in files:
    n = os.path.basename(p)
    for k in ("_S2.tif", "_S1.tif", "_CLASS.tif", "_NDWI.tif"):
        if n.endswith(k):
            kinds[k] += 1
            events[n[:-len(k)]].add(k)
print("kinds:", dict(kinds))
print("events:", len(events),
      "with S2:", sum(1 for v in events.values() if "_S2.tif" in v))

for k in ("_CLASS.tif", "_S2.tif", "_S1.tif"):
    p = next((f for f in files if f.endswith(k)), None)
    if not p:
        continue
    with rasterio.open(p) as ds:
        a = ds.read()
        print("%-12s %s bands=%d dtype=%s min=%s max=%s res=%s" % (
            k, ds.shape, ds.count, ds.dtypes[0], a.min(), a.max(), ds.res))
        if k == "_CLASS.tif":
            u, c = np.unique(a, return_counts=True)
            print("   class values:", dict(zip(u.tolist(), c.tolist())))
