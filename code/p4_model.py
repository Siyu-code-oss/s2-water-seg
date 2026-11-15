# -*- coding: utf-8 -*-
"""Random-forest + SHAP analysis of flood frequency drivers (1 km cells)."""
import json
import os

import numpy as np
import shap
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import KFold, cross_val_score

F2 = os.path.expanduser(os.environ.get("F2_ROOT","~/F2"))
OUT = os.path.join(F2, "runs", "p4")
rows = json.load(open(os.path.join(OUT, "cells.json")))
print("cells", len(rows), flush=True)

FEATS = ["f_water", "f_built", "f_crop", "f_tree", "f_grass", "f_wetland",
         "f_bare", "f_shrub", "elev"]
X = np.array([[r.get(k, 0.0) for k in FEATS] for r in rows], dtype="float32")
y = np.array([r["freq"] for r in rows], dtype="float32")

rf = RandomForestRegressor(n_estimators=500, min_samples_leaf=3,
                           random_state=42, n_jobs=-1)
cv = KFold(5, shuffle=True, random_state=0)
scores = cross_val_score(rf, X, y, cv=cv, scoring="r2")
print("RF R2 folds:", np.round(scores, 3), "mean %.3f" % scores.mean(), flush=True)
rf.fit(X, y)

idx = np.random.RandomState(0).choice(len(X), min(600, len(X)), replace=False)
expl = shap.TreeExplainer(rf)
sv = expl.shap_values(X[idx])
imp = np.abs(sv).mean(0)
order = np.argsort(-imp)
print("SHAP importance:")
for i in order:
    print("  %-10s %.4f" % (FEATS[i], imp[i]), flush=True)

# supply-demand index (SCS-CN, design rainfall 100 mm)
P = 100.0
cn = np.array([r["cn"] for r in rows])
S = 25400.0 / cn - 254.0
Q = np.where(P > 0.2 * S, (P - 0.2 * S) ** 2 / (P + 0.8 * S), 0.0)
supply = P - Q
mismatch = (Q - supply) / P
np.savez(os.path.join(OUT, "p4_result.npz"), X=X, y=y, sv=sv,
         imp=imp, supply=supply, demand=Q, mismatch=mismatch)
res = dict(r2=float(scores.mean()), r2_folds=[float(s) for s in scores],
           shap={FEATS[i]: float(imp[i]) for i in order},
           demand_mean=float(Q.mean()), supply_mean=float(supply.mean()),
           mismatch_mean=float(mismatch.mean()),
           deficit_share=float((mismatch > 0.2).mean()))
json.dump(res, open(os.path.join(OUT, "p4_result.json"), "w"), indent=1)
print("demand %.1f supply %.1f mm  deficit share %.1f%%" % (
    Q.mean(), supply.mean(), 100 * (mismatch > 0.2).mean()), flush=True)
