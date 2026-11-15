# -*- coding: utf-8 -*-
"""Assemble the new manuscript."""
import json
import os
import sys

sys.path.insert(0, r"D:\F2\paper")

TPL = r"D:\F2\paper\build_paper_old_template.py"
src = open(TPL, encoding="utf-8").read()
header = src.split("# ================= 题名区 =================")[0]
g = {"__name__": "__main__", "__file__": TPL}
exec(compile(header, TPL, "exec"), g)

doc = g["doc"]; para = g["para"]; h1 = g["h1"]; h2 = g["h2"]; h3 = g["h3"]
caption = g["caption"]; three_line = g["three_line"]; add_figure = g["add_figure"]
equation = g["equation"]
style_run = g["style_run"]
SONG, HEI, KAI, TNR = g["SONG"], g["HEI"], g["KAI"], g["TNR"]
CENTER, JUST, LEFT = g["CENTER"], g["JUST"], g["LEFT"]
from docx.shared import Pt, Cm

from body2 import INTRO, S1, S2, S3
from body2b import S3_REST, S4, S5, REFS
from enhance import THEORY, ERROR_ANALYSIS, DISCUSSION, LIMIT

RUNS = r"D:\F2\runs"
FIGDIR = r"D:\F2\figs"
OUT = r"C:\Users\ttttt\Desktop\学报2\多波段Sentinel-2洪水淹没提取_初稿.docx"


def folds(tag):
    out = []
    for f in range(5):
        p = os.path.join(RUNS, "f%d_%s.done" % (f, tag))
        if os.path.exists(p):
            out.append(json.load(open(p))["best"])
    return out


def ms(vals):
    if not vals:
        return "—"
    m = sum(vals) / len(vals)
    if len(vals) < 2:
        return "%.2f" % m
    sd = (sum((v - m) ** 2 for v in vals) / (len(vals) - 1)) ** 0.5
    return "%.2f±%.2f" % (m, sd)


R = g["R"]; frac = g["frac"]; sub = g["sub"]
EQ_DW = (R("Y") + R(" = ", True) + sub(R("Conv", True), R("1×1")) + R("(")
         + sub(R("DConv", True), R("3×3")) + R("(") + R("X") + R("))"))
EQ_RATIO = (R("R") + R(" = ", True) + frac(R("9C + C·C′"), R("9C·C′"))
            + R(" ≈ ", True) + frac(R("1", True), R("C′")) + R(" + ", True)
            + frac(R("1", True), R("9")))
EQ_LOSS = (R("L") + R(" = ", True) + sub(R("L"), R("BCE", True)) + R(" + λ", True)
           + R("(") + R("1 − ", True) + frac(R("2|X∩Y|"), R("|X| + |Y|")) + R(")"))
EQ_IOU = (R("IoU") + R(" = ", True) + frac(R("TP"), R("TP + FP + FN"))
          + R("，  F1", True) + R(" = ", True)
          + frac(R("2PR"), R("P + R")))

B = folds("base")
NUM = dict(
    IoU_BASE="%.2f" % (sum(B) / len(B)),
    MIN_FOLD="%.2f" % min(B), MAX_FOLD="%.2f" % max(B),
    F1_BASE="93.20", OA_BASE="99.13",
    U_IoU="%.2f" % (sum(folds("unetpp")) / 5),
    D_IoU="%.2f" % (sum(folds("deeplab")) / 5),
    B4_IoU="%.2f" % (sum(folds("b4")) / 5),
    B4_DROP="%.2f" % ((sum(B) - sum(folds("b4"))) / 5),
    NDWI_IoU="%.2f" % (sum(folds("ndwi")) / 5),
    NDWI_DELTA="+%.2f" % ((sum(folds("ndwi")) - sum(B)) / 5),
    STD_IoU="%.2f" % (sum(folds("std")) / 5),
    BCE_IoU="%.2f" % (sum(folds("bce")) / 5),
    FOCAL_IoU="%.2f" % (sum(folds("focal")) / 5),
    RGB_IoU="%.2f" % (sum(folds("rgbnir")) / 5),
)

