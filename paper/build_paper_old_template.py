# -*- coding: utf-8 -*-
"""按《上海师范大学学报（自然科学版）》版式生成投稿修改稿。"""
import os
import re
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml, OxmlElement

BASE = os.path.dirname(os.path.abspath(__file__))
FIG1 = os.path.join(BASE, "figs", "fig1.png")
FIG2 = os.path.join(BASE, "figs", "fig2.png")
FIG3 = os.path.join(BASE, "figs", "fig3.png")
FIG4 = os.path.join(BASE, "figs", "fig4.png")
OUT = r"C:\Users\ttttt\Desktop\学报\多特征融合的轻量化U-Net SAR影像洪水淹没区提取方法_修改稿.docx"

SONG, HEI, KAI, FANG, TNR = "宋体", "黑体", "楷体", "仿宋", "Times New Roman"
TEXT_W = Cm(14.6)
CENTER = WD_ALIGN_PARAGRAPH.CENTER
JUST = WD_ALIGN_PARAGRAPH.JUSTIFY
LEFT = WD_ALIGN_PARAGRAPH.LEFT

doc = Document()

# ---------- 页面 ----------
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
sec.left_margin = sec.right_margin = Cm(3.2)
sec.top_margin = sec.bottom_margin = Cm(2.54)
sec.header_distance = Cm(1.5)

# ---------- 默认样式 ----------
normal = doc.styles["Normal"]
normal.font.name = TNR
normal.font.size = Pt(10.5)
normal.element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:eastAsia"), SONG)
normal.paragraph_format.space_before = Pt(0)
normal.paragraph_format.space_after = Pt(0)


def style_run(run, size=10.5, cn=SONG, en=TNR, bold=False, italic=False, color=None):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    if color:
        run.font.color.rgb = color
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.insert(0, rFonts)
    rFonts.set(qn("w:ascii"), en)
    rFonts.set(qn("w:hAnsi"), en)
    rFonts.set(qn("w:eastAsia"), cn)
    return run


TOK = re.compile(r"\*\{([^}]*)\}|_\{([^}]*)\}|\^\{([^}]*)\}")


def add_rich(p, text, size=10.5, cn=SONG, en=TNR, bold=False):
    """把 *{...} 写成斜体、_{...} 写成下标、^{...} 写成上标，其余照原样。"""
    pos = 0
    for m in TOK.finditer(text):
        if m.start() > pos:
            style_run(p.add_run(text[pos:m.start()]), size, cn, en, bold)
        if m.group(1) is not None:
            style_run(p.add_run(m.group(1)), size, cn, en, bold, italic=True)
        elif m.group(2) is not None:
            style_run(p.add_run(m.group(2)), size, cn, en, bold).font.subscript = True
        else:
            style_run(p.add_run(m.group(3)), size, cn, en, bold).font.superscript = True
        pos = m.end()
    if pos < len(text):
        style_run(p.add_run(text[pos:]), size, cn, en, bold)


def para(text="", size=10.5, cn=SONG, en=TNR, bold=False, align=JUST,
         indent=True, before=0, after=0, spacing=1.5):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.alignment = align
    pf.first_line_indent = Pt(size * 2) if indent else Pt(0)
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = spacing
    if text:
        if "{" in text:
            add_rich(p, text, size, cn, en, bold)
        else:
            style_run(p.add_run(text), size, cn, en, bold)
    return p


def h1(text):
    p = para(indent=False, align=LEFT, before=14, after=6, spacing=1.4)
    style_run(p.add_run(text), 14, SONG, TNR, True)
    p.paragraph_format.keep_with_next = True
    return p


def h2(text):
    p = para(indent=False, align=LEFT, before=8, after=4, spacing=1.4)
    style_run(p.add_run(text), 11, SONG, TNR, True)
    p.paragraph_format.keep_with_next = True
    return p


def h3(text):
    p = para(indent=False, align=LEFT, before=6, after=3, spacing=1.4)
    style_run(p.add_run(text), 10.5, SONG, TNR, False)
    return p


def caption(text, before=6, after=6, keep_next=False):
    p = para(align=CENTER, indent=False, before=before, after=after, spacing=1.2)
    style_run(p.add_run(text), 9, HEI, TNR, True)
    if keep_next:
        p.paragraph_format.keep_with_next = True
    return p


# ---------- OMML ----------
def R(t, up=False):
    pr = '<m:rPr><m:sty m:val="p"/></m:rPr>' if up else ""
    return f'<m:r>{pr}<m:t xml:space="preserve">{t}</m:t></m:r>'


def sub(e, s):
    return f"<m:sSub><m:e>{e}</m:e><m:sub>{s}</m:sub></m:sSub>"


def sup(e, s):
    return f"<m:sSup><m:e>{e}</m:e><m:sup>{s}</m:sup></m:sSup>"


def subsup(e, sb, sp):
    return f"<m:sSubSup><m:e>{e}</m:e><m:sub>{sb}</m:sub><m:sup>{sp}</m:sup></m:sSubSup>"


def frac(n, d):
    return f"<m:f><m:num>{n}</m:num><m:den>{d}</m:den></m:f>"


def acc(e, ch="\u0303"):
    return (f'<m:acc><m:accPr><m:chr m:val="{ch}"/></m:accPr>'
            f"<m:e>{e}</m:e></m:acc>")


def nary(chr_, s, p, e):
    return (f'<m:nary><m:naryPr><m:chr m:val="{chr_}"/>'
            f'<m:limLoc m:val="undOvr"/></m:naryPr>'
            f"<m:sub>{s}</m:sub><m:sup>{p}</m:sup><m:e>{e}</m:e></m:nary>")


def equation(inner, num):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.alignment = LEFT
    pf.first_line_indent = Pt(0)
    pf.space_before = Pt(6)
    pf.space_after = Pt(6)
    pf.line_spacing = 1.0
    pf.tab_stops.add_tab_stop(Cm(7.3), WD_TAB_ALIGNMENT.CENTER)
    pf.tab_stops.add_tab_stop(Cm(14.6), WD_TAB_ALIGNMENT.RIGHT)
    style_run(p.add_run("\t"), 10.5)
    p._p.append(parse_xml("<m:oMath %s>%s</m:oMath>" % (nsdecls("m", "w"), inner)))
    style_run(p.add_run("\t（%d）" % num), 10.5, SONG, TNR, False)
    return p


SIG = R("σ")
SIG0 = sup(R("σ"), R("0"))


EQ1 = subsup(SIG, R("dB", True), R("0")) + R(" = 10 lg ", True) + SIG0
EQ2 = (sub(R("R"), R("VH/VV")) + R(" = ", True)
       + subsup(SIG, R("dB", True), R("0")) + R("(VH) − ")
       + subsup(SIG, R("dB", True), R("0")) + R("(VV)"))
EQ3 = (acc(R("x")) + R(" = ", True)
       + frac(R("2(") + R("x") + R(" − ") + sub(R("x"), R("min", True)) + R(")"),
              R("(") + sub(R("x"), R("max", True)) + R(" − ")
              + sub(R("x"), R("min", True)) + R(")"))
       + R(" − 1", True))
EQ4 = (R("Y") + R(" = ", True) + sub(R("Conv", True), R("1×1"))
       + R("(") + sub(R("DConv", True), R("3×3")) + R("(") + R("X") + R("))"))
EQ8 =(sub(R("L"), R("BCE", True)) + R(" = −", True)
       + frac(R("1", True), R("N"))
       + nary("∑", R("i=1"), R("N"),
              R("[") + sub(R("y"), R("i")) + R("ln ", True) + sub(R("p"), R("i"))
              + R(" + (1 − ", True) + sub(R("y"), R("i")) + R(")ln(1 − ", True)
              + sub(R("p"), R("i")) + R(")]")))
EQ9 = (R("L") + R(" = ", True) + sub(R("L"), R("BCE", True)) + R(" + λ", True)
       + R("(") + R("1 − ", True)
       + frac(R("2|X∩Y|"), R("|X| + |Y|")) + R(")"))
EQ10 = (R("IoU") + R(" = ", True)
        + frac(R("TP"), R("TP + FP + FN"))
        + R("，  Recall", True) + R(" = ", True)
        + frac(R("TP"), R("TP + FN")))


