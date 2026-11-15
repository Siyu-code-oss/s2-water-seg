# -*- coding: utf-8 -*-
"""Paired Wilcoxon test on per-scene IoU (base vs each baseline)."""
import json
import os

import numpy as np
from scipy.stats import wilcoxon

RUNS = r"D:\F2\runs"
d = json.load(open(os.path.join(RUNS, "per_scene.json")))
base = d["base"]
out = {}
for tag in ["std", "b4", "unetpp", "deeplab"]:
    if tag not in d:
        continue
    common = sorted(set(base) & set(d[tag]))
    a = np.array([base[k] for k in common])
    b = np.array([d[tag][k] for k in common])
    diff = a - b
    if np.allclose(diff, 0):
        out[tag] = dict(n=len(common), mean_diff=0.0, p=1.0)
        continue
    stat, p = wilcoxon(a, b)
    out[tag] = dict(n=len(common), mean_diff=float(diff.mean()), p=float(p))
    print("%-8s n=%d  mean diff=%+.2f pp  p=%.4f" % (tag, len(common), diff.mean(), p))
json.dump(out, open(os.path.join(RUNS, "significance.json"), "w"), indent=1)
print("saved")
