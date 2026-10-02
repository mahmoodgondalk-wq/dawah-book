#!/usr/bin/env python3
"""Stage 5b: turn candidates.json into decisions.

  python3 resolve_refs.py auto     -> writes work/references/auto_decisions.json and review.txt
  (manual decisions are written by hand into work/references/manual_decisions.json:
     [{"file":..,"seg":..,"key":"quran:4:124"|"hadith:bukhari:2440"|"shamela:..."|null,"decision":"add"|"skip","reason":".."}])
  python3 resolve_refs.py final    -> merges auto + manual into work/references/ref_decisions.json

Automatic acceptance (conservative): a Quran reference proposed by the labeler whose surah and verse
numbers both appear as digits in the cited host segment (or the next one), not in a Bible context, and that
exists (surah 1-114, verse within the surah's verse count from quran.com). Everything else goes to review.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from excerpts import WORK  # noqa: E402
from collect_refs import RE_BIBLE_NEAR, BIBLE  # noqa: E402

REF = os.path.join(WORK, "references")
CH = {c["number"]: c for c in json.load(open(os.path.join(REF, "quran_chapters.json"), encoding="utf-8"))["chapters"]}

HADITH_SLUGS = [
    (r"bukh", "bukhari"), (r"muslim", "muslim"), (r"dawu?d|dawood", "abudawud"), (r"tirmi", "tirmidhi"),
    (r"nasa", "nasai"), (r"majah", "ibnmajah"), (r"muwatta|malik", "malik"), (r"ahmad|musnad", "ahmad"),
    (r"riya", "riyadussalihin"), (r"mishkat", "mishkat"), (r"adab", "adab"), (r"nawawi", "nawawi40"),
    (r"bulugh", "bulugh"), (r"shama'?il", "shamail"),
]


def parse_labeler_ref(s):
    s = s.strip()
    m = re.match(r"(?i)^quran\s+(\d{1,3})\s*:\s*(\d{1,3})(?:\s*-\s*(\d{1,3}))?$", s)
    if m:
        a, v1, v2 = int(m.group(1)), int(m.group(2)), int(m.group(3) or m.group(2))
        return ("quran", a, v1, v2)
    m = re.match(r"(?i)^(.*?)\s+(?:no\.?\s*|number\s*|#\s*)?(\d{1,5}[a-z]?)$", s)
    if m and not re.search(r"(?i)\bvol|\bp\.|page", s):
        coll = m.group(1).lower()
        for rx, slug in HADITH_SLUGS:
            if re.search(rx, coll):
                return ("hadith", slug, m.group(2))
    if re.search(r"(?i)\bvol|\bp\.\s*\d|page", s):
        return ("book", s)
    return ("unknown", s)


def quran_key(a, v1, v2):
    return f"quran:{a}:{v1}" + (f"-{v2}" if v2 != v1 else "")


def quran_valid(a, v1, v2):
    return 1 <= a <= 114 and 1 <= v1 <= v2 <= CH[a]["verses_count"]


def main():
    cmd = sys.argv[1]
    cands = json.load(open(os.path.join(REF, "candidates.json"), encoding="utf-8"))
    if cmd == "auto":
        auto, review = [], []
        handled = set()
        for c in cands:
            if "labeler" not in c["sources"]:
                continue
            p = parse_labeler_ref(c["ref"])
            seg_txt = c["context"]
            if p[0] == "quran":
                a, v1, v2 = p[1], p[2], p[3]
                key = quran_key(a, v1, v2)
                # the cited segment itself is the middle element of context (k-1 | k | k+1)
                parts = c["context"].split(" | ")
                own = parts[1] if len(parts) == 3 else parts[0]
                nxt = parts[-1] if len(parts) >= 2 and parts[-1] != own else ""
                window = own + " " + nxt
                digits = re.findall(r"\d+", window)
                bible = bool(RE_BIBLE_NEAR.search(own))
                ok = quran_valid(a, v1, v2) and str(a) in digits and str(v1) in digits and (v2 == v1 or str(v2) in digits) and not bible
                if ok:
                    auto.append({"file": c["file"], "seg": c["seg"], "key": key, "decision": "add",
                                 "reason": "labeler ref; surah and verse numbers stated in the host segment; verse exists"})
                    handled.add((c["file"], c["seg"], key))
                    continue
                review.append((c, key, "quran: numbers not both literally present, Bible context, or invalid verse"))
            elif p[0] == "hadith":
                review.append((c, f"hadith:{p[1]}:{p[2]}", "hadith"))
            else:
                review.append((c, None, p[0]))
        # regex-only candidates not covered by an accepted labeler ref in the same segment
        accepted_segs = {(a["file"], a["seg"]) for a in auto}
        for c in cands:
            if c["sources"] == ["regex"]:
                if (c["file"], c["seg"]) in accepted_segs and not c["ref"].startswith("[hadith") and not c["ref"].startswith("[vol"):
                    # check whether every number of the regex hit is already covered by accepted refs of this segment
                    keys = [a["key"] for a in auto if a["file"] == c["file"] and a["seg"] == c["seg"]]
                    nums = re.findall(r"\d+", c["ref"])
                    knums = set(x for k in keys for x in re.findall(r"\d+", k))
                    if set(nums) <= knums:
                        continue
                review.append((c, None, "regex only"))
        json.dump(auto, open(os.path.join(REF, "auto_decisions.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        with open(os.path.join(REF, "review.txt"), "w", encoding="utf-8") as f:
            for c, key, why in review:
                f.write(f"{c['file']}\t{c['seg']}\t{key}\t{c['ref']}\t[{why}]\t{c['context']}\n")
        print(f"auto-accepted: {len(auto)}; to review: {len(review)}")
    elif cmd == "final":
        auto = json.load(open(os.path.join(REF, "auto_decisions.json"), encoding="utf-8"))
        mp = os.path.join(REF, "manual_decisions.json")
        manual = json.load(open(mp, encoding="utf-8")) if os.path.exists(mp) else []
        allx = {}
        for d in auto + manual:
            allx[(d["file"], d["seg"], d.get("key"))] = d
        out = sorted(allx.values(), key=lambda d: (d["file"], d["seg"], str(d.get("key"))))
        json.dump(out, open(os.path.join(REF, "ref_decisions.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        add = [d for d in out if d["decision"] == "add"]
        print(f"decisions: {len(out)}; add: {len(add)}; skip: {len(out) - len(add)}")


if __name__ == "__main__":
    main()