# ---------- 三线表 ----------
def three_line(header, rows, widths, fsize=9, note=None, rh=0.68):
    ncol = len(header)
    t = doc.add_table(rows=1 + len(rows), cols=ncol)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    tblPr = t._tbl.tblPr
    tblPr.append(parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        '<w:top w:val="single" w:sz="12" w:space="0" w:color="000000"/>'
        '<w:left w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        '<w:bottom w:val="single" w:sz="12" w:space="0" w:color="000000"/>'
        '<w:right w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        '<w:insideH w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        '<w:insideV w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        "</w:tblBorders>"))
    tblPr.append(parse_xml(
        f'<w:tblLayout {nsdecls("w")} w:type="fixed"/>'))

    for ri, rowdata in enumerate([header] + rows):
        row = t.rows[ri]
        row.height = Cm(rh)
        row._tr.get_or_add_trPr().append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
        for ci, val in enumerate(rowdata):
            cell = row.cells[ci]
            cell.width = Cm(widths[ci])
            p = cell.paragraphs[0]
            p.paragraph_format.alignment = CENTER
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.0
            # 除最后一行外与下一行同页，避免三线表被分页切断
            p.paragraph_format.keep_with_next = (ri < len(rows))
            style_run(p.add_run(str(val)), fsize, SONG, TNR, ri == 0)
        if ri == 0:
            for cell in row.cells:
                cell._tc.get_or_add_tcPr().append(parse_xml(
                    f'<w:tcBorders {nsdecls("w")}>'
                    '<w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
                    "</w:tcBorders>"))
    return t


def add_figure(path, width_cm):
    p = doc.add_paragraph()
    p.paragraph_format.alignment = CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.keep_with_next = True   # 图与紧随其后的图题不拆页
    p.add_run().add_picture(path, width=Cm(width_cm))


def placeholder_box(text, width_cm=15.0, height_cm=7.0):
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = t.rows[0].cells[0]
    cell.width = Cm(width_cm)
    t.rows[0].height = Cm(height_cm)
    cell._tc.get_or_add_tcPr().append(parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        '<w:top w:val="dashed" w:sz="6" w:space="0" w:color="999999"/>'
        '<w:left w:val="dashed" w:sz="6" w:space="0" w:color="999999"/>'
        '<w:bottom w:val="dashed" w:sz="6" w:space="0" w:color="999999"/>'
        '<w:right w:val="dashed" w:sz="6" w:space="0" w:color="999999"/>'
        "</w:tcBorders>"))
    p = cell.paragraphs[0]
    p.paragraph_format.alignment = CENTER
    p.paragraph_format.line_spacing = 1.4
    style_run(p.add_run(text), 9, KAI, TNR, color=RGBColor(0x80, 0x80, 0x80))


# ================= 题名区 =================
p = para(align=CENTER, indent=False, before=0, after=5, spacing=1.2)
style_run(p.add_run("多特征融合的轻量化"), 22, SONG, TNR, True)
style_run(p.add_run("U-Net"), 22, SONG, TNR, True)
style_run(p.add_run(" SAR 影像洪水淹没区提取方法"), 22, SONG, TNR, True)

p = para(align=CENTER, indent=False, after=3, spacing=1.2)
style_run(p.add_run("郭思宇"), 14, KAI, TNR)
style_run(p.add_run("1"), 7.5, KAI, TNR).font.superscript = True
style_run(p.add_run("，×××"), 14, KAI, TNR)
style_run(p.add_run("1"), 7.5, KAI, TNR).font.superscript = True

p = para(align=CENTER, indent=False, after=8, spacing=1.2)
style_run(p.add_run("（上海师范大学 信息与机电工程学院，上海 201418）"), 9, KAI, TNR)

# 摘要
p = para(indent=False, after=3, spacing=1.36, size=9)
style_run(p.add_run("摘要："), 9, HEI, TNR, True)
style_run(p.add_run(
    "针对合成孔径雷达（SAR）影像洪水淹没区提取中斑点噪声强、边界模糊及山体阴影与水体易混淆的问题，"
    "提出一种多特征融合的轻量化U-Net方法。以深度可分离卷积替换编解码路径中的标准卷积，将参数量降至原始"
    "U-Net的13.7%；融合后向散射、GLCM纹理与DEM地形特征构成9通道输入，为区分水体与阴影提供几何先验。"
    "在覆盖11个地区的Sen1Floods11数据集上开展实验，5次独立训练的测试集均值为：总体精度96.02%，"
    "Kappa系数0.782，IoU为67.18%，精确率86.80%，召回率74.85%；IoU较SDWI阈值法和原始U-Net分别提升"
    "38.50和2.05个百分点，而参数量与浮点运算量分别仅为原始U-Net的13.7%和22.6%；与加载ImageNet"
    "预训练权重的U-Net++和DeepLabV3+相比，IoU仍分别高出1.32和1.18个百分点，参数量仅为其4.7%和2.6%。"
    "消融实验表明，纹理与地形两组特征单独使用时IoU分别提高"
    "1.70和1.62个百分点；仅使用25%的训练切片时IoU仍达66.21%；二值化阈值在0.30~0.70内变动时"
    "IoU波动不超过1.1个百分点。"
    "结果表明该方法能在地形先验的约束下减少阴影误分，以更小的模型规模取得更高的提取精度。"), 9, KAI)

p = para(indent=False, after=2, spacing=1.36, size=9)
style_run(p.add_run("关键词："), 9, HEI, TNR, True)
style_run(p.add_run("洪水淹没范围提取；合成孔径雷达；深度学习；U-Net；多特征融合；地形特征"), 9, KAI)

p = para(indent=False, after=2, spacing=1.4, size=9)
style_run(p.add_run("中图分类号："), 9, HEI, TNR, True)
style_run(p.add_run("TP751；TP79　　"), 9)
style_run(p.add_run("文献标志码："), 9, HEI, TNR, True)
style_run(p.add_run("A"), 9)

# 英文部分
p = para(align=CENTER, indent=False, before=9, after=4, spacing=1.2)
style_run(p.add_run("A Lightweight Multi-feature Fusion U-Net for Flood "
                    "Inundation Mapping from SAR Imagery"), 14, TNR, TNR, True)

p = para(align=CENTER, indent=False, after=2, spacing=1.2)
style_run(p.add_run("GUO Siyu"), 11, TNR, TNR)
style_run(p.add_run("1"), 7.5, TNR, TNR)
style_run(p.add_run(", ×××"), 11, TNR, TNR)
style_run(p.add_run("1"), 7.5, TNR, TNR)

p = para(align=CENTER, indent=False, after=6, spacing=1.2)
style_run(p.add_run("(College of Information, Mechanical and Electrical Engineering, "
                    "Shanghai Normal University, Shanghai 201418, China)"), 9, TNR, TNR)

p = para(indent=False, after=3, spacing=1.32, size=9, en=TNR)
style_run(p.add_run("Abstract: "), 9, TNR, TNR, True)
style_run(p.add_run(
    "Synthetic aperture radar (SAR) provides all-weather observations for flood monitoring, yet "
    "speckle noise, blurred boundaries and shadow confusion limit the accuracy of inundation "
    "mapping. A lightweight U-Net with multi-feature fusion is proposed. Depthwise separable "
    "convolution replaces the 3×3 standard convolution in both the encoder and the decoder, "
    "reducing the parameters to 13.7% of the original U-Net. Backscatter coefficients, gray-level "
    "co-occurrence matrix textures and DEM-derived terrain features are normalized and "
    "concatenated into a 9-channel input, providing terrain priors that separate water from "
    "shadow. Experiments on the Sen1Floods11 dataset covering 11 regions are averaged over five "
    "independent training runs and give an overall accuracy of 96.02%, a Kappa coefficient of "
    "0.782, an IoU of 67.18%, a precision of 86.80% and a recall of 74.85% on the test set; the "
    "IoU is 38.50 and 2.05 percentage points higher than those of the SDWI method and the original "
    "U-Net, respectively, while the parameters and floating-point operations are only 13.7% and "
    "22.6% of the latter; against ImageNet-pretrained U-Net++ and DeepLabV3+, the IoU is still 1.32 "
    "and 1.18 percentage points higher with only 4.7% and 2.6% of their parameters. An ablation shows "
    "that the terrain and texture features account for the improvement: each feature group alone raises "
    "the IoU by 1.70 and 1.62 percentage points, and the IoU remains 66.21% when only 25% of the training chips are "
    "used; shifting the binarization threshold between 0.30 and 0.70 changes the IoU by at most 1.1 "
    "percentage points."),
    9, en=TNR)

