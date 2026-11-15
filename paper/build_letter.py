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
p("现向贵刊投稿论文《多波段Sentinel-2影像的轻量化U-Net地表水体提取与鄱阳湖应用》，"
  "恳请审阅。", after=10)

p("本研究提出一种以深度可分离卷积为骨干、以Sentinel-2全13个光谱波段为输入的轻量化U-Net，"
  "在FloodsNet的USGS子集上按场景实施5折交叉验证，IoU达87.66%，优于NDWI阈值法（80.44%）"
  "及所比较的深度基线，且折间标准差最小；模型无需微调即可迁移至鄱阳湖，支撑汛期水体动态分析。", after=10)

p("本文的主要贡献包括：", after=4)
for t in ["1）系统量化了Sentinel-2不同波段组合的精度贡献：缺失近红外时IoU降至79.20%，"
          "而仅用RGB+近红外四波段即可达到87.86%、与13波段相当，说明判别信息在近红外已基本饱和，"
          "为轻量化部署的波段裁剪提供了依据；",
          "2）以深度可分离卷积压缩参数，参数量仅为标准U-Net的13.7%时精度不降反升；",
          "3）按场景划分5折交叉验证，避免样本泄漏，并公开代码与数据划分；",
          "4）结合土地利用与地形开展坡面滞蓄情景评估，使方法从提取延伸到应用。"]:
    p(t, after=4)

p("本文为原创研究，未在其他期刊发表或同时投稿。全体作者已阅读并同意投稿，"
  "不存在利益冲突。代码与数据划分已在公开仓库发布（https://github.com/Siyu-code-oss/s2-water-seg），"
  "训练权重与影像数据因体积较大，可应要求提供。", after=10)

p("感谢审阅，期待您的回复。", after=12)
p("此致", after=2)
p("敬礼！", after=16)
p("郭思宇", after=2)
p("上海师范大学 信息与机电工程学院", after=2)
p("　　　　年　　月", after=2)

doc.save(OUT)
print("saved:", OUT)
