# -*- coding: utf-8 -*-
"""Generate the paper figures from the experiment outputs."""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager

FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
if os.path.exists(FONT):
    font_manager.fontManager.addfont(FONT)
    plt.rcParams["font.family"] = font_manager.FontProperties(fname=FONT).get_name()
plt.rcParams["axes.unicode_minus"] = False

F2 = os.path.expanduser("~/sy/F2")
FIG = os.path.join(F2, "out", "figs")
os.makedirs(FIG, exist_ok=True)
RUNS = os.path.join(F2, "runs")
P4 = os.path.join(RUNS, "p4")

# 1) 5-fold comparison
tags = [("base", "本文方法"), ("std", "标准卷积"), ("b4", "仅4波段")]
data = []
for t, name in tags:
    vals = []
    for f in range(5):
        p = os.path.join(RUNS, "f%d_%s.done" % (f, t))
        if os.path.exists(p):
            vals.append(json.load(open(p))["best"])
    data.append((name, vals))
fig, ax = plt.subplots(figsize=(6.4, 3.6))
w = 0.25
for i, (name, vals) in enumerate(data):
    ax.bar(np.arange(len(vals)) + i * w, vals, w, label=name)
ax.set_xticks(np.arange(5) + w)
ax.set_xticklabels(["第%d折" % (f + 1) for f in range(5)])
ax.set_ylabel("IoU / %")
ax.set_ylim(50, 100)
ax.legend(frameon=False, ncol=3, fontsize=8)
ax.grid(axis="y", ls=":", alpha=.4)
fig.tight_layout()
fig.savefig(os.path.join(FIG, "fig_cv.png"), dpi=300)
plt.close(fig)

# 2) flood frequency map
freq = np.load(os.path.join(RUNS, "poyang", "freq.npy"))
fig, ax = plt.subplots(figsize=(5.2, 6.4))
im = ax.imshow(np.where(np.isfinite(freq), freq, np.nan), cmap="Blues",
               vmin=0, vmax=1, interpolation="nearest")
ax.set_xticks([]); ax.set_yticks([])
cb = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
cb.set_label("淹没频率")
ax.set_title("鄱阳湖 2019—2024 淹没频率")
fig.tight_layout()
fig.savefig(os.path.join(FIG, "fig_freq.png"), dpi=300)
plt.close(fig)

# 3) SHAP importance
res = json.load(open(os.path.join(P4, "p4_result.json")))
sh = list(res["shap"].items())[::-1]
names = [k.replace("f_", "") for k, _ in sh]
vals = [v for _, v in sh]
fig, ax = plt.subplots(figsize=(5.4, 3.4))
ax.barh(names, vals, color="#4C78A8")
ax.set_xlabel("平均 |SHAP| 值")
ax.grid(axis="x", ls=":", alpha=.4)
fig.tight_layout()
fig.savefig(os.path.join(FIG, "fig_shap.png"), dpi=300)
plt.close(fig)

# 4) per-date water fraction
rep = json.load(open(os.path.join(RUNS, "poyang", "report.json")))
d = sorted(rep.items())
fig, ax = plt.subplots(figsize=(6.0, 3.0))
ax.bar([x[0][:4] + "-" + x[0][4:6] for x in d], [x[1]["water_pct"] for x in d],
       color="#7AA6C2")
ax.set_ylabel("水体比例 / %")
ax.set_ylim(0, 60)
ax.grid(axis="y", ls=":", alpha=.4)
fig.tight_layout()
fig.savefig(os.path.join(FIG, "fig_dates.png"), dpi=300)
plt.close(fig)
print("saved to", FIG, flush=True)