p = para(indent=False, after=8, spacing=1.35, size=9, en=TNR)
style_run(p.add_run("Key words: "), 9, TNR, TNR, True)
style_run(p.add_run("flood inundation mapping; synthetic aperture radar (SAR); deep learning; "
                    "U-Net; multi-feature fusion; terrain features"), 9, en=TNR)

# 首页地脚（写在首页页脚里，避免正文排版把它挤到第 2 页）
FOOT_LINES = [
    "基金项目：国家自然科学基金（××××××）；上海市自然科学基金（××××××）",
    "作者简介：郭思宇（2002—），女，硕士研究生，研究方向为遥感图像处理."
    "E-mail：×××@163.com",
    "*通信作者：",
]

# ================= 0 引言 =================
h1("0　引言")

para("洪涝灾害是影响我国范围最广、造成损失最严重的自然灾害之一。受季风气候与河网密布的影响，"
     "长江、珠江等流域在汛期常出现大范围洪水，快速、准确地掌握淹没范围是灾情评估、应急调度"
     "与灾后重建的基础。合成孔径雷达（synthetic aperture radar，SAR）具有全天时、全天候的"
     "对地观测能力，不受云雨天气限制，已成为洪涝灾害应急监测的主要数据源[1]。但SAR采用相干"
     "成像，影像中普遍存在斑点噪声；同时山体阴影、建筑物叠掩等几何畸变区域同样呈现低后向散射"
     "特征，与平静水面在灰度上高度相似，使得仅依赖单一后向散射特征的提取方法在复杂地形区"
     "易出现大量误分[2]。")

para("面向SAR影像的水体提取方法大致可分为3类。第1类是基于水体指数与阈值的提取方法。"
     "徐涵秋[3]提出的改进归一化差异水体指数（MNDWI）在光学影像中得到广泛应用；针对SAR数据，"
     "贾诗超等[4]构建了哨兵一号水体指数（SDWI），通过双极化比值放大水体与陆地的差异，"
     "再结合Otsu等自动阈值分割。此类方法计算效率高，但阈值对入射角、地表粗糙度和成像条件"
     "较为敏感，在斑点噪声强烈的区域易产生破碎图斑。第2类是结合纹理与机器学习特征的分类方法。"
     "孙诚等[5]利用SAR纹理特征结合LightGBM实现了洪水淹没区应急监测，验证了纹理信息对水陆"
     "分离的有效性；王棨等[2]采用面向对象的多特征优化策略，在对象层面筛选特征改善了边界完整性，"
     "但分割尺度与规则仍依赖人工经验。第3类是基于深度学习的语义分割方法。Long等[6]提出的"
     "全卷积网络（FCN）首次实现端到端的像素级分类；Ronneberger等[7]提出的U-Net通过编码-解码"
     "结构与跳跃连接兼顾语义信息与空间细节，成为遥感分割的基线模型；Zhang等[8]将残差单元引入"
     "U-Net得到ResU-Net，缓解了深层网络的退化问题；Wang等[9]将SAR与光学特征送入改进的Swin "
     "Transformer实现多特征融合水体提取；Wang等[10]设计了极轻量U-Net用于多源卫星影像洪水检测。"
     "此外，岳凡等[11]将深度森林引入偏多标记学习，说明集成模型在标注不完整的分类任务中仍具优势。")

para("上述研究仍存在两点不足：一是多数模型直接以单一时相的后向散射影像作为输入，水体与阴影的"
     "混淆未被显式建模，网络只能依赖隐式特征区分二者，在阴影连片区域容易失效；二是为提升精度"
     "而不断加深加宽网络，参数量与过拟合风险同步上升，难以适应灾害应急场景中样本有限、部署条件"
     "受限的实际需求。注意力机制为此提供了新的思路：Hu等[12]提出的压缩-激励"
     "（squeeze-and-excitation，SE）模块通过显式建模通道间的相互依赖实现特征重标定，"
     "Woo等[13]在此基础上引入空间注意力形成CBAM；喻赟等[14]将通道注意力用于级联信道估计，"
     "验证了其在低信噪比条件下的特征筛选能力。同时，Chollet[15] 以深度可分离卷积构建的Xception在"
     "精度基本不降的前提下大幅降低了卷积运算量，为轻量化模型设计提供了基础。这两类改进常被默认有效，"
     "但在样本有限的SAR洪水提取任务中是否仍然成立，需要通过对照实验检验。")

para("基于上述分析，本文以U-Net为骨架，构建面向SAR影像洪水淹没区提取的多特征融合网络，"
     "主要工作如下：1）在编解码路径中用深度可分离卷积替换3×3标准卷积，在保持感受野的同时将"
     "参数量降至原始U-Net的13.7%、浮点运算量降至22.6%；2）将后向散射、GLCM纹理与DEM地形"
     "3类特征归一化后按通道拼接为9通道输入，利用地形先验显式区分低散射水体与山体阴影；"
     "3）在5组随机种子下检验通道注意力与多特征融合的作用，并以3组种子拆分纹理与地形两组特征、"
     "考察训练样本量对精度的影响。在Sen1Floods11数据集"
     "（覆盖11个地区、446幅Sentinel-1切片）上的实验表明，该方法测试集总体精度达96.02%，"
     "Kappa系数为0.782，IoU为67.18%，较原始U-Net提升2.05个百分点，且在丘陵河谷等阴影干扰"
     "强烈的区域提升达10.02个百分点。")

# ================= 1 研究方法 =================
h1("1　研究方法")

h2("1.1　总体技术流程")
para("本文方法的总体技术流程如图1所示，包括SAR数据预处理、多特征构建、改进U-Net分割和结果"
     "后处理4个环节。首先获取Sen1Floods11数据集提供的Sentinel-1 GRD切片，其已完成辐射定标、"
     "地形校正并转换为分贝后向散射系数；考虑到斑点噪声的抑制交由网络在特征空间完成，本文不再"
     "施加Lee等前置滤波，以免损失水体边界的高频信息；然后由预处理结果分别提取后向散射、"
     "GLCM纹理和DEM地形3类特征，经归一化后按通道拼接为9通道输入张量；再由改进U-Net输出逐像元"
     "的洪水概率；最后以0.5为阈值二值化，并通过形态学开闭运算和小面积图斑剔除得到最终淹没范围。")
add_figure(FIG1, 13.6)
caption("图1　本文方法总体技术路线")

h2("1.2　多特征构建")
h3("1.2.1　后向散射特征")
para("平静水面在微波波段近似镜面反射，入射能量大多背离雷达方向，后向散射很弱，在SAR影像中表现为明显的低后向散射区。"
     "本文使用Sen1Floods11提供的Sentinel-1 VV和VH双极化影像，其后向散射系数以分贝形式存储，"
     "式（1）给出线性值与分贝值的换算关系：")
equation(EQ1, 1)
para("式中：*{σ}为线性后向散射系数；下标dB表示对应的分贝值，单位为dB。"
     "受入射角与地表粗糙度影响，单一极化的绝对散射强度在整景影像内并不稳定，同一地物在近距端"
     "与远距端的灰度差异可达6 dB以上。为此进一步构造双极化比值特征，见式（2）：")
equation(EQ2, 2)
para("式中*{R}为VH与VV的分贝差。平静水面在两种极化下均接近镜面反射，比值接近0 dB；植被冠层的"
     "体散射使VH相对增强，比值偏高；建筑物二次散射以VV为主，比值偏低。该比值对入射角变化的"
     "敏感性低于单极化绝对强度，可在一定程度上削弱成像几何差异带来的影响。")

