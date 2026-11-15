# -*- coding: utf-8 -*-
"""Per-scene IoU for the RGB+NIR (B2/B3/B4/B8) model, one fold per run."""
import glob
import json
import os
import random
import sys

import torch

sys.path.insert(0, os.path.expanduser("~/sy/F2/code"))
from model import UNet
from train_usgs import FloodDS, IGN, CHIP_DIR, OUT

BANDS = [1, 2, 3, 7]          # B2, B3, B4, B8


def main():
    f = int(sys.argv[1])
    rng = random.Random(42)
    scenes = sorted(os.path.basename(p).replace(".npz", "")
                    for p in glob.glob(os.path.join(CHIP_DIR, "*.npz")))
    order = scenes[:]
    rng.shuffle(order)
    val = order[f::5]
    m = UNet(in_ch=4, ds=True).cuda()
    m.load_state_dict(torch.load(os.path.join(OUT, "u_rgbnir_f%d.pt" % f),
                                 map_location="cuda"))
    m.eval()
    res = {}
    for s in val:
        ds = FloodDS([s], False, 0, CHIP_DIR, BANDS)
        tp = fp = fn = 0
        with torch.no_grad():
            for i in range(len(ds)):
                x, y = ds[i]
                p = torch.sigmoid(m(x.unsqueeze(0).cuda())).squeeze().cpu() > 0.5
                v = y != IGN
                t = y == 1
                tp += (p & t & v).sum().item()
                fp += (p & ~t & v).sum().item()
                fn += (~p & t & v).sum().item()
        res[s.split("_S2")[0]] = 100 * tp / max(1, tp + fp + fn)
    json.dump(res, open(os.path.join(OUT, "per_scene_rgbnir_f%d.json" % f), "w"))
    print("fold", f, "scenes", len(res))


if __name__ == "__main__":
    main()
