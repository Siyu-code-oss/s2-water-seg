# -*- coding: utf-8 -*-
"""External validation: USGS-trained models on the aligned WorldFloods events."""
import glob
import json
import os
import sys

import numpy as np
import torch

sys.path.insert(0, os.path.expanduser("~/sy/F2/code"))
from model import UNet
from train_usgs import IGN

F2 = os.path.expanduser("~/sy/F2")
EXT = os.path.join(F2, "data", "chips")      # WorldFloods chips (13 bands)
OUT = os.path.join(F2, "runs")


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    models = []
    for f in range(5):
        p = os.path.join(OUT, "u_base_f%d.pt" % f)
        if os.path.exists(p):
            m = UNet(in_ch=16, ds=True, se=False).to(device)
            m.load_state_dict(torch.load(p, map_location=device))
            m.eval()
            models.append(m)
    print("models", len(models), flush=True)

    res = {}
    for fp in sorted(glob.glob(os.path.join(EXT, "*.npz"))):
        z = np.load(fp)
        img = z["img"].astype("float32") / 10000.0
        msk = z["mask"]
        n, C, H, W = img.shape
        pad = np.zeros((n, 16, H, W), "float32")
        pad[:, :C] = np.clip(img, 0, 1.5)
        tp = fp_ = fn = 0
        with torch.no_grad():
            for i in range(n):
                x = torch.from_numpy(pad[i:i + 1]).to(device)
                pr = sum(torch.sigmoid(m(x)) for m in models) / len(models)
                p = pr.squeeze().cpu() > 0.5
                y = torch.from_numpy(msk[i]).long()
                v = y != IGN
                t = y == 1
                tp += (p & t & v).sum().item()
                fp_ += (p & ~t & v).sum().item()
                fn += (~p & t & v).sum().item()
        iou = 100 * tp / max(1, tp + fp_ + fn)
        res[os.path.basename(fp)[:40]] = dict(iou=iou, n=int(n))
        print("%-42s chips=%4d IoU=%.2f" % (os.path.basename(fp)[:42], n, iou), flush=True)

    mean = float(np.mean([v["iou"] for v in res.values()]))
    print("MEAN IoU over %d events: %.2f" % (len(res), mean), flush=True)
    json.dump(dict(events=res, mean=mean), open(os.path.join(OUT, "external.json"), "w"),
              indent=1)


if __name__ == "__main__":
    main()
