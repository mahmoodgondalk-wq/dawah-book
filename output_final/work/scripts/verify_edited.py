#!/usr/bin/env python3
"""Stage 8d: verify the EDITED book (output_final/book_edited) against the transcripts.

Checks:
  A2 Fidelity   every paragraph of every passage is, word for word and in order, a sub-sequence of the host's
                transcribed words of that passage (deletion-only editing: nothing added, changed or reordered);
                the author and the source footnote match the labels and files.csv; articles are the unaltered PDFs
  B2 Coverage   every passage of the plan (work/edit/units.json) appears exactly once, unless it was omitted
                (work/edit/omitted.json, listed with its reason); every article appears exactly once
  C2 Attribution the author line/ordering: each passage is under the author of its segments
  D  Join       unchanged from Stage 7 (segments re-join to the transcripts) — re-run here
  F2 References every reference box equals the saved site text, follows a passage that cites it, never inside a passage
Writes work/verify_edited_results.json; exits 1 if any check fails.
"""
import glob
import hashlib
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
from excerpts import HOSTS, WORK, ROOT  # noqa: E402
from verify import parse_tstrings, check_D, load_all  # noqa: E402
from check_edit import tokens, is_subsequence, strip_editorial, EDIT, MAX_EDITORIAL_RATIO, MAX_EDITORIAL_WORDS  # noqa: E402
from assemble import files_index  # noqa: E402

BOOK = os.environ.get("BOOK_DIR", os.path.join(ROOT, "output_final", "book_edited"))


