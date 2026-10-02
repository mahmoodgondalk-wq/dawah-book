#!/usr/bin/env python3
"""Validate work/consolidation/<PART>_out.json against <PART>_in.txt."""
import json
import os
import re
import sys

WORK = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BAD_WORDS = re.compile(r"(?i)\b(debunk\w*|refut\w*|lie|lies|liar|destroy\w*|exposed?|fails?|failed|humiliat\w*|dumb\w*|stupid)\b")


def check(part):
    errs = []
    inp = os.path.join(WORK, "consolidation", f"{part}_in.txt")
    outp = os.path.join(WORK, "consolidation", f"{part}_out.json")
    ids = [l.split(" | ")[0].strip() for l in open(inp, encoding="utf-8") if l.strip()]
    if not os.path.exists(outp):
        return [f"missing {outp}"]
    try:
        O = json.load(open(outp, encoding="utf-8"))
    except Exception as e:
        return [f"invalid JSON: {e}"]
    seen = {}
    for ch in O.get("chapters", []):
        if not ch.get("code") or not ch.get("title"):
            errs.append(f"chapter without code/title: {str(ch)[:80]}")
        if BAD_WORDS.search(ch.get("title", "")):
            errs.append(f"non-neutral chapter title: {ch.get('title')!r}")
        if not ch.get("subchapters"):
            errs.append(f"chapter {ch.get('code')} has no subchapters")
        for sc in ch.get("subchapters", []):
            t = sc.get("title", "")
            if not t.strip():
                errs.append(f"empty subchapter title in {ch.get('code')}")
            if BAD_WORDS.search(t):
                errs.append(f"non-neutral subchapter title: {t!r}")
            if not sc.get("ranges"):
                errs.append(f"empty subchapter {t!r}")
            for r in sc.get("ranges", []):
                seen[r] = seen.get(r, 0) + 1
    for m in O.get("moves", []):
        r = m.get("range")
        seen[r] = seen.get(r, 0) + 1
        if not re.match(r"^P\d\d\.(C\d\d|N\d+)$", m.get("to", "")):
            errs.append(f"move target must be a chapter code: {m}")
    idset = set(ids)
    missing = [i for i in ids if i not in seen]
    extra = [r for r in seen if r not in idset]
    dup = [r for r, c in seen.items() if c > 1]
    if missing:
        errs.append(f"{len(missing)} ranges missing, e.g. {missing[:10]}")
    if extra:
        errs.append(f"{len(extra)} unknown range ids, e.g. {extra[:10]}")
    if dup:
        errs.append(f"{len(dup)} ranges used more than once, e.g. {dup[:10]}")
    return errs


if __name__ == "__main__":
    bad = 0
    for part in sys.argv[1:]:
        e = check(part)
        print(part, "OK" if not e else "ERRORS")
        for x in e:
            print("   -", x)
        bad += bool(e)
    sys.exit(1 if bad else 0)
