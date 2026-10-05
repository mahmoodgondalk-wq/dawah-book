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

## Stage 3: LABEL (classification + speakers + topic ranges) — IN PROGRESS
- Guide: `work/LABELING_GUIDE.md`; seed chapter codes: `work/seed_taxonomy.json`; validator: `work/scripts/validate_labels.py`
- Batches: `work/batches.json` (152 batches of ~25k words). Status: `python3 output_final/work/scripts/batches.py status`;
  next incomplete batches: `python3 output_final/work/scripts/batches.py todo 8` (a file is done when its labels+topics validate).
- Each batch is labeled by one subagent with the identical prompt in `work/scripts/agent_prompt.txt` (replace {FILES}).
- Outputs: `work/labels/<id>.json` (type, confidence, evidence, speaker ranges, doubts), `work/topics/<id>.json` (topic ranges, refs).
- Pilot (ML043, FR054, FR002, ML001) done and checked.
- Labeling status: TOTAL 673/774 files labeled; complete batches: 129/152 (as of 2026-10-05 10:28 UTC)
- NOTE: at ~09:30 UTC the API session limit was hit; batches B54, B57-B63 failed mid-way. To resume: run `batches.py todo 10` and relaunch those batches with the same prompt (files already valid are skipped automatically).
- USER INSTRUCTION (2026-10-04): labeling subagents must run on the default model (Opus 5.5); do NOT switch them to Sonnet.
- Oct 2: the weekly usage limit was hit around B57-B64; resumed Oct 4.
- Remaining stages after labeling: Stage 4 consolidation (CONSOLIDATION_GUIDE.md, consolidate_input.py, check_consolidation.py, build_mapping.py), Stage 5 refs (collect_refs.py, resolve_refs.py auto/final + manual_decisions.json, finalize_refs.py), Stage 6 assemble.py + build_pdf.py, Stage 7 verify.py + check_glyphs.py + render_samples.py.
- After all batches: run `python3 output_final/work/scripts/fixups.py` (idempotent) and `make_classification.py`.
## Stage 4: TAXONOMY + MAPPING — NOT STARTED
## Stage 5: REFERENCE TEXTS — NOT STARTED
## Stage 6: ASSEMBLE + PDF — NOT STARTED
## Stage 7: VERIFY (A-F) — NOT STARTED