h3("1.2.2　纹理特征")
para("斑点噪声使单个像元的后向散射值存在较大随机起伏，但水体在邻域内仍保持低方差、低对比度的"
     "匀质结构，这与山体阴影（通常伴随强梯度边缘）和植被区（随机散射体）存在差异。因此采用"
     "灰度共生矩阵（gray level co-occurrence matrix，GLCM）描述局部纹理。计算时将影像量化至"
     "32级灰度，滑动窗口取5×5，步距为1个像元，统计0°、45°、90°、135° 4个方向的共生矩阵计数"
     "并累加，以降低方向敏感性；选取均值、对比度、相关性和熵4个统计量：均值反映局部散射水平的"
     "集中程度；对比度反映邻域灰度变化幅度；相关性反映像元间的线性依赖关系；熵反映纹理的复杂程度。"
     "水体通常表现为低均值、低对比度和低熵，而城镇建筑区与山体阴影的边缘具有明显更高的对比度与熵值。")

h3("1.2.3　地形辅助特征")
para("山体阴影由地形遮蔽造成，其成像几何决定了阴影区必然位于背坡面，且与坡向、雷达视向的关系密切。"
     "本文引入公开DEM瓦片服务提供的高程数据（约19 m，由SRTM等公开高程数据合成），计算高程*{H}与坡度*{S}两个地形"
     "特征：洪水淹没区通常位于河谷底部，高程低、坡度缓；山体阴影虽同为低后向散射，但其所在位置的"
     "坡度和相对高程显著更高。将两类地形特征与后向散射特征联合输入网络，可为网络提供区分水体与"
     "阴影的显式几何约束，而不必依赖网络从强度数据中自行推断。")

h3("1.2.4　特征归一化")
para("3类特征的量纲与取值范围差异显著：后向散射系数约为−25~0 dB，GLCM统计量随窗口位置剧烈变化，"
     "DEM高程可达数百米。若直接拼接，梯度更新将被数值较大的通道主导。为此按式（3）将各通道线性"
     "归一化至[−1, 1]：")
equation(EQ3, 3)
para("式中：*{x}与*{x̃}分别为归一化前后的特征值；*{x}_{min}、*{x}_{max}为该通道在训练集上的1%和99%分位数，"
     "以避免极值压缩动态范围。验证集与测试集沿用训练集统计量，防止信息泄漏。")

h2("1.3　改进U-Net网络")
h3("1.3.1　深度可分离卷积")
para("标准3×3卷积同时对空间与通道维度进行联合运算，参数量为9*{C}_{in}*{C}_{out}。深度可分离卷积将其分解为"
     "逐通道的深度卷积与1×1逐点卷积两步，见式（4）：")
equation(EQ4, 4)
para("式中：DConv3×3(·)表示对每个输入通道独立卷积的深度卷积；Conv1×1(·)表示负责通道间信息"
     "交互的逐点卷积。二者参数量之和为9*{C}_{in}+*{C}_{in}*{C}_{out}，与标准卷积之比约为1/*{C}_{out}+1/9，当*{C}_{out}较大时"
     "压缩比接近9倍。本文在编码器与解码器的特征提取阶段统一采用深度可分离卷积，仅首层与输出层"
     "保留标准卷积，模型参数量由7.77×10⁶降至1.07×10⁶，仅为原始U-Net的13.7%。"
     "该替换以容量换部署可行性，其对精度的影响由第2.4节的消融实验检验。")

h3("1.3.2　网络结构与跳跃连接")
para("网络整体沿用U-Net的对称编码-解码结构，如图2所示。编码器含4个下采样阶段，各阶段由两组"
     "“深度可分离卷积+批归一化+ReLU”构成，通道数依次为32、64、128、256，"
     "经最大池化降采样后在16×16×512的瓶颈层完成全局语义聚合。解码器通过转置卷积逐级上采样，"
     "与同尺度编码特征在通道维拼接后经卷积融合，最终由1×1卷积与Sigmoid函数输出逐像元洪水概率。")
add_figure(FIG2, 13.4)
caption("图2　改进U-Net网络结构")
para("跳跃连接是U-Net保持边界细节的关键：编码器浅层特征保留了水陆交界处的强梯度信息，深层特征"
     "则携带语义判别能力。本文将跳跃连接应用于全部4个尺度层级，并在拼接后紧接一组深度可分离卷积，"
     "使网络在恢复淹没范围位置信息的同时保留较精细的岸线形态。")

h2("1.4　损失函数与后处理")
para("实验数据中水体像元约占总像元的10.5%，正负样本明显不均衡。若仅使用二分类交叉熵，网络倾向于将"
     "边界像元判为背景。为此采用交叉熵与Dice损失的加权组合，见式（5）和式（6）：")
equation(EQ8, 5)
equation(EQ9, 6)
para("式中：*{N}为参与训练的像元数；*{y}_{i}为真值标签；*{p}_{i}为预测为水体的概率；*{X}、*{Y}分别为预测结果与"
     "真值的水体像元集合；*{λ}为平衡系数，取0.5。交叉熵提供稳定的逐像元梯度，Dice损失直接优化"
     "区域重叠度，二者互补。")
para("分割结果经0.5阈值二值化后，采用3×3结构元进行一次开运算与一次闭运算，去除孤立噪点并填补"
     "内部空洞；随后剔除面积小于100个像元（约0.01 km²）的图斑。该阈值依据研究区最小有意义"
     "淹没地物（如鱼塘、沟渠）的尺度确定。")

# ================= 2 实验与分析 =================
h1("2　实验与分析")

h2("2.1　研究区与实验数据")
para("实验数据采用公开的Sen1Floods11洪水数据集[16]。该数据集基于Sentinel-1 GRD影像构建，"
     "覆盖美国、印度、巴拉圭、加纳、斯里兰卡、西班牙、湄公河流域、巴基斯坦、索马里、尼日利亚与"
     "玻利维亚共11个地区，包含446幅512×512像元、10 m分辨率的VV+VH双极化切片。切片所涉区域"
     "下垫面涵盖平原河网、丘陵河谷与城镇边缘等多种类型，洪泛事件分散于不同年份与季节，"
     "较单一流域影像更能检验方法的区域适应性。数据集的影像、标签与官方划分可从"
     "https://github.com/cloudtostreet/Sen1Floods11 获取。")
para("采用数据集的官方划分，训练集252幅、验证集89幅、测试集90幅；玻利维亚的15幅切片因标签"
     "覆盖不全，未纳入训练与评价。标签为人工勾绘的水体掩膜，无标注像元以无效值标记，"
     "不参与损失计算与精度统计。地形特征取自公开DEM瓦片服务（缩放级别13，空间分辨率约19 m），"
     "先按切片范围拼接，在投影坐标系下计算坡度，再重采样至切片所在的10 m格网。")
para("每个512×512切片按2×2不重叠划分为4幅256×256样本，得到训练样本1 008幅、验证样本356幅、"
     "测试样本360幅。训练阶段在切片上随机裁剪256×256子图并施加几何与强度增强；验证与测试阶段"
     "使用固定四象限子图，逐切片汇总像元统计精度，以免子图边界与增强操作干扰评价结果。")

h2("2.2　实验设置与评价指标")
para("实验基于PyTorch 2.5.1框架实现，硬件平台为NVIDIA RTX 4090 GPU（48 GB显存），"
     "混合精度训练。训练采用Adam优化器，初始学习率为1×10⁻³，按余弦退火衰减至1×10⁻⁵，"
     "批大小为16，训练轮次上限为80，并采用早停策略（验证集IoU连续10个epoch不提升即终止）。"
     "数据增强包括水平与垂直翻转、90°旋转以及随机伽马变换（0.8~1.2，对3个后向散射通道施加），"
     "以提升模型对不同成像条件的适应性。")
para("对比方法包括SDWI阈值法（阈值由Otsu法自动确定）、随机森林（输入为同一组9通道特征，树数量"
     "500）、仅以后向散射为输入的原始U-Net基线，以及U-Net++与DeepLabV3+两种现代分割网络（同样"
     "输入9通道特征，骨干分别取ResNet-34与ResNet-50并加载ImageNet预训练权重）。为保证公平，各方法在同一测试集上评价，各深度"
     "模型在同一训练集上以相同轮次、输入尺寸与数据增强设置训练；考虑到单次训练的随机波动，"
     "所有深度模型均以5个随机种子（42—46）独立训练，并按均值±标准差报告结果。参数量由PyTorch"
     "统计、浮点运算量由thop工具统计，推理时间在批大小为1的条件下取100次前向的平均值。")
