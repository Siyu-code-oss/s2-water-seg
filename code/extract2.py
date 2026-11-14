# -*- coding: utf-8 -*-
"""Extract an archive to a target folder (paths from env)."""
import collections
import os
import sys

import py7zr

SRC = os.path.expanduser(os.environ["SRC"])
DST = os.path.expanduser(os.environ["DST"])
os.makedirs(DST, exist_ok=True)
print("archive:", SRC, "%.2f GB" % (os.path.getsize(SRC) / 1e9), flush=True)
with py7zr.SevenZipFile(SRC, "r") as z:
    names = z.getnames()
    print("entries:", len(names), flush=True)
    for n in names[:10]:
        print("  ", n, flush=True)
    z.extractall(path=DST)
print("extracted to", DST, flush=True)

ext = collections.Counter()
size = collections.Counter()
for root, _, files in os.walk(DST):
    for f in files:
        p = os.path.join(root, f)
        e = os.path.splitext(f)[1].lower()
        ext[e] += 1
        size[e] += os.path.getsize(p)
for e, n in ext.most_common(8):
    print("  %-8s %6d files %9.1f MB" % (e, n, size[e] / 1e6), flush=True)
