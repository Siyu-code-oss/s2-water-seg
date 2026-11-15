# -*- coding: utf-8 -*-
"""Extract src.7z and report what is inside."""
import collections
import os
import sys

import py7zr

F2 = os.path.expanduser(os.environ.get("F2_ROOT","~/F2"))
SRC = os.path.join(F2, "data", "src.7z")
DST = os.path.join(F2, "data", "src")

print("archive:", SRC, "%.2f GB" % (os.path.getsize(SRC) / 1e9))
with py7zr.SevenZipFile(SRC, "r") as z:
    names = z.getnames()
    print("entries:", len(names))
    for n in names[:20]:
        print("  ", n)
    z.extractall(path=DST)
print("extracted to", DST)

ext = collections.Counter()
size = collections.Counter()
for root, _, files in os.walk(DST):
    for f in files:
        p = os.path.join(root, f)
        e = os.path.splitext(f)[1].lower()
        ext[e] += 1
        try:
            size[e] += os.path.getsize(p)
        except OSError:
            pass
print("\nby extension:")
for e, n in ext.most_common():
    print("  %-10s %6d files  %8.1f MB" % (e, n, size[e] / 1e6))

# sample raster metadata
try:
    import rasterio
except ImportError:
    rasterio = None
sample = []
for root, _, files in os.walk(DST):
    for f in files:
        if f.lower().endswith((".tif", ".tiff")):
            sample.append(os.path.join(root, f))
    if len(sample) > 3:
        break
if rasterio and sample:
    print("\nsample rasters:")
    for p in sample[:3]:
        with rasterio.open(p) as ds:
            print("  %s  %s  %s  %s" % (os.path.relpath(p, DST), ds.shape,
                                        ds.dtypes[0], ds.crs))
