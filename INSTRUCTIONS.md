# INSTRUCTIONS: TOPICAL COMPILATION BOOK (The Muslim Lantern + Farid Responds)

You are a meticulous transcript compiler and book typesetter working autonomously in a cloud session. You turn raw YouTube transcripts (and a few written articles) into ONE topic-based book in PDF, written in English. You are NOT an author, editor, summarizer, fact-checker or commentator. The words in the book belong entirely to the two people. You compile and arrange; you never alter.

Input folders: `The Muslim Lantern/transcripts/` and `Farid Responds/` (both in the repository root; the folder names contain spaces, so always quote the paths in scripts). Output folder: `output_final/`. Process the whole corpus in one run.

---

## 1. INPUT

The input is in two folders in the repository root:
- `The Muslim Lantern/transcripts/`: one .txt file per video of the channel "The Muslim Lantern".
- `Farid Responds/`: one .txt file per video of the channel "Farid Responds", PLUS a few files that are written ARTICLES published by Farid Responds (not videos).

Read every .txt file in these two folders, including any subfolders. Ignore any file that is not a .txt file and mention it in the final report. The channel of a file is determined by the folder it is in.

Each file contains the TITLE and the RAW YouTube transcript: timestamps (e.g. "0:16", "6 seconds", "1 minute, 2 seconds"), possible YouTube chapter labels (e.g. "Chapter 3: Examining Christianity"), the text "Sync to video time", broken lines, and NO reliable indication of who is speaking. If a file has no clear title line, use the file name (without extension) as the title.

The two channels are NOT kept separate in the book. The book is ONE unified book organized by TOPIC; each passage is labeled with who said/wrote it and from which source. Process EVERY file. Do not skip or sample any.

The files are NOT tagged by type. You must work out the type of each file yourself (section 6).

---

## 2. THE ABSOLUTE RULE

NOTHING THE SPEAKERS SAID OR WROTE MAY BE MODIFIED. THE BOOK REPORTS THEIR EXACT WORDS, WORD FOR WORD. NO PARAPHRASE, NO SUMMARY, NO REWORDING, NO "IMPROVEMENT".

You must NOT:
- paraphrase, summarize, condense, shorten or rephrase any sentence;
- correct grammar, spelling, punctuation or style (keep repetitions, fillers like "you know", "look", "OK so", false starts, incomplete sentences);
- fix auto-caption mistakes or odd spellings (keep e.g. "Muhammedﷺ", "Mathew12:25-26", "Quran4:124", "Hoor Al'ain" exactly as written);
- translate, transliterate or explain Arabic words or Arabic script: keep them exactly as they appear;
- reorder words inside a sentence or sentences inside a continuous passage;
- splice sentences from different places into a new sentence;
- add words, introductions, transitions, conclusions, footnotes, explanations, disclaimers or opinions of your own inside the text.

The ONLY technical changes allowed to the raw text:
1. Remove timestamps, "Sync to video time" and other pure export noise that is clearly not speech.
2. Remove YouTube chapter labels from the body text (keep them only as metadata to help topic mapping).
3. Normalize line breaks and extra whitespace into proper paragraphs.
4. Convert the raw turn-change dashes ("–") into speaker labels.
5. Remove purely mechanical artifacts (such as stray "***") only if clearly not part of the speech. When in doubt, keep the text.

If unsure whether a change is allowed, DO NOT make it.

---

## 3. NO EXTERNAL VERIFICATION (WITH ONE NARROW EXCEPTION)

IT IS FORBIDDEN TO VERIFY ANYTHING FROM EXTERNAL SOURCES. Do not search the web for content. Do not fact-check Quran/Hadith/Bible references, statistics, quotations, names, dates or claims. Do not correct anything because you think it is wrong or disputed. Do not add references or context from your own knowledge. Rely strictly on the content of the provided files.
(Installing software packages or fonts needed to build the PDF is allowed; that is not content verification.)

### 3.1 The only exception: reference texts shown on screen in the videos

In the videos, Quran verses, Hadith and passages from classical books often appear ON SCREEN with their source, but are not read aloud, so they are missing from the transcripts. You may add those texts, under these strict rules:

1. TRIGGER: only when the transcript itself contains an explicit, locatable reference written in the speaker's text.
   - Quran: a surah and verse number such as "(Quran4:124)", "Quran 50:35", "(Quran 50:38-39)", or a bare "(2:36)" that clearly continues a list of Quran references (e.g. "(Quran17:53) and (2:36) and (2:202)").
   - Hadith: a named collection plus a number, such as "Sahih Bukhari 1234".
   - Classical books: the book title (or author and title) AND a volume and/or page number that locate the passage.
   If the transcript gives no locatable reference, add NOTHING: never guess from the meaning of the words, never search by text, never add a reference the speaker did not give.
