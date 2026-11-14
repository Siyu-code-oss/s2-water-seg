# -*- coding: utf-8 -*-
"""5-fold (by scene) training of the lightweight U-Net on the USGS subset."""
import argparse
import glob
import json
import os
import random

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset

import sys
sys.path.insert(0, os.path.expanduser("~/sy/F2/code"))
from model import UNet

F2 = os.path.expanduser("~/sy/F2")
CHIP_DIR = os.path.join(F2, "data", "chips2")
OUT = os.path.join(F2, "runs")
os.makedirs(OUT, exist_ok=True)
IGN = 255


class FloodDS(Dataset):
    def __init__(self, scenes, augment=False, nbands=0, chipdir=None):
        self.items = []
        self.nb = nbands or 0
        self.aug = augment
        self.dir = chipdir or CHIP_DIR
        self.cache = {}
        for s in scenes:
            z = np.load(os.path.join(self.dir, s + ".npz"))
            self.cache[s] = (z["img"], z["mask"])
            self.items += [(s, i) for i in range(len(z["img"]))]

    def __len__(self):
        return len(self.items)

    def __getitem__(self, k):
        s, i = self.items[k]
        img, msk = self.cache[s]
        x = img[i]
        if self.nb:
            x = x[:self.nb]
        x = x.astype(np.float32) / 10000.0
        y = msk[i].astype(np.int64)
        x = np.clip(x, 0, 1.5)
        if self.aug:
            if random.random() < 0.5:
                x = x[:, :, ::-1]
                y = y[:, ::-1]
            if random.random() < 0.5:
                x = x[:, ::-1, :]
                y = y[::-1, :]
            r = random.randint(0, 3)
            if r:
                x = np.rot90(x, r, (1, 2))
                y = np.rot90(y, r, (0, 1))
            if random.random() < 0.3:
                x = x * random.uniform(0.85, 1.15)
            if random.random() < 0.3:
                x = np.power(np.clip(x, 1e-4, None), random.uniform(0.85, 1.15))
        return torch.from_numpy(np.ascontiguousarray(x)), torch.from_numpy(np.ascontiguousarray(y))


def dice_loss(logit, target, valid):
    p = torch.sigmoid(logit)[valid]
    t = target[valid].float()
    inter = (p * t).sum()
    return 1 - (2 * inter + 1.0) / (p.sum() + t.sum() + 1.0)


def evaluate(model, loader, device):
    model.eval()
    tp = fp = fn = tn = 0
    with torch.no_grad():
        for x, y in loader:
            x = x.to(device)
            y = y.to(device)
            p = torch.sigmoid(model(x)).squeeze(1) > 0.5
            v = y != IGN
            t = y == 1
            tp += (p & t & v).sum().item()
            fp += (p & ~t & v).sum().item()
            fn += (~p & t & v).sum().item()
            tn += (~p & ~t & v).sum().item()
    iou = tp / max(1, tp + fp + fn)
    prec = tp / max(1, tp + fp)
    rec = tp / max(1, tp + fn)
    oa = (tp + tn) / max(1, tp + tn + fp + fn)
    f1 = 2 * prec * rec / max(1e-6, prec + rec)
    return dict(IoU=100 * iou, OA=100 * oa, P=100 * prec, R=100 * rec, F1=100 * f1)


def run_fold(fold, train_scenes, val_scenes, args, device, chipdir=None):
    tr = DataLoader(FloodDS(train_scenes, True, args.nbands, chipdir), batch_size=args.bs,
                    shuffle=True, num_workers=4, drop_last=True)
    va = DataLoader(FloodDS(val_scenes, False, args.nbands, chipdir), batch_size=8,
                    shuffle=False, num_workers=2)
    model = UNet(in_ch=args.nbands or args.ch, ds=bool(args.ds), se=False).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, args.epochs, eta_min=1e-5)
    best, best_ep = -1, -1
    hist = []
    for ep in range(args.epochs):
        model.train()
        tot = 0.0
        for x, y in tr:
            x, y = x.to(device), y.to(device)
            logit = model(x).squeeze(1)
            valid = y != IGN
            bce = F.binary_cross_entropy_with_logits(logit[valid], y[valid].float())
            loss = bce + 0.5 * dice_loss(logit, y, valid)
            opt.zero_grad()
            loss.backward()
            opt.step()
            tot += loss.item() * x.size(0)
        sched.step()
        m = evaluate(model, va, device)
        hist.append(m)
        print("fold%d ep%02d loss=%.3f IoU=%.2f F1=%.2f" % (
            fold, ep, tot / len(tr.dataset), m["IoU"], m["F1"]), flush=True)
        if m["IoU"] > best:
            best, best_ep = m["IoU"], ep
            torch.save(model.state_dict(), os.path.join(OUT, "u_%s_f%d.pt" % (args.tag, fold)))
        elif ep - best_ep >= args.patience:
            print("early stop", flush=True)
            break
    return dict(best=best, epoch=best_ep, hist=hist)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=60)
    ap.add_argument("--bs", type=int, default=8)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--patience", type=int, default=12)
    ap.add_argument("--ch", type=int, default=16)
    ap.add_argument("--ds", type=int, default=1, help="1=depthwise separable, 0=standard")
    ap.add_argument("--nbands", type=int, default=0, help="use first N bands (0=all)")
    ap.add_argument("--tag", default="base")
    ap.add_argument("--chipdir", default="")
    ap.add_argument("--folds", default="0,1,2,3,4")
    args = ap.parse_args()

    chipdir = args.chipdir or CHIP_DIR
    scenes = sorted(os.path.basename(p).replace(".npz", "")
                    for p in glob.glob(os.path.join(chipdir, "*.npz")))
    print("scenes:", len(scenes), flush=True)
    rng = random.Random(42)
    order = scenes[:]
    rng.shuffle(order)
    k = 5
    parts = [order[i::k] for i in range(k)]

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("device:", device, flush=True)
    res = {}
    for f in [int(x) for x in args.folds.split(",")]:
        done_path = os.path.join(OUT, "f%d_%s.done" % (f, args.tag))
        if os.path.exists(done_path):
            print("skip fold%d (%s) already done" % (f, args.tag), flush=True)
            continue
        val = parts[f]
        tr = [s for s in scenes if s not in val]
        out = run_fold(f, tr, val, args, device, chipdir)
        out["val_scenes"] = val
        res["fold%d" % f] = out
        with open(os.path.join(OUT, "cv_%s.json" % args.tag), "w") as fh:
            json.dump(res, fh, indent=1)
        with open(os.path.join(OUT, "f%d_%s.done" % (f, args.tag)), "w") as fh:
            json.dump(out, fh, indent=1)
    ious = [v["best"] for v in res.values()]
    print("CV IoU mean %.2f  folds %s" % (np.mean(ious), [round(x, 2) for x in ious]),
          flush=True)


if __name__ == "__main__":
    main()
