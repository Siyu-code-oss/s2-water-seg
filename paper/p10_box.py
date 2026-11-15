# -*- coding: utf-8 -*-
"""Per-scene IoU box plot (33 scenes x 5 methods)."""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

RUNS = r"D:\F2\runs"
d = json.load(open(os.path.join(RUNS, "per_scene.json")))
ORDER = [("base", "本文方法"), ("std", "标准卷积"), ("unetpp", "U-Net++"),
         ("deeplab", "DeepLabV3+"), ("b4", "仅4波段")]
COL = ["#346696", "#8FB3D9", "#A9C4DC", "#C9D9E8", "#DDE7F0"]

data, names = [], []
for k, n in ORDER:
    if k in d:
        vals = [d[k][s] for s in sorted(d[k])]
        data.append(vals)
        names.append("%s\n%.1f" % (n, np.mean(vals)))

fig, ax = plt.subplots(figsize=(6.6, 3.6))
bp = ax.boxplot(data, patch_artist=True, widths=0.55, showfliers=True,
                flierprops=dict(marker="o", ms=3, mfc="#8A97A3", mec="none", alpha=0.6),
                medianprops=dict(color="#1B2A3A", lw=1.2),
                whiskerprops=dict(color="#6E7C88"), capprops=dict(color="#6E7C88"))
for patch, c in zip(bp["boxes"], COL):
    patch.set_facecolor(c)
    patch.set_edgecolor("#4A5C6E")
    patch.set_linewidth(0.8)
for i, vals in enumerate(data, 1):
    ax.plot(i, np.mean(vals), marker="D", ms=4.5, color="#C0392B", zorder=5)
ax.set_xticklabels(names, fontsize=8)
ax.set_ylabel("逐场景 IoU / %")
ax.set_ylim(0, 105)
ax.grid(axis="y", ls=":", alpha=0.4)
ax.plot([], [], marker="D", ms=4.5, color="#C0392B", ls="none", label="均值")
ax.legend(frameon=False, fontsize=8, loc="lower left")
fig.tight_layout()
out = r"D:\F2\figs\fig_box.png"
fig.savefig(out, dpi=400)
print("saved", out)
