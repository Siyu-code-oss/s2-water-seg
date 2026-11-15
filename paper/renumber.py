# -*- coding: utf-8 -*-
"""Renumber citations by first appearance and reorder the reference list."""
import re

CIT = re.compile(r"\[(\d+)(?:\s*[-–]\s*(\d+))?\]")


def _expand(token):
    inner = token[1:-1]
    out = []
    for part in re.split(r"[,，\-–]", inner):
        part = part.strip()
        if part.isdigit():
            out.append(int(part))
    return out


def renumber(doc, refs):
    order = []
    for p in doc.paragraphs:
        for m in CIT.finditer(p.text):
            for n in _expand(m.group(0)):
                if n not in order:
                    order.append(n)
    mapping = {old: i + 1 for i, old in enumerate(order)}

    def fix(text):
        def rep(m):
            nums = [mapping.get(n, n) for n in _expand(m.group(0))]
            # collapse consecutive runs into a-b
            nums = sorted(set(nums))
            if len(nums) > 2 and nums[-1] - nums[0] == len(nums) - 1:
                return "[%d-%d]" % (nums[0], nums[-1])
            return "[" + ",".join(str(n) for n in nums) + "]"
        return CIT.sub(rep, text)

    for p in doc.paragraphs:
        for r in p.runs:
            if "[" in r.text and re.search(r"\[\d", r.text):
                r.text = fix(r.text)

    return [refs[o - 1] for o in order], mapping


def apply_map(doc, mapping):
    """Apply an explicit old->new citation mapping to every run."""
    def fix(text):
        def rep(m):
            nums = [mapping.get(n, n) for n in _expand(m.group(0))]
            nums = sorted(set(nums))
            if len(nums) > 2 and nums[-1] - nums[0] == len(nums) - 1:
                return "[%d-%d]" % (nums[0], nums[-1])
            return "[" + ",".join(str(n) for n in nums) + "]"
        return CIT.sub(rep, text)
    for p in doc.paragraphs:
        for r in p.runs:
            if "[" in r.text and re.search(r"\[\d", r.text):
                r.text = fix(r.text)
