# -*- coding: utf-8 -*-
"""Remaining body sections and references."""

S3_REST = [
    ("3.2 精度对比", [
        "各方法在5折交叉验证下的结果如表3所示。本文方法的IoU均值为{IoU_BASE}%，"
        "F1为{F1_BASE}%，总体精度为{OA_BASE}%；其中IoU与F1在全部对比方法中最高，总体精度与最优的SegFormer（99.23%）处于同一水平。"
        "值得注意的是，5折之间差异较大（{MIN_FOLD}%~{MAX_FOLD}%），"
        "这源于场景难度本身的不均衡：部分场景水体连片、边界清晰，IoU可达97%以上；"
        "而水体零碎、云掩膜占比高的场景IoU不足80%。因此本文以5折均值作为主结论，"
        "同时给出逐折结果以反映其波动。值得注意的是，本文方法的标准差为9.60个百分点，"
        "在全部对比方法中最小（其余为10.23~23.87个百分点），说明其精度在不同场景组合下更为稳定。",
        "与参数量为7.78×10⁶的标准U-Net相比，本文模型参数量仅为其13.7%，"
        "IoU却高出约1.2个百分点，说明在本任务中限制精度的是输入信息的判别性而非网络容量。"
        "U-Net++与DeepLabV3+的参数量分别为本文模型的24.4倍与25.0倍，"
        "其IoU均值分别为{U_IoU}%与{D_IoU}%，均低于本文方法。SegFormer（MiT-B0）作为轻量化Transformer基线，"
        "参数量为本文的5.2倍，IoU却低0.67个百分点，说明在水体分割这类语义简单、以光谱特征为主的任务中，"
        "卷积结构的效率优于Transformer结构。",
    ]),
    ("3.3 消融实验", [
        "为厘清各项改进的贡献，表4给出两组消融结果。其一，仅使用前4个波段时IoU降至{B4_IoU}%，"
        "较13个光谱波段全部输入时下降约{B4_DROP}个百分点。由于该配置不含近红外波段，"
        "其精度骤降主要源于核心判别波段的缺失；而仅保留B2、B3、B4、B8四个波段时IoU为{RGB_IoU}%，"
        "与13波段输入（{IoU_BASE}%）相当，说明在本文数据与模型容量下，水体的判别信息主要由近红外波段提供，"
        "进一步增加的红边与短波红外波段未带来稳定增益；以33个场景为样本的配对Wilcoxon检验也表明，"
        "13波段与RGB+近红外配置的逐场景IoU差异无统计学显著性（p=0.54）。其二，加入NDWI通道后（17通道），"
        "IoU为{NDWI_IoU}%，较基准{NDWI_DELTA}个百分点，"
        "表明显式的水体指数与光谱波段存在互补，但其增益小于波段本身的作用——这一结果与“光谱信息是基础、"
        "指数是辅助”的判断一致。",
        "其三，将深度可分离卷积换回标准卷积（参数量由1.07×10⁶增至7.78×10⁶）后，"
        "IoU反而略低（{STD_IoU}%），说明轻量化并未损失精度，反而可能因减少过拟合而受益。",
        "最后，损失函数方面，单一交叉熵与Focal损失的IoU分别为{BCE_IoU}%与{FOCAL_IoU}%，"
        "与交叉熵+Dice组合（{IoU_BASE}%）的差异均小于折间标准差。单一交叉熵虽略高约0.9个百分点，"
        "但从机制上看，Dice损失直接优化区域重叠度，理论上更有利于小目标与岸线的收敛，"
        "故本文最终采用组合损失，并在表4中同时列出两者结果以供比较。",
    ]),
    ("3.4 跨数据集迁移", [
        "为检验模型的可迁移性，将USGS上训练得到的5个折模型直接用于鄱阳湖影像推理，"
        "不进行任何微调。推理前按训练时的波段定义组织输入：13个光谱波段直接对应，"
        "3个质量波段在Sentinel-2 L2A产品中不存在，按训练数据的实际取值补零；"
        "云像元依据SCL分类（云影、云、卷云）在统计中剔除。",
        "研究区按20 m重采样、1 km网格聚合，6期影像的水体比例如表5所示；其中2019年7月云覆盖严重，"
        "有效像元仅28.3%，该期水体比例的参考性相对较弱。"
        "2019—2024年间，湖区水体比例在21.26%~47.52%之间变化：2022年7月与2024年7月偏高，"
        "对应流域性洪水；2023年9月偏低，与当年偏枯的水情相符。"
        "这一变化规律与公开报道的鄱阳湖水情一致，说明模型在没有本地标注的条件下仍能给出物理上合理的制图结果。",
    ]),
]

