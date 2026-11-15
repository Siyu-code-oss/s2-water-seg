# -*- coding: utf-8 -*-
"""SHAP dependence plots with axis units and subfigure names below panels."""
import json
import os

import numpy as np
import shap
from sklearn.ensemble import RandomForestRegressor
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
rows = json.load(open(os.path.join(P4, "cells.json")))
FEATS = ["f_water", "f_built", "f_crop", "f_tree", "f_grass", "f_wetland",
         "f_bare", "f_shrub", "elev"]
X = np.array([[r.get(k, 0.0) for k in FEATS] for r in rows], dtype="float32")
y = np.array([r["freq"] for r in rows], dtype="float32")
rf = RandomForestRegressor(n_estimators=500, min_samples_leaf=3, random_state=42, n_jobs=-1).fit(X, y)
sv = shap.TreeExplainer(rf).shap_values(X)

fig, axes = plt.subplots(1, 2, figsize=(8.0, 3.4))
PANELS = ((axes[0], "elev", "高程/m", 1.0, "(a) 高程"), (axes[1], "f_wetland", "湿地比例/%", 100.0, "(b) 湿地比例"))
for ax, feat, label, scale, sub_name in PANELS:
    i = FEATS.index(feat)
    xv = X[:, i] * scale
    ax.scatter(xv, sv[:, i], s=6, alpha=0.5, color="#4E82B2", edgecolors="none")
    ax.axhline(0, color="#8A97A3", lw=0.8, ls=":")
    ax.set_xlabel(label, fontsize=9)
    ax.text(0.5, -0.30, sub_name, transform=ax.transAxes, ha="center", va="top", fontsize=9)
    ax.set_ylabel("SHAP 值", fontsize=9)
    ax.grid(ls=":", alpha=0.4)
    corr = np.corrcoef(X[:, i], sv[:, i])[0, 1]
    ax.text(0.62, 0.92, "r=%.2f" % corr, transform=ax.transAxes,
            fontsize=9, va="top")
fig.tight_layout(rect=(0, 0.06, 1, 1))
fig.savefig(os.path.join(F2, "out", "figs", "fig_shap_dep.png"), dpi=300)
print("saved fig_shap_dep")
for feat in ("elev", "f_wetland"):
    i = FEATS.index(feat)
    print(feat, "corr %.2f" % np.corrcoef(X[:, i], sv[:, i])[0, 1])
