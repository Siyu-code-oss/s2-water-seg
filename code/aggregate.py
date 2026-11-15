# -*- coding: utf-8 -*-
"""Aggregate fold results into the paper's main table."""
import glob
import json
import os
import statistics as st

RUNS = os.path.expanduser("~/F2/runs")
TAGS = ["base", "std", "b4", "tta"]
NAME = {"base": "本文方法（轻量+16波段）", "std": "标准卷积（7.77 M）",
        "b4": "仅前4波段", "tta": "本文+TTA"}

rows = {}
for tag in TAGS:
    vals = []
    for f in range(5):
        p = os.path.join(RUNS, "f%d_%s.done" % (f, tag))
        if os.path.exists(p):
            vals.append(json.load(open(p))["best"])
    if vals:
        rows[tag] = vals

print("%-26s %s" % ("配置", "各折 IoU"))
for tag, vals in rows.items():
    m = st.mean(vals)
    s = st.stdev(vals) if len(vals) > 1 else 0
    print("%-26s %s   mean=%.2f sd=%.2f (n=%d)" % (
        NAME.get(tag, tag), " ".join("%.2f" % v for v in vals), m, s, len(vals)))

out = {t: {"folds": v, "mean": st.mean(v),
           "sd": st.stdev(v) if len(v) > 1 else 0} for t, v in rows.items()}
with open(os.path.join(RUNS, "summary.json"), "w") as f:
    json.dump(out, f, indent=1)
print("written", os.path.join(RUNS, "summary.json"))
