# -*- coding: utf-8 -*-
import re, sys
src = open(r'D:\_scratch\build_paper.py', encoding='utf-8').read()
out = sys.argv[1] if len(sys.argv) > 1 else r'D:\_scratch\_build.docx'
new, n = re.subn(r'(?m)^OUT = r".*"$',
                 'OUT = r"' + out.replace('\\', '\\\\') + '"', src)
assert n == 1, n
g = {'__name__': '__main__', '__file__': r'D:\_scratch\build_paper.py'}
exec(compile(new, r'D:\_scratch\build_paper.py', 'exec'), g)
