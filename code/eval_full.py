# -*- coding: utf-8 -*-
"""Evaluate saved fold weights and store full metrics (IoU/F1/OA/P/R)."""
import glob
import json
import os
import random
import sys

import numpy as np
import torch

sys.path.insert(0, os.path.expanduser("~/sy/F2/code"))
from model import UNet
from train_usgs import FloodDS, IGN, CHIP_DIR, OUT

TAG = sys.argv[1] if len(sys.argv) > 1 else "base"
CHIPDIR = sys.argv[2] if len(sys.argv) > 2 else CHIP_DIR
INCH = int(sys.argv[3]) if len(sys.argv) > 3 else 16


def main():
    scenes = sorted(os.path.basename(p).replace(".npz", "")
                    for p in glob.glob(os.path.join(CHIPDIR, "*.npz")))
    rng = random.Random(42)
    order = scenes[:]
    rng.shuffle(order)
    parts = [order[i::5] for i in range(5)]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    res = {}
    for f in range(5):
        wp = os.path.join(OUT, "u_%s_f%d.pt" % (TAG, f))
        if not os.path.exists(wp):
            continue
        m = UNet(in_ch=INCH, ds=True, se=False).to(device)
        m.load_state_dict(torch.load(wp, map_location=device))
        m.eval()
        ds = FloodDS(parts[f], False, chipdir=CHIPDIR)
        tp = fp = fn = tn = 0
        with torch.no_grad():
            for i in range(len(ds)):
                x, y = ds[i]
                p = torch.sigmoid(m(x.unsqueeze(0).to(device))).squeeze().cpu() > 0.5
                v = y != IGN
                t = y == 1
                tp += (p & t & v).sum().item()
                fp += (p & ~t & v).sum().item()
                fn += (~p & t & v).sum().item()
                tn += (~p & ~t & v).sum().item()
        iou = 100 * tp / max(1, tp + fp + fn)
        pre = 100 * tp / max(1, tp + fp)
        rec = 100 * tp / max(1, tp + fn)
        oa = 100 * (tp + tn) / max(1, tp + tn + fp + fn)
        f1 = 2 * pre * rec / max(1e-6, pre + rec)
        res["fold%d" % f] = dict(IoU=iou, F1=f1, OA=oa, P=pre, R=rec)
        print("fold%d IoU=%.2f F1=%.2f OA=%.2f P=%.2f R=%.2f" % (f, iou, f1, oa, pre, rec),
              flush=True)
    with open(os.path.join(OUT, "metrics_%s.json" % TAG), "w") as fh:
        json.dump(res, fh, indent=1)


if __name__ == "__main__":
    main()
