# -*- coding: utf-8 -*-
"""Tile S2 flood scenes into 256x256 chips with labels and indices."""
import collections
import json
import os

import numpy as np
import rasterio

F2 = os.path.expanduser("~/sy/F2")
SRC = os.path.join(F2, "data", "src")
OUT = os.path.join(F2, "data", "chips")
os.makedirs(OUT, exist_ok=True)

SIZE = 256
STRIDE = 128          # 50% overlap -> more views from few events
VALID_MIN = 0.5       # keep chips with at least half valid (non-ignore) pixels
MIN_WATER = 0.0


def find_pairs():
    d = collections.defaultdict(dict)
    for root, _, files in os.walk(SRC):
        for f in files:
            if not f.lower().endswith(".tif"):
                continue
            for k in ("_S2", "_CLASS", "_NDWI", "_S1"):
                if f.endswith(k + ".tif"):
                    d[f[:-len(k + ".tif")]][k] = os.path.join(root, f)
    return d


def tile(path, name):
    with rasterio.open(path) as ds:
        arr = ds.read()                     # (C, H, W)
    C, H, W = arr.shape
    n = 0
    imgs, masks = [], []
    for y in range(0, H - SIZE + 1, STRIDE):
        for x in range(0, W - SIZE + 1, STRIDE):
            chip = arr[:, y:y + SIZE, x:x + SIZE]
            imgs.append(chip)
            n += 1
    return np.stack(imgs) if imgs else None


def main():
    pairs = find_pairs()
    print("events with S2:", sum(1 for v in pairs.values() if "_S2" in v), flush=True)
    summary = {}
    for ev, files in sorted(pairs.items()):
        if "_S2" not in files or "_CLASS" not in files:
            continue
        tif = os.path.join(OUT, ev + ".npz")
        if os.path.exists(tif):
            print("skip", ev, flush=True)
            continue
        try:
            with rasterio.open(files["_S2"]) as ds:
                s2 = ds.read()
                prof = (ds.count, ds.height, ds.width, ds.dtypes[0])
            with rasterio.open(files["_CLASS"]) as ds:
                cls = ds.read(1)
                cprof = (ds.height, ds.width)
        except Exception as exc:            # noqa: BLE001
            print("fail", ev, exc, flush=True)
            continue
        if s2.shape[1:] != cls.shape:
            print("shape mismatch", ev, s2.shape, cls.shape, flush=True)
            continue
        ndwi = None
        if "_NDWI" in files:
            try:
                with rasterio.open(files["_NDWI"]) as ds:
                    ndwi = ds.read(1).astype("float32")
                if ndwi.shape != cls.shape:
                    ndwi = None
            except Exception:               # noqa: BLE001
                ndwi = None

        # label convention: 1 = flood water, 0 = land, everything else ignore
        lab = np.full(cls.shape, 255, dtype="uint8")
        lab[cls == 0] = 0
        lab[cls == 1] = 1

        C, H, W = s2.shape
        n = 0
        ids = []
        imgs, masks, nds = [], [], []
        for y in range(0, H - SIZE + 1, STRIDE):
            for x in range(0, W - SIZE + 1, STRIDE):
                m = lab[y:y + SIZE, x:x + SIZE]
                if (m != 255).mean() < VALID_MIN:
                    continue
                imgs.append(s2[:, y:y + SIZE, x:x + SIZE])
                masks.append(m)
                if ndwi is not None:
                    nds.append(ndwi[y:y + SIZE, x:x + SIZE])
                ids.append((y, x))
                n += 1
        if not n:
            print("no valid chips", ev, flush=True)
            continue
        img = np.stack(imgs)
        msk = np.stack(masks)
        payload = dict(img=img.astype("uint16"), mask=msk.astype("uint8"),
                       ids=np.array(ids))
        if nds:
            payload["ndwi"] = np.stack(nds).astype("float16")
        np.savez_compressed(tif, **payload)
        summary[ev] = {"chips": n, "bands": C, "shape": [H, W],
                       "class_counts": {int(k): int(v) for k, v in
                                        zip(*np.unique(msk, return_counts=True))}}
        print("ok %s chips=%d bands=%d %dx%d" % (ev, n, C, H, W), flush=True)

    with open(os.path.join(OUT, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1, ensure_ascii=False)
    print("events written:", len(summary),
          "chips:", sum(v["chips"] for v in summary.values()), flush=True)


if __name__ == "__main__":
    main()
