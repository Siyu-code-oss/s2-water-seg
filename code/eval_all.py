# -*- coding: utf-8 -*-
"""Full metrics (IoU/F1/OA/P/R) for every trained configuration, one fold per run."""
import argparse
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
CHIPS17 = os.path.join(F2, "data", "chips17")
ARCH = ["base", "std", "b4", "ndwi", "unetpp", "deeplab", "segformer"]


def build(tag):
    if tag == "base":
        return UNet(in_ch=16, ds=True), None, CHIP_DIR
    if tag == "std":
        return UNet(in_ch=16, ds=False), None, CHIP_DIR
    if tag == "b4":
        return UNet(in_ch=4, ds=True), 4, CHIP_DIR
    if tag == "ndwi":
        return UNet(in_ch=17, ds=True), None, CHIPS17
    import segmentation_models_pytorch as smp
    if tag == "unetpp":
        return smp.UnetPlusPlus("resnet34", encoder_weights=None, in_channels=16,
                                classes=1), None, CHIP_DIR
    if tag == "deeplab":
        return smp.DeepLabV3Plus("resnet50", encoder_weights=None, in_channels=16,
                                 classes=1), None, CHIP_DIR
    return smp.Unet("mit_b0", encoder_weights=None, in_channels=16, classes=1), None, CHIP_DIR


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fold", type=int, required=True)
    f = ap.parse_args().fold
    scenes = sorted(os.path.basename(p).replace(".npz", "")
                    for p in glob.glob(os.path.join(CHIP_DIR, "*.npz")))
    rng = random.Random(42)
    order = scenes[:]
    rng.shuffle(order)
    val = order[f::5]
    device = torch.device("cuda")
    res = {}
    for tag in ARCH:
        wp = os.path.join(OUT, "u_%s_f%d.pt" % (tag, f))
        if not os.path.exists(wp):
            continue
        m, nb, cdir = build(tag)
        m.load_state_dict(torch.load(wp, map_location=device))
        m.eval().to(device)
        ds = FloodDS(val, False, nb or 0, cdir)
        tp = fp = fn = tn = 0
        with torch.no_grad():
            for i in range(len(ds)):
                x, y = ds[i]
                p = torch.sigmoid(m(x.unsqueeze(0).to(device))).squeeze().cpu() > 0.5
                v = y != IGN
                t = y == 1
                tp += (p & t & v).sum().item(); fp += (p & ~t & v).sum().item()
                fn += (~p & t & v).sum().item(); tn += (~p & ~t & v).sum().item()
        iou = 100 * tp / max(1, tp + fp + fn)
        pre = 100 * tp / max(1, tp + fp); rec = 100 * tp / max(1, tp + fn)
        oa = 100 * (tp + tn) / max(1, tp + tn + fp + fn)
        f1 = 2 * pre * rec / max(1e-6, pre + rec)
        res[tag] = dict(IoU=iou, F1=f1, OA=oa, P=pre, R=rec)
        print("fold%d %-9s IoU=%.2f F1=%.2f OA=%.2f P=%.2f R=%.2f" % (
            f, tag, iou, f1, oa, pre, rec), flush=True)
        del m
        torch.cuda.empty_cache()
    json.dump(res, open(os.path.join(OUT, "metrics_all_f%d.json" % f), "w"), indent=1)


if __name__ == "__main__":
    main()