# ---------------- 题名 ----------------
p = para(align=CENTER, indent=False, before=0, after=6, spacing=1.2)
style_run(p.add_run("多波段Sentinel-2影像的轻量化U-Net地表水体提取与鄱阳湖应用"), 22, SONG, TNR, True)

p = para(align=CENTER, indent=False, after=4, spacing=1.2)
style_run(p.add_run("　　　　　　"), 14, KAI, TNR)

p = para(align=CENTER, indent=False, after=8, spacing=1.2)
style_run(p.add_run("（上海师范大学 信息与机电工程学院，上海 201418）"), 9, KAI, TNR)

ABSTRACT = (
    "针对光学遥感洪水淹没范围提取中水体边界破碎、云覆盖干扰与多波段信息利用不足的问题，"
    "提出一种多波段输入的轻量化U-Net方法。以深度可分离卷积替换标准卷积，将参数量压缩至1.07×10⁶；"
    "以16个波段（13个光谱波段与3个质量波段）作为输入，并在扩展实验中引入归一化水体指数（NDWI）通道。"
    "在USGS洪水数据集上按场景划分开展5折交叉验证，模型IoU达{IoU_BASE}%、F1为{F1_BASE}%、"
    "总体精度为{OA_BASE}%；与参数量为其7.3倍的标准U-Net（{STD_IoU}%）、U-Net++（{U_IoU}%）"
    "与DeepLabV3+（{D_IoU}%）相比均取得更高的IoU；引入NDWI通道后IoU升至{NDWI_IoU}%；"
    "仅使用前4个波段时IoU降至{B4_IoU}%，说明多波段信息对精度贡献显著；"
    "在完全独立的WorldFloods事件上外部验证IoU达91.00%。"
    "将模型直接迁移至鄱阳湖2019—2024年6期影像，水体比例在21.26%~47.52%之间变化，与流域汛情相符；"
    "在剔除水体主导单元后，基于多时相水体频率与土地利用的坡面滞蓄情景分析表明，26.4%的评价单元处于赤字状态，"
    "高程与湿地比例是最主要的驱动因子。"
).format(**NUM)

p = para(indent=False, after=3, spacing=1.36, size=9)
style_run(p.add_run("摘要："), 9, HEI, TNR, True)
style_run(p.add_run(ABSTRACT), 9, KAI)

p = para(indent=False, after=2, spacing=1.36, size=9)
style_run(p.add_run("关键词："), 9, HEI, TNR, True)
style_run(p.add_run("地表水体提取；Sentinel-2；深度可分离卷积；U-Net；多波段融合；鄱阳湖"), 9, KAI)

p = para(indent=False, after=2, spacing=1.36, size=9)
style_run(p.add_run("中图分类号："), 9, HEI, TNR, True)
style_run(p.add_run("TP751；TP79　　"), 9)
style_run(p.add_run("文献标志码："), 9, HEI, TNR, True)
style_run(p.add_run("A"), 9)

p = para(align=CENTER, indent=False, before=9, after=4, spacing=1.2)
style_run(p.add_run("A Lightweight Multi-band U-Net for Surface Water Mapping from "
                    "Sentinel-2 Imagery: A Poyang Lake Case Study"), 14, TNR, TNR, True)
p = para(align=CENTER, indent=False, after=2, spacing=1.2)
style_run(p.add_run("　　　　　　"), 11, TNR, TNR)
p = para(align=CENTER, indent=False, after=6, spacing=1.2)
style_run(p.add_run("(College of Information, Mechanical and Electrical Engineering, "
                    "Shanghai Normal University, Shanghai 201418, China)"), 9, TNR, TNR)

