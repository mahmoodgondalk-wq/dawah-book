#!/usr/bin/env python3
"""Stage 4a: prepare per-part listings of topic ranges for taxonomy consolidation.

Writes work/consolidation/<Pxx>_in.txt with one line per topic range that contains host speech:
  RANGE_ID | chapter_code | subtopic | role | host_words | channel | title
RANGE_ID = <file_id>:<first>-<last>. Ranges whose code is "NEW: ..." are listed under the part named
after the '|' in the proposal (or P16 if none), with the proposed title in the code column.
Also writes work/topic_ranges.json (all ranges, for mapping).
"""
import csv
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from excerpts import HOSTS, WORK  # noqa: E402

files = {r["file_id"]: r for r in csv.DictReader(open(os.path.join(WORK, "files.csv"), encoding="utf-8"))}
seed = json.load(open(os.path.join(WORK, "seed_taxonomy.json"), encoding="utf-8"))
codes = {c["code"] for p in seed["parts"] for c in p["chapters"]}


def main():
    allr = []
    for fid in sorted(files):
        tp = os.path.join(WORK, "topics", fid + ".json")
        lp = os.path.join(WORK, "labels", fid + ".json")
        if not os.path.exists(tp):
            print("missing topics for", fid)
            continue
        T = json.load(open(tp, encoding="utf-8"))
        L = json.load(open(lp, encoding="utf-8"))
        seg = json.load(open(os.path.join(WORK, "segments", fid + ".json"), encoding="utf-8"))
        n = len(seg["segments"])
        spk = [None] * (n + 1)
        for a, b, l in L["speakers"]:
            for k in range(a, b + 1):
                spk[k] = l
        for a, b, code, sub, role in T["ranges"]:
            hw = sum(len(seg["segments"][k - 1]["text"].split()) for k in range(a, b + 1) if spk[k] in HOSTS)
            part = code[:3] if code in codes else None
            if part is None:
                m = re.search(r"\|\s*(P\d\d)", code)
                part = m.group(1) if m else "P16"
            allr.append({"id": f"{fid}:{a}-{b}", "file": fid, "first": a, "last": b, "code": code, "part": part,
                         "subtopic": sub, "role": role, "host_words": hw, "channel": files[fid]["channel"],
                         "title": files[fid]["title"]})
    json.dump(allr, open(os.path.join(WORK, "topic_ranges.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    os.makedirs(os.path.join(WORK, "consolidation"), exist_ok=True)
    by = {}
    for r in allr:
        if r["host_words"] == 0:
            continue
        by.setdefault(r["part"], []).append(r)
    for part, rs in sorted(by.items()):
        rs.sort(key=lambda r: (r["code"], r["subtopic"].lower()))
        with open(os.path.join(WORK, "consolidation", f"{part}_in.txt"), "w", encoding="utf-8") as f:
            for r in rs:
                ch = "ML" if r["channel"] == "The Muslim Lantern" else "FR"
                f.write(f'{r["id"]} | {r["code"]} | {r["subtopic"]} | {r["role"]} | {r["host_words"]} | {ch} | {r["title"][:70]}\n')
        print(part, len(rs), "ranges,", sum(r["host_words"] for r in rs), "host words")
    print("total ranges", len(allr), "with host speech", sum(1 for r in allr if r["host_words"] > 0))


if __name__ == "__main__":
    main()
