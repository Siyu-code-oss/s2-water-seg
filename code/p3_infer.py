# -*- coding: utf-8 -*-
"""Run the 5 trained models over the Poyang stacks and build a flood-frequency map."""
import glob
import json
import os
import sys

import numpy as np
import torch

sys.path.insert(0, os.path.expanduser("~/sy/F2/code"))
from model import UNet

F2 = os.path.expanduser("~/sy/F2")
SRC = os.path.join(F2, "data", "poyang")
OUT = os.path.join(F2, "runs", "poyang")
os.makedirs(OUT, exist_ok=True)
TILE = 256
CLOUD = {3, 8, 9, 10}


def load_models(device):
    ms = []
    for f in range(5):
        p = os.path.join(F2, "runs", "u_base_f%d.pt" % f)
        if os.path.exists(p):
            m = UNet(in_ch=16, ds=True, se=False).to(device)
            m.load_state_dict(torch.load(p, map_location=device))
            m.eval()
            ms.append(m)
    return ms


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    models = load_models(device)
    print("models:", len(models), flush=True)
    files = sorted(glob.glob(os.path.join(SRC, "*.npz")))
    print("dates:", [os.path.basename(f)[:8] for f in files], flush=True)

    acc = None
    cnt = None
    report = {}
    for fp in files:
        d = np.load(fp)
        img = d["img"].astype(np.float32) / 10000.0
        scl = d["scl"]
        img = np.clip(img, 0, 1.5)
        _, H, W = img.shape
        prob = np.zeros((H, W), "float32")
        with torch.no_grad():
            for y in range(0, H, TILE):
                for x in range(0, W, TILE):
                    h = min(TILE, H - y)
                    w = min(TILE, W - x)
                    if h < 32 or w < 32:
                        continue
                    patch = np.zeros((1, 16, TILE, TILE), "float32")
                    patch[0, :, :h, :w] = img[:, y:y + h, x:x + w]
                    t = torch.from_numpy(patch).to(device)
                    p = 0
                    for m in models:
                        p = p + torch.sigmoid(m(t))
                    prob[y:y + h, x:x + w] = (p / len(models))[0, 0, :h, :w].cpu().numpy()
        water = (prob > 0.5)
        valid = (scl != 0) & (~np.isin(scl, list(CLOUD)))
        report[os.path.basename(fp)[:8]] = {
            "water_pct": 100 * float(water[valid].mean()) if valid.any() else 0.0,
            "valid_pct": 100 * float(valid.mean())}
        if acc is None:
            acc = np.zeros((H, W), "float32")
            cnt = np.zeros((H, W), "float32")
        acc += water.astype("float32") * valid
        cnt += valid.astype("float32")
        np.save(os.path.join(OUT, "mask_%s.npy" % os.path.basename(fp)[:8]), water)
        print("ok %s water=%.2f%% valid=%.1f%%" % (
            os.path.basename(fp)[:8], report[os.path.basename(fp)[:8]]["water_pct"],
            100 * float(valid.mean())), flush=True)

    freq = np.where(cnt > 0, acc / np.maximum(cnt, 1), np.nan)
    np.save(os.path.join(OUT, "freq.npy"), freq)
    with open(os.path.join(OUT, "report.json"), "w") as f:
        json.dump(report, f, indent=1)
    ok = np.isfinite(freq)
    print("frequency map: mean=%.3f  >0.5 area=%.1f%%" % (
        float(np.nanmean(freq[ok])), 100 * float((freq[ok] > 0.5).mean())), flush=True)


if __name__ == "__main__":
    main()