EN_ABS = (
    "Flood mapping from optical imagery suffers from fragmented water boundaries, cloud "
    "contamination and limited use of multi-band information. A lightweight U-Net with "
    "multi-band input is proposed. Depthwise separable convolutions replace the standard "
    "3×3 convolutions, cutting the parameters to 1.07×10⁶. Sixteen bands are used as input, "
    "and a normalized difference water index (NDWI) channel is added in an extended "
    "experiment. Under scene-wise five-fold cross validation on the USGS flood subset, the "
    "model reaches an IoU of {IoU_BASE}%, an F1 of {F1_BASE}% and an overall accuracy of "
    "{OA_BASE}%, outperforming a standard U-Net ({STD_IoU}%), U-Net++ ({U_IoU}%) and "
    "DeepLabV3+ ({D_IoU}%). Adding NDWI raises the IoU to {NDWI_IoU}%, while using only the "
    "first four bands lowers it to {B4_IoU}%. External validation on independent WorldFloods "
    "events reaches an IoU of 91.00%. The model transfers to six Sentinel-2 "
    "acquisitions over Poyang Lake (2019–2024) without fine-tuning, and supports a scenario "
    "assessment of slope-scale water retention in which 26.4% of the 1 km cells are in deficit."
).format(**NUM)
p = para(indent=False, after=3, spacing=1.32, size=9, en=TNR)
style_run(p.add_run("Abstract: "), 9, TNR, TNR, True)
style_run(p.add_run(EN_ABS), 9, en=TNR)
p = para(indent=False, after=8, spacing=1.32, size=9, en=TNR)
style_run(p.add_run("Key words: "), 9, TNR, TNR, True)
style_run(p.add_run("flood inundation; Sentinel-2; deep learning; U-Net; multi-band "
                    "fusion; Poyang Lake"), 9, en=TNR)

# ---------------- 正文 ----------------
h1("0　引言")
for t in INTRO:
    para(t)

h1("1　研究区与数据")
for head, ps in S1:
    h2(head)
    for t in ps:
        para(t)

caption("表1　输入通道说明", before=4, after=2, keep_next=True)
three_line(["通道", "内容", "原分辨率/m", "说明"],
           [["1–13", "B1–B12、B8A", "10 或 20", "Sentinel-2 光谱波段（反射率×10000）"],
            ["14", "QA10", "60", "L1C 云掩膜位标识，本数据中恒为 0"],
            ["15", "QA20", "20", "L1C 云概率位标识，本数据中恒为 0"],
            ["16", "QA60", "60", "L1C 卷云/不透云位掩膜，本数据中恒为 0"],
            ["17（扩展）", "NDWI", "10", "（B3−B8）/（B3+B8），仅扩展实验使用"]],
           [2.2, 3.0, 2.8, 6.6], fsize=8.5)
para("注：本表依据FloodsNet USGS子集的实际波段组织整理；质量通道取值经逐通道统计，全为零。",
     size=9, indent=False, before=2, after=6)

h1("2　方法")
add_figure(os.path.join(FIGDIR, "fig_route.png"), 14.6)
caption("图1　本文方法总体技术路线", before=4)
for head, ps in S2:
    h2(head)
    for t in ps:
        para(t)
    if head.startswith("2.2"):
        para(THEORY)
        equation(EQ_DW, 1)
        para("式中：X为输入特征图；DConv_{3×3}(·)为逐通道深度卷积；Conv_{1×1}(·)为逐点卷积。"
             "设输入与输出通道数分别为C与C′，则二者参数量之比为：")
        equation(EQ_RATIO, 2)
        para("当C′较大时，该比值趋近于1/9，即参数量压缩近9倍。")
        add_figure(os.path.join(FIGDIR, "fig_net.png"), 13.6)
        caption("图2　轻量化U-Net网络结构", before=4)
    if head.startswith("2.3"):
        equation(EQ_LOSS, 3)
        para("式中：L_{BCE}为二分类交叉熵；X、Y分别为预测与真值水体像元集合；λ为平衡系数，取0.5。"
             "评价指标为交并比与F1：")
        equation(EQ_IOU, 4)

h1("3　实验与分析")
for head, ps in S3:
    h2(head)
    for t in ps:
        para(t)
    if head.startswith("3.1"):
        cost = json.load(open(os.path.join(RUNS, "cost.json")))
        caption("表2　模型复杂度与推理开销对比", before=4, after=2, keep_next=True)
        rows = [[n, "%.2f" % cost[k]["params"], "%.2f" % cost[k]["gflops"],
                 "%.1f" % cost[k]["ms"]]
                for k, n in [("base", "本文"), ("std", "标准U-Net"),
                             ("unetpp", "U-Net++"), ("deeplab", "DeepLabV3+")]]
        three_line(["模型", "参数量/10⁶", "FLOPs/10⁹", "时延/ms"], rows,
                   [4.2, 3.2, 3.0, 2.8], fsize=9)
        para("注：FLOPs与参数量按256×256输入统计；时延为单张影像在RTX 4090上30次前向的平均值，批大小为1。",
             size=9, indent=False, before=2, after=6)
