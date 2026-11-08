#!/usr/bin/env python3
"""Stage 8 (audit, user instruction 2026-11-08): list every cut of a batch, for a review that restores everything cut by
judging the host's words (as wrong, doubtful, exaggerated, offensive, harsh, weak, off-topic...) instead of as superfluous.

For each passage of the batch (source = work/edit/units.json, edited = work/edit/out/E###.txt) the words of the source that
are not in the edited text are grouped into cut spans (difflib alignment). Spans with fewer than 3 content words (fillers,
"you know", "right?", stammers) are not listed. Each span is shown between the kept words before and after it, with the
share of its content words that also occur in the kept text of the same sub-chapter ("seen") - a high share suggests a
repetition, a low share a point that is not in the book. Omitted passages are listed whole, with their reason.
  python3 audit_cuts.py E079 [...]   -> work/edit/audit/E079.in.txt
"""
import difflib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_edit import units, parse_out, OMIT, EDIT, TOKEN, strip_editorial  # noqa: E402

FILLER = set("""a an the and or but so if of to in on at by for with from as is are was were be been being am i you he she it we
they me him her us them my your his its our their this that these those there here what which who whom whose when where why how
not no yes yeah yep okay ok oh uh um uhm hmm like just right well now then also very really actually basically literally kind
sort know mean say said says gonna wanna gotta let lets do does did done have has had will would can could should shall may
might must about all any some one thing things stuff guys bro brother sister man look listen see go going get got okay""".split())
AUD = os.path.join(EDIT, "audit")


def toks(s):
    return [(m.group(0).lower(), m.start(), m.end()) for m in TOKEN.finditer(s.replace("’", "'"))]


def content(ws):
    return [w for w in ws if w not in FILLER and len(w) > 1]


def main(batch):
    U = units()
    blocks = parse_out(os.path.join(EDIT, "out", batch + ".txt"))
    kept_sub = {}
    for uid, t in blocks:
        if not OMIT.match(t.strip()):
            kept_sub.setdefault(U[uid]["sub"], set()).update(w for w, *_ in toks(strip_editorial(t)[0]))
    out, n_spans, n_words = [], 0, 0
    for uid, t in blocks:
        u = U[uid]
        src = u["text"]
        t = t.strip()
        m = OMIT.match(t)
        if m:
            out.append(f"### {uid} | {u['sub']} | OMITTED: {m.group(1)}")
            out.append("    " + " ".join(src.split()))
            out.append("")
            n_words += len(src.split())
            continue
        st = toks(src)
        ot = [w for w, *_ in toks(strip_editorial(t)[0])]
        sm = difflib.SequenceMatcher(None, [w for w, *_ in st], ot, autojunk=False)
        kept = set()
        for a, b, n in sm.get_matching_blocks():
            kept.update(range(a, a + n))
        spans, i = [], 0
        while i < len(st):
            if i in kept:
                i += 1
                continue
            j = i
            while j < len(st) and j not in kept:
                j += 1
            spans.append((i, j))
            i = j
        lines = []
        seen_words = kept_sub.get(u["sub"], set())
        for i, j in spans:
            cw = content([w for w, *_ in st[i:j]])
            if len(cw) < 3:
                continue
            seen = sum(w in seen_words for w in cw) / len(cw)
            a, b = st[i][1], st[j - 1][2]
            pre = src[max(0, (st[max(0, i - 8)][1] if i else 0)):a]
            post = src[b:(st[min(len(st) - 1, j + 7)][2] if j < len(st) else b)]
            lines.append(f"  [{len(lines) + 1}] seen {seen:.0%} | …{' '.join(pre.split())} ⟨CUT: {' '.join(src[a:b].split())}⟩ {' '.join(post.split())}…")
            n_spans += 1
            n_words += j - i
        if lines:
            out.append(f"### {uid} | {u['sub']} | kept passage")
            out.extend(lines)
            out.append("")
    os.makedirs(AUD, exist_ok=True)
    with open(os.path.join(AUD, batch + ".in.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print(f"{batch}: {n_spans} cut spans + {sum(1 for x in out if 'OMITTED' in x)} omitted passages, {n_words} words to review")


if __name__ == "__main__":
    for b in sys.argv[1:]:
        main(b)
