# -*- coding: utf-8 -*-
"""Per-scene metrics, model cost and visual comparison panels."""
import glob
import json
import os
import random
import sys
import time

import numpy as np
import torch

sys.path.insert(0, os.path.expanduser("~/sy/F2/code"))
from model import UNet
from train_usgs import FloodDS, IGN, CHIP_DIR, OUT

F2 = os.path.expanduser("~/sy/F2")
FIG = os.path.join(F2, "out", "figs")
os.makedirs(FIG, exist_ok=True)


def scenes_split():
    scenes = sorted(os.path.basename(p).replace(".npz", "")
                    for p in glob.glob(os.path.join(CHIP_DIR, "*.npz")))
    rng = random.Random(42)
    order = scenes[:]
    rng.shuffle(order)
    return scenes, [order[i::5] for i in range(5)]


def load_model(tag, f, device):
    if tag in ("base", "std", "b4", "ndwi"):
        ch = 17 if tag == "ndwi" else (4 if tag == "b4" else 16)
        m = UNet(in_ch=ch, ds=(tag != "std"), se=False)
    elif tag == "unetpp":
        import segmentation_models_pytorch as smp
        m = smp.UnetPlusPlus("resnet34", encoder_weights=None, in_channels=16, classes=1)
    else:
        import segmentation_models_pytorch as smp
        m = smp.DeepLabV3Plus("resnet50", encoder_weights=None, in_channels=16, classes=1)
    p = os.path.join(OUT, "u_%s_f%d.pt" % (tag, f))
    m.load_state_dict(torch.load(p, map_location=device))
    return m.to(device).eval()


def per_scene(tags):
    scenes, parts = scenes_split()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    res = {}
    for tag in tags:
        chipdir = os.path.join(F2, "data", "chips17") if tag == "ndwi" else CHIP_DIR
        nb = 17 if tag == "ndwi" else (4 if tag == "b4" else 0)
        out = {}
        for f in range(5):
            if not os.path.exists(os.path.join(OUT, "u_%s_f%d.pt" % (tag, f))):
                continue
            m = load_model(tag, f, device)
            for s in parts[f]:
                ds = FloodDS([s], False, nb, chipdir)
                tp = fp = fn = 0
                with torch.no_grad():
                    for i in range(len(ds)):
                        x, y = ds[i]
                        pr = torch.sigmoid(m(x.unsqueeze(0).to(device))).squeeze().cpu() > 0.5
                        v = y != IGN
                        t = y == 1
                        tp += (pr & t & v).sum().item(); fp += (pr & ~t & v).sum().item()
                        fn += (~pr & t & v).sum().item()
                out[s.split("_S2")[0]] = 100 * tp / max(1, tp + fp + fn)
            del m
            torch.cuda.empty_cache()
        res[tag] = out
        print(tag, "scenes", len(out), "mean %.2f" % np.mean(list(out.values())), flush=True)
    json.dump(res, open(os.path.join(OUT, "per_scene.json"), "w"), indent=1)


def cost(tags):
    from thop import profile
    device = torch.device("cuda")
    out = {}
    for tag in tags:
        m = load_model(tag, 0, device)
        ch = 17 if tag == "ndwi" else 16
        x = torch.zeros(1, ch, 256, 256, device=device)
        macs, params = profile(m, inputs=(x,), verbose=False)
        with torch.no_grad():
            for _ in range(5):
                m(x)
            torch.cuda.synchronize()
            t0 = time.time()
            for _ in range(30):
                m(x)
            torch.cuda.synchronize()
        out[tag] = dict(params=params / 1e6, gflops=2 * macs / 1e9,
                        ms=1000 * (time.time() - t0) / 30)
        print("%-8s params=%.2f M  GFLOPs=%.2f  %.1f ms" % (
            tag, out[tag]["params"], out[tag]["gflops"], out[tag]["ms"]), flush=True)
        del m
        torch.cuda.empty_cache()
    json.dump(out, open(os.path.join(OUT, "cost.json"), "w"), indent=1)


def visual(tags=("base", "deeplab", "unetpp", "std")):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    fp = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
    if os.path.exists(fp):
        font_manager.fontManager.addfont(fp)
        plt.rcParams["font.family"] = font_manager.FontProperties(fname=fp).get_name()
    scenes, parts = scenes_split()
    device = torch.device("cuda")
    picks = []
    for f in range(5):
        for s in parts[f]:
            z = np.load(os.path.join(CHIP_DIR, s + ".npz"), mmap_mode="r")
            w = float((z["mask"] == 1).mean())
            if 0.08 < w < 0.45:
                picks.append((f, s))
    rng = random.Random(3)
    rng.shuffle(picks)
    picks = picks[:3]
    models = {}
    for t in tags:
        models[t] = {f: load_model(t, f, device) for f in {p[0] for p in picks}}
    fig, axes = plt.subplots(3, len(tags) + 2, figsize=(11.5, 6.6))
    for r, (f, s) in enumerate(picks):
        ds = FloodDS([s], False)
        zz = np.load(os.path.join(CHIP_DIR, s + ".npz"))
        fr = (zz["mask"] == 1).reshape(len(zz["mask"]), -1).mean(1)
        idx = int(np.argmin(np.abs(fr - 0.30)))
        x, y = ds[idx]
        img = x.numpy()
        rgb = np.stack([img[3], img[2], img[1]], -1)
        lo, hi = np.percentile(rgb, 2), np.percentile(rgb, 98)
        rgb = np.clip((rgb - lo) / (hi - lo + 1e-6), 0, 1)
        axes[r, 0].imshow(rgb); axes[r, 0].set_ylabel(s.split("_")[1], fontsize=8)
        gt = np.where(y.numpy() == 1, 1, 0)
        axes[r, 1].imshow(gt, cmap="Blues", vmin=0, vmax=1)
        for c, t in enumerate(tags, 2):
            with torch.no_grad():
                pr = torch.sigmoid(models[t][f](x.unsqueeze(0).to(device))).squeeze().cpu().numpy()
            axes[r, c].imshow(pr > 0.5, cmap="Blues", vmin=0, vmax=1, interpolation="nearest")
        for c in range(len(tags) + 2):
            axes[r, c].set_xticks([]); axes[r, c].set_yticks([])
    titles = ["影像", "真值"] + [t for t in tags]
    for c, t in enumerate(titles):
        axes[0, c].set_title(t, fontsize=9)
    fig.tight_layout(pad=0.4)
    fig.savefig(os.path.join(FIG, "fig_vis.png"), dpi=300)
    print("saved fig_vis", flush=True)


if __name__ == "__main__":
    what = sys.argv[1]
    if what == "scene":
        tags = sys.argv[2].split(",") if len(sys.argv) > 2 else ["base", "std", "b4", "unetpp", "deeplab"]
        per_scene(tags)
    elif what == "cost":
        cost(["base", "std", "unetpp", "deeplab"])
    else:
        visual()
