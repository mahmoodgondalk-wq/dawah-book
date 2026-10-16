#!/usr/bin/env python3
"""Stage 4b: list the passages that the part agents moved to another part, with the target chapters' sub-chapters.

Reads work/consolidation/P??_out.json and work/topic_ranges.json.
Writes work/consolidation/moves_in.txt:
  # CHAPTER <code> | <title>
  #   S: <sub-chapter title>            (existing sub-chapters of that chapter, in order)
  MOVE <RANGE_ID> | <subtopic> | <role> | <host_words> | <channel> | <video title> | from <part>: <reason>
and work/consolidation/chapters.txt (every chapter code and title, for moves whose target code does not exist).
The placement decisions go into work/consolidation/moves_out.json (see build_mapping.py).
"""
import glob
import json
import os

WORK = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
C = os.path.join(WORK, "consolidation")


def main():
    outs = {}
    for p in sorted(glob.glob(os.path.join(C, "P??_out.json"))):
        O = json.load(open(p, encoding="utf-8"))
        outs[O["part"]] = O
    chapters = {}
    for part, O in outs.items():
        for ch in O["chapters"]:
            chapters[ch["code"]] = ch
    ranges = {r["id"]: r for r in json.load(open(os.path.join(WORK, "topic_ranges.json"), encoding="utf-8"))}
    by = {}
    for part, O in outs.items():
        for m in O.get("moves", []):
            by.setdefault(m["to"], []).append((part, m))
    with open(os.path.join(C, "chapters.txt"), "w", encoding="utf-8") as f:
        for part in sorted(outs):
            for ch in outs[part]["chapters"]:
                f.write(f'{ch["code"]} | {ch["title"]} | {len(ch["subchapters"])} sub-chapters\n')
    n = 0
    with open(os.path.join(C, "moves_in.txt"), "w", encoding="utf-8") as f:
        for code in sorted(by):
            ch = chapters.get(code)
            f.write(f"# CHAPTER {code} | {ch['title'] if ch else '(code not found: choose another chapter from chapters.txt)'}\n")
            if ch:
                for sc in ch["subchapters"]:
                    f.write(f"#   S: {sc['title']}\n")
            for part, m in by[code]:
                r = ranges.get(m["range"], {})
                f.write(f'MOVE {m["range"]} | {r.get("subtopic", "?")} | {r.get("role", "?")} | {r.get("host_words", "?")} | '
                        f'{"ML" if r.get("channel") == "The Muslim Lantern" else "FR"} | {str(r.get("title", ""))[:70]} | '
                        f'from {part}: {m.get("reason", "")}\n')
                n += 1
    print(f"{n} moved passages into {len(by)} chapters")


if __name__ == "__main__":
    main()