para("精度评价采用总体精度（overall accuracy，OA）、Kappa系数、交并比（intersection over "
     "union，IoU）与召回率（recall），其中IoU与召回率按式（7）计算：")
equation(EQ10, 7)
para("式中：TP、FP、FN分别为水体类的真正例、假正例与假负例。为便于复核，本文的代码、数据划分、训练与评估脚本以及逐项"
     "实验结果的汇总文件公开于 https://github.com/Siyu-code-oss/sar-flood-seg；训练权重与"
     "测试集特征文件体积较大，可向作者索取。")

h2("2.3　精度对比结果")
para("各方法在测试集上的精度对比如表1所示，其中深度模型的数值为5次独立训练（随机种子42—46）"
     "的均值±标准差。")
caption("表1　不同方法洪水提取精度对比", before=4, after=2, keep_next=True)
three_line(
    ["方法", "OA/%", "Kappa", "IoU/%", "召回率/%", "精确率/%", "参数量/10⁶"],
    [["SDWI", "81.97", "0.352", "28.68", "66.64", "33.48", "—"],
     ["随机森林", "95.65", "0.749", "62.97", "68.01", "89.47", "—"],
     ["U-Net", "95.62±0.07", "0.764±0.001", "65.13±0.11", "75.30±1.22", "82.87±1.46", "7.77"],
     ["U-Net++", "95.84±0.06", "0.771±0.005", "65.86±0.68", "73.87±1.59", "85.91±1.24", "22.54"],
     ["DeepLabV3+", "95.85±0.08", "0.772±0.004", "66.00±0.49", "74.09±0.96", "85.82±1.14", "40.37"],
     ["本文方法", "96.02±0.09", "0.782±0.005", "67.18±0.66", "74.85±1.53", "86.80±1.49", "1.07"]],
    [2.35, 2.05, 2.15, 2.05, 2.05, 2.1, 1.85], fsize=8.5)
para("注：SDWI与随机森林为确定性方法，不涉及随机种子；U-Net++编码器为ResNet-34、DeepLabV3+编码器"
     "为ResNet-50，二者均使用ImageNet预训练权重，本文方法与U-Net均从头训练。",
     size=9, indent=False, before=2, after=6)
para("由表1可见，本文方法总体精度、Kappa系数与IoU均取得最优。SDWI阈值法的总体精度为81.97%，"
     "但其IoU仅28.68%，精确率仅33.48%，说明低后向散射区中，山体阴影与建筑背坡被大量误判为"
     "水体，斑点噪声又使图斑破碎，漏分与误分并存。随机森林引入纹理与地形特征后总体精度提升至"
     "95.65%，精确率达89.47%，但由于逐像元独立分类缺乏空间上下文约束，细窄河道与岸线处漏分"
     "明显，召回率仅68.01%，IoU为62.97%。原始U-Net的召回率为75.30%，水体主体较为完整，"
     "但仅以3个后向散射通道作为输入时，网络难以从数据中自发学到区分阴影的几何线索，"
     "精确率降至82.87%，IoU为65.13%。", before=6)
para("本文方法总体精度达96.02%，较原始U-Net提升0.40个百分点，IoU提升2.05个百分点，Kappa系数"
     "为0.782。与原始U-Net相比，召回率基本持平（74.85%对75.30%），精确率则由82.87%提升至"
     "86.80%，说明精度的增益主要来自误分的减少：纹理与地形特征使网络能够把连片阴影和建筑背坡"
     "从水体中排除。5次训练的IoU标准差仅为0.66个百分点，且5次结果（66.36%~67.98%）全部高于"
     "基线5次结果的最高值（65.32%），增益并非随机种子的偶然波动。这一增益方向与洪水应急监测中"
     "“既要少漏、也要少误”的需求一致，因为成片误分同样会误导淹没面积统计与灾情评估。"
     "在模型规模上，本文模型参数量为1.07×10⁶、浮点运算量为6.48 GFLOPs，分别仅为原始U-Net的"
     "13.7%和22.6%，单幅256×256子图的前向时延为2.44 ms。")
para("为进一步检验方法的竞争力，按相同的数据划分、损失函数、优化器与训练轮数加入了两种现代分割"
     "网络作为对照：U-Net++以嵌套稠密跳跃连接替代U-Net的直连跳跃[17]，编码器为ResNet-34；"
     "DeepLabV3+以空洞卷积与空洞空间金字塔池化（ASPP）扩大感受野，编码器为ResNet-50[18]。"
     "为充分利用有限的训练样本，两者均加载ImageNet预训练权重，首层卷积由3通道权重按均值扩展"
     "至9通道；本文方法则从头训练。结果表明，U-Net++与DeepLabV3+的IoU分别为65.86%和66.00%，"
     "仍低于本文方法的67.18%，且参数量分别为本文方法的21.1倍和37.7倍，单幅子图时延为6.4和"
     "7.4 ms。换言之，在不使用预训练、参数量仅为二者4.7%与2.6%的条件下，多特征输入的轻量化"
     "U-Net仍取得了更高的提取精度，说明本任务的主要矛盾在于输入特征能否显式表达“阴影—水体”"
     "差异，而非网络容量。")

h2("2.4　消融实验")
para("为厘清各项改进的贡献，在相同数据划分与训练配置下进行消融实验，结果如表2所示。")
caption("表2　消融实验结果", before=4, after=2, keep_next=True)
three_line(
    ["配置", "OA/%", "Kappa", "IoU/%"],
    [["U-Net（基线，仅3通道）", "95.62±0.07", "0.764±0.001", "65.13±0.11"],
     ["基线+DSConv", "95.61±0.32", "0.768±0.008", "65.59±0.88"],
     ["基线+DSConv+SE", "95.53±0.35", "0.766±0.010", "65.36±1.06"],
     ["基线+DSConv+多特征（本文方法）", "96.02±0.09", "0.782±0.005", "67.18±0.66"],
     ["完整配置（DSConv+SE+多特征）", "95.86±0.18", "0.774±0.011", "66.21±1.40"]],
    [5.4, 2.9, 2.9, 2.8], fsize=8.5)
para("注：基线为表1的原始U-Net；数值为5次独立训练（种子42—46）的均值±标准差。",
     size=9, indent=False, before=2, after=6)
para("以表1中的原始U-Net为基线，单独引入深度可分离卷积后总体精度为95.61%，IoU为65.59%，"
     "较基线提高0.46个百分点，约为其种子标准差（0.88个百分点）的一半，而参数量由7.77×10⁶"
     "降至1.07×10⁶。这说明在本数据规模下模型尚未触及容量瓶颈，深度可分离卷积的作用主要在于"
     "压缩部署开销，而非提升精度；同时也意味着由此释放的容量需要由更具判别性的输入来填充。",
     before=6)
para("在此基础上加入SE通道注意力（压缩—激励：全局平均池化获取通道描述子，经两层全连接与"
     "Sigmoid得到通道权重后逐通道加权[12]）后，IoU为65.36%，低于单独使用深度可分离卷积的"
     "65.59%，且两项的标准差（1.06与0.88个百分点）已覆盖该差异。进一步将压缩比例r取4、8、16"
     "并以9通道输入训练完整配置，IoU分别为66.40%、66.21%和66.95%，标准差为0.49~1.40个百分点，"
     "既无随压缩比例单调变化的趋势，也始终低于不含SE的多特征模型（67.18%）。因此在本文的样本"
     "规模下，通道重标定未能带来可复现的收益，最终模型不包含SE模块。")
para("在保持深度可分离卷积的前提下加入纹理与地形特征后，IoU由65.59%升至67.18%，总体精度由"
     "95.61%升至96.02%，精确率由82.09%升至86.80%，召回率由76.76%变为74.85%，即在召回小幅"
     "下降的同时显著减少了误分；5次训练的IoU波动仅0.66个百分点，增益稳定。将SE与多特征同时"
     "加入（95.86%、66.21%）反而低于仅用多特征的配置，说明在本任务中结构模块的叠加并不能转化"
     "为精度，判别性特征的引入才是增益的主要来源。")

