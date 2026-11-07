#!/usr/bin/env python3
"""Check E (footnotes), on the built PDF of the edited book: from the text of every page (pdftotext -layout), the footnotes
of each page are numbered 1, 2, 3 ... (numbering restarts on every page), the first footnote of each page names its video
(never "Ibid."), and no footnote mark stands alone on a line. Writes work/footnote_pdf_check.json.
  python3 check_pdf_footnotes.py <pdf>
"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
from excerpts import WORK  # noqa: E402

NOTE = re.compile(r"^\s{0,8}(\d{1,3})(The Muslim Lantern|Farid Responds|Ibid\.)", re.M)
MARK_ALONE = re.compile(r"\s{0,6}\d{1,2}\s*")


def main(pdf):
    text = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True, check=True).stdout
    pages = text.split("\f")[:-1]
    errors, n_notes, n_pages = [], 0, 0
    for n, p in enumerate(pages, 1):
        ms = list(NOTE.finditer(p))
        if ms:
            n_pages += 1
            n_notes += len(ms)
            nums = [int(m.group(1)) for m in ms]
            if nums != list(range(1, len(nums) + 1)):
                errors.append(f"page {n}: footnotes numbered {nums}")
            if ms[0].group(2) == "Ibid.":
                errors.append(f"page {n}: the first footnote says Ibid.")
        ls = p.split("\n")
        for j, line in enumerate(ls):
            if 0 < j < len(ls) - 6 and MARK_ALONE.fullmatch(line) and ls[j - 1].strip():
                errors.append(f"page {n}: footnote mark alone on a line")
    out = {"pdf": os.path.basename(pdf), "pdf_pages": len(pages), "pages_with_footnotes": n_pages, "footnotes": n_notes,
           "errors": errors, "pass": not errors}
    json.dump(out, open(os.path.join(WORK, "footnote_pdf_check.json"), "w", encoding="utf-8"), indent=1)
    print({k: v for k, v in out.items() if k != "errors"}, errors[:10])


if __name__ == "__main__":
    main(sys.argv[1])