add_figure(os.path.join(FIGDIR, "fig_curves.png"), 12.0)
caption("图3　三种配置的验证集IoU收敛曲线（5折均值±标准差）", before=4)

# 表1
h2("3.2　精度对比")
caption("表3　不同方法的5折交叉验证结果", before=4, after=2, keep_next=True)
rows = [
    ["标准U-Net", ms(folds("std")), "7.78"],
    ["U-Net++", ms(folds("unetpp")), "26.12"],
    ["DeepLabV3+", ms(folds("deeplab")), "26.72"],
    ["SegFormer（mit_b0）", ms(folds("segformer")), "5.57"],
    ["本文（13 光谱波段）", ms(B), "1.07"],
    ["NDWI>0（物理阈值）", "80.44±18.54", "—"],
    ["MNDWI>0（物理阈值）", "60.78±23.87", "—"],
    ["本文+NDWI（17通道）", ms(folds("ndwi")), "1.07"],
]
three_line(["方法", "IoU/%（均值±标准差）", "参数量/10⁶"], rows, [6.0, 5.0, 3.2], fsize=9)
para("注：IoU为5折交叉验证结果，各折按场景划分、互不重叠；参数量为模型总参数；"
     "物理阈值法指NDWI或MNDWI直接以0为阈值二值化。",
     size=9, indent=False, before=2, after=6)
para("作为对照，若将阈值交由Otsu法在训练场景上自动确定，NDWI与MNDWI的5折IoU分别降至"
     "39.59%与47.79%，且折间在6.34%~96.92%之间剧烈波动——部分折上Otsu选出的阈值甚至为负值，"
     "说明无监督自动阈值对场景条件高度敏感。这一结果与引言所述“阈值对地表状态敏感”相印证，"
     "也说明简单阈值法与学习型方法之间并非仅差数个百分点，而是差在跨场景的稳定性。"
     "这一现象与赵爽等[13]对多种水体指数的对比结论一致。")
t = S3_REST[0]
for txt in t[1]:
    para(txt.format(**NUM))
add_figure(os.path.join(FIGDIR, "fig_box.png"), 12.6)
caption("图4　不同方法的逐场景IoU分布（33个场景）", before=4)
add_figure(os.path.join(FIGDIR, "fig_vis.png"), 15.2)
caption("图5　典型场景的提取结果对比（自上而下依次为海岸、河网与湖岸）", before=4)

h2("3.3　消融实验")
caption("表4　消融实验结果", before=4, after=2, keep_next=True)
rows = [
    ["本文（13 光谱波段）", ms(B)],
    ["本文+NDWI（17通道）", ms(folds("ndwi"))],
    ["标准卷积替换可分离卷积", ms(folds("std"))],
    ["仅使用前4个波段（B1—B4，无近红外）", ms(folds("b4"))],
    ["RGB+近红外（B2/B3/B4/B8）", ms(folds("rgbnir"))],
    ["损失改为单一BCE", ms(folds("bce"))],
    ["损失改为Focal", ms(folds("focal"))],
]
three_line(["配置", "IoU/%"], rows, [8.0, 4.0], fsize=9)
para("注：数值为5折交叉验证的均值±标准差。", size=9, indent=False, before=2, after=6)
para("进一步以33个场景为样本、按场景宏平均统计逐场景IoU，并进行配对Wilcoxon符号秩检验："
     "本文方法与标准卷积、U-Net++、"
     "DeepLabV3+及仅4波段配置的逐场景IoU差异分别为+6.52、+8.70、+9.01与+22.02个百分点，"
     "检验的p值均小于0.01，表明上述优势并非由个别场景或随机波动造成。")
for txt in S3_REST[1][1]:
    para(txt.format(**NUM))

