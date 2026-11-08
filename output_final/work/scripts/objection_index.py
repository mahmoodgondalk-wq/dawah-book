#!/usr/bin/env python3
"""Index of the objections to Islam and the hosts' answers (user request 2026-11-08): for every topic of the book that is an
objection to Islam (work/objection_subs.json: sections with the chosen sub-chapters, numbered as in the edited book), EVERY
video in which it comes up, with the time span of each exchange: the objection (put by a guest, a caller or a clip, or
quoted by the host) together with the host's answer. Spans come from the excerpts of work/mapping.json (all speakers),
not only from the host's passages as in topic_index.py.
Output: output_final/objection_index/index.typ -> output_final/Objections_to_Islam_Index.pdf, output_final/objection_index.csv
  python3 objection_index.py
"""
import csv
import json
import os
import sys

import typst

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from excerpts import WORK, ROOT  # noqa: E402
from timestamps import file_times, second_at, fmt  # noqa: E402
from assemble import tstr, files_index, articles_index, merge_adjacent  # noqa: E402
from topic_index import book_numbers  # noqa: E402

OUT_DIR = os.path.join(ROOT, "output_final", "objection_index")
PDF = os.path.join(ROOT, "output_final", "Objections_to_Islam_Index.pdf")
CSV = os.path.join(ROOT, "output_final", "objection_index.csv")
FONTS = [os.path.join(ROOT, "output_final", "book", "fonts")]


def excerpt_span(f, first, last):
    d, seg_start, _, _ = file_times(f)
    a = seg_start[first - 1]
    b = seg_start[last - 1] + max(0, len(d["segments"][last - 1]["text"]) - 1)
    return second_at(f, a), second_at(f, b)


def main():
    tax = json.load(open(os.path.join(WORK, "taxonomy.json"), encoding="utf-8"))
    mapping = json.load(open(os.path.join(WORK, "mapping.json"), encoding="utf-8"))
    sections = json.load(open(os.path.join(WORK, "objection_subs.json"), encoding="utf-8"))
    subs = {s["id"]: (s, ch) for p in tax["parts"] for ch in p["chapters"] for s in ch["subchapters"]}
    idx = files_index()
    arts = articles_index()
    sub_no, ch_no = book_numbers()
    os.makedirs(OUT_DIR, exist_ok=True)
    t = open(os.path.join(ROOT, "output_final", "topic_index", "template.typ"), encoding="utf-8").read()
    t = t.replace("[Part #num. #title]", "[#num. #title]").replace("Topic Index of the Videos", "Objections to Islam: Index of the Videos")
    open(os.path.join(OUT_DIR, "template.typ"), "w", encoding="utf-8").write(t)
    L = ['#import "template.typ": *', "#show: setup", '#include "intro.typ"', ""]
    rows, videos, n_ex = [], set(), 0
    for k, (title, ids) in enumerate(sections, 1):
        L.append(f"#part({tstr(str(k))}, {tstr(title)})")
        last_ch = None
        for sid in ids:
            sub, ch = subs[sid]
            exs = merge_adjacent(mapping.get(sid, []))
            if not exs:
                continue
            if ch["id"] != last_ch:
                L.append(f"#chapter({tstr(str(ch_no.get(ch['id'], '–')))}, {tstr(ch['title'])})")
                last_ch = ch["id"]
            L.append(f"#sub({tstr(sub_no.get(sid, '–'))}, {tstr(sub['title'])})")
            order, spans = [], {}
            for e in exs:
                if "article" in e:
                    continue
                if e["file"] not in spans:
                    order.append(e["file"])
                    spans[e["file"]] = []
                spans[e["file"]].append(excerpt_span(e["file"], e["first"], e["last"]))
            for f in order:
                r = idx[f]
                videos.add(f)
                ss = sorted(spans[f])
                n_ex += len(ss)
                times = ", ".join(f"({a}, {tstr(fmt(a) if fmt(a) == fmt(b) else fmt(a) + '–' + fmt(b))})" for a, b in ss)
                L.append(f"#video({tstr(r['channel'])}, {tstr(r['title'])}, {tstr(r['url'])}, ({times},))")
                for a, b in ss:
                    rows.append([title, sub_no.get(sid, ""), sub["title"], r["channel"], r["title"], fmt(a), fmt(b), f"{r['url']}&t={a}s"])
            for e in exs:
                if "article" in e:
                    L.append(f"#article-entry({tstr(arts[e['article']]['title'])})")
    open(os.path.join(OUT_DIR, "index.typ"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    with open(CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["section", "subchapter", "objection_topic", "channel", "video_title", "start", "end", "link"])
        w.writerows(rows)
    typst.compile(os.path.join(OUT_DIR, "index.typ"), output=PDF, root=ROOT, font_paths=FONTS)
    print(f"sections {len(sections)}, videos {len(videos)}, exchanges {n_ex}, csv rows {len(rows)}")


if __name__ == "__main__":
    main()
