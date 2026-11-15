# -*- coding: utf-8 -*-
"""Body text and tables of the new manuscript."""
import json
import os

RUNS = r"D:\F2\runs"
P4 = os.path.join(RUNS, "p4")


def load(tag):
    p = os.path.join(RUNS, "metrics_%s.json" % tag)
    if not os.path.exists(p):
        return None
    return json.load(open(p))


def mean(d, k):
    vals = [v[k] for v in d.values()]
    return sum(vals) / len(vals)


def table_rows(tag, name):
    d = load(tag)
    if not d:
        return None
    folds = sorted(d)
    return [name] + ["%.2f" % d[f][k] for f in folds for k in ("IoU", "F1", "OA")], \
        [d[f]["IoU"] for f in folds]
