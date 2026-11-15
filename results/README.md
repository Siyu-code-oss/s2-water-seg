# results/

- `f{0-4}_{tag}.done`：每折最优权重对应的验证指标（IoU）与 val_scenes
- `summary.json`：各配置 5 折均值/标准差
- `per_scene.json`：33 个场景逐场景 IoU（各配置）
- `cost.json`：参数量、FLOPs、单幅时延
- `external.json`：WorldFloods 5 个外部事件的 IoU
- `threshold_baselines.json` / `threshold_fixed.json`：Otsu 与固定 0 阈值的 NDWI/MNDWI 结果
- `p4_result.json`：坡面滞蓄与 SHAP 结果

tag 含义：base=本文，ndwi=+NDWI，std=标准卷积，b4=前4波段，rgbnir=RGB+NIR，
bce/focal=损失函数，unetpp/deeplab/segformer=基线，s256=不重叠切块。
