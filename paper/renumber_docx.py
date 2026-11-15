# -*- coding: utf-8 -*-
"""Renumber citations in a built .docx by first appearance, verify, then replace."""
import re
import shutil
import sys

from docx import Document
from docx.shared import Pt

SRC = r"C:\Users\ttttt\Desktop\学报2\多波段Sentinel-2洪水淹没提取_初稿.docx"
TMP = r"D:\F2\paper\_renum.docx"
CIT = re.compile(r"\[(\d+)(?:\s*[-–]\s*(\d+))?\]")


def expand(tok):
    out = []
    for part in re.split(r"[,，\-–]", tok[1:-1]):
        part = part.strip()
        if part.isdigit():
            out.append(int(part))
    return out


def main():
    doc = Document(SRC)
    paras = list(doc.paragraphs)

    # locate the reference section
    ref_start = None
    for i, p in enumerate(paras):
        if p.text.strip() == "参考文献":
            ref_start = i + 1
            break
    body = [p for p in paras if not p.text.strip().startswith("[")]

    order = []
    for p in body:
        for m in CIT.finditer(p.text):
            for n in expand(m.group(0)):
                if n not in order:
                    order.append(n)
    mapping = {o: i + 1 for i, o in enumerate(order)}
    inv = {i + 1: o for o, i in mapping.items()}
    print("cited", len(order), "max", max(order))

    def fix(text):
        def rep(m):
            nums = sorted({mapping.get(n, n) for n in expand(m.group(0))})
            if len(nums) > 2 and nums[-1] - nums[0] == len(nums) - 1:
                return "[%d-%d]" % (nums[0], nums[-1])
            return "[" + ",".join(str(n) for n in nums) + "]"
        return CIT.sub(rep, text)

    for p in body:
        for r in p.runs:
            if re.search(r"\[\d", r.text):
                r.text = fix(r.text)

    # reorder reference entries
    if ref_start:
        entries = [p.text for p in paras[ref_start:] if p.text.strip()]
        entries = [re.sub(r"^\[\d+\]\s*", "", e) for e in entries]
        print("entries", len(entries), "expected", len(inv))
        if len(entries) == len(inv):
            for i, p in enumerate(paras[ref_start:], 1):
                if not p.text.strip():
                    continue
                old = inv[i]
                body_txt = entries[old - 1]
                for r in list(p.runs):
                    r._r.getparent().remove(r._r)
                run = p.add_run("[%d]　%s" % (i, body_txt))
                run.font.size = Pt(9)
                run.font.name = "宋体"
        else:
            print("SKIP reorder: count mismatch")
    doc.save(TMP)
    print("saved", TMP)


if __name__ == "__main__":
    main()
