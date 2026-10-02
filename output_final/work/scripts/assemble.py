#!/usr/bin/env python3
"""ASSEMBLE: generate the Typst book source from taxonomy.json + mapping.json + segments + labels + references.

All speaker text is pulled from the segment files by ID; nothing is typed by hand.
Every turn call in the generated source is preceded by a machine-readable comment
  // T <file_id> <seg ids comma-separated> | <label> | dash:<k,...> | cut:<0/1>
and every reference box by
  // R <reference file name>
so that verify.py can check fidelity, coverage, attribution and references (checks A, B, C, F).

Usage: python3 output_final/work/scripts/assemble.py [--out output_final/book]
"""
import argparse
import csv
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from excerpts import HOSTS, WORK, ROOT, build_turns, load  # noqa: E402

ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV",
         "XVI", "XVII", "XVIII", "XIX", "XX"]


def tstr(s):
    """Typst string literal (exact)."""
    out = []
    for ch in s:
        if ch == "\\":
            out.append("\\\\")
        elif ch == '"':
            out.append('\\"')
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\r":
            out.append("\\r")
        elif ch == "\t":
            out.append("\\t")
        elif ord(ch) < 32:
            out.append("\\u{%x}" % ord(ch))
        else:
            out.append(ch)
    return '"' + "".join(out) + '"'


def files_index():
    return {r["file_id"]: r for r in csv.DictReader(open(os.path.join(WORK, "files.csv"), encoding="utf-8"))}


def source_line(fid, idx):
    r = idx[fid]
    return f'Source: {r["channel"]}, "{r["title"]}"'


def load_ref_index():
    p = os.path.join(WORK, "references", "approved_refs.json")
    if not os.path.exists(p):
        return {}
    # {file_id: {seg_number(str): [ref_file_name, ...]}}
    return json.load(open(p, encoding="utf-8"))


def ref_box(ref_file):
    d = json.load(open(os.path.join(WORK, "references", ref_file), encoding="utf-8"))
    lines = [f"// R {ref_file}"]
    if d["kind"] == "quran":
        items = ", ".join(f"({tstr(v['key'])}, {tstr(v['text'])})" for v in d["verses"])
        lines.append(f'#refbox({tstr(d["label"])}, ({items},))')
    elif d["kind"] == "hadith":
        items = ", ".join(f'("", {tstr(p)})' for p in d["paragraphs"])
        lines.append(f'#refbox({tstr(d["label"])}, ({items},))')
    elif d["kind"] == "shamela":
        items = ", ".join(f'("", {tstr(p)})' for p in d["paragraphs"])
        lines.append(f'#refbox({tstr(d["label"])}, ({items},), arabic: true)')
    else:
        raise ValueError(ref_file)
    return lines


def render_excerpt(ex, idx, refidx):
    fid, first, last = ex["file"], ex["first"], ex["last"]
    turns = build_turns(fid, first, last)
    if not turns:
        return None, []
    out = [f"// EXCERPT {fid} {first}-{last}"]
    for t in turns:
        segs = [k for p in t["paras"] for k in p[0]]
        dash = [p[0][0] for p in t["paras"] if p[2]]
        out.append(f"// T {fid} {','.join(map(str, segs))} | {t['label']} | dash:{','.join(map(str, dash))} | cut:{1 if t['cut'] else 0}")
        paras = ", ".join(tstr(p[1]) for p in t["paras"])
        if t["is_host"]:
            out.append(f"#host({tstr(t['label'])}, ({paras},))")
        else:
            out.append(f"#other({tstr(t['label'])}, ({paras},){', cut: true' if t['cut'] else ''})")
    out.append(f"#source({tstr(source_line(fid, idx))})")
    # reference boxes: refs cited in host segments of this excerpt, in order of first citation
    seen = []
    fr = refidx.get(fid, {})
    host_segs = [k for t in turns if t["is_host"] for p in t["paras"] for k in p[0]]
    for k in host_segs:
        for rf in fr.get(str(k), []):
            if rf not in seen:
                seen.append(rf)
    for rf in seen:
        out.extend(ref_box(rf))
    return out, host_segs


