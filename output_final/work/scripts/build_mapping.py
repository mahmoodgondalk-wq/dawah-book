#!/usr/bin/env python3
"""Stage 4c: build work/taxonomy.json and work/mapping.json from the consolidation outputs.

Inputs : work/consolidation/<PART>_out.json (one per part), work/consolidation/moves_out.json (placement of the
         passages that a part agent moved to another part), work/seed_taxonomy.json (part order and titles),
         work/part_order.json (optional: final order of parts).
Outputs: work/taxonomy.json  {"parts": [{"id","title","chapters":[{"id","title","subchapters":[{"id","title"}]}]}]}
         work/mapping.json   {"<subchapter id>": [{"file","first","last"} | {"article": "FAxx"}, ...]}  (ordered)
Checks : every range with host speech (work/topic_ranges.json) and every article is placed exactly once.
"""
import glob
import json
import os
import re
import sys

WORK = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def parse_id(rid):
    if rid.startswith("ARTICLE:"):
        return {"article": rid.split(":", 1)[1]}
    m = re.match(r"^([A-Z]{2}\d{3}):(\d+)-(\d+)$", rid)
    return {"file": m.group(1), "first": int(m.group(2)), "last": int(m.group(3))}


def main():
    seed = json.load(open(os.path.join(WORK, "seed_taxonomy.json"), encoding="utf-8"))
    order_p = os.path.join(WORK, "part_order.json")
    part_order = json.load(open(order_p)) if os.path.exists(order_p) else [p["code"] for p in seed["parts"]]
    part_titles = {p["code"]: p["title"] for p in seed["parts"]}
    tp = os.path.join(WORK, "part_titles.json")
    if os.path.exists(tp):
        part_titles.update(json.load(open(tp, encoding="utf-8")))
    outs = {}
    for p in glob.glob(os.path.join(WORK, "consolidation", "P??_out.json")):
        O = json.load(open(p, encoding="utf-8"))
        outs[O["part"]] = O
    # moved passages: placement decided in moves_out.json:
    # {"placements": [{"range": id, "chapter": code, "subchapter": title, "after": id-or-null}]}
    mv = os.path.join(WORK, "consolidation", "moves_out.json")
    placements = json.load(open(mv, encoding="utf-8"))["placements"] if os.path.exists(mv) else []
    chapters = {}
    for part, O in outs.items():
        for ch in O["chapters"]:
            chapters[ch["code"]] = ch
    for pl in placements:
        ch = chapters.get(pl["chapter"])
        if ch is None:
            sys.exit(f"placement into unknown chapter {pl['chapter']}")
        sc = next((s for s in ch["subchapters"] if s["title"] == pl["subchapter"]), None)
        if sc is None:
            sc = {"title": pl["subchapter"], "ranges": []}
            ch["subchapters"].append(sc)
        if pl.get("after") and pl["after"] in sc["ranges"]:
            sc["ranges"].insert(sc["ranges"].index(pl["after"]) + 1, pl["range"])
        else:
            sc["ranges"].append(pl["range"])
    tax = {"parts": []}
    mapping = {}
    placed = {}
    for part in part_order:
        if part not in outs:
            continue
        P = {"id": part, "title": part_titles[part], "chapters": []}
        for ci, ch in enumerate(outs[part]["chapters"], 1):
            cid = ch["code"]
            C = {"id": cid, "title": ch["title"], "subchapters": []}
            for si, sc in enumerate(ch["subchapters"], 1):
                sid = f"{cid}.S{si:02d}"
                C["subchapters"].append({"id": sid, "title": sc["title"]})
                mapping[sid] = [parse_id(r) for r in sc["ranges"]]
                for r in sc["ranges"]:
                    placed[r] = placed.get(r, 0) + 1
            P["chapters"].append(C)
        tax["parts"].append(P)
    # checks
    ranges = json.load(open(os.path.join(WORK, "topic_ranges.json"), encoding="utf-8"))
    need = {r["id"] for r in ranges if r["host_words"] > 0}
    need |= {"ARTICLE:" + a["file_id"] for a in json.load(open(os.path.join(WORK, "articles.json"), encoding="utf-8"))}
    missing = sorted(need - set(placed))
    extra = sorted(set(placed) - need)
    dup = sorted(r for r, c in placed.items() if c > 1)
    print(f"parts {len(tax['parts'])}, chapters {sum(len(p['chapters']) for p in tax['parts'])}, "
          f"subchapters {len(mapping)}, placed {len(placed)}; missing {len(missing)}, extra {len(extra)}, duplicated {len(dup)}")
    if missing or extra or dup:
        print("missing:", missing[:20]); print("extra:", extra[:20]); print("dup:", dup[:20])
        sys.exit(1)
    json.dump(tax, open(os.path.join(WORK, "taxonomy.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(mapping, open(os.path.join(WORK, "mapping.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)


if __name__ == "__main__":
    main()
