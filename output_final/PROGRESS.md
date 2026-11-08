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
- Labeling status: TOTAL 774/774 files labeled; complete batches: 152/152 (as of 2026-11-08 08:46 UTC)
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

## Stage 8: EDITED BOOK (user instruction 2026-10-16) — DONE (2026-11-07): output_final/The_Muslim_Lantern_and_Farid_Responds_The_Arguments.pdf, 3327 pages, 80 MB (git-ignored); checks A-F PASS (checks_edited.md); final report REPORT_edited.md
- USER INSTRUCTION: the verbatim compilation is unreadable as a book. New goal: a well-written book made of the two hosts' OWN WORDS,
  "removing the superfluous from the sentences" — not written by me, no dialogues. English. Complete (all arguments).
  Interpretation: deletion-only editing of the hosts' speech (fillers, repetitions, false starts, chatter, logistics removed; punctuation,
  capitalization and paragraphs free; never add/change/reorder a word), guests and clips dropped, Part P16 (Other Remarks) dropped,
  articles kept as embedded pages, references kept as boxes, source of each passage in a footnote.
- Guide: work/EDITING_GUIDE.md; plan: `python3 output_final/work/scripts/edit_batches.py plan|status|todo N` (147 batches, 5738 passages, 2.32M words)
  inputs work/edit/in/E###.txt, outputs work/edit/out/E###.txt, checker work/scripts/check_edit.py (deletion-only sub-sequence check).
- Each batch is edited by one Opus subagent with the prompt in work/scripts/edit_prompt.txt ({BATCH}, {WORDS}, {N}).
- After all batches: assemble_edited.py -> output_final/book_edited/, build_pdf.py -> output_final/The_Muslim_Lantern_and_Farid_Responds_The_Arguments.pdf,
  verify_edited.py (fidelity = sub-sequence check against the transcripts, coverage of passages, references), checks_edited.md.
