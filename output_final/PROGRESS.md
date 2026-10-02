# PROGRESS

Resume rule: read this file first, then continue from the first stage that is not marked DONE.
All scripts are in `work/scripts/`. Run them from the repository root.

## Stage 1-2: NORMALIZE + SEGMENT — DONE
- Script: `python3 output_final/work/scripts/normalize_segment.py` (deterministic; also regenerates `work/view/*.txt`, which is git-ignored)
- 774 .txt files (424 The Muslim Lantern, 350 Farid Responds) -> `work/segments/<file_id>.json`, index in `work/files.csv`
- 355,663 segments, 3,226,878 words. Join check (D) passes for all files.
- 8 non-.txt files ignored (PDFs in `Farid Responds/`), listed in `work/ignored_files.txt`.
  Reason: INSTRUCTIONS section 1 ("Ignore any file that is not a .txt file"); this rule was added to INSTRUCTIONS.md after the PDFs were uploaded.

## Stage 3: LABEL (classification + speakers + topic ranges) — IN PROGRESS
- Guide: `work/LABELING_GUIDE.md`; seed chapter codes: `work/seed_taxonomy.json`; validator: `work/scripts/validate_labels.py`
- Batches: `work/batches.json` (152 batches of ~25k words). Status: `python3 output_final/work/scripts/batches.py status`;
  next incomplete batches: `python3 output_final/work/scripts/batches.py todo 8` (a file is done when its labels+topics validate).
- Each batch is labeled by one subagent with the identical prompt in `work/scripts/agent_prompt.txt` (replace {FILES}).
- Outputs: `work/labels/<id>.json` (type, confidence, evidence, speaker ranges, doubts), `work/topics/<id>.json` (topic ranges, refs).
- Pilot (ML043, FR054, FR002, ML001) done and checked.
## Stage 4: TAXONOMY + MAPPING — NOT STARTED
## Stage 5: REFERENCE TEXTS — NOT STARTED
## Stage 6: ASSEMBLE + PDF — NOT STARTED
## Stage 7: VERIFY (A-F) — NOT STARTED