h2("2.5　特征组贡献与训练样本量分析")
para("第2.4节的消融实验表明，在深度可分离卷积骨架上加入纹理与地形特征可带来稳定增益。为区分"
     "两组特征的独立贡献，固定网络骨架与训练配置，仅改变输入通道组合进行对照："
     "双极化后向散射（3通道）、双极化+纹理（7通道）、双极化+地形（5通道）以及全部特征（9通道，"
     "即本文方法）。本节新增配置均以3次独立训练（随机种子42—44）评价，作为对照的3通道与9通道"
     "配置同样只取这3个种子，以保证组内可比；结果如表3所示。")
caption("表3　不同特征组合的提取精度对比", before=4, after=2, keep_next=True)
three_line(
    ["输入特征（通道数）", "OA/%", "Kappa", "IoU/%", "精确率/%"],
    [["双极化（3）", "95.58±0.08", "0.764±0.002", "65.17±0.15", "82.12±1.34"],
     ["双极化+纹理（7）", "95.83±0.09", "0.778±0.005", "66.87±0.61", "83.06±0.89"],
     ["双极化+地形（5）", "95.95±0.12", "0.778±0.004", "66.79±0.41", "86.19±1.85"],
     ["双极化+纹理+地形（9，本文方法）", "96.06±0.07", "0.785±0.003", "67.59±0.44", "86.70±1.97"]],
    [5.2, 2.3, 2.6, 2.3, 2.2], fsize=8.5)
para("注：各配置均为深度可分离卷积骨架，仅输入通道不同；数值为3次训练（种子42—44）的均值±标准差。",
     size=9, indent=False, before=2, after=6)
para("由表3可见，仅加入纹理或仅加入地形都能在3通道输入的基础上提高IoU约1.6~1.7个百分点"
     "（66.87%和66.79%对65.17%），两者合并后进一步提高到67.59%：两组特征提供的信息并不完全重复，"
     "合并增益（+2.42个百分点）小于两组单独增益之和（约3.3个百分点），说明二者所纠正的误差有"
     "相当程度的重叠——山体阴影既可依据纹理斑块的均一性被剔除，也可依据坡度与高程的几何关系"
     "被排除。", before=6)
para("两组特征带来的误差结构变化并不相同。纹理组在提高召回率（77.43%对75.96%）的同时将"
     "精确率由82.12%提高到83.06%，主要抑制了斑点噪声引起的碎斑；地形组的精确率提升更明显"
     "（86.19%），代价是召回率下降约1.1个百分点（74.82%），即坡度与高程在排除阴影视作水体的"
     "同时也会误伤部分浅水。9通道模型在总体精度、Kappa系数、IoU与精确率上均为4组对照中的最优，"
     "且保持了与地形组相近的高精确率，是两组特征互补的结果。此外，纹理组与地形组的IoU"
     "增益分别为1.70和1.62个百分点，二者之差远小于种子间波动，不宜据此判断何者更为重要。")
para("实际灾情应急中标注切片往往不足，因此进一步考察训练样本量对精度的影响：将训练集按固定"
     "种子随机抽取25%（63幅）与50%（126幅），两种方法各以3个种子重新训练，结果如表4所示。")
caption("表4　不同训练样本比例下的精度对比", before=4, after=2, keep_next=True)
three_line(
    ["训练样本比例", "U-Net OA/%", "U-Net IoU/%", "本文方法 OA/%", "本文方法 IoU/%"],
    [["25%（63幅）", "95.23±0.16", "63.98±0.32", "95.82±0.15", "66.21±1.39"],
     ["50%（126幅）", "95.26±0.40", "64.46±1.67", "95.91±0.06", "67.32±0.48"],
     ["100%（252幅）", "95.58±0.08", "65.17±0.15", "96.06±0.07", "67.59±0.44"]],
    [3.2, 2.85, 2.85, 2.85, 2.85], fsize=8.5)
para("注：数值为3次独立训练（随机种子42—44）的均值±标准差；25%与50%的抽样种子与训练种子相同，"
     "两种方法在同一种子下使用相同的训练子集。", size=9, indent=False, before=2, after=6)
para("由表4可见，训练切片由252幅减少到63幅时，原始U-Net的IoU由65.17%降至63.98%，本文方法由"
     "67.59%降至66.21%，退化幅度均在1~1.5个百分点，明显小于纹理与地形特征带来的2.42个百分点"
     "增益，说明在本数据规模下精度对训练样本量并不十分敏感。更值得注意的是，本文方法仅用63幅"
     "切片（25%）时IoU为"
     "66.21%，已接近原始U-Net使用全部252幅切片的65.17%，使用126幅（50%）时达67.32%，高于后者"
     "的全量训练结果；两种方法的差距在3个比例下稳定在2.2~2.9个百分点，未随样本减少而收窄。"
     "这表明多特征融合的增益并非依赖大量标注的“数据红利”，在标注稀缺的洪涝事件应急场景中，"
     "其可作为减少人工标注负担的替代手段。", before=6)

h2("2.6　不同下垫面结果分析")
para("将测试集按地表特征划分为平原河段、丘陵河谷和城镇边缘3类，分别统计IoU，结果如表5所示。"
     "划分规则为：非水体像元中VV强反射像元（>−6 dB）占比不低于0.12的切片归为城镇边缘，"
     "其余切片中平均坡度不低于3.2°的归为丘陵河谷，剩余的归为平原河段；3类切片分别为27、27和36幅。")
caption("表5　不同下垫面下IoU对比", before=4, after=2, keep_next=True)
three_line(
    ["区域类型", "样本数", "U-Net IoU/%", "本文方法 IoU/%", "提升/百分点"],
    [["平原河段", "36", "76.02±0.97", "78.42±0.89", "+2.40"],
     ["丘陵河谷", "27", "44.40±1.98", "54.42±1.27", "+10.02"],
     ["城镇边缘", "27", "57.68±0.67", "54.46±1.49", "−3.22"]],
    [2.8, 1.8, 3.0, 3.2, 3.0])
para("注：表中数值为5次独立训练（随机种子42—46）的均值±标准差。",
     size=9, indent=False, before=2, after=6)
para("平原河段地势平坦、水体连片，2种方法均能取得较高精度：原始U-Net的IoU为76.02%，"
     "本文方法为78.42%，提升2.40个百分点，大于两类模型种子间的标准差；逐项看，"
     "精确率由86.65%升至89.99%，召回率基本持平（86.13%对85.94%），说明平坦区地形特征"
     "几乎不提供额外信息，改善主要来自纹理特征对斑点噪声的抑制。", before=6)
para("丘陵河谷区差异最为显著：原始U-Net的IoU仅44.40%，大量背坡阴影被误判为水体；本文方法"
     "提升至54.42%，增幅达10.02个百分点，远大于种子波动，且召回率（57.34%升至63.79%）与精确率"
     "（66.49%升至78.92%）同时上升，表明网络既找回了被阴影掩盖的真实水体，也排除了阴影误分，"
     "坡度与高程特征在此提供了决定性的判别线索。")
para("城镇边缘区则出现反转：本文方法IoU为54.46%，低于原始U-Net的57.68%（−3.22个百分点）。"
     "该区建筑与水体交错、地表异质性强，后续宜配合更高分辨率的地形数据与建筑掩膜使用。")

h2("2.7　可视化结果分析")
para("图3给出3个典型区域的洪水提取结果对比，3行自上而下依次取自印度747992切片（丘陵河谷连片"
     "淹没）、巴拉圭271769切片（平原农田中的狭窄河道）与印度592446切片（城镇边缘的河网交汇）。")
add_figure(FIG3, 13.9)
caption("图3　不同方法洪水提取结果对比", before=4)
para("注：(a) VV后向散射影像；(b) 真值标注；(c) SDWI法；(d) 随机森林；(e) 原始U-Net；"
     "(f) 本文方法。蓝色为水体提取或标注结果。", size=9, indent=False, before=2, after=6)