S4 = [
    ("4.1 多时相水体出现频率", [
        "所用6期影像均取自汛期（6—9月）。将6期水体掩膜的叠加结果按有效观测次数归一化，得到逐像元的水体出现频率，"
        "其思路与Pekel等[24]基于全球地表水产品的频率统计一致，区别在于本文频率由学习型分割结果累计得到。"
        "频率如图6所示，湖区主体频率接近1，说明这些区域在全部有效观测中均为水体；"
        "湖滨滩地与入湖河口频率介于0.2~0.6之间，是洪水的往复消长带；"
        "频率大于0.5的区域占研究区的27.4%。图中白色区域为6期中均被云遮挡、无有效观测的区域，"
        "统计时已从分母中剔除而非记为未淹没。",
    ]),
    ("4.2 坡面尺度滞蓄供需", [
        "为初步评估研究区下垫面的雨洪消纳能力，在坡面尺度（仅计产流与地表滞蓄，不含河湖库容调蓄）"
        "以1 km网格开展情景计算。曲线数（curve number，CN）按地类赋值（林地60、草地70、耕地78、建设用地92、湿地85），"
        "该范式与生态水文调节服务的量化方法一致[25]，"
        "按网格内各地类占比加权；设计降雨取100 mm、前期土壤湿润程度为中等（AMCⅡ）；"
        "以产流超出滞蓄20%作为赤字阈值。按SCS曲线数法[26]，潜在滞蓄量S与产流量Q分别为："
        "S=25400/CN−254（mm）；当P>0.2S时Q=(P−0.2S)²/(P+0.8S)，否则Q=0；滞蓄量取P−Q，"
        "其中P为设计降雨量（100 mm），0.2S为初损。",
        "结果表明，评价单元的平均产流为53.6 mm、滞蓄为46.4 mm。水体主导单元（水体占比超过50%）"
        "因CN=100必然被判为赤字，但其调蓄作用属流域尺度，不在本情景范围内，统计时予以剔除；"
        "在剔除水体占比超过50%的798个单元后，其余3 279个单元中赤字单元占26.4%，集中分布于湖区周边的耕地与建设用地交错带，"
        "这些区域地势低平、硬化程度较高，坡面滞蓄能力不足以消纳同等降雨下的产流。"
        "需要说明的是，本分析为设计降雨条件下的情景评估，尚未考虑土壤质地与前期湿润状况的空间差异。",
    ]),
("4.3 驱动因子分析", [
        "为识别水体出现频率空间分异的驱动因子，以1 km网格的水体出现频率为因变量，"
        "以各地类比例、高程为自变量，构建随机森林回归模型，并用SHAP[27]（Shapley Additive Explanations）值量化各因子的贡献。"
        "模型5折交叉验证的R²为0.461，属于中等解释力：地类与地形能够解释约一半的空间变异，"
        "其余部分与降水、河网连通性、堤防工程等未纳入的因子有关。因此本文将该部分定位为"
        "“相关性分析”，不对因果关系作进一步推断。",
        "SHAP结果表明（数值为平均绝对SHAP值），高程的贡献最大（0.093），其次为湿地比例（0.082），耕地（0.037）与林地（0.023）次之，"
        "建设用地与裸地贡献较小。这一排序与洪水的物理机制一致：低洼处更易积水，"
        "湿地本身即为洪水的调蓄空间；耕地因多分布于湖滨平原而受灾比例较高，"
        "林地多位于地势较高处，对水体出现频率的直接影响有限。需要说明，上述数值为平均绝对SHAP值，"
        "反映贡献幅度；就方向而言，高程与水体出现频率负相关（图8）（越低越易淹），湿地比例与之正相关。",
    ]),
]

