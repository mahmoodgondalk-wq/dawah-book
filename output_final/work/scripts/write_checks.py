#!/usr/bin/env python3
"""Stage 7: write output_final/checks.md from
  work/verify_results.json   (checks A, B, C, D, F from verify.py)
  work/glyph_check.json      (check E, font coverage: {"uncovered": [...]} written by check_glyphs.py --json)
  work/visual_check.json     (check E, visual inspection: {"pdf_pages": N, "pages_inspected": [...], "findings": [...], "pass": bool})
  work/references/unretrieved.json, approved_refs.json (reference statistics)
"""
import json
import os
import sys

WORK = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(WORK, "..", "checks.md")

DESC = {
    "A": "Fidelity: every speaker turn in the book is exactly the text of its source segments (only timestamps/noise removed, "
         "whitespace normalized, a turn dash removed only at a real speaker change); articles are the unaltered original PDF pages (sha256)",
    "B": "Coverage: every host segment (The Muslim Lantern / Farid Responds) appears exactly once; every article appears exactly once",
    "C": "Attribution: every turn carries the label of its segments; host/other styles match the labels",
    "D": "Join: the normalized segments of every file re-join to the normalized original transcript",
    "E": "Visual: fonts cover every character (no empty boxes); sample pages inspected (cover, contents, chapter openings, "
         "Arabic reference boxes, article pages, index of sources)",
    "F": "References: every reference box is an unaltered text from quran.com (Saheeh International) / sunnah.com / shamela.ws, "
         "cited by a host segment of the excerpt above it, never inside the speakers' words; never for Bible references",
}


def main():
    V = json.load(open(os.path.join(WORK, "verify_results.json"), encoding="utf-8"))
    G = json.load(open(os.path.join(WORK, "glyph_check.json"), encoding="utf-8"))
    E = json.load(open(os.path.join(WORK, "visual_check.json"), encoding="utf-8"))
    S = V["summary"]
    lines = ["# Verification checks (A-F)", "",
             "Produced by `work/scripts/verify.py` (A, B, C, D, F), `check_glyphs.py` and a visual inspection of rendered pages (E).",
             "", "| Check | Result | Errors |", "|---|---|---|"]
    allok = True
    for c in "ABCDEF":
        if c == "E":
            errs = [f"uncovered character {x}" for x in G.get("uncovered", [])] + ([] if E.get("pass") else ["visual inspection failed"])
        else:
            errs = V["errors"][c]
        ok = not errs
        allok &= ok
        lines.append(f"| {c} | {'PASS' if ok else 'FAIL'} | {len(errs)} |")
    lines += ["", f"**Overall: {'ALL CHECKS PASSED' if allok else 'FAILED'}**", "", "## What each check verifies", ""]
    for c in "ABCDEF":
        lines.append(f"- **{c}** — {DESC[c]}")
    lines += ["", "## Figures", "",
              f"- Transcript files: {S['files']} (all labeled: {S['labeled_files']})",
              f"- Host segments: {S['host_segments_total']} in the sources, {S['host_segments_in_book']} in the book (each exactly once)",
              f"- Speaker turns in the book: {S['turns_in_book']}",
              f"- Articles: {S['articles_in_book']} of {S['articles_total']} (original PDF pages embedded)",
              f"- Reference boxes: {S['reference_boxes']}",
              f"- PDF pages: {E.get('pdf_pages', '?')}; pages inspected visually: {len(E.get('pages_inspected', []))}",
              ""]
    for c in "ABCDF":
        if V["errors"][c]:
            lines += [f"## Errors in check {c}", ""] + [f"- {e}" for e in V["errors"][c][:50]] + [""]
    lines += ["## Check E details", ""]
    lines += [f"- Fonts: {'every character covered' if not G.get('uncovered') else 'UNCOVERED: ' + ', '.join(G['uncovered'])}"]
    lines += [f"- Pages inspected: {', '.join(str(p) for p in E.get('pages_inspected', []))}"]
    lines += [f"- {x}" for x in E.get("findings", [])]
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines[:12]))
    sys.exit(0 if allok else 1)


if __name__ == "__main__":
    main()
