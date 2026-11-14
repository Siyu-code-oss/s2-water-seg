# -*- coding: utf-8 -*-
"""Train two modern segmentation baselines (smp) with the same 5-fold split."""
import argparse
import glob
import json
import os
import random
import sys

import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader

import segmentation_models_pytorch as smp

sys.path.insert(0, os.path.expanduser("~/sy/F2/code"))
from train_usgs import FloodDS, IGN, CHIP_DIR, OUT, evaluate, dice_loss

F2 = os.path.expanduser("~/sy/F2")
ARCH = {
    "unetpp": lambda: smp.UnetPlusPlus("resnet34", encoder_weights=None,
                                       in_channels=16, classes=1),
    "deeplab": lambda: smp.DeepLabV3Plus("resnet50", encoder_weights=None,
                                         in_channels=16, classes=1),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arch", required=True)
    ap.add_argument("--folds", default="0")
    ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--bs", type=int, default=8)
    ap.add_argument("--lr", type=float, default=5e-4)
    args = ap.parse_args()

    scenes = sorted(os.path.basename(p).replace(".npz", "")
                    for p in glob.glob(os.path.join(CHIP_DIR, "*.npz")))
    rng = random.Random(42)
    order = scenes[:]
    rng.shuffle(order)
    parts = [order[i::5] for i in range(5)]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    for f in [int(x) for x in args.folds.split(",")]:
        done = os.path.join(OUT, "f%d_%s.done" % (f, args.arch))
        if os.path.exists(done):
            print("skip", f, args.arch, flush=True)
            continue
        val = parts[f]
        tr = [s for s in scenes if s not in val]
        dl_tr = DataLoader(FloodDS(tr, True), batch_size=args.bs, shuffle=True,
                           num_workers=4, drop_last=True)
        dl_va = DataLoader(FloodDS(val, False), batch_size=8, num_workers=2)
        model = ARCH[args.arch]().to(device)
        opt = torch.optim.Adam(model.parameters(), lr=args.lr)
        sch = torch.optim.lr_scheduler.CosineAnnealingLR(opt, args.epochs, 1e-5)
        best, best_ep = -1, -1
        for ep in range(args.epochs):
            model.train()
            for x, y in dl_tr:
                x, y = x.to(device), y.to(device)
                logit = model(x).squeeze(1)
                v = y != IGN
                loss = F.binary_cross_entropy_with_logits(logit[v], y[v].float()) \
                    + 0.5 * dice_loss(logit, y, v)
                opt.zero_grad()
                loss.backward()
                opt.step()
            sch.step()
            m = evaluate(model, dl_va, device)
            print("%s fold%d ep%02d IoU=%.2f F1=%.2f" % (
                args.arch, f, ep, m["IoU"], m["F1"]), flush=True)
            if m["IoU"] > best:
                best, best_ep = m["IoU"], ep
                torch.save(model.state_dict(),
                           os.path.join(OUT, "u_%s_f%d.pt" % (args.arch, f)))
            elif ep - best_ep >= 10:
                break
        with open(done, "w") as fh:
            json.dump(dict(best=best, epoch=best_ep), fh)
        print("%s fold%d best %.2f" % (args.arch, f, best), flush=True)


if __name__ == "__main__":
    main()
