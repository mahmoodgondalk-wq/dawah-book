#!/usr/bin/env python3
"""VERIFY (INSTRUCTIONS section 11): checks A, B, C, D, F by script. Check E (visual) is done by
rendering pages (render_samples.py) and looking at them.

  A fidelity    : every turn text in the generated book source (output_final/book/content/*.typ),
                  parsed back from the Typst string literals, equals the segment texts it claims
                  (joined with single spaces; paragraph breaks are whitespace). The only allowed
                  difference is the removal of a raw turn dash at a real speaker change.
  B coverage    : every host segment appears in the book exactly once (and every segment at most
                  once as host text); lists missing / duplicated segments.
  C attribution : every shown segment is under the speaker label given in work/labels/.
  D join        : for every file, segments joined with single spaces == normalized text, and the
                  normalized text is re-derived from the raw input file and compared.
  F references  : every reference box is byte-identical to its file in work/references/, follows an
                  excerpt whose host segments cite it, is never inside speaker text, and only
                  Quran / Hadith / classical-book references were added.
Writes output_final/checks.md (results) and exits 1 if any check fails.
"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import normalize_segment as NS  # noqa: E402
from excerpts import HOSTS, WORK, ROOT  # noqa: E402

BOOK = os.environ.get("BOOK_DIR", os.path.join(ROOT, "output_final", "book"))
DASH_RE = re.compile(r"^[–-] ")


def parse_tstrings(line):
    """Return all Typst string literals in a line, decoded."""
    out = []
    i = 0
    n = len(line)
    while i < n:
        if line[i] == '"':
            i += 1
            buf = []
            while True:
                c = line[i]
                if c == "\\":
                    nx = line[i + 1]
                    if nx == "\\":
                        buf.append("\\"); i += 2
                    elif nx == '"':
                        buf.append('"'); i += 2
                    elif nx == "n":
                        buf.append("\n"); i += 2
                    elif nx == "r":
                        buf.append("\r"); i += 2
                    elif nx == "t":
                        buf.append("\t"); i += 2
                    elif nx == "u":
                        j = line.index("}", i)
                        buf.append(chr(int(line[i + 3:j], 16))); i = j + 1
                    else:
                        raise ValueError("bad escape in " + line[:80])
                elif c == '"':
                    i += 1
                    break
                else:
                    buf.append(c); i += 1
            out.append("".join(buf))
        else:
            i += 1
    return out


def ws(s):
    return re.sub(r"\s+", " ", s).strip()


def load_all():
    segs, labels, spk = {}, {}, {}
    for p in glob.glob(os.path.join(WORK, "segments", "*.json")):
        d = json.load(open(p, encoding="utf-8"))
        fid = d["file_id"]
        segs[fid] = d
        lp = os.path.join(WORK, "labels", fid + ".json")
        if os.path.exists(lp):
            L = json.load(open(lp, encoding="utf-8"))
            labels[fid] = L
            arr = [None] * (len(d["segments"]) + 1)
            for a, b, l in L["speakers"]:
                for k in range(a, b + 1):
                    arr[k] = l
            spk[fid] = arr
    return segs, labels, spk


def check_D(segs):
    errs = []
    rows = {}
    import csv
    for r in csv.DictReader(open(os.path.join(WORK, "files.csv"), encoding="utf-8")):
        rows[r["file_id"]] = r
    for fid, d in segs.items():
        if " ".join(s["text"] for s in d["segments"]) != d["normalized_text"]:
            errs.append(f"{fid}: segments joined != normalized text")
        raw_path = os.path.join(ROOT, d["folder"], d["file_name"])
        again = NS.build(raw_path, d["channel"], fid, d["folder"])
        if again["normalized_text"] != d["normalized_text"]:
            errs.append(f"{fid}: normalized text differs from a fresh normalization of the raw input")
        if [s["text"] for s in again["segments"]] != [s["text"] for s in d["segments"]]:
            errs.append(f"{fid}: segmentation differs from a fresh run")
    return errs


def parse_book():
    """Yield records from the generated content files."""
    recs = []
    for p in sorted(glob.glob(os.path.join(BOOK, "content", "*.typ"))):
        lines = open(p, encoding="utf-8").read().split("\n")
        excerpt = None
        for i, line in enumerate(lines):
            if line.startswith("// EXCERPT "):
                _, _, fid, rng = line.split(" ")
                excerpt = {"file": fid, "range": rng, "host_segs": [], "line": i, "path": p}
                recs.append(("excerpt", excerpt))
            elif line.startswith("// T "):
                meta = line[5:]
                left, label, dash, cut = [x.strip() for x in meta.split("|")]
                fid, segl = left.split(" ")
                ks = [int(x) for x in segl.split(",")]
                dash_ks = [int(x) for x in dash[5:].split(",") if x]
                call = lines[i + 1]
                if not (call.startswith("#host(") or call.startswith("#other(")):
                    recs.append(("error", f"{p}:{i + 2}: turn comment not followed by a turn call"))
                    continue
                strs = parse_tstrings(call)
                recs.append(("turn", {"file": fid, "segs": ks, "label": label, "dash": dash_ks,
                                       "call_label": strs[0], "paras": strs[1:], "is_host_call": call.startswith("#host("),
                                       "excerpt": excerpt, "where": f"{os.path.basename(p)}:{i + 2}"}))
            elif line.startswith("// ARTICLE "):
                parts = line.split()
                recs.append(("article", {"id": parts[2], "pages": int(parts[3].split(":")[1]), "sha": parts[4].split(":")[1],
                                          "call": lines[i + 1], "where": f"{os.path.basename(p)}:{i + 2}"}))
            elif line.startswith("// R "):
                call = lines[i + 1]
                if not call.startswith("#refbox("):
                    recs.append(("error", f"{p}:{i + 2}: reference comment not followed by refbox"))
                    continue
                recs.append(("ref", {"file": line[5:].strip(), "strings": parse_tstrings(call), "excerpt": excerpt,
                                      "where": f"{os.path.basename(p)}:{i + 2}"}))
            elif line.startswith("#host(") or line.startswith("#other(") or line.startswith("#refbox(") or line.startswith("#article(") or line.startswith("#wide-article("):
                if not (lines[i - 1].startswith("// T ") or lines[i - 1].startswith("// R ") or lines[i - 1].startswith("// ARTICLE ")):
                    recs.append(("error", f"{p}:{i + 1}: call without its ID comment"))
    return recs


def main():
    segs, labels, spk = load_all()
    results = {}
    # ---------- D ----------
    errD = check_D(segs)
    results["D"] = errD
    # ---------- parse ----------
    recs = parse_book()
    errA, errC, errF, errStruct = [], [], [], []
    host_count = {}
    n_turns = 0
    n_refs = 0
    for kind, r in recs:
        if kind == "error":
            errStruct.append(r)
        elif kind == "turn":
            n_turns += 1
            fid = r["file"]
            d = segs[fid]
            texts = []
            for k in r["segs"]:
                t = d["segments"][k - 1]["text"]
                if k in r["dash"]:
                    # allowed only at a real speaker change, on a dash-marked segment
                    if not (DASH_RE.match(t) and k > 1 and spk[fid][k - 1] != spk[fid][k]):
                        errA.append(f"{r['where']}: dash removed at {fid}-{k} without a speaker change")
                    t = t[2:]
                texts.append(t)
            expected = " ".join(texts)
            got = " ".join(r["paras"])
            if got != expected:
                if ws(got) == ws(expected):
                    pass  # whitespace-only difference is allowed
                else:
                    errA.append(f"{r['where']}: text differs from segments {fid} {r['segs'][0]}-{r['segs'][-1]}")
            # segments must be consecutive within a turn
            if r["segs"] != list(range(r["segs"][0], r["segs"][-1] + 1)):
                errA.append(f"{r['where']}: non-consecutive segments in one turn")
            # C attribution
            for k in r["segs"]:
                if spk[fid][k] != r["label"]:
                    errC.append(f"{r['where']}: {fid}-{k} shown as {r['label']!r}, labels say {spk[fid][k]!r}")
            if r["call_label"] != r["label"]:
                errC.append(f"{r['where']}: call label {r['call_label']!r} != comment label {r['label']!r}")
            if (r["label"] in HOSTS) != r["is_host_call"]:
                errC.append(f"{r['where']}: host/other style does not match label {r['label']!r}")
            if r["label"] in HOSTS:
                for k in r["segs"]:
                    host_count[(fid, k)] = host_count.get((fid, k), 0) + 1
                if r["excerpt"] is not None:
                    r["excerpt"]["host_segs"].extend(r["segs"])
        elif kind == "ref":
            n_refs += 1
            rf = r["file"]
            p = os.path.join(WORK, "references", rf)
            if not os.path.exists(p):
                errF.append(f"{r['where']}: reference file {rf} missing")
                continue
            ref = json.load(open(p, encoding="utf-8"))
            if ref["kind"] == "quran":
                expected = [ref["label"]] + [x for v in ref["verses"] for x in (v["key"], v["text"])]
            else:
                expected = [ref["label"]] + [x for para in ref["paragraphs"] for x in ("", para)]
            if r["strings"] != expected:
                errF.append(f"{r['where']}: reference box differs from {rf}")
            ex = r["excerpt"]
            cites = approved.get(ex["file"], {}) if ex else {}
            if not ex or not any(rf in cites.get(str(k), []) for k in ex["host_segs"]):
                errF.append(f"{r['where']}: reference box {rf} not cited by a host segment of the excerpt above it")
    # ---------- articles (A: unaltered original pages; B: every article and every page exactly once) ----------
    import hashlib, subprocess
    arts = {a["file_id"]: a for a in json.load(open(os.path.join(WORK, "articles.json"), encoding="utf-8"))}
    seen_art = {}
    for kind, r in recs:
        if kind != "article":
            continue
        a = arts.get(r["id"])
        seen_art[r["id"]] = seen_art.get(r["id"], 0) + 1
        if not a:
            errA.append(f"{r['where']}: unknown article {r['id']}")
            continue
        path = os.path.join(ROOT, a["folder"], a["file_name"])
        sha = hashlib.sha256(open(path, "rb").read()).hexdigest()
        if sha != a["sha256"] or sha != r["sha"]:
            errA.append(f"{r['where']}: article file {a['file_name']} differs from the input recorded in articles.json")
        info = subprocess.run(["pdfinfo", path], capture_output=True, text=True).stdout
        npages = int([l for l in info.split("\n") if l.startswith("Pages:")][0].split()[1])
        strs = parse_tstrings(r["call"])
        if strs[0] != "Farid Responds" or strs[1] != f'Source: Farid Responds, article "{a["title"]}"' or strs[2] != "/" + a["folder"] + "/" + a["file_name"]:
            errA.append(f"{r['where']}: article call arguments do not match articles.json")
        if r["call"].startswith("#article("):
            m = re.search(r",\s*(\d+)\)\s*$", r["call"])
            if not m or int(m.group(1)) != npages or r["pages"] != npages:
                errA.append(f"{r['where']}: article {r['id']} does not include all {npages} pages")
        elif not (npages == 1 and a.get("wide_slices")):
            errA.append(f"{r['where']}: wide-article used for a multi-page PDF")
    errB_art = [f"article {k} not in the book" for k in arts if k not in seen_art] + \
               [f"article {k} appears {c} times" for k, c in seen_art.items() if c > 1]
    # ---------- B ----------
    errB = list(errB_art)
    missing = []
    for fid, d in segs.items():
        if fid not in spk:
            errB.append(f"{fid}: no labels")
            continue
        for k in range(1, len(d["segments"]) + 1):
            if spk[fid][k] in HOSTS:
                c = host_count.get((fid, k), 0)
                if c == 0:
                    missing.append(f"{fid}-{k:04d}")
                elif c > 1:
                    errB.append(f"{fid}-{k:04d} appears {c} times")
    if missing:
        errB.append(f"{len(missing)} host segments missing, e.g. {missing[:20]}")
    # ---------- F (source-side) ----------
    for fid, m in approved.items():
        for k, rfs in m.items():
            k = int(k)
            if spk.get(fid) and spk[fid][k] not in HOSTS:
                errF.append(f"approved ref at {fid}-{k} is not in a host segment")
            for rf in rfs:
                ref = json.load(open(os.path.join(WORK, "references", rf), encoding="utf-8"))
                if ref["kind"] not in ("quran", "hadith", "shamela"):
                    errF.append(f"{rf}: kind {ref['kind']} not allowed")
    # reference text never inside speaker text
    ref_texts = set()
    for p in glob.glob(os.path.join(WORK, "references", "*.json")):
        if not re.match(r"^(quran|hadith|shamela)_", os.path.basename(p)) or os.path.basename(p).startswith("quran_chapters"):
            continue
        ref = json.load(open(p, encoding="utf-8"))
        if ref.get("kind") == "quran":
            ref_texts.update(v["text"] for v in ref["verses"] if len(v["text"]) > 60)
        elif ref.get("kind") in ("hadith", "shamela"):
            ref_texts.update(x for x in ref["paragraphs"] if len(x) > 60)
    for kind, r in recs:
        if kind == "turn":
            joined = " ".join(r["paras"])
            for t in ref_texts:
                if t in joined:
                    errF.append(f"{r['where']}: a reference text appears inside speaker text")
    results["A"] = errA + errStruct
    results["B"] = errB
    results["C"] = errC
    results["F"] = errF
    nhost = sum(1 for fid in spk for k in range(1, len(segs[fid]["segments"]) + 1) if spk[fid][k] in HOSTS)
    summary = {
        "files": len(segs), "labeled_files": len(labels), "turns_in_book": n_turns, "reference_boxes": n_refs,
        "host_segments_total": nhost, "host_segments_in_book": len(host_count),
        "articles_in_book": len(seen_art), "articles_total": len(arts),
    }
    with open(os.path.join(ROOT, "output_final", "work", "verify_results.json"), "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "errors": results}, f, ensure_ascii=False, indent=1)
    ok = True
    for c in "ABCDF":
        status = "PASS" if not results[c] else f"FAIL ({len(results[c])})"
        if results[c]:
            ok = False
        print(f"Check {c}: {status}")
        for e in results[c][:10]:
            print("   ", e)
    print(json.dumps(summary))
    sys.exit(0 if ok else 1)


approved = {}
_ap = os.path.join(WORK, "references", "approved_refs.json")
if os.path.exists(_ap):
    approved = json.load(open(_ap, encoding="utf-8"))

if __name__ == "__main__":
    main()
