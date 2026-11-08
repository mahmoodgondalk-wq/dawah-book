#!/usr/bin/env python3
"""Stage 8 (audit): statistics said by the hosts that are not in the edited book.
Find statistics (percentages, millions/billions, 'statistics/study/survey' figures) in the hosts' source passages that are
not in the edited book: dropped inside a kept passage, or in an omitted passage; and whether the same figure is kept elsewhere
in the same sub-chapter / anywhere in the book.
Usage: python3 output_final/work/scripts/dropped_stats.py -> work/edit/dropped_stats.json (see output_final/removed_statistics.md).
"""
import difflib, glob, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_edit import units, parse_out, OMIT, EDIT, TOKEN, strip_editorial
U = units()
edits, omitted = {}, {}
for p in sorted(glob.glob(os.path.join(EDIT, 'out', 'E*.txt'))):
    for uid, text in parse_out(p):
        t = text.strip()
        m = OMIT.match(t)
        if m: omitted[uid] = m.group(1)
        else: edits[uid] = t
NUMW = r"(?:\d[\d,.]*|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred)"
STAT = re.compile(rf"\b{NUMW}(?:[\s-]+{NUMW})*\s*(?:%|percent\b|per cent\b|million\b|billion\b|thousand\b|out of (?:\d+|ten|a hundred|100)\b|in (?:every )?(?:\d+|two|three|four|five|six|seven|eight|nine|ten|a hundred|100|a thousand)\b(?= (?:women|men|people|children|marriages|muslims|christians|americans|britons|kids|girls|boys|of)\b)|times (?:more|less|higher|lower)\b)|\b(?:half|a third|one third|two thirds|a quarter|three quarters) of (?:the )?(?:women|men|people|children|marriages|population|americans|christians|muslims|world|country|uk|us)\b|\bstatistic\w*\b[^.?!]{{0,80}}?\d+", re.I)
def toks(s): return [m.group(0).lower() for m in TOKEN.finditer(s.replace('’', "'"))]
kept_text_by_sub, kept_all = {}, []
for uid, t in edits.items():
    plain = strip_editorial(t)[0]
    kept_text_by_sub.setdefault(U[uid]['sub'], []).append(plain.lower())
    kept_all.append(plain.lower())
kept_all = '\n'.join(kept_all)
def norm_fig(s): return ' '.join(toks(s))
rows = []
for uid, u in U.items():
    src = u['text'].replace('⟦…⟧', ' ')
    found = list(STAT.finditer(src))
    if not found: continue
    # token offsets of the source
    stoks = [(m.group(0).lower(), m.start()) for m in TOKEN.finditer(src.replace('’', "'"))]
    if uid in edits:
        out = toks(strip_editorial(edits[uid])[0])
        sm = difflib.SequenceMatcher(None, [t for t, _ in stoks], out, autojunk=False)
        kept = set()
        for a, b, n in sm.get_matching_blocks(): kept.update(range(a, a + n))
    else:
        kept = set()
    starts = [o for _, o in stoks]
    import bisect
    for m in found:
        i0 = bisect.bisect_left(starts, m.start()); i1 = bisect.bisect_left(starts, m.end())
        idx = range(i0, max(i1, i0 + 1))
        if all(i in kept for i in idx): continue
        fig = norm_fig(m.group(0))
        sub = u['sub']
        in_sub = any(fig in ' '.join(toks(x)) for x in kept_text_by_sub.get(sub, []))
        in_book = fig in ' '.join(toks(kept_all)) if not in_sub else True
        a = max(0, m.start() - 220); b = min(len(src), m.end() + 160)
        rows.append({'uid': uid, 'host': u['host'], 'sub': sub, 'figure': m.group(0), 'status': 'omitted: ' + omitted[uid] if uid in omitted else 'cut inside kept passage',
                     'kept_in_subchapter': in_sub, 'kept_in_book': in_book, 'context': ' '.join(src[a:b].split())})
json.dump(rows, open(os.path.join(EDIT, 'dropped_stats.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
import collections
print('dropped figures:', len(rows))
print(collections.Counter((r['status'].split(':')[0], r['kept_in_subchapter']) for r in rows))
print('not kept anywhere in sub-chapter:', sum(not r['kept_in_subchapter'] for r in rows), '; nowhere in book:', sum(not r['kept_in_book'] for r in rows))