def merge_adjacent(excerpts):
    """Merge consecutive excerpts of the same file that are contiguous (same source, continuous passage)."""
    out = []
    for e in excerpts:
        if out and out[-1]["file"] == e["file"] and out[-1]["last"] + 1 == e["first"]:
            out[-1] = dict(out[-1], last=e["last"])
        else:
            out.append(dict(e))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "output_final", "book"))
    ap.add_argument("--taxonomy", default=os.path.join(WORK, "taxonomy.json"))
    ap.add_argument("--mapping", default=os.path.join(WORK, "mapping.json"))
    args = ap.parse_args()
    tax = json.load(open(args.taxonomy, encoding="utf-8"))
    mapping = json.load(open(args.mapping, encoding="utf-8"))
    idx = files_index()
    refidx = load_ref_index()
    cdir = os.path.join(args.out, "content")
    os.makedirs(cdir, exist_ok=True)
    for f in os.listdir(cdir):
        if f.endswith(".typ"):
            os.remove(os.path.join(cdir, f))
    used_files = set()
    includes = []
    chap_no = 0
    stats = {"excerpts": 0, "turns": 0}
    for pi, part in enumerate(tax["parts"], 1):
        lines = ['#import "../template.typ": *', ""]
        part_has = False
        plines = [f"= Part {ROMAN[pi]}. {part['title']}", ""]
        body = []
        for ch in part["chapters"]:
            ch_lines = []
            sub_no = 0
            for sub in ch["subchapters"]:
                exs = merge_adjacent(mapping.get(sub["id"], []))
                rendered = []
                for ex in exs:
                    r, hs = render_excerpt(ex, idx, refidx)
                    if r:
                        rendered.append(r)
                        used_files.add(ex["file"])
                if not rendered:
                    continue
                sub_no += 1
                if sub_no == 1:
                    chap_no += 1
                ch_lines.append(f"=== {chap_no}.{sub_no} {sub['title']}")
                ch_lines.append(f"// NODE {sub['id']}")
                for i, r in enumerate(rendered):
                    if i:
                        ch_lines.append("#sep()")
                    ch_lines.extend(r)
                    stats["excerpts"] += 1
                ch_lines.append("")
            if ch_lines:
                part_has = True
                body.append(f"== {chap_no}. {ch['title']}")
                body.append("")
                body.extend(ch_lines)
        if part_has:
            lines.extend(plines)
            lines.extend(body)
            name = f"{part['id']}.typ"
            with open(os.path.join(cdir, name), "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")
            includes.append(f'#include "content/{name}"')
    # index of sources
    src = ['#import "template.typ": *', "", "= Index of Sources", ""]
    for ch in ("The Muslim Lantern", "Farid Responds"):
        rows = sorted((r for r in idx.values() if r["file_id"] in used_files and r["channel"] == ch),
                      key=lambda r: r["file_name"])
        if not rows:
            continue
        src.append(f"#source-group({tstr(ch)}, (")
        for r in rows:
            src.append(f"  {tstr(r['title'])},")
        src.append("))")
    with open(os.path.join(args.out, "sources.typ"), "w", encoding="utf-8") as f:
        f.write("\n".join(src) + "\n")
    book = ['#import "template.typ": *', "#show: book-setup", '#include "front.typ"', "#body-start()"] + includes + \
           ['#include "sources.typ"']
    with open(os.path.join(args.out, "book.typ"), "w", encoding="utf-8") as f:
        f.write("\n".join(book) + "\n")
    print(f"parts: {len(includes)}, chapters: {chap_no}, excerpts: {stats['excerpts']}, sources: {len(used_files)}")


if __name__ == "__main__":
    main()
