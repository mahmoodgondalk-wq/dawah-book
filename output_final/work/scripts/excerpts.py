#!/usr/bin/env python3
"""Shared logic: turn an excerpt (file_id, first_seg, last_seg) into a list of turns.

Rules (INSTRUCTIONS 8, 9.2, 9.4):
- every host segment of the excerpt is included, in order, verbatim;
- consecutive segments of the same speaker are merged with a single space;
- a raw turn-change dash at the start of a turn ("– " / "- ") is dropped ONLY when it marks an
  actual speaker change (it is converted into the speaker label); otherwise it stays;
- guest/clip speech is included only as context for the host: a guest/clip turn is kept if
  some host speech FOLLOWS it inside the excerpt; long guest/clip turns are shortened to their
  final segments (the part right before the host answers); the omission is shown as a marker
  outside the text;
- guest/clip turns after the last host segment of the excerpt are not included.
"""
import json
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
WORK = os.path.join(ROOT, "output_final", "work")
HOSTS = ("The Muslim Lantern", "Farid Responds")
CONTEXT_WORDS = {"Clip": 70}
DEFAULT_CONTEXT_WORDS = 90
PARA_TARGET = 120
PARA_MAX = 200
DASH_RE = re.compile(r"^[–-] ")

_cache = {}


def load(fid):
    if fid not in _cache:
        seg = json.load(open(os.path.join(WORK, "segments", fid + ".json"), encoding="utf-8"))
        lab = json.load(open(os.path.join(WORK, "labels", fid + ".json"), encoding="utf-8"))
        spk = [None] * (len(seg["segments"]) + 1)
        for a, b, l in lab["speakers"]:
            for k in range(a, b + 1):
                spk[k] = l
        _cache[fid] = (seg, lab, spk)
    return _cache[fid]


def seg_text(seg, k):
    return seg["segments"][k - 1]["text"]


def display_text(fid, k, turn_start):
    """Text of segment k as shown in the book: the leading turn dash is removed only when
    segment k starts a turn and the speaker really changes at k."""
    seg, lab, spk = load(fid)
    t = seg_text(seg, k)
    if turn_start and k > 1 and spk[k - 1] != spk[k] and DASH_RE.match(t):
        return t[2:], True
    return t, False


def split_paragraphs(fid, ks, first_is_turn_start):
    """Group segment numbers ks (one speaker, consecutive) into paragraphs.
    Returns list of (list_of_k, text, dash_dropped_at_first)."""
    paras = []
    cur, words = [], 0
    for k in ks:
        cur.append(k)
        t = seg_text(load(fid)[0], k)
        words += len(t.split())
        ends = bool(re.search(r"[.!?…][\"'”’)\]]*$", t))
        if (words >= PARA_TARGET and ends) or words >= PARA_MAX:
            paras.append(cur)
            cur, words = [], 0
    if cur:
        if paras and sum(len(seg_text(load(fid)[0], k).split()) for k in cur) < 25:
            paras[-1].extend(cur)
        else:
            paras.append(cur)
    out = []
    for i, p in enumerate(paras):
        texts = []
        dropped = False
        for j, k in enumerate(p):
            t, d = display_text(fid, k, first_is_turn_start and i == 0 and j == 0)
            dropped = dropped or d
            texts.append(t)
        out.append((p, " ".join(texts), dropped))
    return out


def build_turns(fid, first, last):
    """Return list of turns: dict(label, is_host, segs=[k...], paras=[(ks, text, dash_dropped)], cut=bool)."""
    seg, lab, spk = load(fid)
    start = first
    if spk[first] in HOSTS and first > 1 and spk[first - 1] not in HOSTS:
        # the host's first words answer the turn just before the excerpt: include that turn as context
        start = first - 1
        while start > 1 and spk[start - 1] == spk[first - 1]:
            start -= 1
    raw = []
    for k in range(start, last + 1):
        if raw and raw[-1]["label"] == spk[k]:
            raw[-1]["segs"].append(k)
        else:
            raw.append({"label": spk[k], "segs": [k]})
    host_idx = [i for i, t in enumerate(raw) if t["label"] in HOSTS]
    if not host_idx:
        return []
    last_host = host_idx[-1]
    turns = []
    for i, t in enumerate(raw):
        is_host = t["label"] in HOSTS
        if not is_host and i > last_host:
            continue  # nothing of the host follows: not needed as context
        ks = t["segs"]
        cut = False
        if not is_host:
            limit = CONTEXT_WORDS.get(t["label"], DEFAULT_CONTEXT_WORDS)
            keep, words = [], 0
            for k in reversed(ks):
                w = len(seg_text(seg, k).split())
                if keep and words + w > limit:
                    break
                keep.insert(0, k)
                words += w
            ks = keep
            # shown part does not begin where this person's turn begins in the file
            cut = ks[0] > 1 and spk[ks[0] - 1] == t["label"]
        paras = split_paragraphs(fid, ks, True)
        turns.append({"label": t["label"], "is_host": is_host, "segs": ks, "paras": paras, "cut": cut})
    return turns
