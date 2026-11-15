# -*- coding: utf-8 -*-
"""Draw the route and network schematics in a unified blue palette."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False
INK, SUB = "#1B2A3A", "#4A5C6E"
BLUE = ["#E8F1FA", "#D5E5F5", "#C2D8EF", "#AECBE8", "#9BBEE1"]
EDGE = ["#5B8DBB", "#4E82B2", "#4377A8", "#3B6E9F", "#346696"]
OUT = r"D:\F2\figs"


def canvas(w, h):
    fig = plt.figure(figsize=(w / 2.54, h / 2.54), dpi=400)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")
    return fig, ax


def box(ax, x, y, w, h, i=2, lw=1.1):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.4",
                                fc=BLUE[i], ec=EDGE[i], lw=lw, zorder=3))


def txt(ax, x, y, s, fs=7.6, b=False, c=INK):
    ax.text(x, y, s, ha="center", va="center", fontsize=fs, color=c, zorder=6,
            fontweight="bold" if b else "normal")


def arrow(ax, p1, p2, lw=1.2, ls="-", rad=0.0, ms=9):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=ms, lw=lw,
                                 color="#5B8DBB", linestyle=ls, shrinkA=0, shrinkB=0,
                                 connectionstyle="arc3,rad=%g" % rad, zorder=2))


# ---------------- 图1 ----------------
fig, ax = canvas(16.0, 4.4)
y, h, w, gap = 34, 32, 17.0, 2.6
cards = [(1, "影像输入", "Sentinel-2 L2A", "13 光谱 + 3 质量"),
         (2, "波段组织", "16 通道张量", "归一化 [0, 1.5]"),
         (3, "轻量化 U-Net", "深度可分离卷积", "参数 1.07 M"),
         (4, "淹没范围", "阈值 0.5 二值化", "逐期水体掩膜"),
         (1, "应用分析", "淹没频率 / 供需匹配", "驱动因子（SHAP）")]
for k, (i, t1, t2, t3) in enumerate(cards):
    x = 1.8 + k * (w + gap)
    box(ax, x, y, w, h, i)
    txt(ax, x + w / 2, y + h - 7.0, t1, 8.0, True)
    txt(ax, x + w / 2, y + h / 2 - 1.5, t2, 6.8, False, SUB)
    txt(ax, x + w / 2, y + 6.0, t3, 6.5, False, SUB)
    if k < 4:
        arrow(ax, (x + w, y + h / 2), (x + w + gap, y + h / 2))
fig.savefig(OUT + os.sep + "fig_route.png", facecolor="white")
plt.close(fig)

# ---------------- 图2 ----------------
fig, ax = canvas(15.0, 7.2)
EX, DX, BW, BH = 12.0, 68.0, 20.0, 11.0
rows = [(74.0, 1, "256×256×32"), (56.5, 2, "128×128×64"),
        (39.0, 3, "64×64×128"), (21.5, 4, "32×32×256")]
for y, i, t in rows:
    for x, j in ((EX, i), (DX, i)):
        box(ax, x, y, BW, BH, j)
        txt(ax, x + BW / 2, y + BH * 0.63, t, 7.2, True)
        txt(ax, x + BW / 2, y + BH * 0.26, "DSConv×2", 6.6, False, SUB)
for i in range(3):
    y0 = rows[i][0]
    y1 = rows[i + 1][0] + BH
    arrow(ax, (EX + BW / 2, y0), (EX + BW / 2, y1), lw=1.0, ms=7)
    arrow(ax, (DX + BW / 2, y1), (DX + BW / 2, y0), lw=1.0, ms=7)
    yc = y0 + BH / 2
    arrow(ax, (EX + BW, yc), (DX, yc), lw=0.9, ms=6, ls=(0, (4, 2.4)))
box(ax, 39.0, 3.0, 20.0, 11.0, 0)
txt(ax, 49.0, 10.4, "16×16×512", 7.2, True)
txt(ax, 49.0, 5.8, "DSConv×2", 6.6, False, SUB)
arrow(ax, (EX + BW / 2, rows[3][0]), (41.0, 14.0), lw=1.0, ms=7, rad=-0.12)
arrow(ax, (57.0, 14.0), (DX + BW / 2, rows[3][0]), lw=1.0, ms=7, rad=0.12)
arrow(ax, (EX + BW / 2, 93.0), (EX + BW / 2, 85.0), lw=1.1)
txt(ax, EX + BW / 2, 95.5, "16 波段输入", 7.2, True)
arrow(ax, (DX + BW / 2, 85.0), (DX + BW / 2, 93.0), lw=1.1)
txt(ax, DX + BW / 2, 95.5, "水体概率图", 7.2, True)
txt(ax, EX + BW / 2, 15.0, "编码器", 7.4, True, EDGE[3])
txt(ax, DX + BW / 2, 15.0, "解码器", 7.4, True, EDGE[3])
fig.savefig(OUT + r"\fig_net.png", facecolor="white")
plt.close(fig)
print("done")
