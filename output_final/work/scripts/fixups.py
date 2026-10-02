#!/usr/bin/env python3
"""Deterministic, idempotent label fixes applied after labeling (recorded in work/labels_fixups.log).

1. The recurring inserted sound bite "You asked me excellent, excellent question" in Farid Responds videos
   is played audio (it stands between caption voice-change markers and is not Farid's narration):
   if a segment consists only of that sound bite and is labeled with a host label, relabel it `Clip`
   and add a doubt explaining why.
"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from excerpts import HOSTS, WORK  # noqa: E402

SOUNDBITE = re.compile(r"^(?:[–-] )?you asked me excellent,? excellent,? question[.!]?$", re.I)


def expand(ranges, n):
    arr = [None] * (n + 1)
    for a, b, l in ranges:
        for k in range(a, b + 1):
            arr[k] = l
    return arr


def compress(arr):
    out = []
    for k in range(1, len(arr)):
        if out and out[-1][2] == arr[k]:
            out[-1][1] = k
        else:
            out.append([k, k, arr[k]])
    return out


def main():
    log = []
    for lp in sorted(glob.glob(os.path.join(WORK, "labels", "*.json"))):
        fid = os.path.basename(lp)[:-5]
        seg = json.load(open(os.path.join(WORK, "segments", fid + ".json"), encoding="utf-8"))
        L = json.load(open(lp, encoding="utf-8"))
        n = len(seg["segments"])
        arr = expand(L["speakers"], n)
        changed = False
        for k in range(1, n + 1):
            t = seg["segments"][k - 1]["text"].strip()
            if SOUNDBITE.match(t) and arr[k] in HOSTS:
                arr[k] = "Clip"
                changed = True
                L["doubts"] = [d for d in L["doubts"] if not (d[0] == k and d[1] == k)]
                L["doubts"].append([k, k, "inserted recurring sound bite (played audio between voice-change markers); labeled Clip, not the host"])
                log.append(f"{fid}-{k:04d}: host -> Clip (sound bite)")
        if changed:
            L["speakers"] = compress(arr)
            L["doubts"].sort(key=lambda d: d[0])
            with open(lp, "w", encoding="utf-8") as f:
                json.dump(L, f, ensure_ascii=False)
    if log:
        with open(os.path.join(WORK, "labels_fixups.log"), "a", encoding="utf-8") as f:
            f.write("\n".join(log) + "\n")
    print(f"{len(log)} fixes applied")
    for x in log:
        print("  ", x)


if __name__ == "__main__":
    main()
