#!/usr/bin/env python3
"""Stage 5c: fetch the accepted references and build the index used by the assembler.

Reads work/references/ref_decisions.json (decision == "add"):
  quran:S:V[-W]          -> fetch_quran.py (quran.com, Saheeh International)
  hadith:<slug>:<number> -> fetch_sunnah.js (sunnah.com, English text as shown), then this script
                            builds hadith_<slug>_<number>.json from the raw page data
  shamela:<file>         -> a reference file prepared from shamela.ws (see shamela notes in the file)
Writes:
  work/references/approved_refs.json : {file_id: {segment: [reference file names]}}
  work/references/unretrieved.json    : references accepted but not retrievable (reported, nothing added)
"""
import glob
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
from excerpts import WORK, ROOT  # noqa: E402

REF = os.path.join(WORK, "references")
SCRIPTS = os.path.dirname(__file__)


def quran_file(key):
    _, s, vv = key.split(":")
    s = int(s)
    if "-" in vv:
        a, b = (int(x) for x in vv.split("-"))
    else:
        a = b = int(vv)
    return f"quran_{s:03d}_{a:03d}" + (f"-{b:03d}" if b != a else "") + ".json", f"{s}:{a}" + (f"-{b}" if b != a else "")


def hadith_build(slug, num):
    raw = os.path.join(REF, f"hadith_{slug}_{num}.json.raw")
    out = os.path.join(REF, f"hadith_{slug}_{num}.json")
    if os.path.exists(out):
        return os.path.basename(out), None
    if not os.path.exists(raw):
        return None, "not fetched"
    d = json.load(open(raw, encoding="utf-8"))
    hs = [h for h in d["hadiths"] if h["text"] or h["narrated"]]
    if len(hs) != 1:
        return None, f"sunnah.com page shows {len(hs)} hadith entries for this number"
    h = hs[0]
    name = d["page_title"].split(" - ")[0].strip()
    paras = [p for p in [h["narrated"]] + [x.strip() for x in h["text"].split("\n") if x.strip()] if p]
    doc = {"kind": "hadith", "ref": f"{slug}:{num}", "label": f"Reference text: sunnah.com, {name}",
           "source": "sunnah.com (English text as shown on the page)", "url": d["url"], "final_url": d["final_url"],
           "page_title": d["page_title"], "retrieved_utc": d["retrieved_utc"],
           "processing": "narrator line and English text copied verbatim (innerText); split into paragraphs at the page's line breaks",
           "reference_table": h["reference_table"], "paragraphs": paras}
    json.dump(doc, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return os.path.basename(out), None


def main():
    dec = json.load(open(os.path.join(REF, "ref_decisions.json"), encoding="utf-8"))
    add = [d for d in dec if d["decision"] == "add" and d.get("key")]
    qkeys = sorted({d["key"] for d in add if d["key"].startswith("quran:")})
    hkeys = sorted({d["key"] for d in add if d["key"].startswith("hadith:")})
    # fetch Quran
    todo = [quran_file(k)[1] for k in qkeys if not os.path.exists(os.path.join(REF, quran_file(k)[0]))]
    for i in range(0, len(todo), 40):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "fetch_quran.py")] + todo[i:i + 40], check=False)
    # fetch Hadith
    htodo = [f"{k.split(':')[1]}:{k.split(':')[2]}" for k in hkeys
             if not os.path.exists(os.path.join(REF, f"hadith_{k.split(':')[1]}_{k.split(':')[2]}.json.raw"))]
    if htodo:
        npm_root = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip()
        subprocess.run(["node", os.path.join(SCRIPTS, "fetch_sunnah.js")] + htodo, env=dict(os.environ, NODE_PATH=npm_root), check=False)
    approved, unretrieved = {}, []
    for d in add:
        k = d["key"]
        if k.startswith("quran:"):
            fn, _ = quran_file(k)
            ok = os.path.exists(os.path.join(REF, fn))
            why = None if ok else "not retrievable from quran.com"
        elif k.startswith("hadith:"):
            _, slug, num = k.split(":")
            fn, why = hadith_build(slug, num)
            ok = fn is not None
        elif k.startswith("shamela:"):
            fn = k.split(":", 1)[1]
            ok = os.path.exists(os.path.join(REF, fn))
            why = None if ok else "shamela text not prepared"
        else:
            ok, why = False, "unknown kind"
        if ok:
            approved.setdefault(d["file"], {}).setdefault(str(d["seg"]), [])
            if fn not in approved[d["file"]][str(d["seg"])]:
                approved[d["file"]][str(d["seg"])].append(fn)
        else:
            unretrieved.append(dict(d, why=why))
    json.dump(approved, open(os.path.join(REF, "approved_refs.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(unretrieved, open(os.path.join(REF, "unretrieved.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    used = {fn for m in approved.values() for l in m.values() for fn in l}
    print(f"approved citations: {sum(len(l) for m in approved.values() for l in m.values())}; distinct reference files: {len(used)}; unretrieved: {len(unretrieved)}")
    # remove fetched files that are not used anymore (keep raw hadith pages for the record)
    for p in glob.glob(os.path.join(REF, "quran_*.json")) + glob.glob(os.path.join(REF, "hadith_*.json")):
        if os.path.basename(p) not in used and not os.path.basename(p).startswith("quran_chapters"):
            os.remove(p)


if __name__ == "__main__":
    main()
