# -*- coding: utf-8 -*-
"""Same tiling as build_chips2 but appends the NDWI band (17 channels)."""
import json
import os
import re

import numpy as np
import rasterio

F2 = os.path.expanduser("~/sy/F2")
SRC = os.path.join(F2, "data", "usgs", "usgs")
OUT = os.path.join(F2, "data", "chips17")
os.makedirs(OUT, exist_ok=True)
SIZE, STRIDE, VALID_MIN = 256, 128, 0.5


def main():
    files = [f for f in os.listdir(SRC) if f.endswith(".tif")]
    cls, ndwi, scenes = {}, {}, []
    for f in files:
        m = re.match(r"(usgs_wv2_\d+)", f)
        if not m:
            continue
        k = m.group(1)
        if f.endswith("_CLASS.tif"):
            cls[k] = os.path.join(SRC, f)
        elif f.endswith("_NDWI.tif"):
            ndwi[f[:-9]] = os.path.join(SRC, f)
        elif f.endswith("_S2.tif"):
            scenes.append((k, f, os.path.join(SRC, f)))
    print("scenes", len(scenes), "ndwi", len(ndwi), flush=True)

    summary = {}
    for k, fn, p in sorted(scenes):
        stem = fn[:-len("_S2.tif")]
        if k not in cls or stem not in ndwi:
            print("skip no ndwi", k, flush=True)
            continue
        dst = os.path.join(OUT, fn.replace(".tif", ".npz"))
        if os.path.exists(dst):
            continue
        try:
            with rasterio.open(p) as ds:
                img = ds.read()
            with rasterio.open(cls[k]) as ds:
                c = ds.read(1)
            with rasterio.open(ndwi[stem]) as ds:
                nw = ds.read(1).astype("float32")
        except Exception as exc:       # noqa: BLE001
            print("fail", k, exc, flush=True)
            continue
        if img.shape[1:] != c.shape:
            print("shape skip", k, img.shape, c.shape, flush=True)
            continue
        if nw.shape != c.shape:
            print("ndwi shape mismatch, filling zeros", k, flush=True)
            nw = np.zeros(c.shape, "float32")
        lab = np.full(c.shape, 255, "uint8")
        lab[c == 0] = 0
        lab[c == 1] = 1
        C, H, W = img.shape
        imgs, masks = [], []
        for y in range(0, H - SIZE + 1, STRIDE):
            for x in range(0, W - SIZE + 1, STRIDE):
                m = lab[y:y + SIZE, x:x + SIZE]
                if (m != 255).mean() < VALID_MIN:
                    continue
                patch = np.zeros((17, SIZE, SIZE), "int16")
                patch[:C] = img[:, y:y + SIZE, x:x + SIZE].astype("int16")
                patch[16] = np.clip(nw[y:y + SIZE, x:x + SIZE], -20000, 20000).astype("int16")
                imgs.append(patch)
                masks.append(m)
        if not imgs:
            continue
        a = np.stack(imgs)
        b = np.stack(masks)
        np.savez_compressed(dst, img=a, mask=b)
        summary[k] = len(imgs)
        print("ok %-24s %4d" % (k, len(imgs)), flush=True)
    json.dump(summary, open(os.path.join(OUT, "summary.json"), "w"))
    print("total chips", sum(summary.values()), flush=True)


if __name__ == "__main__":
    main()