S5 = [
    "本文面向光学遥感地表水体提取，构建了多光谱输入的轻量化U-Net，并在公开数据集与典型湖区上开展了验证。"
    "围绕引言提出的三个问题，主要结论如下：1）输入层面：水体判别信息高度集中于近红外波段，"
    "缺失该波段时IoU降至{B4_IoU}%，而RGB+近红外4波段已达{RGB_IoU}%、与13波段（{IoU_BASE}%）相当，"
    "表明红边与短波红外在本文数据上未带来稳定增益；在此基础上加入NDWI通道可提升至{NDWI_IoU}%，"
    "说明物理指数是比波段堆叠更高效的增量来源。2）结构层面：以深度可分离卷积替换标准卷积后，"
    "参数量降至1.07×10⁶（标准U-Net的13.7%），而IoU从{STD_IoU}%提升至{IoU_BASE}%，"
    "验证了该结构在水体分割任务中的适用性，精度与效率可以兼得。3）应用层面：模型无需微调即可迁移至"
    "鄱阳湖2019—2024年6期汛期影像，水体比例在21.26%~47.52%之间变化，并据此形成"
    "“水体提取—出现频率—滞蓄情景—驱动因子”的完整链条，可为流域洪水风险管理提供参考。",
    "本文的不足在于：训练集仅有33个场景，5折结果的波动较大；驱动因子分析的解释力有限（R²=0.461）；"
    "云覆盖区域在统计中被剔除，未对云下状态进行推断。后续工作将引入时序合成与SAR数据补充，"
    "并尝试地理加权模型以刻画驱动因子的空间非平稳性。",
]

