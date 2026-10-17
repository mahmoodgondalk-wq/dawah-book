#!/usr/bin/env python3
"""Stage 8 (condense pass for batches edited with guide v1): build work/edit/cin/<BATCH>.txt from the cleaned
output work/edit/out/<BATCH>.txt, with the sub-chapter headers of the batch, and back up the v1 output to
work/edit/out_v1/<BATCH>.txt. The condense agent then rewrites work/edit/out/<BATCH>.txt (deletion only).
  python3 condense_input.py E001 [E002 ...]
"""
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(__file__))
from check_edit import EDIT, parse_out, units  # noqa: E402
from assemble import files_index  # noqa: E402


def main():
    B = {b["batch"]: b for b in json.load(open(os.path.join(EDIT, "batches.json")))}
    U = units()
    idx = files_index()
    tax = json.load(open(os.path.join(EDIT, "..", "taxonomy.json"), encoding="utf-8"))
    titles = {}
    for p in tax["parts"]:
        for c in p["chapters"]:
            for s in c["subchapters"]:
                titles[s["id"]] = (s["title"], c["title"], p["title"])
    os.makedirs(os.path.join(EDIT, "cin"), exist_ok=True)
    os.makedirs(os.path.join(EDIT, "out_v1"), exist_ok=True)
    for batch in sys.argv[1:]:
        src = os.path.join(EDIT, "out", batch + ".txt")
        bak = os.path.join(EDIT, "out_v1", batch + ".txt")
        if not os.path.exists(bak):
            shutil.copy(src, bak)
        blocks = dict(parse_out(bak))
        n = 0
        with open(os.path.join(EDIT, "cin", batch + ".txt"), "w", encoding="utf-8") as f:
            last = None
            for uid in B[batch]["units"]:
                u = U[uid]
                if u["sub"] != last:
                    t, c, p = titles[u["sub"]]
                    f.write(f"## SUB-CHAPTER {u['sub']} — {t}   (chapter: {c}; part: {p})\n\n")
                    last = u["sub"]
                f.write(f'### {uid} | {u["host"]} | "{idx[u["file"]]["title"]}"\n{blocks[uid].strip()}\n\n')
                n += 1
        print(batch, n, "passages")


if __name__ == "__main__":
    main()
