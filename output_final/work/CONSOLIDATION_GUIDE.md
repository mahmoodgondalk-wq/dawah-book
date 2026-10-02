# CONSOLIDATION GUIDE (Stage 4: taxonomy and order)

You organize labeled passages of a topical book into sub-chapters and put them in reading order.
You work ONLY with labels (range IDs, chapter codes, short subtopic labels, roles, sizes, source titles).
You never see or write the speakers' text, and you never invent content.

## Input
`output_final/work/consolidation/<PART>_in.txt`, one line per passage (topic range):
`RANGE_ID | chapter_code | subtopic | role | host_words | channel(ML/FR) | video title`
- RANGE_ID = `<file_id>:<first>-<last>` (must be copied exactly).
- chapter_code = the chapter assigned by the labeler (from `output_final/work/seed_taxonomy.json`), or `NEW: <proposed title> | <part>`.
- role = overview / argument / response / illustration / conclusion / other.

## Task
For every chapter of your part (see seed_taxonomy.json; include NEW proposals):
1. Create sub-chapters (neutral, descriptive titles of 2-8 words, no opinions, no evaluative words such as "debunked", "refuted", "lies", "destroyed"). Sub-chapters group passages about the same specific question or argument. Typical size 4-60 passages; a small chapter may have one sub-chapter. Avoid one-passage sub-chapters unless the subject is really distinct.
2. Order the sub-chapters inside the chapter from the most general/foundational to the most specific.
3. Order the passages inside each sub-chapter so the sub-chapter reads as a coherent whole: introductions/definitions (overview) first, then arguments in natural progression, illustrations near the argument they illustrate, then objections and responses, then conclusions. Passages making the SAME point (from different videos) must be placed next to each other.
4. You may move a passage to another chapter of your part if its subtopic clearly belongs there. If it clearly belongs to a chapter of ANOTHER part, list it in `moves` instead (do not place it).
5. NEW proposals: either merge them into an existing chapter of your part (preferred) or keep a new chapter with a neutral title (give it code `<PART>.N1`, `<PART>.N2`, ...).
6. Chapter titles: keep the seed titles; you may adjust a title only to describe its content more accurately (neutral wording).

Every RANGE_ID of the input must appear exactly once in your output (in one sub-chapter, or in `moves`).

## Output: `output_final/work/consolidation/<PART>_out.json`
```json
{"part": "P08",
 "chapters": [
   {"code": "P08.C01", "title": "The Trinity",
    "subchapters": [
      {"title": "Definition of the Trinity", "ranges": ["ML066:1-40", "FR129:3-60"]},
      {"title": "The Trinity and the oneness of God", "ranges": ["..."]}
    ]}
 ],
 "moves": [{"range": "ML043:291-373", "to": "P02.C08", "reason": "about Islamic practices"}]
}
```
Chapters are listed in the seed order (new chapters after the seed chapter they are closest to).
Then run `python3 output_final/work/scripts/check_consolidation.py <PART>` and fix every error until it prints OK.
Do not modify any other file. Do not run git.
