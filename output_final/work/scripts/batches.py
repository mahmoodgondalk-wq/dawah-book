#!/usr/bin/env python3
"""Plan labeling batches and report their status.
  python3 batches.py plan      -> writes work/batches.json (only if it does not exist)
  python3 batches.py status    -> per batch: done/total files (done = labels+topics validate without errors)
  python3 batches.py todo N    -> print the next N batches that are not complete
"""
import csv
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
WORK = os.path.join(ROOT, "output_final", "work")
BFILE = os.path.join(WORK, "batches.json")
TARGET_WORDS = 25000

sys.path.insert(0, os.path.dirname(__file__))
from validate_labels import validate  # noqa: E402


def plan():
    if os.path.exists(BFILE):
        print("batches.json exists; not overwriting")
        return
    rows = list(csv.DictReader(open(os.path.join(WORK, "files.csv"), encoding="utf-8")))
    batches = []
    cur, words = [], 0
    for r in rows:  # file order: FR..., ML...
        w = int(r["n_words"])
        if cur and words + w > TARGET_WORDS:
            batches.append({"batch": f"B{len(batches) + 1:02d}", "files": cur, "words": words})
            cur, words = [], 0
        cur.append(r["file_id"])
        words += w
    if cur:
        batches.append({"batch": f"B{len(batches) + 1:02d}", "files": cur, "words": words})
    json.dump(batches, open(BFILE, "w"), indent=1)
    print(len(batches), "batches")


def is_done(fid):
    errs, _ = validate(fid)
    return not errs


def status(verbose=True):
    batches = json.load(open(BFILE))
    out = []
    for b in batches:
        done = [f for f in b["files"] if is_done(f)]
        out.append((b["batch"], len(done), len(b["files"]), b["words"]))
        if verbose:
            print(f'{b["batch"]}: {len(done)}/{len(b["files"])} files, {b["words"]} words')
    return batches, out


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "plan":
        plan()
    elif cmd == "status":
        _, out = status()
        tot = sum(o[2] for o in out)
        dn = sum(o[1] for o in out)
        print(f"TOTAL {dn}/{tot} files labeled; complete batches: {sum(1 for o in out if o[1] == o[2])}/{len(out)}")
    elif cmd == "todo":
        n = int(sys.argv[2])
        batches, out = status(verbose=False)
        k = 0
        for b, o in zip(batches, out):
            if o[1] < o[2]:
                missing = [f for f in b["files"] if not is_done(f)]
                print(b["batch"], " ".join(missing))
                k += 1
                if k >= n:
                    break


if __name__ == "__main__":
    main()
