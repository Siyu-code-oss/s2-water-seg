# -*- coding: utf-8 -*-
"""Frequency map with lon/lat ticks, scale bar and NoData legend."""
import os

import numpy as np
import rasterio
from rasterio.warp import transform, transform_bounds
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy.ma as ma
from matplotlib import font_manager

fp = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
if os.path.exists(fp):
    font_manager.fontManager.addfont(fp)
    plt.rcParams["font.family"] = font_manager.FontProperties(fname=fp).get_name()
plt.rcParams["axes.unicode_minus"] = False

F2 = os.path.expanduser("~/sy/F2")
freq = np.load(os.path.join(F2, "runs", "poyang", "freq.npy"))
BBOX = (115.90, 28.90, 116.45, 29.60)
CRS = "EPSG:32650"
left, bottom, right, top = transform_bounds("EPSG:4326", CRS, *BBOX)

cm = plt.cm.Blues.copy()
cm.set_bad("#E6EAEE")
fig, ax = plt.subplots(figsize=(5.6, 6.6))
im = ax.imshow(ma.masked_invalid(freq), cmap=cm, vmin=0, vmax=1,
               interpolation="nearest", extent=(left, right, bottom, top))

# lon/lat ticks
xt = np.linspace(left, right, 5)
yt = np.linspace(bottom, top, 5)
lon, _ = transform(CRS, "EPSG:4326", xt, [bottom] * len(xt))
_, lat = transform(CRS, "EPSG:4326", [left] * len(yt), yt)
ax.set_xticks(xt); ax.set_xticklabels(["%.2f°E" % v for v in lon], fontsize=7)
ax.set_yticks(yt); ax.set_yticklabels(["%.2f°N" % v for v in lat], fontsize=7)

# scale bar 10 km
x0 = left + 0.06 * (right - left)
y0 = bottom + 0.04 * (top - bottom)
ax.plot([x0, x0 + 10000], [y0, y0], color="#1B2A3A", lw=3, solid_capstyle="butt")
ax.text(x0 + 5000, y0 + 1200, "10 km", ha="center", fontsize=7, color="#1B2A3A")
# north arrow
ax.annotate("N", xy=(right - 0.08 * (right - left), top - 0.05 * (top - bottom)),
            xytext=(right - 0.08 * (right - left), top - 0.14 * (top - bottom)),
            ha="center", fontsize=9, fontweight="bold",
            arrowprops=dict(arrowstyle="-|>", color="#1B2A3A", lw=1.2))

cb = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
cb.set_label("水体出现频率")
ax.set_title("鄱阳湖2019—2024年多时相水体出现频率", fontsize=9)
ax.text(0.02, 0.02, "灰色为无有效观测区域", transform=ax.transAxes, fontsize=7,
        color="#4A5C6E", bbox=dict(fc="white", ec="none", alpha=0.8, pad=1.5))
fig.tight_layout()
fig.savefig(os.path.join(F2, "out", "figs", "fig_freq.png"), dpi=300)
print("saved fig_freq with graticule")
