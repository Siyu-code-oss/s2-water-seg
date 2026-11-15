# -*- coding: utf-8 -*-
"""Build the cover letter."""
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt

OUT = r"C:\Users\ttttt\Desktop\学报2\投稿信.docx"
doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
sec.left_margin = sec.right_margin = Cm(2.6)
sec.top_margin = sec.bottom_margin = Cm(2.4)

st = doc.styles["Normal"]
st.font.name = "Times New Roman"
st.font.size = Pt(10.5)


def p(text="", bold=False, size=10.5, after=6, align=WD_ALIGN_PARAGRAPH.LEFT):
    par = doc.add_paragraph()
    par.alignment = align
    par.paragraph_format.space_after = Pt(after)
    par.paragraph_format.line_spacing = 1.35
    r = par.add_run(text)
    r.font.size = Pt(size)
    r.font.bold = bold
    return par


p("尊敬的编辑：", after=10)
p("您好！", after=10)
p("现向贵刊投稿论文《多波段Sentinel-2影像的轻量化U-Net地表水体提取与鄱阳湖应用》，"
  "恳请审阅。", after=10)

p("本研究针对光学遥感洪水制图中水体边界破碎、云覆盖干扰与多波段信息利用不足的问题，"
  "提出一种以深度可分离卷积为骨干、以Sentinel-2全13个光谱波段为输入的轻量化U-Net。"
  "在FloodsNet的USGS子集上按场景实施5折交叉验证，IoU达87.66%，优于NDWI物理阈值法（80.44%）与"
  "两种现代分割网络，且5折标准差最小；"
  "与参数量为其7.3倍的标准U-Net（86.46%）、U-Net++（84.96%）和DeepLabV3+（86.80%）相比，"
  "本文方法在参数量仅1.07×10⁶的条件下取得了更高的精度。模型无需微调即可迁移至鄱阳湖，"
  "并进一步支撑了多时相水体出现频率、坡面滞蓄情景与驱动因子分析。", after=10)

p("本文的主要贡献包括：", after=4)
for t in ["1）系统量化了Sentinel-2不同波段组合的精度贡献：缺失近红外时IoU降至79.20%，"
          "而仅用RGB+近红外四波段即可达到87.86%、与13波段相当，说明判别信息在近红外已基本饱和，"
          "为轻量化部署的波段裁剪提供了依据；",
          "2）以深度可分离卷积压缩参数，在参数量仅为标准U-Net的13.7%时精度不降反升，"
          "为应急场景的快速部署提供了可行方案；",
          "3）采用按场景划分的5折交叉验证，避免同场景样本泄漏导致的精度虚高，"
          "并公开全部代码与数据划分，便于复现；",
          "4）将制图结果与土地利用、地形结合，给出坡面尺度滞蓄供需的情景评估，"
          "使方法从“提取”延伸到“应用”。"]:
    p(t, after=4)

p("本文为原创研究，未在其他期刊发表或同时投稿。全体作者已阅读并同意投稿，"
  "不存在利益冲突。代码与数据划分已在公开仓库发布（https://github.com/Siyu-code-oss/s2-water-seg），"
  "训练权重与影像数据因体积较大，可应要求提供。", after=10)

p("感谢您在百忙之中审阅本文，期待您的回复。", after=16)
p("此致", after=2)
p("敬礼！", after=16)
p("郭思宇", after=2)
p("上海师范大学 信息与机电工程学院", after=2)
p("　　　　年　　月", after=2)

doc.save(OUT)
print("saved:", OUT)