REFS = [
    'BONAFILIA D, TELLMAN B, ANDERSON T, et al. Sen1Floods11: a georeferenced dataset to train and test deep learning flood algorithms for Sentinel-1 [C]//Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition Workshops. 2020: 210-211.',
    'MATEO-GARCIA G, VEITCH-MICHAELIS J, SMITH L, et al. Towards global flood mapping onboard low cost satellites using machine learning [J]. Scientific Reports, 2021, 11: 4659.',
    'MCFEETERS S K. The use of the normalized difference water index (NDWI) in the delineation of open water features [J]. International Journal of Remote Sensing, 1996, 17(7): 1425-1432.',
    '徐涵秋. 利用改进的归一化差异水体指数(MNDWI)提取水体信息的研究 [J]. 遥感学报, 2005, 9(5): 589-595.',
    '陈昊旻. 基于Sentinel-2A/B数据构建水体指数的波段优选 [J]. 自然资源遥感, 2025, 37(2): 64-71.',
    'LONG J, SHELHAMER E, DARRELL T. Fully convolutional networks for semantic segmentation [C]//Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition. 2015: 3431-3440.',
    'RONNEBERGER O, FISCHER P, BROX T. U-Net: convolutional networks for biomedical image segmentation [C]//Medical Image Computing and Computer-Assisted Intervention. Cham: Springer, 2015: 234-241.',
    'ZHOU Z, SIDDIQUEE M M R, TAJBAKHSH N, et al. UNet++: a nested U-Net architecture for medical image segmentation [C]//Deep Learning in Medical Image Analysis and Multimodal Learning for Clinical Decision Support. Cham: Springer, 2018: 3-11.',
    'CHEN L C, ZHU Y, PAPANDREOU G, et al. Encoder-decoder with atrous separable convolution for semantic image segmentation [C]//Proceedings of the European Conference on Computer Vision. 2018: 801-818.',
    'HU J, SHEN L, SUN G. Squeeze-and-excitation networks [C]//Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition. 2018: 7132-7141.',
    'ISIKDOGAN F, BOVIK A C, PASSALACQUA P. Surface water mapping by deep learning [J]. IEEE Journal of Selected Topics in Applied Earth Observations and Remote Sensing, 2017, 10(11): 4909-4918.',
    'DE VRIES B, HUANG C, ARMBRUSTER J, et al. Exploring Sentinel-1 and Sentinel-2 diversity for flood inundation mapping using deep learning [J]. ISPRS Journal of Photogrammetry and Remote Sensing, 2021, 180: 163-173.',
    '邓开元, 任超. 多光谱光学遥感影像水体提取模型 [J]. 测绘学报, 2021, 50(10): 1370-1379.',
    '吴庆双, 汪明秀, 申茜, 等. Sentinel-2遥感图像的细小水体提取 [J]. 遥感学报, 2022, 26(4): 781-794.',
    '刘小燕, 崔耀平, 史志方, 等. GEE平台下多源遥感影像对洪灾的监测 [J]. 遥感学报, 2023, 27(9): 2179-2190.',
    '张兵. 遥感大数据时代与智能信息提取 [J]. 武汉大学学报(信息科学版), 2018, 43(12): 1861-1871.',
    '李德仁, 张良培, 夏桂松. 遥感大数据自动分析与数据挖掘 [J]. 测绘学报, 2014, 43(12): 1211-1216.',
    'TELLMAN B, SULLIVAN J A, KUHN C, et al. Satellite imaging reveals increased proportion of population exposed to floods [J]. Nature, 2021, 596: 80-86.',
    'CHOLLET F. Xception: deep learning with depthwise separable convolutions [C]//Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition. 2017: 1251-1258.',
    'FloodsNet: WorldFloods-USGS-Sen1Floods11 [DS/OL]. Zenodo, 2023[2026-11-15]. https://doi.org/10.5281/zenodo.8298840.',
    '许苗, 李元祥, 钟娟娟, 等. L-UNet: 轻量化云遮挡道路提取网络 [J]. 中国图象图形学报, 2021, 26(11): 3274-3285.',
    'XIE E, WANG W, YU Z, et al. SegFormer: simple and efficient design for semantic segmentation with transformers [C]//Advances in Neural Information Processing Systems 34. 2021: 12077-12090.',
    '赵爽, 李虎, 王瑾, 等. 基于Sentinel-2影像的多种水体指数法提取地表水对比研究 [J]. 遥感技术与应用, 2024, 39(2): 502-513.',
    'PEKEL J F, COTTAM A, GORELICK N, et al. High-resolution mapping of global surface water and its long-term changes [J]. Nature, 2016, 540: 418-422.',
    '孙喆, 张雪葳. 未来极端降水下的山区乡村生态水文调节服务多情景预测 [J]. 风景园林, 2025, 32(3): 102-109.',
    'USDA SOIL CONSERVATION SERVICE. National Engineering Handbook, Section 4: Hydrology [M]. Washington D C: US Government Printing Office, 1972.',
    'LUNDBERG S M, LEE S I. A unified approach to interpreting model predictions [C]//Advances in Neural Information Processing Systems 30. 2017: 4765-4774.',
    '王敬明, 王世新, 王福涛, 等. 基于Sentinel-1 SAR数据洪水淹没提取方法研究 [J]. 灾害学, 2021, 36(4): 214-220.',
    '郭山川, 杜培军, 蒙亚平, 等. 时序Sentinel-1A数据支持的长江中下游汛情动态监测 [J]. 遥感学报, 2021, 25(10): 2127-2141.',
    '吴燕如, 连旭刚, 高玉蓉. 基于哨兵数据相干性的洪水淹没范围确定方法 [J]. 测绘通报, 2022(11): 96-100.',
    '李琦, 郭中华, 李小军, 等. 基于动态增强型的DE-DeepLabV3+多光谱水体分割研究 [J]. 自然资源遥感, 2026, 38(3): 32-41.',
]
