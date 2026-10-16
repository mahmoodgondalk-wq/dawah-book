#!/usr/bin/env python3
"""Stage 8a: plan the editing batches and write their input files.

  python3 edit_batches.py plan      -> work/edit/units.json, work/edit/batches.json, work/edit/in/E###.txt (only if batches.json is absent)
  python3 edit_batches.py status    -> per batch: done or not (done = out/E###.txt exists and check_edit passes)
  python3 edit_batches.py todo N    -> the next N batches that are not done

A unit is the host speech of one excerpt of the mapping (one file, one host, consecutive host segments; other
speakers' segments in between are replaced by the marker ⟦…⟧). Units are listed in book order (part_order,
chapters, sub-chapters, passages); Part P16 (Other Remarks: greetings, announcements, logistics) is left out
of the edited book. Articles are kept as embedded PDF pages and are not units.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from excerpts import HOSTS, WORK, load  # noqa: E402
from assemble import files_index, merge_adjacent  # noqa: E402

EDIT = os.path.join(WORK, "edit")
TARGET_WORDS = 18000
MAX_WORDS = 30000
SKIP_PARTS = {"P16"}
MARK = " ⟦…⟧ "


def units_of_excerpt(fid, first, last):
    """Split an excerpt into units: one per run of host segments with the same host label."""
    seg, lab, spk = load(fid)
    units = []
    cur = None  # {"host", "segs": [k...], "text_parts": [...]}
    gap = False
    for k in range(first, last + 1):
        lbl = spk[k]
        if lbl in HOSTS:
            if cur and cur["host"] != lbl:
                units.append(cur)
                cur = None
            if cur is None:
                cur = {"host": lbl, "segs": [], "parts": []}
                gap = False
            if gap:
                cur["parts"].append(MARK.strip())
            cur["parts"].append(seg["segments"][k - 1]["text"])
            cur["segs"].append(k)
            gap = False
        else:
            gap = cur is not None
    if cur:
        units.append(cur)
    out = []
    for u in units:
        text = " ".join(u["parts"])
        out.append({"id": f"{fid}:{u['segs'][0]}-{u['segs'][-1]}", "file": fid, "host": u["host"],
                    "first": u["segs"][0], "last": u["segs"][-1], "segs": u["segs"], "text": text,
                    "words": sum(len(p.split()) for p in u["parts"] if p != MARK.strip())})
    return out


def plan():
    bfile = os.path.join(EDIT, "batches.json")
    if os.path.exists(bfile):
        print("edit/batches.json exists; not overwriting")
        return
    tax = json.load(open(os.path.join(WORK, "taxonomy.json"), encoding="utf-8"))
    mapping = json.load(open(os.path.join(WORK, "mapping.json"), encoding="utf-8"))
    idx = files_index()
    os.makedirs(os.path.join(EDIT, "in"), exist_ok=True)
    os.makedirs(os.path.join(EDIT, "out"), exist_ok=True)
    units, subs = [], []
    for pi, part in enumerate(tax["parts"], 1):
        if part["id"] in SKIP_PARTS:
            continue
        for ch in part["chapters"]:
            for sub in ch["subchapters"]:
                su = []
                for ex in merge_adjacent(mapping.get(sub["id"], [])):
                    if "article" in ex:
                        continue
                    for u in units_of_excerpt(ex["file"], ex["first"], ex["last"]):
                        if u["words"] == 0:
                            continue
                        u["sub"] = sub["id"]
                        su.append(u)
                if su:
                    subs.append({"id": sub["id"], "title": sub["title"], "chapter": ch["title"], "part": part["title"],
                                 "units": [u["id"] for u in su], "words": sum(u["words"] for u in su)})
                    units.extend(su)
    json.dump(units, open(os.path.join(EDIT, "units.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    # batches: whole sub-chapters, ~TARGET_WORDS each; a huge sub-chapter is split by passages
    batches, cur, words, cur_subs = [], [], 0, []
    def flush():
        nonlocal cur, words, cur_subs
        if cur:
            batches.append({"batch": f"E{len(batches) + 1:03d}", "units": cur, "words": words, "subchapters": cur_subs})
        cur, words, cur_subs = [], 0, []
    by_id = {u["id"]: u for u in units}
    for s in subs:
        if cur and words + s["words"] > TARGET_WORDS:
            flush()
        for uid in s["units"]:
            if words + by_id[uid]["words"] > MAX_WORDS and cur:
                flush()
            cur.append(uid)
            words += by_id[uid]["words"]
            if s["id"] not in cur_subs:
                cur_subs.append(s["id"])
    flush()
    json.dump(batches, open(bfile, "w"), indent=1)
    subinfo = {s["id"]: s for s in subs}
    for b in batches:
        with open(os.path.join(EDIT, "in", b["batch"] + ".txt"), "w", encoding="utf-8") as f:
            last_sub = None
            for uid in b["units"]:
                u = by_id[uid]
                if u["sub"] != last_sub:
                    s = subinfo[u["sub"]]
                    f.write(f'## SUB-CHAPTER {s["id"]} — {s["title"]}   (chapter: {s["chapter"]}; part: {s["part"]})\n\n')
                    last_sub = u["sub"]
                f.write(f'### {uid} | {u["host"]} | "{idx[u["file"]]["title"]}"\n{u["text"]}\n\n')
    print(f"{len(units)} units, {sum(u['words'] for u in units)} words, {len(subs)} sub-chapters, {len(batches)} batches")


def done(batch):
    from check_edit import check
    p = os.path.join(EDIT, "out", batch + ".txt")
    if not os.path.exists(p):
        return False
    errs, _ = check(batch)
    return not errs


def main():
    cmd = sys.argv[1]
    if cmd == "plan":
        plan()
        return
    batches = json.load(open(os.path.join(EDIT, "batches.json")))
    if cmd == "status":
        n = 0
        for b in batches:
            d = done(b["batch"])
            n += d
            print(b["batch"], "done" if d else "todo", b["words"], "words", len(b["units"]), "passages")
        print(f"TOTAL {n}/{len(batches)} batches done")
    elif cmd == "todo":
        k = int(sys.argv[2])
        for b in batches:
            if not done(b["batch"]):
                print(b["batch"], b["words"], "words", len(b["units"]), "passages")
                k -= 1
                if k == 0:
                    break


if __name__ == "__main__":
    main()
