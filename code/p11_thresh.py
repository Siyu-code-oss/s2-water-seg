# -*- coding: utf-8 -*-
"""NDWI / MNDWI + Otsu baselines on the same scene-wise folds."""
import glob
import json
import os
import random
import sys

import numpy as np
from skimage.filters import threshold_otsu

sys.path.insert(0, os.path.expanduser("~/sy/F2/code"))
from train_usgs import CHIP_DIR, OUT, IGN

B = {"B1": 0, "B2": 1, "B3": 2, "B4": 3, "B5": 4, "B6": 5, "B7": 6, "B8": 7,
     "B8A": 8, "B9": 9, "B10": 10, "B11": 11, "B12": 12}


def idx(n, t):
    ok = (t == 1)
    return ok, (t == IGN)


def main():
    scenes = sorted(os.path.basename(p).replace(".npz", "")
                    for p in glob.glob(os.path.join(CHIP_DIR, "*.npz")))
    rng = random.Random(42)
    order = scenes[:]
    rng.shuffle(order)
    parts = [order[i::5] for i in range(5)]
    res = {}
    for name, f in [("NDWI", lambda g, n, s: (g - n) / (g + n + 1e-6)),
                    ("MNDWI", lambda g, n, s: (g - s) / (g + s + 1e-6))]:
        ious = []
        for k in range(5):
            # threshold chosen on the first half of the fold's scenes, applied to the rest
            tr, te = parts[k][::2], parts[k][1::2]
            vals = []
            for s in tr:
                z = np.load(os.path.join(CHIP_DIR, s + ".npz"), mmap_mode="r")
                img = z["img"].astype("float32")
                g = img[:, B["B3"]] / 1e4; n = img[:, B["B8"]] / 1e4
                s11 = img[:, B["B11"]] / 1e4
                vals.append(f(g, n, s11).ravel())
            thr = 0.0 if os.environ.get('FIXED0') else threshold_otsu(np.concatenate(vals[:8]))
            tp = fp = fn = 0
            for s in te:
                z = np.load(os.path.join(CHIP_DIR, s + ".npz"), mmap_mode="r")
                img = z["img"].astype("float32")
                msk = z["mask"]
                g = img[:, B["B3"]] / 1e4; n = img[:, B["B8"]] / 1e4
                s11 = img[:, B["B11"]] / 1e4
                v = f(g, n, s11) > thr
                ok = msk == 1
                bad = msk == IGN
                tp += (v & ok & ~bad).sum(); fp += (v & ~ok & ~bad).sum()
                fn += (~v & ok & ~bad).sum()
            ious.append(100 * tp / max(1, tp + fp + fn))
            print("%s fold%d thr=%.3f IoU=%.2f" % (name, k, thr, ious[-1]), flush=True)
        res[name] = dict(folds=ious, mean=float(np.mean(ious)))
    name_out = "threshold_fixed.json" if os.environ.get("FIXED0") else "threshold_baselines.json"
    json.dump(res, open(os.path.join(OUT, name_out), "w"), indent=1)
    print("NDWI mean %.2f  MNDWI mean %.2f" % (res["NDWI"]["mean"], res["MNDWI"]["mean"]))


if __name__ == "__main__":
    main()
