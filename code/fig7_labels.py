# -*- coding: utf-8 -*-
"""Redraw the SHAP importance bar chart with value labels."""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

fp = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
if os.path.exists(fp):
    font_manager.fontManager.addfont(fp)
    plt.rcParams["font.family"] = font_manager.FontProperties(fname=fp).get_name()
plt.rcParams["axes.unicode_minus"] = False

F2 = os.path.expanduser("~/sy/F2")
P4 = os.path.join(F2, "runs", "p4")
FIG = os.path.join(F2, "out", "figs")

res = json.load(open(os.path.join(P4, "p4_result.json")))
sh = list(res["shap"].items())[::-1]
names = [k.replace("f_", "") for k, _ in sh]
vals = [v for _, v in sh]
fig, ax = plt.subplots(figsize=(5.6, 3.4))
ax.barh(names, vals, color="#4C78A8")
for i, v in enumerate(vals):
    ax.text(v + 0.0015, i, "%.3f" % v, va="center", fontsize=7.5, color="#2B3A4A")
ax.set_xlabel("平均 |SHAP| 值")
ax.set_xlim(0, max(vals) * 1.12)
ax.grid(axis="x", ls=":", alpha=0.4)
fig.tight_layout()
fig.savefig(os.path.join(FIG, "fig_shap.png"), dpi=300)
print("saved fig_shap with labels")
