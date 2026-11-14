# -*- coding: utf-8 -*-
"""Plot validation-IoU learning curves for the main configurations."""
import glob
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager

fp = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
if os.path.exists(fp):
    font_manager.fontManager.addfont(fp)
    plt.rcParams["font.family"] = font_manager.FontProperties(fname=fp).get_name()
plt.rcParams["axes.unicode_minus"] = False

RUNS = os.path.expanduser("~/sy/F2/runs")
FIG = os.path.expanduser("~/sy/F2/out/figs")
COL = {"base": "#346696", "std": "#8FB3D9", "b4": "#C9D9E8"}
NAME = {"base": "本文方法", "std": "标准卷积", "b4": "仅4波段"}

fig, ax = plt.subplots(figsize=(6.2, 3.4))
for tag in ("base", "std", "b4"):
    curves = []
    for f in range(5):
        p = os.path.join(RUNS, "f%d_%s.done" % (f, tag))
        if os.path.exists(p):
            d = json.load(open(p))
            if "hist" in d:
                curves.append([h["IoU"] for h in d["hist"]])
    if not curves:
        continue
    n = min(len(c) for c in curves)
    arr = np.array([c[:n] for c in curves])
    ep = np.arange(1, n + 1)
    ax.plot(ep, arr.mean(0), color=COL[tag], lw=1.8, label=NAME[tag])
    ax.fill_between(ep, arr.mean(0) - arr.std(0), arr.mean(0) + arr.std(0),
                    color=COL[tag], alpha=0.18, lw=0)
ax.set_xlabel("训练轮次")
ax.set_ylabel("验证集 IoU / %")
ax.grid(ls=":", alpha=0.45)
ax.legend(frameon=False, fontsize=8)
fig.tight_layout()
fig.savefig(os.path.join(FIG, "fig_curves.png"), dpi=300)
print("saved fig_curves")
