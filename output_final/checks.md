# Verification checks (A-F)

Produced by `work/scripts/verify.py` (A, B, C, D, F), `check_glyphs.py` and a visual inspection of rendered pages (E).

| Check | Result | Errors |
|---|---|---|
| A | PASS | 0 |
| B | PASS | 0 |
| C | PASS | 0 |
| D | PASS | 0 |
| E | PASS | 0 |
| F | PASS | 0 |

**Overall: ALL CHECKS PASSED**

## What each check verifies

- **A** — Fidelity: every speaker turn in the book is exactly the text of its source segments (only timestamps/noise removed, whitespace normalized, a turn dash removed only at a real speaker change); articles are the unaltered original PDF pages (sha256)
- **B** — Coverage: every host segment (The Muslim Lantern / Farid Responds) appears exactly once; every article appears exactly once
- **C** — Attribution: every turn carries the label of its segments; host/other styles match the labels
- **D** — Join: the normalized segments of every file re-join to the normalized original transcript
- **E** — Visual: fonts cover every character (no empty boxes); sample pages inspected (cover, contents, chapter openings, Arabic reference boxes, article pages, index of sources)
- **F** — References: every reference box is an unaltered text from quran.com (Saheeh International) / sunnah.com / shamela.ws, cited by a host segment of the excerpt above it, never inside the speakers' words; never for Bible references

## Figures

- Transcript files: 774 (all labeled: 774)
- Host segments: 248116 in the sources, 248116 in the book (each exactly once)
- Speaker turns in the book: 64354
- Articles: 8 of 8 (original PDF pages embedded)
- Reference boxes: 1492
- PDF pages: 6688; pages inspected visually: 24

## Check E details

- Fonts: every character covered
- Pages inspected: 1, 2, 3, 4, 5, 20, 24, 32, 123, 304, 545, 740, 1883, 1913, 4720, 4721, 6257, 6258, 6500, 6501, 6673, 6674, 6680, 6688
- Cover, title page, 'How to read this book' legend and the clickable contents (17 parts, 95 chapters, 804 sub-chapters, with page numbers) render correctly; front matter numbered in roman numerals, body in arabic numerals
- Running header shows the current chapter title; page numbers in the footer; every part and chapter opens on a new page
- Host passages in upright type with bold labels; guest/clip passages indented in italics with a left bar; source line under every passage
- Reference boxes (Quran, Saheeh International; sunnah.com hadith) shaded and clearly separated from the speakers' words; Arabic inside speaker text and in hadith boxes is shaped and right-to-left correct
- Article pages are the original PDF pages (vector, unaltered) with the article source line; the wide isnad diagram is shown in overlapping landscape slices
- Index of Sources lists the video titles per channel and the articles; no empty glyph boxes anywhere (501 distinct characters, all covered by the fonts)
