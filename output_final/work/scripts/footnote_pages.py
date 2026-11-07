#!/usr/bin/env python3
"""Stage 8 (footnotes): make the first footnote of every page name its video.

A footnote after the first paragraph of a passage says "Ibid." (same video as the footnote before it). When such a
footnote is the first one on its page, the reader would have to turn back to find the video, so it must give the
channel and title again. Which footnote is first on a page is only known after layout, and naming the video makes a
footnote longer, which can move later ones; so this script iterates:
  query the laid-out book for the page of every footnote (metadata <fnpos> = (passage id, paragraph, page), in document
  order) -> add every "Ibid." footnote that is first on its page to book_edited/fullnotes.json -> repeat until none is
  added. The list only grows (a footnote that names its video stays so), so it converges.
Writes work/footnote_pages.json with the result (used by write_checks.py --edited, check E).
  python3 footnote_pages.py [book_dir]
"""
import json
import os
import subprocess
import sys
import time

import typst

sys.path.insert(0, os.path.dirname(__file__))
from excerpts import WORK, ROOT  # noqa: E402

QUERY = "--query" in sys.argv
ARGS = [a for a in sys.argv[1:] if a != "--query"]
BOOK = ARGS[0] if ARGS else os.path.join(ROOT, "output_final", "book_edited")
FULL = os.path.join(BOOK, "fullnotes.json")
FONTS = [os.path.join(ROOT, "output_final", "book", "fonts")]
MAX_ROUNDS = 12


def positions():
    """Each query runs in its own process: the typst module keeps its caches, and repeated queries of the whole book
    in one process run out of memory."""
    t = time.time()
    res = subprocess.run([sys.executable, __file__, "--query", BOOK], capture_output=True, text=True, check=True).stdout
    vals = json.loads(res)
    print(f"  query: {len(vals)} footnotes in {time.time() - t:.0f}s", flush=True)
    return [tuple(v) for v in vals]


def first_per_page(pos):
    first = {}
    for pid, i, page in pos:  # document order
        first.setdefault(page, (pid, i))
    return first


def main():
    full = {}
    if os.path.exists(FULL):
        full = {k: set(v) for k, v in json.load(open(FULL, encoding="utf-8")).items()}
    for rnd in range(1, MAX_ROUNDS + 1):
        pos = positions()
        first = first_per_page(pos)
        add = [(pid, i) for pid, i in first.values() if i != 0 and i not in full.get(str(pid), set())]
        print(f"round {rnd}: {len(first)} pages with footnotes, {len(add)} 'Ibid.' footnotes first on their page", flush=True)
        if not add:
            break
        for pid, i in add:
            full.setdefault(str(pid), set()).add(i)
        json.dump({k: sorted(v) for k, v in sorted(full.items(), key=lambda kv: int(kv[0]))}, open(FULL, "w", encoding="utf-8"))
    else:
        sys.exit("footnote_pages: did not converge")
    # final state: every page's first footnote names its video
    bad = [(pid, i, p) for p, (pid, i) in first.items() if i != 0 and i not in full.get(str(pid), set())]
    pages = {}
    for _pid, _i, page in pos:
        pages[page] = pages.get(page, 0) + 1
    out = {"rounds": rnd, "footnotes": len(pos), "pages_with_footnotes": len(first),
           "footnotes_naming_video_again": sum(len(v) for v in full.values()),
           "pages_whose_first_footnote_is_ibid": len(bad), "max_footnotes_on_a_page": max(pages.values()),
           "pass": not bad}
    json.dump(out, open(os.path.join(WORK, "footnote_pages.json"), "w", encoding="utf-8"), indent=1)
    print(out)


if __name__ == "__main__":
    if QUERY:
        print(typst.query(os.path.join(BOOK, "book.typ"), "<fnpos>", field="value", root=ROOT, font_paths=FONTS))
    else:
        main()