para("从图3可以看出：SDWI法对阈值十分敏感，在第2行将大片低后向散射的农田与湿地整体"
     "误判为水体，在第1、3行也留下成片孤立碎斑；随机森林法在第2行几乎漏掉整条河道，"
     "在第1行阴影区同样漏分严重；原始U-Net在第1行仍沿阴影带块状误分，第3行支流断续、图斑"
     "偏碎；本文方法在第1行误分明显收敛、图斑完整，在第2行保留了狭窄河道、对低散射农田的"
     "误判面积远小于原始U-Net，第3行则把河网交汇处的细窄支流连成一体。这印证了纹理与地形特征对阴影与湿地误分的"
     "抑制作用。")
para("为进一步量化，对这3个场景逐像元统计精度如表6所示。")
caption("表6　典型区域各方法提取精度对比", before=4, after=2, keep_next=True)
three_line(
    ["场景", "方法", "OA/%", "IoU/%", "召回率/%"],
    [["印度747992\n（丘陵河谷）", "SDWI", "78.97", "54.39", "56.04"],
     ["", "随机森林", "70.58", "35.44", "36.09"],
     ["", "原始U-Net", "68.87±4.37", "31.13±9.92", "31.50±10.17"],
     ["", "本文方法", "78.33±1.49", "53.25±3.71", "55.22±4.46"],
     ["巴拉圭271769\n（平原农田）", "SDWI", "61.06", "1.45", "57.48"],
     ["", "随机森林", "99.07", "23.57", "28.78"],
     ["", "原始U-Net", "92.51±5.17", "10.72±7.48", "61.92±8.81"],
     ["", "本文方法", "99.35±0.04", "49.34±2.07", "63.20±5.12"],
     ["印度592446\n（城镇边缘）", "SDWI", "95.66", "42.02", "91.12"],
     ["", "随机森林", "97.83", "46.03", "53.74"],
     ["", "原始U-Net", "97.88±0.20", "48.11±7.24", "57.51±11.04"],
     ["", "本文方法", "98.10±0.10", "56.49±3.39", "71.88±7.53"]],
    [3.0, 2.0, 3.1, 3.1, 3.4], fsize=8.5, rh=0.60)
para("注：深度模型为5次独立训练（随机种子42—46）的均值±标准差。", size=9, indent=False,
     before=2, after=6)
para("由表6可见，本文方法在3个场景中的IoU均高于原始U-Net，提升幅度分别为22.12、38.62和"
     "8.38个百分点，均明显大于全测试集的2.05个百分点，说明多特征融合的优势在困难场景中更为"
     "突出。与阈值法相比，本文方法在第2、3行的IoU分别为49.34%和56.49%，远高于SDWI的1.45%和"
     "42.02%，因为农田、湿地的低后向散射与水体相近，仅凭后向散射阈值无法区分；在第1行两者"
     "相当（53.25%对54.39%），此时水域连片、阴影有限，阈值法已能稳定分离，本文方法的优势体现"
     "在图斑更完整、孤立碎斑更少。随机森林在这3个场景中表现最弱，说明缺乏空间上下文约束的"
     "逐像元分类难以处理细窄河道与异质地表。", before=6)

h2("2.8　阈值与后处理参数的敏感性")
para("本文的二值化阈值取0.5、最小图斑面积取100像元，均为经验设定。为检验上述结论是否依赖这两个"
     "参数，固定已训练的权重，仅在测试阶段改变阈值与最小图斑面积，对5次训练的预测结果重新统计，"
     "结果如图4所示。阈值由0.30增至0.70时，本文方法的IoU在66.30%~67.35%之间变化，最大波动约"
     "1.0个百分点；原始U-Net在64.80%~65.33%之间变化。两者在各阈值下的高低次序保持不变，本文"
     "方法始终高出至少1.5个百分点，且峰值出现在阈值0.30~0.40附近，0.5并非精调所得的最优点。"
     "最小图斑面积由0增至400像元时，本文方法IoU由67.37%单调降至66.53%，仍高于原始U-Net在二者"
     "各设定下的最高值65.33%。可见方法之间的比较结论不依赖阈值与小图斑剔除参数的具体取值。",
     before=6)
add_figure(FIG4, 13.4)
caption("图4　阈值与最小图斑面积对IoU的影响")

# ================= 3 讨论 =================
h1("3　讨论")
para("本文方法的有效性可从3个层面理解。特征层面：SAR对水体的可观测性本质上依赖介电常数与表面"
     "粗糙度，平静水面镜面反射导致低后向散射，但山体阴影、平滑铺装路面与机场跑道具有相似的散射"
     "行为，单靠强度无法分离；引入坡度与高程后，这一混淆在几何维度上被打破，第2.6节的分组统计"
     "正是这一机制的体现——丘陵河谷区IoU提升10.02个百分点，而城镇边缘区反而下降3.22个百分点，"
     "说明地形先验的价值取决于地形本身是否可靠。结构层面：与Lee滤波等前置去噪手段相比，"
     "本文把去噪交给网络在特征空间完成，避免损失水体边界的高频信息，而真正起作用的机制是"
     "纹理与地形特征提供的统计与几何约束。训练层面：深度可分离卷积将参数量压缩至13.7%，但其单独使用时IoU仅比基线"
     "高0.46个百分点（65.59%对65.13%），说明“压缩容量”本身并不自动转化为泛化收益；只有当模型表达"
     "能力与任务难度相匹配时，减少参数才产生正面作用。这也解释了为何轻量化必须与判别性特征"
     "同步引入，而非单独作为精度手段。第2.5节的样本量对照支持这一判断：本文方法仅用25%的"
     "训练切片时IoU仍达66.21%，接近基线全量训练的水平，且两种方法的差距在25%~100%范围内"
     "稳定在2.2~2.9个百分点，说明其增益来自输入特征的判别性，而非对标注量的依赖。")
para("与已有研究相比，孙诚等[5]以SAR纹理结合LightGBM、Wang等[9]以Transformer自注意力融合多源"
     "特征，都能在各自的实验设置下取得与本文相近的精度，但前者依赖逐像元分类、后者参数量与显存"
     "开销显著更高，均不利于应急场景的快速部署；且各文所用数据与洪泛事件不同，绝对精度不宜直接"
     "比较。本文方法在参数量仅为常规U-Net 13.7%的前提下取得了最高的IoU。")
para("本文方法仍有进一步改进的空间：1）对含沙量高、流速快的浑浊水体，水面布拉格散射增强使后向散射"
     "系数升高，部分开阔水域出现漏分；2）DEM取自空间分辨率约19 m的公开瓦片，与10 m的SAR切片之间存在尺度差异，在坡度"
     "剧变的峡谷段会被放大为地形特征错位；3）数据虽覆盖11个地区，但均为Sentinel-1单传感器、"
     "单一时相影像，跨传感器（如高分三号、TerraSAR-X）与洪水中动态过程的泛化能力尚待检验。"
     "后续工作将引入时序SAR相干性变化检测，利用洪水前后相干性骤降的特性补充强度信息的不足；"
     "同时探索知识蒸馏与通道剪枝，进一步压缩模型规模，以满足星上处理或无人机平台的部署需求。")

# ================= 4 结论 =================
h1("4　结论")
para("针对SAR影像洪水淹没区提取中斑点噪声干扰、边界模糊与阴影混淆的问题，本文提出了一种多特征"
     "融合的轻量化U-Net方法。该方法以深度可分离卷积替代编解码路径中的标准卷积，将参数量降至原始"
     "U-Net的13.7%、浮点运算量降至22.6%；并将后向散射、GLCM纹理与DEM地形特征归一化后拼接为"
     "9通道输入，为网络提供区分水体与山体阴影的几何先验。在覆盖11个地区的Sen1Floods11数据集上"
     "的5次独立训练表明，该方法平均总体精度为96.02%，Kappa系数为0.782，IoU为67.18%，"
     "召回率为74.85%，较SDWI阈值法与原始U-Net分别提升38.50和2.05个百分点，在丘陵河谷区的"
     "IoU提升达10.02个百分点；对同样使用9通道输入、且加载ImageNet预训练权重的U-Net++与"
     "DeepLabV3+，IoU仍分别高出1.32和1.18个百分点，而参数量仅为其4.7%和2.6%。")
