# -*- coding: utf-8 -*-
"""Three-colour error maps: TP blue, FN orange, FP red, TN white."""
import os
import random
import sys

import numpy as np
import torch

sys.path.insert(0, os.path.expanduser("~/sy/F2/code"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Patch

from p6_eval import load_model, scenes_split
from train_usgs import FloodDS, IGN, CHIP_DIR

fp = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
if os.path.exists(fp):
    font_manager.fontManager.addfont(fp)
    plt.rcParams["font.family"] = font_manager.FontProperties(fname=fp).get_name()
plt.rcParams["axes.unicode_minus"] = False

FIG = os.path.expanduser("~/sy/F2/out/figs")
TP = np.array([0.18, 0.37, 0.55])
FN = np.array([0.91, 0.64, 0.24])
FP = np.array([0.75, 0.22, 0.17])
TN = np.array([1.0, 1.0, 1.0])
TAGS = [("base", "本文方法"), ("deeplab", "DeepLabV3+"),
        ("unetpp", "U-Net++"), ("std", "标准卷积")]


def colour(gt, pr, valid):
    out = np.ones((*gt.shape, 3))
    out[valid & (gt == 1) & pr] = TP
    out[valid & (gt == 1) & ~pr] = FN
    out[valid & (gt == 0) & pr] = FP
    return out


def main():
    scenes, parts = scenes_split()
    device = torch.device("cuda")
    rng = random.Random(7)
    picks = []
    for f in range(5):
        for s in parts[f]:
            z = np.load(os.path.join(CHIP_DIR, s + ".npz"))
            fr = (z["mask"] == 1).reshape(len(z["mask"]), -1).mean(1)
            sel = np.where((fr > 0.15) & (fr < 0.45))[0]
            if len(sel):
                picks.append((f, s, int(sel[0])))
    rng.shuffle(picks)
    picks = picks[:3]

    models = {}
    for _, _, _ in picks:
        pass
    for f in {p[0] for p in picks}:
        for t, _ in TAGS:
            models[(t, f)] = load_model(t, f, device)

    fig, axes = plt.subplots(3, 2 + len(TAGS), figsize=(11.6, 6.4))
    for r, (f, s, idx) in enumerate(picks):
        ds = FloodDS([s], False)
        x, y = ds[idx]
        img = x.numpy()
        rgb = np.stack([img[3], img[2], img[1]], -1)
        lo, hi = np.percentile(rgb, 2), np.percentile(rgb, 98)
        rgb = np.clip((rgb - lo) / (hi - lo + 1e-6), 0, 1)
        axes[r, 0].imshow(rgb)
        gt = y.numpy()
        valid = gt != IGN
        g = np.ones((*gt.shape, 3))
        g[valid & (gt == 1)] = TP
        axes[r, 1].imshow(g)
        for c, (t, _) in enumerate(TAGS, 2):
            with torch.no_grad():
                pr = torch.sigmoid(models[(t, f)](x.unsqueeze(0).to(device))).squeeze().cpu().numpy()
            axes[r, c].imshow(colour(gt, pr > 0.5, valid))
        for c in range(2 + len(TAGS)):
            axes[r, c].set_xticks([]); axes[r, c].set_yticks([])
    for c, name in enumerate(["影像", "真值"] + [n for _, n in TAGS]):
        axes[0, c].set_title(name, fontsize=9)
    handles = [Patch(fc=TP, label="判对"), Patch(fc=FN, label="漏分"),
               Patch(fc=FP, label="误分")]
    fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False, fontsize=9)
    fig.tight_layout(rect=(0, 0.05, 1, 1), pad=0.5)
    fig.savefig(os.path.join(FIG, "fig_vis.png"), dpi=300)
    print("saved fig_vis")


if __name__ == "__main__":
    main()
