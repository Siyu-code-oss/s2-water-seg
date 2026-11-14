# -*- coding: utf-8 -*-
"""Evaluate the trained folds with 8-way flip/rotation test-time augmentation."""
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

F2 = os.path.expanduser("~/sy/F2")


def transforms():
    for k in range(4):
        for flip in (False, True):
            yield k, flip


def apply(x, k, flip):
    x = torch.rot90(x, k, (2, 3))
    if flip:
        x = torch.flip(x, (3,))
    return x


def undo(p, k, flip):
    if flip:
        p = torch.flip(p, (3,))
    return torch.rot90(p, -k, (2, 3))


def main():
    scenes = sorted(os.path.basename(p).replace(".npz", "")
                    for p in glob.glob(os.path.join(CHIP_DIR, "*.npz")))
    rng = random.Random(42)
    order = scenes[:]
    rng.shuffle(order)
    parts = [order[i::5] for i in range(5)]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    for f in range(5):
        wp = os.path.join(OUT, "u_base_f%d.pt" % f)
        if not os.path.exists(wp):
            print("no weights", f, flush=True)
            continue
        model = UNet(in_ch=16, ds=True, se=False).to(device)
        model.load_state_dict(torch.load(wp, map_location=device))
        model.eval()
        ds = FloodDS(parts[f], False)
        tp = fp = fn = tn = 0
        with torch.no_grad():
            for i in range(len(ds)):
                x, y = ds[i]
                x = x.unsqueeze(0).to(device)
                y = y.to(device)
                acc = 0
                for k, flip in transforms():
                    xt = apply(x, k, flip)
                    p = torch.sigmoid(model(xt))
                    acc = acc + undo(p, k, flip)
                p = (acc / 8).squeeze(1).squeeze(0) > 0.5
                v = y != IGN
                t = y == 1
                tp += (p & t & v).sum().item()
                fp += (p & ~t & v).sum().item()
                fn += (~p & t & v).sum().item()
                tn += (~p & ~t & v).sum().item()
        iou = 100 * tp / max(1, tp + fp + fn)
        rec = 100 * tp / max(1, tp + fn)
        pre = 100 * tp / max(1, tp + fp)
        oa = 100 * (tp + tn) / max(1, tp + tn + fp + fn)
        f1 = 2 * pre * rec / max(1e-6, pre + rec)
        print("fold%d TTA IoU=%.2f F1=%.2f OA=%.2f P=%.2f R=%.2f" % (
            f, iou, f1, oa, pre, rec), flush=True)
        with open(os.path.join(OUT, "f%d_tta.done" % f), "w") as fh:
            json.dump(dict(best=iou, F1=f1, OA=oa, P=pre, R=rec), fh)


if __name__ == "__main__":
    main()
