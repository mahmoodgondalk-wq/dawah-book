#!/usr/bin/env python3
"""Validate labels/<id>.json and topics/<id>.json for one or more file ids.
Usage: python3 output_final/work/scripts/validate_labels.py ML043 FR002 ...   (or 'all')
Prints OK per file or the list of errors."""
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
WORK = os.path.join(ROOT, "output_final", "work")
HOSTS = {"The Muslim Lantern", "Farid Responds"}
TYPES = {"SOLO", "CONVERSATION", "REACTION", "MIXED"}
ROLES = {"overview", "argument", "response", "illustration", "conclusion", "other"}


def seed_codes():
    t = json.load(open(os.path.join(WORK, "seed_taxonomy.json"), encoding="utf-8"))
    codes = set()
    for p in t["parts"]:
        for c in p["chapters"]:
            codes.add(c["code"])
    return codes


CODES = seed_codes()


def check_partition(ranges, n, what, errs):
    expect = 1
    for i, r in enumerate(ranges):
        if not isinstance(r, list) or len(r) < 3:
            errs.append(f"{what}[{i}] malformed: {r!r}")
            return
        a, b = r[0], r[1]
        if not (isinstance(a, int) and isinstance(b, int)):
            errs.append(f"{what}[{i}] bounds not integers: {r[:2]}")
            return
        if a != expect:
            errs.append(f"{what}[{i}] starts at {a}, expected {expect} (gap or overlap)")
            return
        if b < a:
            errs.append(f"{what}[{i}] ends before it starts: {a}-{b}")
            return
        expect = b + 1
    if expect != n + 1:
        errs.append(f"{what} cover 1..{expect - 1}, but file has {n} segments")


def norm_digits(s):
    return re.findall(r"\d+", s)


def validate(fid):
    errs = []
    warns = []
    seg = json.load(open(os.path.join(WORK, "segments", fid + ".json"), encoding="utf-8"))
    n = len(seg["segments"])
    host = seg["channel"]
    lp = os.path.join(WORK, "labels", fid + ".json")
    tp = os.path.join(WORK, "topics", fid + ".json")
    if not os.path.exists(lp):
        return [f"missing {lp}"], warns
    if not os.path.exists(tp):
        return [f"missing {tp}"], warns
    try:
        L = json.load(open(lp, encoding="utf-8"))
    except Exception as e:
        return [f"labels JSON invalid: {e}"], warns
    try:
        T = json.load(open(tp, encoding="utf-8"))
    except Exception as e:
        return [f"topics JSON invalid: {e}"], warns
    if L.get("file_id") != fid:
        errs.append("labels file_id mismatch")
    if L.get("type") not in TYPES:
        errs.append(f"type must be one of {sorted(TYPES)}")
    if L.get("confidence") not in {"high", "medium", "low"}:
        errs.append("confidence must be high/medium/low")
    if not isinstance(L.get("evidence"), str) or not L.get("evidence").strip():
        errs.append("evidence missing")
    sp = L.get("speakers")
    if not isinstance(sp, list) or not sp:
        errs.append("speakers missing")
    else:
        check_partition(sp, n, "speakers", errs)
        prev = None
        for r in sp:
            if len(r) != 3 or not isinstance(r[2], str) or not r[2].strip():
                errs.append(f"speaker range malformed: {r!r}")
                continue
            lab = r[2]
            if lab != lab.strip():
                errs.append(f"label has surrounding spaces: {lab!r}")
            if prev == lab:
                errs.append(f"adjacent ranges with same label {lab!r} at {r[0]} (merge them)")
            prev = lab
            if lab.lower() in {"host", "farid", "muslim lantern", "the muslim lantern:", "farid responds:", "muhammed ali", "mohammed ali", "farid al-bahraini"}:
                errs.append(f"use the exact host label, not {lab!r}")
        labels = {r[2] for r in sp if len(r) == 3}
        if not (labels & HOSTS):
            warns.append("no host label at all in this file")
        if L.get("type") == "SOLO" and labels - HOSTS:
            warns.append(f"type SOLO but non-host labels present: {sorted(labels - HOSTS)}")
        if L.get("type") == "REACTION" and "Clip" not in labels:
            warns.append("type REACTION but no Clip label")
    dl = L.get("doubts")
    if not isinstance(dl, list):
        errs.append("doubts must be a list")
    else:
        for d in dl:
            if not (isinstance(d, list) and len(d) == 3 and isinstance(d[0], int) and isinstance(d[1], int)
                    and 1 <= d[0] <= d[1] <= n and isinstance(d[2], str)):
                errs.append(f"doubt malformed: {d!r}")
    if T.get("file_id") != fid:
        errs.append("topics file_id mismatch")
    rg = T.get("ranges")
    if not isinstance(rg, list) or not rg:
        errs.append("topic ranges missing")
    else:
        check_partition(rg, n, "ranges", errs)
        for r in rg:
            if len(r) != 5:
                errs.append(f"topic range must have 5 items: {r!r}")
                continue
            code, sub, role = r[2], r[3], r[4]
            if not isinstance(code, str) or not (code in CODES or code.startswith("NEW:")):
                errs.append(f"unknown chapter code {code!r} at {r[0]}")
            if not isinstance(sub, str) or not sub.strip():
                errs.append(f"empty subtopic at {r[0]}")
            elif len(sub.split()) > 14:
                errs.append(f"subtopic too long at {r[0]} (max ~9 words)")
            if role not in ROLES:
                errs.append(f"role {role!r} invalid at {r[0]}; use one of {sorted(ROLES)}")
    refs = T.get("refs")
    if not isinstance(refs, list):
        errs.append("refs must be a list")
    else:
        texts = [s["text"] for s in seg["segments"]]
        spk = {}
        if isinstance(sp, list):
            for r in sp:
                if len(r) == 3 and isinstance(r[0], int) and isinstance(r[1], int):
                    for k in range(r[0], r[1] + 1):
                        spk[k] = r[2]
        for ref in refs:
            if not (isinstance(ref, list) and len(ref) == 2 and isinstance(ref[0], int) and isinstance(ref[1], str)):
                errs.append(f"ref malformed: {ref!r}")
                continue
            k, s = ref
            if not 1 <= k <= n:
                errs.append(f"ref segment out of range: {ref!r}")
                continue
            if spk.get(k) not in HOSTS:
                warns.append(f"ref at {k} is in a non-host segment ({spk.get(k)}); it will be ignored")
            window = " ".join(texts[k - 1:k + 2])
            nums = norm_digits(s.split(" ", 1)[1] if s.lower().startswith("quran") else s)
            missing = [x for x in nums if x not in norm_digits(window)]
            if missing:
                warns.append(f"ref {s!r} at {k}: numbers {missing} not found in segments {k}-{k + 2} (check it is really stated there)")
    return errs, warns


def main():
    ids = sys.argv[1:]
    if ids == ["all"]:
        ids = sorted(f[:-5] for f in os.listdir(os.path.join(WORK, "labels")) if f.endswith(".json"))
    bad = 0
    for fid in ids:
        errs, warns = validate(fid)
        if errs:
            bad += 1
            print(f"{fid}: ERRORS")
            for e in errs:
                print("   -", e)
        else:
            print(f"{fid}: OK")
        for w in warns:
            print("   warning:", w)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
