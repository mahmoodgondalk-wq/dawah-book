#!/usr/bin/env python3
"""Compile the Typst book source into the PDF.
Usage: python3 output_final/work/scripts/build_pdf.py [book_dir] [output_pdf]
Typst root = repository root (articles are referenced in place under "/Farid Responds/")."""
import os
import resource
import sys
import time

import typst

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
book_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "output_final", "book")
out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "output_final", "The_Muslim_Lantern_and_Farid_Responds_A_Topical_Compilation.pdf")
t = time.time()
typst.compile(os.path.join(book_dir, "book.typ"), output=out, root=ROOT,
              font_paths=[os.path.join(ROOT, "output_final", "book", "fonts")])
print(f"compiled {out} in {time.time() - t:.1f}s, max RSS {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024} MB")
