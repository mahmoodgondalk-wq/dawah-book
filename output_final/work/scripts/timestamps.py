#!/usr/bin/env python3
"""Stage 8 (footnotes): the time in the video at which each paragraph of the edited book was spoken.

The transcripts have one caption line per timestamp ("[12:34] words ..."). normalize_segment.py built the normalized text
of a file by joining the cleaned caption lines with spaces, and the segments re-join to that text exactly (check D), so
every character of a segment can be traced back to its caption line and that line's timestamp.

An edited paragraph is a sub-sequence of the words of its passage (deletion-only editing). The words of the passage are
aligned to the transcript words with difflib (contiguous runs, i.e. the kept phrases; the rest in order between them);
the paragraph's time range is the timestamp of the caption line of its first word to that of its last word.
  python3 timestamps.py E001 [...]   -> prints the paragraph times of these batches (a check)
"""
import bisect
import difflib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from excerpts import WORK, ROOT  # noqa: E402
from normalize_segment import parse_file, caption_texts, TS_RE  # noqa: E402
from check_edit import TOKEN, strip_editorial  # noqa: E402

TS_VAL = re.compile(r"^\[(\d{1,2}):(\d{2})(?::(\d{2}))?\]")
_files = {}


def _norm(s):
    return s.replace("’", "'").replace("ʼ", "'").replace("‘", "'")


def file_times(fid):
    """(segments doc, list of segment start chars, caption line start chars, caption line seconds) for a file."""
    if fid in _files:
        return _files[fid]
    d = json.load(open(os.path.join(WORK, "segments", fid + ".json"), encoding="utf-8"))
    _, _, body = parse_file(os.path.join(ROOT, d["folder"], d["file_name"]))
    caps = caption_texts(body)
    text, starts, secs = "", [], []
    for line, (ctext, _offs, _trailing) in zip(body, caps):
        if not ctext:
            continue
        m = TS_VAL.match(line)
        if m:
            a, b, c = m.group(1), m.group(2), m.group(3)
            sec = int(a) * 3600 + int(b) * 60 + int(c) if c is not None else int(a) * 60 + int(b)
        else:  # a caption line without its own timestamp continues the previous one
            sec = secs[-1] if secs else 0
        start = len(text) + (1 if text else 0)
        text = (text + " " + ctext) if text else ctext
        starts.append(start)
        secs.append(sec)
    assert text == d["normalized_text"], f"{fid}: caption lines do not rebuild the normalized text"
    seg_start, pos = [], 0
    for s in d["segments"]:
        seg_start.append(pos)
        pos += len(s["text"]) + 1
    _files[fid] = (d, seg_start, starts, secs)
    return _files[fid]


def second_at(fid, char):
    _, _, starts, secs = file_times(fid)
    return secs[bisect.bisect_right(starts, char) - 1]


def source_tokens(unit):
    """[(token, global char offset in the normalized text)] of the host segments of a passage, in order."""
    d, seg_start, _, _ = file_times(unit["file"])
    out = []
    for k in unit["segs"]:
        t = _norm(d["segments"][k - 1]["text"])
        base = seg_start[k - 1]
        out.extend((m.group(0).lower(), base + m.start()) for m in TOKEN.finditer(t))
    return out


def paragraph_times(unit, paras):
    """[(start second, end second)] for each paragraph of an edited passage."""
    src = source_tokens(unit)
    stoks = [t for t, _ in src]
    ptoks = [[t.lower() for t in TOKEN.findall(_norm(strip_editorial(p)[0]))] for p in paras]
    out = [t for p in ptoks for t in p]
    pos = [None] * len(out)
    sm = difflib.SequenceMatcher(None, stoks, out, autojunk=False)
    for a, b, n in sm.get_matching_blocks():
        for i in range(n):
            pos[b + i] = a + i
    # words outside the matched runs: first occurrence in order between their neighbours
    last = -1
    for i, t in enumerate(out):
        if pos[i] is not None:
            last = pos[i]
            continue
        nxt = next((pos[j] for j in range(i + 1, len(out)) if pos[j] is not None), len(stoks))
        j = last + 1
        while j < nxt and stoks[j] != t:
            j += 1
        if j >= nxt:  # cannot happen for a valid deletion-only edit (check_edit); fall back to the neighbour
            j = min(last + 1, len(stoks) - 1)
        pos[i] = last = j
    res, i = [], 0
    for p in ptoks:
        if not p:
            res.append(res[-1] if res else (0, 0))
            continue
        a, b = pos[i], pos[i + len(p) - 1]
        res.append((second_at(unit["file"], src[a][1]), second_at(unit["file"], src[b][1])))
        i += len(p)
    return res


def fmt(sec):
    h, r = divmod(int(sec), 3600)
    m, s = divmod(r, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def fmt_range(a, b):
    return fmt(a) if fmt(a) == fmt(b) else f"{fmt(a)}–{fmt(b)}"


if __name__ == "__main__":
    from check_edit import parse_out, OMIT, units, EDIT
    U = units()
    for batch in sys.argv[1:]:
        for uid, text in parse_out(os.path.join(EDIT, "out", batch + ".txt")):
            t = text.strip()
            if OMIT.match(t):
                continue
            paras = [" ".join(x.split()) for x in t.split("\n\n") if x.strip()]
            times = paragraph_times(U[uid], paras)
            print(uid, " ".join(fmt_range(a, b) for a, b in times))
