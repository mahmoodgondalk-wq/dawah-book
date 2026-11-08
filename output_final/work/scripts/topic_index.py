#!/usr/bin/env python3
"""Topic index of the videos (user request 2026-11-08): for every topic of the book (part, chapter, sub-chapter, same
order, titles and numbers as the edited book), EVERY video in which a host speaks about it, with the time span of each
passage (from the caption timestamps), even when several videos say the same thing and even for passages that are not in
the book. The user writes his own notes from it.

Sources: work/taxonomy.json (tree), work/mapping.json (order of the excerpts in each sub-chapter, articles),
work/edit/units.json (host passages: file, segments, sub-chapter), caption timestamps (timestamps.py),
book_edited/content/*.typ (book numbering: "== n. title", "=== n.m title" + "// NODE id").
Output: output_final/topic_index/index.typ -> output_final/Topic_Index_of_the_Videos.pdf (built here),
        output_final/topic_index.csv (one row per passage).
  python3 topic_index.py
"""
import csv
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from excerpts import WORK, ROOT  # noqa: E402
from timestamps import file_times, second_at, fmt  # noqa: E402
from assemble import tstr, files_index, articles_index, ROMAN  # noqa: E402
from edit_batches import SKIP_PARTS  # noqa: E402

OUT_DIR = os.path.join(ROOT, "output_final", "topic_index")
PDF = os.path.join(ROOT, "output_final", "Topic_Index_of_the_Videos.pdf")
CSV = os.path.join(ROOT, "output_final", "topic_index.csv")


def book_numbers():
    """{sub id: "n.m"}, {chapter id: n} from the edited book's content files."""
    sub_no, ch_no = {}, {}
    for path in glob.glob(os.path.join(ROOT, "output_final", "book_edited", "content", "*.typ")):
        cur_ch, last_sub = None, None
        for line in open(path, encoding="utf-8"):
            m = re.match(r"^== (\d+)\. ", line)
            if m:
                cur_ch = int(m.group(1))
            m = re.match(r"^=== (\d+\.\d+) ", line)
            if m:
                last_sub = m.group(1)
            m = re.match(r"^// NODE (\S+)", line)
            if m and last_sub:
                sub_no[m.group(1)] = last_sub
                ch_no[m.group(1).rsplit(".", 1)[0]] = cur_ch
    return sub_no, ch_no


def span(u):
    """(start second, end second) of a passage: caption line of its first and of its last character."""
    d, seg_start, _, _ = file_times(u["file"])
    a = seg_start[u["first"] - 1]
    b = seg_start[u["last"] - 1] + max(0, len(d["segments"][u["last"] - 1]["text"]) - 1)
    return second_at(u["file"], a), second_at(u["file"], b)


def main():
    tax = json.load(open(os.path.join(WORK, "taxonomy.json"), encoding="utf-8"))
    mapping = json.load(open(os.path.join(WORK, "mapping.json"), encoding="utf-8"))
    units = json.load(open(os.path.join(WORK, "edit", "units.json"), encoding="utf-8"))
    idx = files_index()
    arts = articles_index()
    by_sub = {}
    for u in units:
        by_sub.setdefault(u["sub"], []).append(u)
    sub_no, ch_no = book_numbers()
    os.makedirs(OUT_DIR, exist_ok=True)
    L = ['#import "template.typ": *', "#show: setup", '#include "intro.typ"', ""]
    rows = []
    n_videos, n_pass, part_no = set(), 0, 0
    for part in tax["parts"]:
        if part["id"] in SKIP_PARTS:
            continue
        body = []
        for ch in part["chapters"]:
            ch_lines = []
            for sub in ch["subchapters"]:
                us = by_sub.get(sub["id"], [])
                art = [e["article"] for e in mapping.get(sub["id"], []) if "article" in e]
                if not us and not art:
                    continue
                # videos in the order their excerpts appear in the sub-chapter, each with its passages in time order
                order = []
                for e in mapping.get(sub["id"], []):
                    if "file" in e and e["file"] not in order:
                        order.append(e["file"])
                for u in us:
                    if u["file"] not in order:
                        order.append(u["file"])
                vids = []
                for f in order:
                    spans = sorted(span(u) + (u["id"], u["host"]) for u in us if u["file"] == f)
                    if not spans:
                        continue
                    r = idx[f]
                    n_videos.add(f)
                    n_pass += len(spans)
                    times = ", ".join(f"({a}, {tstr(fmt(a) if fmt(a) == fmt(b) else fmt(a) + '–' + fmt(b))})" for a, b, *_ in spans)
                    vids.append(f"#video({tstr(r['channel'])}, {tstr(r['title'])}, {tstr(r['url'])}, ({times},))")
                    for a, b, uid, host in spans:
                        rows.append([ROMAN[part_no + 1], part["title"], ch_no.get(ch["id"], ""), ch["title"], sub_no.get(sub["id"], ""),
                                     sub["title"], r["channel"], host, r["title"], fmt(a), fmt(b), f"{r['url']}&t={a}s", uid])
                for a in art:
                    vids.append(f"#article-entry({tstr(arts[a]['title'])})")
                num = sub_no.get(sub["id"])
                ch_lines.append(f"#sub({tstr(num or '–')}, {tstr(sub['title'])})")
                ch_lines.extend(vids)
            if ch_lines:
                body.append(f"#chapter({tstr(str(ch_no.get(ch['id'], '–')))}, {tstr(ch['title'])})")
                body.extend(ch_lines)
        if body:
            part_no += 1
            L.append(f"#part({tstr(ROMAN[part_no])}, {tstr(part['title'])})")
            L.extend(body)
    open(os.path.join(OUT_DIR, "index.typ"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    with open(CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["part", "part_title", "chapter", "chapter_title", "subchapter", "subchapter_title", "channel", "speaker",
                    "video_title", "start", "end", "link", "passage_id"])
        w.writerows(rows)
    print(f"parts {part_no}, videos {len(n_videos)}, passages {n_pass}, csv rows {len(rows)}")


if __name__ == "__main__":
    main()
