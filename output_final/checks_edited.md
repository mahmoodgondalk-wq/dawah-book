# Verification checks (A-F) - edited book

Produced by `work/scripts/verify_edited.py` (A, B, C, D, F), `check_glyphs.py` and a visual inspection of rendered pages (E).

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

- **A** — Fidelity: every paragraph of every passage is, word for word and in order, a sub-sequence of the host's transcribed words (deletion-only editing: nothing added, changed or reordered; only short square-bracket corrections of garbled caption words, within the limits of the editing guide); every paragraph's footnote gives the right video, link and time (recomputed from the timestamped caption lines); articles are the unaltered original PDF pages (sha256)
- **B** — Coverage: every passage of the plan appears exactly once, unless it was omitted as a repetition or as not an argument (listed in work/edit/omitted.json with its reason); every article appears exactly once
- **C** — Attribution: every passage is shown under the host whose labeled segments it comes from
- **D** — Join: the normalized segments of every file re-join to the normalized original transcript
- **E** — Visual: fonts cover every character (no empty boxes); footnotes numbered 1, 2, 3... on every page of the PDF and the first footnote of every page names its video; sample pages inspected
- **F** — References: every reference box is an unaltered text from quran.com (Saheeh International) / sunnah.com / shamela.ws, cited by the passage above it, never inside the speakers' words; never for Bible references

## Figures

- Transcript files: 774
- Passages in the plan: 5738; in the book: 5181; omitted: 557
- Words: 2321154 transcribed host words, 1357009 in the book (58%)
- Editorial corrections in square brackets: 6065
- Footnotes (one per paragraph, with the video and the time): 13120
- Reference boxes: 1461
- Articles: 8 of 8 (original PDF pages embedded)
- PDF pages: 3327; pages inspected visually: 17

## Check E details

- Fonts: every character covered
- Footnotes in the PDF (The_Muslim_Lantern_and_Farid_Responds_The_Arguments.pdf): 13120 on 2847 pages; numbered from 1 on every page, the first one of each page names its video (2416 'Ibid.' footnotes name it again because they fall first on a page), no mark alone on a line: PASS
- Pages inspected: 1, 3, 4, 23, 24, 25, 60, 958, 959, 1892, 2601, 2783, 3136, 3200, 3311, 3312, 3313
- Cover, About this book, Contents, part title pages (Part I, Part XIII, Part XV), chapter openings, running headers and page numbers render correctly.
- Passages: author line in small capitals, justified text, paragraph footnote marks; square-bracket corrections visible as such.
- Footnotes: numbered from 1 on every page (pdftotext check of all 3327 pages: 2847 pages with footnotes, 13120 footnotes, numbering 1..n on every page); the first footnote of every page names the channel and video (footnote_pages.py: 2416 'Ibid.' footnotes that fall first on a page name the video again; check_pdf_footnotes.py: 0 pages starting with Ibid.); every time is a link to the video at that second (checked on p. 25).
- Fixed during this check: in the first build, footnote numbers were wrong on 116 pages (footnote text that depended on its position did not converge in layout); replaced by footnote_pages.py, which fixes the list of footnotes naming the video before the final layout.
- Fixed during this check: 3 footnote marks stood alone on a line after a question mark (p. 60, 639, 2331); a word joiner now keeps the mark with the last word (0 left).
- Reference boxes (quran.com Saheeh International, sunnah.com) are shaded, headed with their source and placed after the passage, outside the hosts' words (pp. 60, 2783, 959).
- Arabic quoted by a host inside a passage renders right-to-left with the Amiri font (pp. 2783, 959); no empty boxes (font check: 0 uncovered characters).
- Articles are reproduced as their original pages with a source line (p. 958).
- Index of Sources lists the video titles by channel (pp. 3312-3313).
- Known limitation, not a layout error: a few names garbled by the automatic captions are left as captioned when the right name could not be established (e.g. 'Navich', p. 3200).
