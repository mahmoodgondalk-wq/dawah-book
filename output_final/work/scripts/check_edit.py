#!/usr/bin/env python3
"""Stage 8b: validate an edited batch (work/edit/out/<BATCH>.txt) against its input units.

Rule: the words of every edited passage, in order, must be a sub-sequence of the words of the host's
transcribed passage (deletion-only editing; case, punctuation and whitespace are free). Nothing may be added,
changed or reordered. A passage may be omitted with "[omitted: reason]".
  python3 check_edit.py <BATCH> [...]   -> prints errors/warnings, "OK" when there are no errors
"""
import json
import os
import re
import sys

WORK = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EDIT = os.path.join(WORK, "edit")
TOKEN = re.compile(r"[^\W_]+(?:'[^\W_]+)*")
OMIT = re.compile(r"^\[omitted:\s*(.+?)\]\s*$", re.S)
_units = None


def tokens(s):
    s = s.replace("’", "'").replace("ʼ", "'").replace("‘", "'")
    return [t.lower() for t in TOKEN.findall(s)]


def is_subsequence(out, src):
    """Returns (ok, index_of_first_bad_output_token)."""
    j = 0
    n = len(src)
    for i, t in enumerate(out):
        while j < n and src[j] != t:
            j += 1
        if j == n:
            return False, i
        j += 1
    return True, None


def units():
    global _units
    if _units is None:
        _units = {u["id"]: u for u in json.load(open(os.path.join(EDIT, "units.json"), encoding="utf-8"))}
    return _units


def parse_out(path):
    blocks, cur, buf = [], None, []
    for line in open(path, encoding="utf-8"):
        if line.startswith("### "):
            if cur is not None:
                blocks.append((cur, "".join(buf)))
            cur, buf = line[4:].strip().split(" ")[0].split("|")[0].strip(), []
        elif cur is not None:
            buf.append(line)
    if cur is not None:
        blocks.append((cur, "".join(buf)))
    return blocks


def check(batch):
    errs, warns = [], []
    B = {b["batch"]: b for b in json.load(open(os.path.join(EDIT, "batches.json")))}
    if batch not in B:
        return [f"unknown batch {batch}"], []
    path = os.path.join(EDIT, "out", batch + ".txt")
    if not os.path.exists(path):
        return [f"missing {path}"], []
    U = units()
    expected = B[batch]["units"]
    blocks = parse_out(path)
    seen = {}
    for uid, text in blocks:
        seen[uid] = seen.get(uid, 0) + 1
        if uid not in U or uid not in expected:
            errs.append(f"{uid}: not a passage of this batch")
            continue
        if seen[uid] > 1:
            errs.append(f"{uid}: appears more than once")
            continue
        t = text.strip()
        if OMIT.match(t):
            warns.append(f"{uid}: omitted ({OMIT.match(t).group(1).strip()})")
            continue
        if "⟦" in t or "⟧" in t or "[guest" in t.lower() or "[omitted" in t.lower():
            errs.append(f"{uid}: marker or bracketed note left in the text")
        src = tokens(U[uid]["text"].replace("⟦…⟧", " "))
        out = tokens(t)
        if not out:
            errs.append(f"{uid}: empty text (use [omitted: reason] to leave a passage out)")
            continue
        ok, i = is_subsequence(out, src)
        if not ok:
            ctx = " ".join(out[max(0, i - 4):i + 4])
            errs.append(f"{uid}: added or changed word {out[i]!r} (output word {i + 1}: '...{ctx}...')")
            continue
        r = len(out) / max(1, len(src))
        if r < 0.4:
            warns.append(f"{uid}: low retention {r:.0%} ({len(out)}/{len(src)} words) - check that no argument was lost")
        elif r > 0.985:
            warns.append(f"{uid}: no change ({r:.0%} kept)")
    missing = [u for u in expected if u not in seen]
    if missing:
        errs.append(f"{len(missing)} passages missing, e.g. {missing[:8]}")
    if [b[0] for b in blocks if b[0] in expected] != [u for u in expected if u in seen]:
        warns.append("passages are not in the input order")
    return errs, warns


if __name__ == "__main__":
    bad = 0
    for b in sys.argv[1:]:
        e, w = check(b)
        for x in w:
            print("   warning:", x)
        for x in e:
            print("   ERROR:", x)
        print(b, "OK" if not e else f"{len(e)} ERRORS")
        bad += bool(e)
    sys.exit(1 if bad else 0)
