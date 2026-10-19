#!/usr/bin/env python3
"""Stage 8c: generate the Typst source of the EDITED book from the edited batches.

Inputs : work/taxonomy.json, work/mapping.json, work/edit/units.json, work/edit/batches.json, work/edit/out/E###.txt,
         work/references/approved_refs.json, work/articles.json, work/files.csv
Output : output_final/book_edited/{book.typ, content/P??.typ, sources.typ}
Every passage call is preceded by a machine-readable comment
  // U <unit id> | <host> | <n paragraphs>
so that verify_edited.py can re-check fidelity (deletion-only), coverage and references.
Part P16 (Other Remarks) is left out; omitted passages ("[omitted: ...]") are listed in work/edit/omitted.json.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from excerpts import WORK, ROOT  # noqa: E402
from assemble import tstr, files_index, articles_index, render_article, load_ref_index, ref_box, merge_adjacent, ROMAN  # noqa: E402
from check_edit import parse_out, OMIT, EDIT  # noqa: E402
from edit_batches import SKIP_PARTS  # noqa: E402


def load_edits(only=None):
    """{unit id: list of paragraphs} for every edited passage; {unit id: reason} for omitted ones.
    only: optional set of batch ids (preview builds)."""
    edits, omitted = {}, {}
    batches = json.load(open(os.path.join(EDIT, "batches.json")))
    for b in batches:
        if only and b["batch"] not in only:
            continue
        p = os.path.join(EDIT, "out", b["batch"] + ".txt")
        if not os.path.exists(p):
            if "--partial" in sys.argv:
                continue
            sys.exit(f"missing edited batch {b['batch']}")
        for uid, text in parse_out(p):
            t = text.strip()
            m = OMIT.match(t)
            if m:
                omitted[uid] = m.group(1).strip()
            else:
                paras = [" ".join(x.split()) for x in t.split("\n\n")]
                edits[uid] = [x for x in paras if x]
    return edits, omitted


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "output_final", "book_edited"))
    ap.add_argument("--partial", action="store_true", help="test build with the batches edited so far")
    ap.add_argument("--batches", default="", help="preview build: comma-separated batch ids (implies --partial)")
    ap.add_argument("--no-articles", action="store_true", help="preview build: leave the articles out")
    args = ap.parse_args()
    only = set(x for x in args.batches.split(",") if x) or None
    if only and "--partial" not in sys.argv:
        sys.argv.append("--partial")
    tax = json.load(open(os.path.join(WORK, "taxonomy.json"), encoding="utf-8"))
    mapping = json.load(open(os.path.join(WORK, "mapping.json"), encoding="utf-8"))
    units = {u["id"]: u for u in json.load(open(os.path.join(EDIT, "units.json"), encoding="utf-8"))}
    by_excerpt = {}
    for u in units.values():
        by_excerpt.setdefault((u["file"], u["sub"]), []).append(u)
    edits, omitted = load_edits(only)
    idx = files_index()
    refidx = load_ref_index()
    arts = articles_index()
    cdir = os.path.join(args.out, "content")
    os.makedirs(cdir, exist_ok=True)
    for f in os.listdir(cdir):
        if f.endswith(".typ"):
            os.remove(os.path.join(cdir, f))
    used_files, used_articles, includes = set(), set(), []
    chap_no = 0
    stats = {"passages": 0, "omitted": 0, "refboxes": 0}
    part_no = 0
    for part in tax["parts"]:
        if part["id"] in SKIP_PARTS:
            continue
        part_no += 1
        lines = ['#import "../template.typ": *', "", f"= Part {ROMAN[part_no]}. {part['title']}", ""]
        part_has = False
        body = []
        for ch in part["chapters"]:
            ch_lines, sub_no = [], 0
            for sub in ch["subchapters"]:
                rendered, last_author = [], None
                for ex in merge_adjacent(mapping.get(sub["id"], [])):
                    if "article" in ex:
                        if args.no_articles:
                            continue
                        rendered.extend(render_article(ex["article"], arts))
                        used_articles.add(ex["article"])
                        last_author = None
                        continue
                    # units of this excerpt (same file and sub-chapter, inside the excerpt range), in order
                    us = sorted((u for u in by_excerpt.get((ex["file"], sub["id"]), []) if ex["first"] <= u["first"] and u["last"] <= ex["last"]),
                                key=lambda u: u["first"])
                    for u in us:
                        if u["id"] in omitted:
                            stats["omitted"] += 1
                            continue
                        paras = edits.get(u["id"])
                        if not paras:
                            if "--partial" in sys.argv:
                                continue
                            sys.exit(f"no edited text for {u['id']}")
                        if u["host"] != last_author:
                            rendered.append(f"#author({tstr(u['host'])})")
                            last_author = u["host"]
                        rendered.append(f"// U {u['id']} | {u['host']} | {len(paras)}")
                        src = f'{idx[u["file"]]["channel"]}, "{idx[u["file"]]["title"]}"'
                        rendered.append(f"#passage(({', '.join(tstr(p) for p in paras)},), {tstr(src)})")
                        used_files.add(u["file"])
                        stats["passages"] += 1
                        # reference boxes cited in the host segments of this unit
                        seen = []
                        fr = refidx.get(u["file"], {})
                        for k in u["segs"]:
                            for rf in fr.get(str(k), []):
                                if rf not in seen:
                                    seen.append(rf)
                        for rf in seen:
                            rendered.extend(ref_box(rf))
                            stats["refboxes"] += 1
                if not rendered:
                    continue
                sub_no += 1
                if sub_no == 1:
                    chap_no += 1
                ch_lines.append(f"=== {chap_no}.{sub_no} {sub['title']}")
                ch_lines.append(f"// NODE {sub['id']}")
                ch_lines.extend(rendered)
                ch_lines.append("")
            if ch_lines:
                part_has = True
                body.append(f"== {chap_no}. {ch['title']}")
                body.append("")
                body.extend(ch_lines)
        if part_has:
            lines.extend(body)
            name = f"{part['id']}.typ"
            with open(os.path.join(cdir, name), "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")
            includes.append(f'#include "content/{name}"')
        else:
            part_no -= 1
    src = ['#import "template.typ": *', "", "= Index of Sources", ""]
    for ch in ("The Muslim Lantern", "Farid Responds"):
        rows = sorted((r for r in idx.values() if r["file_id"] in used_files and r["channel"] == ch), key=lambda r: r["file_name"])
        if rows:
            src.append(f"#source-group({tstr(ch)}, (")
            src.extend(f"  {tstr(r['title'])}," for r in rows)
            src.append("))")
    arows = sorted((a for a in arts.values() if a["file_id"] in used_articles), key=lambda a: a["file_name"])
    if arows:
        src.append(f"#source-group({tstr('Farid Responds (articles)')}, (")
        src.extend(f"  {tstr(a['title'])}," for a in arows)
        src.append("))")
    with open(os.path.join(args.out, "sources.typ"), "w", encoding="utf-8") as f:
        f.write("\n".join(src) + "\n")
    book = ['#import "template.typ": *', "#show: book-setup", '#include "front.typ"', "#body-start()"] + includes + ['#include "sources.typ"']
    with open(os.path.join(args.out, "book.typ"), "w", encoding="utf-8") as f:
        f.write("\n".join(book) + "\n")
    json.dump(omitted, open(os.path.join(EDIT, "omitted.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"parts: {len(includes)}, chapters: {chap_no}, passages: {stats['passages']}, omitted: {stats['omitted']}, "
          f"reference boxes: {stats['refboxes']}, sources: {len(used_files)}, articles: {len(used_articles)}")


if __name__ == "__main__":
    main()