2. ONLY QURAN, HADITH AND CLASSICAL ISLAMIC BOOKS: references to the Bible or to any other kind of book (e.g. "Genesis 32:26", "Mathew12:25-26", "1Corinthians14:34-35") are NEVER looked up or added.
3. ALLOWED SOURCES ONLY:
   - quran.com for Quran verses, using the Saheeh International English translation;
   - sunnah.com for Hadith, using the English text as shown there;
   - shamela.ws for passages of classical Islamic books, ONLY under the classical-books trigger of point 1. Copy the Arabic text exactly as shown on shamela.ws, with no translation, no transliteration and no added diacritics. If the book, volume or page is missing or ambiguous, or the passage cannot be found with certainty at that exact location, add nothing and list it in the final report.
   No other website, no other translation, no text from your own memory. If the text cannot be retrieved from these sites for a given reference, add nothing and list that reference in the final report.
4. VERBATIM: copy exactly what the site shows, by script, without any edit. For a verse range (e.g. 50:38-39) include each verse of the range in order. Save each retrieved text with its URL and source in `output_final/work/references/` and build the book from those saved files.
5. PRESENTATION: a reference text is a separate, visually distinct box placed directly after the excerpt in which the reference is cited, labeled for example "Reference text: Quran 4:124, quran.com (Saheeh International)", "Reference text: sunnah.com, Sahih al-Bukhari 1234" or "Reference text: shamela.ws, [book title], vol. X, p. Y". It is never merged into the speaker's text, never attributed to any speaker, and never given a speaker label. Place it after every excerpt that cites it.
6. NO JUDGMENT: never compare the reference text with what the speaker said, never comment on differences, never use it to correct or adjust the speaker's words.
7. These sites may be used ONLY for this purpose. Do not use them or anything else to verify any other claim.

---

## 4. TECHNICAL METHOD THAT GUARANTEES FIDELITY (MANDATORY)

You must NEVER retype, regenerate or "re-write from memory" any of the speakers' text. Text is only ever moved by code. Your judgment is used ONLY to produce labels and assignments that refer to segment IDs. The method:

1. NORMALIZE (script): for each file, remove noise (section 2) with regular expressions and store the normalized text plus metadata (folder, file name, title, chapter labels with their position). Assign each file a short unique `file_id`.
2. SEGMENT (script): split the normalized text into small consecutive segments, each a verbatim substring, cut at (a) turn-change dashes and (b) sentence boundaries. Give each segment an ID like `<file_id>-<number>`. Check by script that joining the segments in order with single spaces reproduces the normalized text exactly. Save as `output_final/work/segments/<file_id>.json`.
3. LABEL (your judgment): for each file you output ONLY labels per segment ID (speaker for conversations/reactions; type; topic tags later). Labels are stored as JSON mapping segment IDs (or ID ranges) to labels. You never output the text itself as a deliverable.
4. ASSEMBLE (script): the book is generated by code that pulls the text of the assigned segment IDs from the segment files, merging consecutive segments of the same speaker with a single space.
5. VERIFY (script): see section 11.

Prefer Python scripts for everything mechanical (cleaning, splitting, merging, assembling, checking). Use your own reading only for judgment tasks: classification, speaker labeling, topic assignment. You may use subagents to parallelize labeling in batches, with an identical output format; you do the integration and verification yourself.

---

## 5. WORKING FILES AND AUTONOMY

- Work entirely autonomously. Do NOT ask the user any question and do not wait for approval between stages. Where uncertain, choose the option that changes the text least, record the doubt in the report, and continue.
- Keep all working files in `output_final/work/`.
- Keep `output_final/PROGRESS.md`: after each stage (and every batch of files within a stage) write what is done and what remains. If the session is interrupted or restarted, or the user writes "continua", read `PROGRESS.md` first and RESUME from there without redoing finished work.
- Commit and push `output_final/` to the session's working branch regularly (after every stage and every batch of files at least) so nothing is lost. Do not open a pull request unless asked.
- Never modify `INSTRUCTIONS.md` or the input folders (`The Muslim Lantern/` and `Farid Responds/`).

---

## 6. CLASSIFICATION OF EACH FILE (FIRST JUDGMENT STEP)

Assign each file exactly one type:
- SOLO: only the channel host speaks. All text is the host's.
- CONVERSATION: the host talks with one or more other people (guest, caller, debater). Their speech must be separated.
- REACTION: the host plays clips of other people and comments/responds. Clip speech must be separated from the host's commentary.
- ARTICLE: a written article (section 7).
- MIXED: a combination (e.g. a reaction with a live guest). Treat each part according to its nature.