para("消融实验表明，精度提升主要来自纹理与地形特征的引入，而非网络结构的改动：深度可分离卷积"
     "将参数量压缩至13.7%的同时精度与基线基本持平（IoU提高0.46个百分点）。"
     "这说明在SAR洪水提取任务中，判别性特征的引入比结构模块的堆叠更为关键。"
     "仅用25%训练切片时本文方法的IoU仍达66.21%，表明该优势并不依赖大规模标注。"
     "本文方法可作为洪涝灾害应急监测中快速获取淹没范围的一种技术手段。后续将围绕时序相干性"
     "变化检测、跨传感器泛化与轻量化部署展开研究。")

# ================= 参考文献 =================
h1("参考文献")
REFS = [
    "MARTINIS S, TWELE A, VOIGT S. Towards operational near real-time flood detection using a "
    "split-based automatic thresholding procedure on high resolution TerraSAR-X data [J]. Natural "
    "Hazards and Earth System Sciences, 2009, 9(2): 303-314.",

    "王棨, 狄立, 张伟剑, 等. 基于面向对象的多特征优化SAR影像洪水提取方法 [J]. 山东农业科学, 2025, 57(2): 142-149.\n"
    "WANG Q, DI L, ZHANG W J, et al. Object-oriented flood extraction from SAR imagery with "
    "optimized multi-features [J]. Shandong Agricultural Sciences, 2025, 57(2): 142-149.",

    "徐涵秋. 利用改进的归一化差异水体指数(MNDWI)提取水体信息的研究 [J]. 遥感学报, 2005, 9(5): 589-595.\n"
    "XU H Q. A study on information extraction of water body with the modified normalized difference "
    "water index (MNDWI) [J]. National Remote Sensing Bulletin, 2005, 9(5): 589-595.",

    "贾诗超, 薛东剑, 李成绕, 等. 基于Sentinel-1数据的水体信息提取方法研究 [J]. 人民长江, 2019, 50(2): 213-217.\n"
    "JIA S C, XUE D J, LI C R, et al. Study on water body information extraction based on Sentinel-1 "
    "data [J]. Yangtze River, 2019, 50(2): 213-217.",

    "孙诚, 沈芳, 唐儒罡. 基于SAR纹理和LightGBM的洪水淹没地区遥感应急监测 [J]. 华东师范大学学报(自然科学版), "
    "2023(3): 82-92.\n"
    "SUN C, SHEN F, TANG R G. Remote sensing emergency monitoring of flood inundation areas based on "
    "SAR texture and LightGBM [J]. Journal of East China Normal University (Natural Science), "
    "2023(3): 82-92.",

    "LONG J, SHELHAMER E, DARRELL T. Fully convolutional networks for semantic segmentation [C]//"
    "Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition. 2015: 3431-3440.",

    "RONNEBERGER O, FISCHER P, BROX T. U-Net: convolutional networks for biomedical image "
    "segmentation [C]//International Conference on Medical Image Computing and Computer-Assisted "
    "Intervention. Cham: Springer, 2015: 234-241.",

    "ZHANG Z, LIU Q, WANG Y. Road extraction by deep residual U-Net [J]. IEEE Geoscience and Remote "
    "Sensing Letters, 2018, 15(5): 749-753.",

    "WANG L, ZHANG Y, LIU H. MSFSwin: a multi-feature fusion water extraction method combining SAR "
    "and an improved Swin Transformer [J]. Journal of Geo-information Science, 2025, 27(7): 1638-1655.",

    "WANG Z, WANG X, LI G. An extremely lightweight U-Net with soft fusion for flood detection using "
    "multi-source satellite images [C]//IGARSS 2023: IEEE International Geoscience and Remote Sensing "
    "Symposium. IEEE, 2023: 5260-5263.",

    "岳凡, 邱峰. 基于深度森林的偏多标记学习方法 [J]. 上海师范大学学报(自然科学版中英文), 2025, 54(5): 568-581.\n"
    "YUE F, QIU F. Partial multi-label learning method based on deep forest [J]. Journal of Shanghai "
    "Normal University (Natural Sciences), 2025, 54(5): 568-581.",

    "HU J, SHEN L, SUN G. Squeeze-and-excitation networks [C]//Proceedings of the IEEE Conference on "
    "Computer Vision and Pattern Recognition. 2018: 7132-7141.",

    "WOO S, PARK J, LEE J Y, et al. CBAM: convolutional block attention module [C]//Proceedings of "
    "the European Conference on Computer Vision. Cham: Springer, 2018: 3-19.",

    "喻赟, 张静. 采用通道注意力机制的RIS辅助MIMO级联信道估计 [J]. 上海师范大学学报(自然科学版中英文), 2024, 53(2): 228-235.\n"
    "YU Y, ZHANG J. Channel estimation for RIS assisted MIMO cascaded channels via attention "
    "mechanism [J]. Journal of Shanghai Normal University (Natural Sciences), 2024, 53(2): 228-235.",

    "CHOLLET F. Xception: deep learning with depthwise separable convolutions [C]//Proceedings of the "
    "IEEE Conference on Computer Vision and Pattern Recognition. 2017: 1251-1258.",

    "BONAFILIA D, TELLMAN B, SMITHYEAR T, et al. Sen1Floods11: a georeferenced dataset to train and "
    "test deep learning flood algorithms for Sentinel-1 [C]//Proceedings of the IEEE/CVF Conference "
    "on Computer Vision and Pattern Recognition Workshops. 2020: 210-211.",

    "ZHOU Z, SIDDIQUEE M M R, TAJBAKHSH N, et al. UNet++: a nested U-Net architecture for medical "
    "image segmentation [C]//Deep Learning in Medical Image Analysis and Multimodal Learning for "
    "Clinical Decision Support. Cham: Springer, 2018: 3-11.",

    "CHEN L C, ZHU Y, PAPANDREOU G, et al. Encoder-decoder with atrous separable convolution for "
    "semantic image segmentation [C]//Proceedings of the European Conference on Computer Vision. "
    "2018: 801-818.",
]
for i, ref in enumerate(REFS, 1):
    lines = ref.split("\n")
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.alignment = JUST
    pf.left_indent = Cm(0.85)
    pf.first_line_indent = Cm(-0.85)
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.line_spacing = 1.1
    style_run(p.add_run("[%d]　" % i), 9, SONG, TNR)
    style_run(p.add_run(lines[0]), 9, SONG, TNR)
    for extra in lines[1:]:
        p2 = doc.add_paragraph()
        pf2 = p2.paragraph_format
        pf2.alignment = JUST
        pf2.left_indent = Cm(0.85)
        pf2.first_line_indent = Cm(0)
        pf2.space_before = Pt(0)
        pf2.space_after = Pt(2)
        pf2.line_spacing = 1.1
        style_run(p2.add_run(extra), 8.5, SONG, TNR)

# ---------- 页脚页码 ----------
def page_field(p):
    p.paragraph_format.alignment = CENTER
    r = p.add_run()
    fld1 = OxmlElement("w:fldChar"); fld1.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText"); instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    fld2 = OxmlElement("w:fldChar"); fld2.set(qn("w:fldCharType"), "end")
    r._r.append(fld1); r._r.append(instr); r._r.append(fld2)
    style_run(r, 9, SONG, TNR)


page_field(sec.footer.paragraphs[0])

# ---------- 首页页脚：基金/作者简介 + 页码 ----------
sec.different_first_page_header_footer = True
sec.footer_distance = Cm(0.75)
fp = sec.first_page_footer.paragraphs[0]
fp.paragraph_format.alignment = LEFT
fp.paragraph_format.first_line_indent = Pt(0)
fp.paragraph_format.space_before = Pt(0)
fp.paragraph_format.space_after = Pt(0)
fp.paragraph_format.line_spacing = 1.0
for i, line in enumerate(FOOT_LINES):
    style_run(fp.add_run(line), 9, SONG, TNR)
    if i < len(FOOT_LINES) - 1:
        fp.add_run().add_break()
page_field(sec.first_page_footer.add_paragraph())

doc.save(OUT)
print("saved:", OUT)

