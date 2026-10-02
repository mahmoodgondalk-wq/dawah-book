#!/usr/bin/env python3
"""Stage 5a: collect candidate references (Quran / Hadith / classical books) cited in HOST segments.

Sources of candidates:
  (a) refs listed by the labelers in work/topics/<id>.json
  (b) a regex scan of host segments (cross-check, catches misses)
Output: work/references/candidates.json  (one entry per (file, segment, normalized ref)), with the
segment text and its neighbours for review. Decisions are taken in work/references/ref_decisions.json.
"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from excerpts import HOSTS, WORK  # noqa: E402

BIBLE = r"(?:gen(?:esis)?|exo(?:dus)?|ex|lev(?:iticus)?|num(?:bers)?|deut(?:eronomy)?|josh(?:ua)?|judg(?:es)?|ruth|samuel|sam|kings|kgs|chron(?:icles)?|ezra|neh(?:emiah)?|esther|job|psalms?|ps|prov(?:erbs)?|eccl(?:esiastes)?|song(?: of songs| of solomon)?|isa(?:iah)?|jer(?:emiah)?|lam(?:entations)?|ezek(?:iel)?|dan(?:iel)?|hos(?:ea)?|joel|amos|obad(?:iah)?|jonah|mic(?:ah)?|nah(?:um)?|hab(?:akkuk)?|zeph(?:aniah)?|hag(?:gai)?|zech(?:ariah)?|mal(?:achi)?|matt?(?:hew)?|mathew|mark|mk|luke|lk|john|jn|acts|rom(?:ans)?|cor(?:inthians)?|gal(?:atians)?|eph(?:esians)?|phil(?:ippians)?|col(?:ossians)?|thess(?:alonians)?|tim(?:othy)?|titus|philemon|heb(?:rews)?|james|jas|pet(?:er)?|jude|rev(?:elations?)?|maccabees|sirach|enoch|barnabas|thomas)"
RE_BIBLE_NEAR = re.compile(r"(?i)\b(?:[1-3]\s?)?" + BIBLE + r"\s*(?:chapter\s*)?\(?\s*\d")

PATTERNS = [
    ("quran", re.compile(r"(?i)\b(?:quran|qur'?an|qur’an|koran)\s*,?\s*(?:chapter\s*|surah?\s*|sura\s*)?\(?\s*(\d{1,3})\s*[:：]\s*(\d{1,3})(?:\s*(?:-|–|to)\s*(\d{1,3}))?")),
    ("glued", re.compile(r"\(\s*([A-Za-z][A-Za-z'’\-]{1,20})\s*(\d{1,3})\s*:\s*(\d{1,3})(?:\s*[-–]\s*(\d{1,3}))?\s*\)")),
    ("bare", re.compile(r"\(\s*(\d{1,3})\s*:\s*(\d{1,3})(?:\s*[-–]\s*(\d{1,3}))?\s*\)")),
    ("chapverse", re.compile(r"(?i)\b(?:chapter|surah?|surat|sura)\s*(?:number\s*)?(\d{1,3})\s*[,:]?\s*(?:verses?|ayahs?|ayat|aya|v\.?)\s*(?:number\s*)?(\d{1,3})(?:\s*(?:-|–|to|and)\s*(\d{1,3}))?")),
    ("chapcolon", re.compile(r"(?i)\b(?:chapter|surah?|surat|sura)\s*(\d{1,3})\s*:\s*(\d{1,3})(?:\s*(?:-|–|to)\s*(\d{1,3}))?")),
    ("versechap", re.compile(r"(?i)\bverses?\s*(?:number\s*)?(\d{1,3})(?:\s*(?:-|–|to|and)\s*(\d{1,3}))?\s*(?:of|in|from)\s*(?:chapter|surah?|surat|sura)\s*(?:number\s*)?(\d{1,3})")),
    ("surahname", re.compile(r"(?i)\b(?:surah?|surat|sura)\s+((?:al|an|ar|as|at|ash|az|ad|adh|ath)?[\s\-]?[a-z'’]{2,15})\s*,?\s*(?:verses?|ayahs?|ayat|aya)\s*(?:number\s*)?(\d{1,3})(?:\s*(?:-|–|to|and)\s*(\d{1,3}))?")),
    ("hadith", re.compile(r"(?i)\b(bukhari|bukhaari|muslim|tirmidhi|tirmizi|abu dawu?d|abu dawood|abi dawud|nasa'?i|nasai|ibn majah|musnad ahmad|ahmad|muwatta|malik|riyad us saliheen|riyadh|mishkat|adab al-mufrad)\b[^.?!]{0,50}?\b(?:hadith|number|no\.?|#|narration)\s*(?:number\s*)?(\d{1,5})")),
    ("hadith2", re.compile(r"(?i)\b(?:sahih|saheeh|sunan|jami|jami')\s*(?:al[\s\-]?)?(bukhari|muslim|tirmidhi|abu dawud|abi dawud|nasai|ibn majah)\s*,?\s*(\d{1,5})\b")),
    ("volpage", re.compile(r"(?i)\b(?:volume|vol\.?)\s*(\d{1,3})[^.?!]{0,30}?\b(?:page|p\.|pg\.?)\s*(\d{1,4})")),
    ("page", re.compile(r"(?i)\bpage\s*(?:number\s*)?(\d{1,4})\b")),
]


def main():
    cands = {}
    for tp in sorted(glob.glob(os.path.join(WORK, "topics", "*.json"))):
        fid = os.path.basename(tp)[:-5]
        T = json.load(open(tp, encoding="utf-8"))
        seg = json.load(open(os.path.join(WORK, "segments", fid + ".json"), encoding="utf-8"))
        L = json.load(open(os.path.join(WORK, "labels", fid + ".json"), encoding="utf-8"))
        n = len(seg["segments"])
        spk = [None] * (n + 1)
        for a, b, l in L["speakers"]:
            for k in range(a, b + 1):
                spk[k] = l
        texts = [None] + [s["text"] for s in seg["segments"]]

        def add(k, ref, src):
            key = (fid, k, ref)
            if key not in cands:
                cands[key] = {"file": fid, "seg": k, "ref": ref, "sources": [], "speaker": spk[k],
                              "context": " | ".join(texts[j] for j in range(max(1, k - 1), min(n, k + 1) + 1))}
            if src not in cands[key]["sources"]:
                cands[key]["sources"].append(src)

        for k, ref in T.get("refs", []):
            add(k, ref.strip(), "labeler")
        for k in range(1, n + 1):
            if spk[k] not in HOSTS:
                continue
            t = texts[k]
            win = t + (" " + texts[k + 1] if k < n else "")
            for name, rx in PATTERNS:
                for m in rx.finditer(t):
                    pre = (texts[k - 1] if k > 1 else "")[-40:] + " " + t[:m.start()]
                    bible_ctx = bool(RE_BIBLE_NEAR.search(pre[-30:] + m.group(0)))
                    if name == "glued" and re.match(r"(?i)" + BIBLE + r"$", m.group(1)):
                        continue
                    if name == "page" and re.search(r"(?i)vol", t):
                        continue
                    add(k, f"[{name}] {m.group(0)}" + (" [bible-context?]" if bible_ctx else ""), "regex")
    out = sorted(cands.values(), key=lambda c: (c["file"], c["seg"]))
    os.makedirs(os.path.join(WORK, "references"), exist_ok=True)
    json.dump(out, open(os.path.join(WORK, "references", "candidates.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    by = {}
    for c in out:
        by[tuple(c["sources"])] = by.get(tuple(c["sources"]), 0) + 1
    print(len(out), "candidates", by)


if __name__ == "__main__":
    main()