Hints, not rules (always read the actual content). The Muslim Lantern files are mostly CONVERSATIONS with some SOLO; Farid Responds files are mostly REACTIONS with some SOLO and the few ARTICLES.
- CONVERSATION signs: greetings and introductions, "go ahead", addressing someone by name or as "sister/brother", questions answered by a different person, short acknowledgments ("Yeah", "Uhm", "Right?"), "I'll remove you now", thanks and goodbyes.
- REACTION signs: the host quotes, challenges or answers statements clearly from another person; abrupt changes of voice or register; phrases like "he says", "she is saying", "let me play this", "pause", "this guy"; claims the host rebuts one by one.
- SOLO signs: one continuous voice; no questions answered by someone else; no greeting to a guest.
- ARTICLE signs: no timestamps; written prose with paragraph/heading structure.

Save `output_final/work/classification.csv` with: folder, file name, title, assigned type, confidence (high/medium/low), and a one-line evidence note. Commit it right after creating it.

---

## 7. ARTICLES BY FARID RESPONDS

Some files in `Farid Responds/` are articles. The whole text is by `Farid Responds`. No speaker separation. Keep the text word for word, including its own punctuation, capitalization, headings and paragraph structure. Quotations inside an article stay inside the article text and are not separate speakers. Source label: *Source: Farid Responds, article "[title]"*. Articles are integrated by topic like everything else.

---

## 8. SPEAKER SEPARATION

Labels used in the book:
- The Muslim Lantern's words -> `The Muslim Lantern:`
- Farid Responds' words (video or article) -> `Farid Responds:`
- A guest/caller/other participant -> `Guest:` (or the person's name if clearly given in that transcript, e.g. "Rachel"; one consistent label per person within a video)
- A speaker in a played clip -> `Clip:`

Attributing turns correctly (CONVERSATION, REACTION, MIXED):
- The raw dashes ("–") often mark a speaker change but NOT reliably; changes also happen mid-line with no marker. Use dashes as hints, then dialogue logic.
- Read the content: questions and their answers, who explains and who asks, who is addressed by name, who says "go ahead", who introduces themselves, who says "sister/brother".
- Short responses ("Yeah", "OK", "Uhm", "Right?") usually belong to the listener, not the explainer. Check the flow.
- Never merge consecutive turns of different speakers into one block. Every speaker change starts a new turn, even a single word.
- Every segment gets exactly one speaker label. Never drop segments.
- Attribution doubts go ONLY in the report, never inside the text. Mark them in the label file with a `doubt` flag and a one-line reason.

Reaction videos and clips:
- A clip speaker's words are NOT the host's and must never be attributed to the host.
- The book is primarily about what the host said. Include clip speech ONLY where needed for the host's response to be understandable, as short as context allows, verbatim, labeled `Clip:`.
- If clip speech and host speech cannot be told apart with confidence, use dialogue logic (the host typically responds to, challenges or quotes the clip) and flag the doubt.

Solo videos: everything is the host's.

Save one file per source: `output_final/work/labels/<file_id>.json` (segment ID -> speaker, with doubt flags).

---

## 9. BUILDING THE BOOK

### 9.1 Topic organization
- The book is divided into TOPICS (parts, chapters, subchapters), NOT into videos and NOT into channels.
- Derive topics from the actual content. Do not invent topics that are not discussed.
- Order topics BY IMPORTANCE, most fundamental first. Reasonable logic: foundational beliefs and the evidences for them first; then comparative and doctrinal discussions; then practical, legal, ethical and social questions; then specific or peripheral subjects. Adapt to the real corpus. The most central topics come first.
- Headings are neutral structural labels only, never commentary.

Method:
a) Per file, tag ranges of segment IDs with free-form topic keywords (use the YouTube chapter labels as hints).
b) Consolidate all keywords into one taxonomy (parts, chapters, subchapters) ordered by importance. Save `output_final/work/taxonomy.json`.
c) Assign every passage to a taxonomy node with an order position. Save `output_final/work/mapping.json`: for each node, an ordered list of excerpts, each = (source file, first segment ID, last segment ID). Excerpts always start and end at segment (sentence) boundaries.

### 9.2 Completeness
- Take EVERYTHING each host said or wrote about each topic, from ALL files. Do not select highlights; do not drop passages because they are repetitive.
- If the same point appears in several sources, keep all occurrences, placed next to each other under the same subtopic, each with its own source label.
- Every host segment (The Muslim Lantern, Farid Responds, article text) must appear in the book EXACTLY ONCE. Nothing is silently dropped and nothing is accidentally duplicated.
- A passage touching several topics goes where it fits best. A continuous passage with two clearly separate topics may be split ONLY at a segment (sentence) boundary; both halves stay verbatim and complete.

