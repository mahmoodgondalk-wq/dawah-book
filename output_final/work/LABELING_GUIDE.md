# LABELING GUIDE (Stage 3)

You label transcript segments for a book that compiles, word for word, what two YouTube hosts said:
**The Muslim Lantern** (Muhammed Ali; folder "The Muslim Lantern") and **Farid Responds** (Farid al-Bahraini; folder "Farid Responds").
You NEVER rewrite, copy out or summarize the text. You only output labels that refer to segment NUMBERS.

## Input
- `output_final/work/view/<FILE_ID>.txt`: line k == segment k (the Read tool's line number IS the segment number).
  A line starting with `» ` had a raw caption turn-change marker (">>") before it — a hint, not proof, of a speaker change.
  Lines starting with "– " or "- " may also mark a turn change (also only a hint).
- `output_final/work/files.csv`: file_id, channel, title, n_segments.
- `output_final/work/seed_taxonomy.json`: the chapter codes for topics.

Read EVERY line of the file (use Read with offset/limit for files over 2000 lines). Do not sample or skim.

## Output 1: `output_final/work/labels/<FILE_ID>.json`
```json
{"file_id": "ML043",
 "type": "CONVERSATION",
 "confidence": "high",
 "evidence": "Host answers questions from a caller named Eric; greetings and back-and-forth.",
 "speakers": [[1, 2, "The Muslim Lantern"], [3, 8, "Eric"], [9, 9, "The Muslim Lantern"], [10, 10, "Eric"]],
 "doubts": [[120, 134, "unclear whether the host or the guest says this; dialogue logic suggests host"]]
}
```
- `type`: one of `SOLO`, `CONVERSATION`, `REACTION`, `MIXED`.
  - SOLO: only the channel host speaks (monologue, lecture without audience questions, commentary without played clips).
  - CONVERSATION: the host talks with one or more other people (guest, caller, debater, interviewer, audience).
  - REACTION: the host plays clips of other people and comments/responds.
  - MIXED: a combination (e.g. reaction with a live guest, lecture followed by Q&A with clips). Use only when two natures are both substantial.
  - (ARTICLE is not used: all files here are video transcripts.)
- `confidence`: high / medium / low. `evidence`: one line, your own words, no quotation longer than 5 words.
- `speakers`: consecutive ranges `[first, last, label]` covering EVERY segment 1..N exactly once, in order, no gaps, no overlaps.
  A new range starts at every speaker change, even for a one-word reply ("Yeah", "OK", "Right?").
  Adjacent ranges must have different labels (merge them otherwise).
- Speaker labels (exact strings):
  - `The Muslim Lantern` — the host of The Muslim Lantern channel (Muhammed Ali).
  - `Farid Responds` — the host of the Farid Responds channel (Farid).
  - Either host may appear in the other's videos: label them by who they are.
  - `Guest` — any other live participant (guest, caller, debater, interviewer, audience member, co-host).
    If the transcript clearly gives the person's name, use the name instead (e.g. `Eric`, `Sneako`, `Sheikh Uthman`), one consistent label per person within the file.
    Several unnamed participants: `Guest`, `Guest 2`, `Guest 3` (consistent per person when distinguishable; if not distinguishable, use `Guest`).
  - `Clip` — any OTHER person speaking inside a played clip/video/recording.
    Exception: if a played recording is of one of the two hosts themselves speaking (e.g. an old debate of Farid, a clip of The Muslim Lantern), label those segments with that host's label and add a doubt whose reason starts with "host recording:".
  - A whole file that is simply the recording of a debate/conversation the host took part in is a CONVERSATION (the host is labeled as the host).
- Dashes in manually written subtitles: a line such as "– It doesn't? – No, no" holds two speakers, one per dash. In dash PAIRS the first dash does not by itself mean the speaker changed from the previous line; read the flow.
- Isolated "Yeah"/"OK"/"Right" inside a long answer: give it to the listener only when it answers a question/check or the flow clearly shows the other person speaking; otherwise keep it with the current speaker. Flag a doubt only when it is genuinely unclear.
- A name counts as "clearly given" when the transcript clearly addresses or introduces that participant by it (even once, e.g. in the goodbye).
- Reading tweets, comments or documents aloud is the host's own speech (host label). Played audio/video of other people is `Clip`.
- When a clip or turn starts or ends in the middle of a segment, assign the segment to whoever says most of it and add a doubt for that boundary segment.
- How to attribute: use the » and dash markers as hints, then dialogue logic: who asks and who answers, who explains, who is addressed by name, "go ahead", "brother/sister", greetings, introductions, "I'll remove you now", thanks/goodbyes. Short acknowledgments usually belong to the listener. In reactions, the host pauses the clip ("pause", "he says", "let's see what he says", "this guy") and responds; the clip speaker presents the claim being rebutted. Auto-captions without punctuation may change speaker mid-segment: assign the segment to the speaker who says most of it and add a doubt.
- `doubts`: ranges whose attribution you are genuinely unsure about, with a one-line reason. Use `[]` if none. Do not flag routine cases.

## Output 2: `output_final/work/topics/<FILE_ID>.json`
```json
{"file_id": "ML043",
 "ranges": [[1, 61, "P08.C03", "Return of Jesus according to hadith", "overview"],
            [62, 140, "P08.C02", "Jesus denies divinity at his return", "response"]],
 "refs": [[23, "Quran 4:157"], [88, "Sahih al-Bukhari 3448"], [301, "Tafsir Ibn Kathir vol. 2 p. 45"]]
}
```
- `ranges`: consecutive topic ranges `[first, last, chapter_code, subtopic, role]` covering EVERY segment 1..N exactly once, in order.
  - Cut where the subject changes. A range = one coherent discussion of one point (typically 10-150 segments; shorter only when the subject really changes).
    Keep a question together with its answer. Very short incidental bits (fewer than ~10 segments) stay inside the adjacent range, including a short opening greeting (merge into the first range) or a short goodbye (merge into the last range).
    Off-topic stretches of 10+ segments (greetings, stream logistics, channel news, banter, sponsor reads) get their own P16 range.
  - `chapter_code`: the best-fitting code from seed_taxonomy.json (read the scope notes). If really nothing fits, use `"NEW: <proposed chapter title> | <closest Pxx>"`.
  - `subtopic`: a short NEUTRAL label (3-9 words) naming the specific point or question, e.g. "Kalam cosmological argument", "Who wrote the Gospel of Mark", "Age of Aisha: historical context", "Moon splitting reports". No opinions, no evaluation words ("debunked", "destroyed", "lies"). Prefer standard, reusable wording so the same point from different videos gets the same label.
  - `role`: `overview` (introduces/defines/frames the topic), `argument` (host presents a case or evidence), `response` (host answers a question, objection or claim), `illustration` (story, example, anecdote), `conclusion` (summary/closing of the topic), `other` (for P16 ranges: greetings, logistics, announcements, banter).
- `refs`: every place where a HOST segment (The Muslim Lantern / Farid Responds, not Guest/Clip) states an explicit, locatable reference to:
  - the Quran: surah number or name + verse number (any form: "Quran 4:34", "chapter 4 verse 34", "Surah an-Nisa verse 34", "(2:36)" continuing a Quran list). Write as `"Quran S:V"` or `"Quran S:V-W"` (convert a surah name to its number).
  - a hadith collection + hadith number ("Bukhari 2926", "Sahih Muslim hadith number 1234"). Write as `"<Collection> <number>"` using the collection as named (e.g. "Sahih al-Bukhari 2926", "Sunan Abi Dawud 4920", "Jami at-Tirmidhi 3000").
  - a classical Islamic book + volume and/or page ("Tafsir al-Tabari volume 3 page 120"). Write as `"<Book> vol. X p. Y"`.
  References written into the subtitles by the transcriber, e.g. "(Yunus10:62)" or "(Quran4:124)" inside a host segment, DO count (they are written in the host's text).
  Only when the locator (numbers) is actually said/written in that segment (or split over two adjacent segments: give the first). NEVER infer a reference from the meaning of the words, never add a reference the host did not state. Do NOT list Bible or any non-Islamic references. A surah name without a verse number is not a reference. If none, `[]`.

## Rules
- Never copy transcript text into your outputs except at most 5-word fragments inside `evidence`/`doubts` reasons.
- Every segment gets exactly one speaker and exactly one topic range. Never drop segments.
- After writing both files for a FILE_ID, run: `python3 output_final/work/scripts/validate_labels.py <FILE_ID>` and fix every error it reports until it prints OK.
- Do not modify anything else in the repository. Do not run git.
