# -*- coding: utf-8 -*-
"""Minimal inference demo: one scene -> water mask (CPU or GPU)."""
import numpy as np, torch, sys
from model import UNet

ckpt, npy = sys.argv[1], sys.argv[2]      # weights, scene .npz (img 16xHxW)
z = np.load(npy)
img = torch.from_numpy(z["img"].astype("float32") / 10000.0)[None].clamp(0, 1.5)
m = UNet(in_ch=16, ds=True)
m.load_state_dict(torch.load(ckpt, map_location="cpu"))
m.eval()
with torch.no_grad():
    prob = torch.sigmoid(m(img))[0, 0].numpy()
mask = (prob > 0.5).astype("uint8")
np.save("mask.npy", mask)
print("water fraction %.2f%%" % (100 * mask.mean()))