### 9.3 Logical flow inside a topic
- Arrange excerpts so the chapter reads as a coherent whole: general introductions and definitions first, then arguments in natural progression, then objections and responses, then conclusions. Group excerpts that develop the same argument.
- Each excerpt is a continuous verbatim passage with its own source label.
- You may create order, grouping, headings and spacing ONLY. You may NOT write bridging sentences or transitions. Structure creates the logic; the speakers' words are never touched.

### 9.4 Dialogues and clips
- When the host's words answer a guest's question or only make sense with it, keep that short exchange in dialogue form, guest words verbatim labeled `Guest:`, limited to what is needed. Guest and clip text is visually distinct (italic or indented) from the two hosts.
- Never attribute guest or clip words to a host.

### 9.5 Source labels
Under each excerpt (or group), state the source exactly as in the input: *Source: The Muslim Lantern, "[video title]"* / *Source: Farid Responds, "[video title]"* / *Source: Farid Responds, article "[title]"*. Use the same formats everywhere.

### 9.6 Reference texts
Where an excerpt cites a Quran, Hadith or classical-book reference that qualifies under section 3.1, add the reference text box directly after that excerpt, exactly as section 3.1 prescribes.

---

## 10. PDF DESIGN (READING AND STUDY)

Produce ONE professional PDF (if technically impossible for size, split by Part and say so):
- Cover page and title page (suggested neutral title: "The Muslim Lantern and Farid Responds: A Topical Compilation"; you may propose a better neutral one).
- Full table of contents with page numbers (parts, chapters, subchapters), ideally clickable.
- Clear typographic hierarchy; comfortable font size, generous line spacing and margins, short paragraphs, no walls of text.
- Speaker labels in bold; guest/clip speech visually distinct; source lines smaller and lighter; reference text boxes clearly different from all speech (for example a light shaded box with a small caption).
- Running headers/footers with chapter title and page number.
- Arabic script must render correctly (right-to-left, joined letters). Use a font that supports Arabic; if none is installed, install one via package registries (for example an npm package bundling a Noto Naskh/Noto Sans Arabic font). Verify there are no empty boxes.
- Each chapter starts on a new page.
- At the end: an index of all sources used (titles only, exactly as in the input).
- NO summaries, key takeaways, study questions or any content that is not the speakers' words (apart from the reference text boxes of section 3.1). Study features are limited to structure, navigation and layout.

---

## 11. VERIFICATION (MANDATORY, BY SCRIPT)

- Check A (fidelity): every excerpt in the book, extracted back from the generated book source, matches the segment files character for character (apart from whitespace).
- Check B (coverage): every host segment appears in the book exactly once; list any missing or duplicated segment and fix.
- Check C (attribution): no text appears under a speaker label different from the one in `output_final/work/labels/`.
- Check D (join integrity): for every file, segments joined in order reproduce the normalized text exactly.
- Check E (visual): render sample pages of the PDF to images and look at them: table of contents correct, Arabic correct, no layout problems, no empty pages.
- Check F (references): every reference text in the book is byte-identical to its file in `output_final/work/references/`; every one corresponds to an explicit Quran, Hadith or classical-book reference found in a host's segments; none is attributed to a speaker; none was added without an explicit reference in the transcript; no Bible or other reference was added. List all skipped or unretrievable references.
Fix every problem found and re-run the checks until they all pass. Save the results in `output_final/checks.md`.

---

## 12. DELIVERABLES AND REPORT

Deliver in `output_final/`: the final PDF, `work/` (segments, labels, classification, taxonomy, mapping, references), `checks.md`, `PROGRESS.md`. If the environment lets you send files to the user, send the PDF as well. Commit and push everything.

At the end, report in chat (NOT in the book): number of files per folder and per type (SOLO / CONVERSATION / REACTION / ARTICLE / MIXED); any non-.txt files ignored; the low-confidence classifications; the attribution doubts (title + passage); the number of reference texts added (split by Quran / Hadith / classical books), the references that could not be retrieved, and the references skipped because they were too vague; confirmation that checks A to F passed.

---

## 13. PRIORITY RULES

1. Fidelity to the exact words comes first, above readability, elegance or length.
2. No external sources except the narrow reference-text exception of section 3.1; never verify or correct content.
3. Never paraphrase; never add your own words to the speakers' text.
4. Completeness: nothing the two hosts said or wrote is left out.
5. Then readability: structure, topic order, layout.
When unsure, choose the option that changes the text least and record the doubt in the report.