- The verbatim compilation (Stages 1-7) is kept as ..._A_Topical_Compilation.pdf.
- 2026-10-17: REPETITIONS. The option the user chose said "complete, organized by topic, without repetitions, ~800-1200 pages".
  Cleaning alone keeps ~78% (=> ~3,500 pages), so a second deletion-only step removes repetitions across the passages of each
  sub-chapter (keep each point once, in its fullest telling): guide work/EDITING_GUIDE_V2.md.
  * Batches E001-E023 were cleaned with guide v1 -> condense pass: `scripts/condense_input.py E###` (backs up to edit/out_v1/,
    writes edit/cin/E###.txt) + agent with scripts/condense_prompt.txt -> rewrites edit/out/E###.txt. Done list: work/edit/condensed.txt
  * Batches E024-E147: one pass with scripts/edit_prompt_v2.txt (clean + condense).
- 2026-10-23: bracket corrections of garbled caption words raised from max(3 words, 2%) to max(5 words, 3%) per passage
  (check_edit.py MIN_EDITORIAL_ALLOWANCE / MAX_EDITORIAL_RATIO, also used by verify_edited.py), and the guide now says that
  misspelt names count as garbled (agents had left e.g. "NS bin Malik"). front.typ explains the square brackets.
  Planned final polish: scan all outputs for misspelt names left uncorrected (E001-E041 used the old limit).
- 2026-10-23: one agent hit the 128k output-token limit of a single response (E039) -> both prompts now say: write per sub-chapter,
  each write under ~3,000 words, short thinking. Agents stopped by a usage limit are resumed with SendMessage (context kept).
- 2026-10-31 USER REQUEST: "a footnote for EVERY thing written, with the video and the minute it comes from" ->
  one footnote per paragraph: channel, "title", m:ss–m:ss (first to last word), linked to youtube &t=<s>; footnotes numbered
  per page (counter reset in the page header); a following paragraph of the same passage says "Ibid." unless its note is
  the first on the page. Times: work/scripts/timestamps.py (caption-line timestamps of the raw transcripts, difflib alignment
  of the edited words); assemble_edited.py emits them, verify_edited.py check A recomputes them. front.typ explains it.
- 2026-10-31: bracket allowance raised again to max(8 words, 6%) per passage (agents were deleting details of badly captioned
  Farid Responds passages - scholars' names, numbers, sources - because of the 3% cap). Guide: correct a garbled name rather
  than delete the detail. Details dropped earlier for this reason are listed in work/edit/restore_todo.md (restore pass at the end).
- STATUS 2026-11-07 night: ALL 147 BATCHES EDITED AND CHECKED (check_edit OK). Full assembly + verify_edited.py: A-F PASS
  (5181 passages in the book, 557 omitted: 263 repetitions, 172 dialogue-only, 66 greetings/logistics, 38 fragments, 18 other;
  1,356,938 words = 58% of 2,321,154; 6056 bracket corrections; 1461 reference boxes; 13120 footnotes; 8/8 articles).
  Remaining: restore pass E045/E047 (agent running), final build of the PDF, glyph + visual check, checks_edited.md, report.
  Usage limits: weekly limit hit 2026-10-24 and 2026-10-31 (each time resumed a week later); 5-hour limit 2026-10-31.
  NEW CONTAINER (2026-11-07): the clone was on the initial commit -> `git fetch origin claude/upbeat-ptolemy-ph4o7a &&
  git checkout -B claude/upbeat-ptolemy-ph4o7a origin/claude/upbeat-ptolemy-ph4o7a`; then `python3 -m pip install typst fonttools`
  (python3 = /usr/local/bin/python3.11; plain `pip` installs into another python). Git-ignored PDFs are not kept across containers.
- DONE 2026-11-07 (final): restore pass E045/E047 merged; reference boxes ML065 fixed; full assembly; A-F PASS.
  Final figures: 5181 passages (4273 The Muslim Lantern, 908 Farid Responds), 557 omitted (267 repetitions, 183 dialogue-only,
  63 greetings/logistics, 25 fragments, 19 other: references to other videos, asides), 1,357,009 words = 58% of 2,321,154;
  6065 bracket corrections; 1461 reference boxes; 13120 footnotes; 8/8 articles; 16 parts, 91 chapters, 774 sub-chapters.
- FOOTNOTE LAYOUT (2026-11-07): the first build had wrong per-page note numbers on 116 pages (note text chosen with
  `context` from the per-page counter did not converge). Now: notes always "Ibid." after the first paragraph of a passage,
  except those listed in book_edited/fullnotes.json; `footnote_pages.py` queries the laid-out book (metadata <fnpos> in every
  note: passage id, paragraph, page) and adds every "Ibid." note that is first on its page, until none is added (monotone;
  converged in 6 rounds, 2416 notes). Run it after every assemble_edited.py, before build_pdf.py. A word joiner keeps the note
  mark with the last word (3 marks stood alone after "?"). check_pdf_footnotes.py checks the built PDF (numbering 1..n per
  page, first note never Ibid., no lone mark) -> work/footnote_pdf_check.json, used by write_checks.py --edited (check E).
- build_pdf.py re-saves the PDF with pikepdf object streams when pikepdf is installed (107 MB -> 80 MB, lossless).
  New container: `python3 -m pip install typst fonttools pikepdf` (+ `--ignore-installed pillow` for page renders).
- 2026-11-08 USER INSTRUCTION (after reading the audit of removed statistics): "how dare you remove all this, it goes against the
  rules: put everything back in the book, EVERYTHING, also anything else removed as 'other'; as per the rule only the host's
  words WITHOUT JUDGING THEM". Done at once: the 2 details E014 cut as wrong, the 26 statistics cut without a reason
  (removed_statistics.md; 2 listed items were false positives, already in the book) and the 19 passages omitted as "other"
  restored by hand (check_edit OK); book rebuilt: 5200 passages, 538 omitted, 13141 footnotes, 3333 pages, A-F PASS.
  AUDIT OF ALL CUTS (running): work/scripts/audit_cuts.py lists every cut span (>= 3 content words) and every omitted passage per
  batch -> work/edit/audit/E###.in.txt (872,725 words in all); one Opus agent per batch with work/scripts/audit_prompt.txt
  ({BATCH}) restores everything cut by judging (wrong, doubtful, exaggerated, offensive, controversial, digression...), keeps
  out only superfluous cuts (filler, repetition in the same sub-chapter, dialogue-only, logistics, garble, other speaker),
  edits work/edit/out/E###.txt, runs check_edit, writes work/edit/audit/E###.log.md. Done list: work/edit/audited.txt.
  To resume: launch the batches not in audited.txt; then assemble_edited.py, reset book_edited/fullnotes.json to {} and run
  footnote_pages.py, build_pdf.py, verify_edited.py, check_glyphs.py, check_pdf_footnotes.py, write_checks.py --edited.
