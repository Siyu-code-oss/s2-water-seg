# -*- coding: utf-8 -*-
"""Tile the USGS subset into chips (S2 scene + CLASS label of the same id)."""
import json
import os
import re

import numpy as np
import rasterio

F2 = os.path.expanduser("~/sy/F2")
SRC = os.path.join(F2, "data", "usgs", "usgs")
OUT = os.path.join(F2, "data", "chips2")
os.makedirs(OUT, exist_ok=True)
SIZE = 256
STRIDE = 128
VALID_MIN = 0.5


def main():
    files = [f for f in os.listdir(SRC) if f.endswith(".tif")]
    cls = {}
    scenes = []
    for f in files:
        m = re.match(r"(usgs_wv2_\d+)", f)
        if not m:
            continue
        k = m.group(1)
        if f.endswith("_CLASS.tif"):
            cls[k] = os.path.join(SRC, f)
        elif f.endswith("_S2.tif"):
            scenes.append((k, os.path.join(SRC, f)))
    print("class ids:", len(cls), "s2 scenes:", len(scenes), flush=True)

    summary = {}
    for k, p in sorted(scenes):
        if k not in cls:
            continue
        dst = os.path.join(OUT, os.path.basename(p).replace(".tif", ".npz"))
        if os.path.exists(dst):
            continue
        try:
            with rasterio.open(p) as ds:
                img = ds.read()
            with rasterio.open(cls[k]) as ds:
                c = ds.read(1)
        except Exception as exc:      # noqa: BLE001
            print("fail", k, exc, flush=True)
            continue
        if img.shape[1:] != c.shape:
            print("skip shape", k, img.shape, c.shape, flush=True)
            continue
        lab = np.full(c.shape, 255, dtype="uint8")
        lab[c == 0] = 0
        lab[c == 1] = 1
        C, H, W = img.shape
        imgs, masks = [], []
        for y in range(0, H - SIZE + 1, STRIDE):
            for x in range(0, W - SIZE + 1, STRIDE):
                m = lab[y:y + SIZE, x:x + SIZE]
                if (m != 255).mean() < VALID_MIN:
                    continue
                imgs.append(img[:, y:y + SIZE, x:x + SIZE])
                masks.append(m)
        if not imgs:
            print("empty", k, flush=True)
            continue
        a = np.stack(imgs)
        b = np.stack(masks)
        np.savez_compressed(dst, img=a.astype("uint16"), mask=b)
        w = float((b == 1).mean())
        summary[os.path.basename(p)] = {"chips": len(imgs), "water": w}
        print("ok %-28s chips=%4d water=%.1f%%" % (k, len(imgs), 100 * w), flush=True)

    with open(os.path.join(OUT, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1)
    print("scenes:", len(summary), "chips:", sum(v["chips"] for v in summary.values()),
          flush=True)


if __name__ == "__main__":
    main()