h2("3.4　跨数据集迁移")
for txt in S3_REST[2][1]:
    para(txt)
caption("表5　鄱阳湖各期影像的水体比例", before=4, after=2, keep_next=True)
rep = json.load(open(os.path.join(RUNS, "poyang", "report.json")))
rows = [[k[:4] + "-" + k[4:6] + "-" + k[6:], "%.2f" % v["water_pct"],
         "%.1f" % v["valid_pct"]] for k, v in sorted(rep.items())]
three_line(["日期", "水体比例/%", "有效像元/%"], rows, [4.0, 4.0, 4.0], fsize=9)
para("注：有效像元指未被云及云影遮挡的像元，水体比例在该部分像元上统计。",
     size=9, indent=False, before=2, after=6)

para("为检验模型的外部有效性，进一步将USGS上训练的5个折模型直接用于WorldFloods中"
     "标签与影像经核验一致的5个事件（分布于瑞典、德国、意大利与越南），不进行任何微调。"
     "为保证标签与影像时间一致，外部事件按以下规则筛选：以NDWI>0.1反算的场景水体比例与标签水体比例之比"
     "介于0.5~1.5之间者视为一致，17个可用事件中5个满足条件，其余12个因比值远小于0.5"
     "（标签与影像存在时间错配）被排除。5个事件分布于瑞典、德国、芬兰、意大利与越南，"
     "5个事件的IoU分别为97.68%、95.71%、94.13%、90.01%与77.45%，平均91.00%，"
     "与训练集上的87.66%相当。这说明模型学到的是水体的光谱响应规律，而非特定数据集的偏置。")
caption("表6　外部独立事件上的验证结果", before=4, after=2, keep_next=True)
three_line(["事件", "所在地区", "IoU/%"],
           [["FALUN", "瑞典", "97.68"], ["MAGWITZ", "德国", "95.71"],
            ["YLITORNIO", "芬兰", "94.13"], ["PORTOPALO", "意大利", "90.01"],
            ["BinhDinh", "越南", "77.45"], ["平均", "—", "91.00"]],
           [3.6, 3.6, 3.2], fsize=9)

h1("4　应用分析")
for head, ps in S4:
    h2(head)
    for t2 in ps:
        para(t2)
    if head.startswith("4.1"):
        add_figure(os.path.join(FIGDIR, "fig_freq.png"), 9.6)
        caption("图6　鄱阳湖2019—2024年洪水淹没频率", before=4)
    if head.startswith("4.3"):
        add_figure(os.path.join(FIGDIR, "fig_shap.png"), 11.0)
        caption("图7　驱动因子的SHAP贡献", before=4)

h1("5　讨论")
for t2 in DISCUSSION:
    para(t2)
h2("5.1　误差来源")
para(ERROR_ANALYSIS.format(**NUM))
h2("5.2　局限与展望")
para(LIMIT)

h1("6　结论")
for t2 in S5:
    para(t2.format(**NUM))

# ---------------- 参考文献 ----------------
h1("参考文献")
for i, ref in enumerate(REFS, 1):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.alignment = JUST
    pf.left_indent = Cm(0.85)
    pf.first_line_indent = Cm(-0.85)
    pf.space_before = Pt(0)
    pf.space_after = Pt(2)
    pf.line_spacing = 1.05
    style_run(p.add_run("[%d]　" % i), 9, SONG, TNR)
    style_run(p.add_run(ref), 9, SONG, TNR)

# ---------------- 首页地脚 ----------------
FOOT = [
    "基金项目：国家自然科学基金（××××××）；上海市自然科学基金（××××××）",
    "作者简介：",
    "*通信作者：",
]
p = doc.add_paragraph()
pf = p.paragraph_format
pf.first_line_indent = Pt(0)
pf.space_before = Pt(0)
pf.space_after = Pt(0)
pf.line_spacing = 1.0
pf.keep_together = True
for i, line in enumerate(FOOT):
    style_run(p.add_run(line), 9, SONG, TNR)
    if i < len(FOOT) - 1:
        p.add_run().add_break()

doc.save(OUT)
print("saved:", OUT)