def main():
    units = {u["id"]: u for u in json.load(open(os.path.join(EDIT, "units.json"), encoding="utf-8"))}
    omitted = json.load(open(os.path.join(EDIT, "omitted.json"), encoding="utf-8"))
    approved = json.load(open(os.path.join(WORK, "references", "approved_refs.json"), encoding="utf-8"))
    idx = files_index()
    arts = {a["file_id"]: a for a in json.load(open(os.path.join(WORK, "articles.json"), encoding="utf-8"))}
    segs, labels, spk = load_all()
    errA, errB, errC, errF = [], [], [], []
    seen, seen_art = {}, {}
    n_pass, n_ref, n_words = 0, 0, 0
    n_editorial = [0]
    ref_texts = set()
    for p in glob.glob(os.path.join(WORK, "references", "*.json")):
        b = os.path.basename(p)
        if not re.match(r"^(quran|hadith|shamela)_", b) or b.startswith("quran_chapters"):
            continue
        ref = json.load(open(p, encoding="utf-8"))
        if ref.get("kind") == "quran":
            ref_texts.update(v["text"] for v in ref["verses"] if len(v["text"]) > 60)
        else:
            ref_texts.update(x for x in ref["paragraphs"] if len(x) > 60)
    for path in sorted(glob.glob(os.path.join(BOOK, "content", "*.typ"))):
        lines = open(path, encoding="utf-8").read().split("\n")
        cur_author, cur_unit = None, None
        for i, line in enumerate(lines):
            where = f"{os.path.basename(path)}:{i + 1}"
            if line.startswith("#author("):
                cur_author = parse_tstrings(line)[0]
            elif line.startswith("// U "):
                uid, host, npar = [x.strip() for x in line[5:].split("|")]
                call = lines[i + 1]
                if not call.startswith("#passage("):
                    errA.append(f"{where}: unit comment not followed by a passage call")
                    continue
                strs = parse_tstrings(call)
                paras, src = strs[:-1], strs[-1]
                u = units.get(uid)
                if u is None:
                    errB.append(f"{where}: unknown passage {uid}")
                    continue
                seen[uid] = seen.get(uid, 0) + 1
                cur_unit = u
                n_pass += 1
                if uid in omitted:
                    errB.append(f"{where}: {uid} is listed as omitted but appears in the book")
                if len(paras) != int(npar) or not paras:
                    errA.append(f"{where}: paragraph count mismatch for {uid}")
                plain, ins = strip_editorial(" ".join(paras))
                out = tokens(plain)
                n_words += len(out)
                if any(len(tokens(x)) > MAX_EDITORIAL_WORDS for x in ins) or sum(len(tokens(x)) for x in ins) > MAX_EDITORIAL_RATIO * max(1, len(out)):
                    errA.append(f"{where}: {uid}: editorial insertions exceed the allowed limit")
                n_editorial[0] += len(ins)
                srcw = tokens(u["text"].replace("⟦…⟧", " "))
                ok, bad = is_subsequence(out, srcw)
                if not ok:
                    errA.append(f"{where}: {uid}: word {out[bad]!r} (output word {bad + 1}) is not in the transcript in this order")
                if "⟦" in " ".join(paras):
                    errA.append(f"{where}: {uid}: marker left in the text")
                # author / attribution
                if host != u["host"] or cur_author != u["host"]:
                    errC.append(f"{where}: {uid} shown under {cur_author!r}/{host!r}, labels say {u['host']!r}")
                for k in u["segs"]:
                    if spk[u["file"]][k] != u["host"]:
                        errC.append(f"{where}: {uid}: segment {k} is not labeled {u['host']!r}")
                exp_src = f'{idx[u["file"]]["channel"]}, "{idx[u["file"]]["title"]}"'
                if src != exp_src:
                    errA.append(f"{where}: {uid}: source footnote does not match files.csv")
                joined = " ".join(paras)
                for t in ref_texts:
                    if t in joined:
                        errF.append(f"{where}: a reference text appears inside a passage")
            elif line.startswith("// R "):
                rf = line[5:].strip()
                call = lines[i + 1]
                n_ref += 1
                pr = os.path.join(WORK, "references", rf)
                if not os.path.exists(pr):
                    errF.append(f"{where}: reference file {rf} missing")
                    continue
                ref = json.load(open(pr, encoding="utf-8"))
                if ref["kind"] == "quran":
                    expected = [ref["label"]] + [x for v in ref["verses"] for x in (v["key"], v["text"])]
                else:
                    expected = [ref["label"]] + [x for para in ref["paragraphs"] for x in ("", para)]
                if parse_tstrings(call) != expected:
                    errF.append(f"{where}: reference box differs from {rf}")
                cites = approved.get(cur_unit["file"], {}) if cur_unit else {}
                if not cur_unit or not any(rf in cites.get(str(k), []) for k in cur_unit["segs"]):
                    errF.append(f"{where}: reference box {rf} not cited by the passage above it")
            elif line.startswith("// ARTICLE "):
                parts = line.split()
                aid, pages, sha = parts[2], int(parts[3].split(":")[1]), parts[4].split(":")[1]
                seen_art[aid] = seen_art.get(aid, 0) + 1
                a = arts.get(aid)
                if not a:
                    errA.append(f"{where}: unknown article {aid}")
                    continue
                fp = os.path.join(ROOT, a["folder"], a["file_name"])
                real = hashlib.sha256(open(fp, "rb").read()).hexdigest()
                info = subprocess.run(["pdfinfo", fp], capture_output=True, text=True).stdout
                npages = int([l for l in info.split("\n") if l.startswith("Pages:")][0].split()[1])
                if real != a["sha256"] or real != sha:
                    errA.append(f"{where}: article {aid} file differs from the input")
                call = lines[i + 1]
                strs = parse_tstrings(call)
                if strs[1] != f'Source: Farid Responds, article "{a["title"]}"' or strs[2] != "/" + a["folder"] + "/" + a["file_name"]:
                    errA.append(f"{where}: article call arguments do not match articles.json")
                if call.startswith("#article(") and (pages != npages or not re.search(r",\s*%d\)\s*$" % npages, call)):
                    errA.append(f"{where}: article {aid} does not include all {npages} pages")
                cur_unit = None
    # coverage
    for uid, u in units.items():
        c = seen.get(uid, 0)
        if uid in omitted:
            continue
        if c == 0:
            errB.append(f"{uid}: passage missing from the book")
        elif c > 1:
            errB.append(f"{uid}: passage appears {c} times")
    for k in arts:
        if seen_art.get(k, 0) != 1:
            errB.append(f"article {k} appears {seen_art.get(k, 0)} times")
    errD = check_D(segs)
    results = {"A": errA, "B": errB, "C": errC, "D": errD, "F": errF}
    src_words = sum(u["words"] for u in units.values())
    summary = {"passages_in_plan": len(units), "passages_in_book": n_pass, "passages_omitted": len(omitted),
               "words_transcribed": src_words, "words_in_book": n_words, "editorial_insertions": n_editorial[0], "reference_boxes": n_ref,
               "articles_in_book": sum(seen_art.values()), "articles_total": len(arts), "files": len(segs)}
    json.dump({"summary": summary, "errors": results}, open(os.path.join(WORK, "verify_edited_results.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    ok = True
    for c in "ABCDF":
        print(f"Check {c}: {'PASS' if not results[c] else 'FAIL (%d)' % len(results[c])}")
        for e in results[c][:10]:
            print("   ", e)
        ok &= not results[c]
    print(json.dumps(summary))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
