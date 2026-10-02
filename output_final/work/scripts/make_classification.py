#!/usr/bin/env python3
"""Write work/classification.csv from the label files (folder, file name, title, type, confidence, evidence)."""
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from excerpts import WORK  # noqa: E402

rows = list(csv.DictReader(open(os.path.join(WORK, "files.csv"), encoding="utf-8")))
out = []
missing = 0
for r in rows:
    lp = os.path.join(WORK, "labels", r["file_id"] + ".json")
    if not os.path.exists(lp):
        missing += 1
        continue
    L = json.load(open(lp, encoding="utf-8"))
    out.append([r["folder"], r["file_name"], r["title"], L["type"], L["confidence"], L["evidence"], r["file_id"]])
ap = os.path.join(WORK, "articles.json")
if os.path.exists(ap):
    for a in json.load(open(ap, encoding="utf-8")):
        ev = {"FA03": "one-page isnad diagram (no timestamps); published by Farid Responds"}.get(
            a["file_id"], "PDF with written prose, headings and footnotes; no timestamps")
        conf = "medium" if a["file_id"] in ("FA03",) else "high"
        out.append([a["folder"], a["file_name"], a["title"], "ARTICLE", conf, ev, a["file_id"]])
with open(os.path.join(WORK, "classification.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["folder", "file_name", "title", "type", "confidence", "evidence", "file_id"])
    w.writerows(out)
print(f"classification.csv: {len(out)} rows ({missing} files not yet labeled)")
