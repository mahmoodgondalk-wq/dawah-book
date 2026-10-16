# PROGRESS

Resume rule: read this file first, then continue from the first stage that is not marked DONE.
All scripts are in `work/scripts/`. Run them from the repository root.

## Stage 1-2: NORMALIZE + SEGMENT — DONE
- Script: `python3 output_final/work/scripts/normalize_segment.py` (deterministic; also regenerates `work/view/*.txt`, which is git-ignored)
- 774 .txt files (424 The Muslim Lantern, 350 Farid Responds) -> `work/segments/<file_id>.json`, index in `work/files.csv`
- 355,663 segments, 3,226,878 words. Join check (D) passes for all files.
- The 8 PDFs in `Farid Responds/` were first set aside (INSTRUCTIONS section 1), but the USER THEN SAID: "don't ignore the PDF articles".
  They are now included as ARTICLES (metadata: `work/articles.json`, ids FA01-FA08, sha256 of each input file).
  Method (fidelity first): the original PDF pages are embedded unaltered (vector) in the book, one original page per book page
  (`article()` in book/template.typ); the very wide one-page isnad diagram (FA03) is shown in 6 overlapping landscape slices
  (view cropping only). No text is re-extracted, so Arabic, footnotes, tables and diagrams stay exactly as published.
  Each article is labeled `Farid Responds:` with `Source: Farid Responds, article "<title>"` and placed by topic.
  Typst root = repository root (the PDFs are referenced in place as "/Farid Responds/<file>").

## Stage 3: LABEL (classification + speakers + topic ranges) — DONE (2026-10-11)
- Guide: `work/LABELING_GUIDE.md`; seed chapter codes: `work/seed_taxonomy.json`; validator: `work/scripts/validate_labels.py`
- Batches: `work/batches.json` (152 batches of ~25k words). Status: `python3 output_final/work/scripts/batches.py status`;
  next incomplete batches: `python3 output_final/work/scripts/batches.py todo 8` (a file is done when its labels+topics validate).
- Each batch is labeled by one subagent with the identical prompt in `work/scripts/agent_prompt.txt` (replace {FILES}).
- Outputs: `work/labels/<id>.json` (type, confidence, evidence, speaker ranges, doubts), `work/topics/<id>.json` (topic ranges, refs).
- Pilot (ML043, FR054, FR002, ML001) done and checked.
- Labeling status: TOTAL 774/774 files labeled; complete batches: 152/152 (as of 2026-10-16 15:14 UTC)
- NOTE: at ~09:30 UTC the API session limit was hit; batches B54, B57-B63 failed mid-way. To resume: run `batches.py todo 10` and relaunch those batches with the same prompt (files already valid are skipped automatically).
- USER INSTRUCTION (2026-10-04): labeling subagents must run on the default model (Opus 5.5); do NOT switch them to Sonnet.
- Oct 2: the weekly usage limit was hit around B57-B64; resumed Oct 4.
- Remaining stages after labeling: Stage 4 consolidation (CONSOLIDATION_GUIDE.md, consolidate_input.py, check_consolidation.py, build_mapping.py), Stage 5 refs (collect_refs.py, resolve_refs.py auto/final + manual_decisions.json, finalize_refs.py), Stage 6 assemble.py + build_pdf.py, Stage 7 verify.py + check_glyphs.py + render_samples.py.
- After all batches: run `python3 output_final/work/scripts/fixups.py` (idempotent) and `make_classification.py`.
## Stage 4: TAXONOMY + MAPPING — DONE (2026-10-16)
- `python3 output_final/work/scripts/consolidate_input.py` -> work/consolidation/Pxx_in.txt + work/topic_ranges.json
- One Opus subagent per part with the prompt in `work/scripts/consolidation_prompt.txt` ({PART}, {N}) and CONSOLIDATION_GUIDE.md
  -> work/consolidation/Pxx_out.json; check: `python3 output_final/work/scripts/check_consolidation.py P01 ... P16`
- Then: place the 'moves' (work/consolidation/moves_out.json), `build_mapping.py` -> work/taxonomy.json + work/mapping.json
- USER INSTRUCTION (2026-10-16): the book order must be first everything about Islam, then all other religions and/or ideologies.
  Implemented in `work/part_order.json` (P01-P07, P11-P15 = Islam; then P08 Christianity, P09 Bible, P10 Judaism and other religions,
  P17 "Atheism, Secularism and Other Worldviews" = chapters P01.C02, P01.C06, P01.C07, P13.C06, P14.C04 moved there via
  `work/chapter_parts.json` + `work/part_titles.json`; P16 Other Remarks last). build_mapping.py applies these files.
- Reference review notes collected during labeling: work/report_notes.md (manual decisions already in references/manual_decisions.json)
## Stage 5: REFERENCE TEXTS — DONE (2026-10-16)
- collect_refs.py -> resolve_refs.py auto -> manual_decisions.json (250 decisions) -> resolve_refs.py final -> finalize_refs.py
- 1581 approved citations, 783 distinct reference files (quran.com Saheeh International / sunnah.com), 0 unretrieved; shamela.ws: none used (classical book page references skipped, edition uncertain)
## Stage 6: ASSEMBLE + PDF — DONE (2026-10-16): 6688 pages, 104 MB (the PDF is git-ignored: above GitHub's 100 MB file limit; it is sent to the user directly)
- `python3 output_final/work/scripts/assemble.py` -> output_final/book/{book.typ,content/*.typ,sources.typ}; `build_pdf.py` -> output_final/The_Muslim_Lantern_and_Farid_Responds_A_Topical_Compilation.pdf
- taxonomy: 17 parts, 95 chapters, 804 sub-chapters (work/taxonomy.json, work/mapping.json)
## Stage 7: VERIFY (A-F) — DONE (2026-10-16): all checks pass, see output_final/checks.md; final report in output_final/REPORT.md
- verify.py (A,B,C,D,F) -> work/verify_results.json; check_glyphs.py -> work/glyph_check.json; render_samples.py + visual inspection -> work/visual_check.json; write_checks.py -> output_final/checks.md

## Stage 8: EDITED BOOK (user instruction 2026-10-16) — IN PROGRESS
- USER INSTRUCTION: the verbatim compilation is unreadable as a book. New goal: a well-written book made of the two hosts' OWN WORDS,
  "removing the superfluous from the sentences" — not written by me, no dialogues. English. Complete (all arguments).
  Interpretation: deletion-only editing of the hosts' speech (fillers, repetitions, false starts, chatter, logistics removed; punctuation,
  capitalization and paragraphs free; never add/change/reorder a word), guests and clips dropped, Part P16 (Other Remarks) dropped,
  articles kept as embedded pages, references kept as boxes, source of each passage in a footnote.
- Guide: work/EDITING_GUIDE.md; plan: `python3 output_final/work/scripts/edit_batches.py plan|status|todo N` (147 batches, 5738 passages, 2.32M words)
  inputs work/edit/in/E###.txt, outputs work/edit/out/E###.txt, checker work/scripts/check_edit.py (deletion-only sub-sequence check).
- Each batch is edited by one Opus subagent with the prompt in work/scripts/edit_prompt.txt ({BATCH}, {WORDS}, {N}).
- After all batches: assemble_edited.py -> output_final/book_edited/, build_pdf.py -> output_final/The_Muslim_Lantern_and_Farid_Responds_Edited.pdf,
  verify_edited.py (fidelity = sub-sequence check against the transcripts, coverage of passages, references), checks_edited.md.
- The verbatim compilation (Stages 1-7) is kept as ..._A_Topical_Compilation.pdf.
