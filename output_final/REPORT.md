# Final report — "The Muslim Lantern and Farid Responds: A Topical Compilation"

Deliverables in `output_final/`: the PDF (`The_Muslim_Lantern_and_Farid_Responds_A_Topical_Compilation.pdf`, 6,688 pages, 104 MB), `checks.md`, `PROGRESS.md`, `work/` (segments, labels, topics, classification, taxonomy, mapping, references, scripts), `attribution_doubts.md`, `skipped_references.md`.

## Book structure

17 parts, 95 chapters, 804 sub-chapters; 6,107 excerpts from 774 transcripts plus 8 articles; 64,354 speaker turns; 1,492 reference boxes.
Order (as instructed on 2026-10-16: first everything about Islam, then the other religions and ideologies):

I God: Existence and Knowledge of God · II Tawheed and Islamic Creed · III Finding the True Religion: The Case for Islam · IV The Prophethood of Muhammad · V The Quran · VI The Sunnah and the Hadith · VII The Prophet Muhammad: Life and Criticisms · VIII Sunni and Shia, Sects and Groups · IX Islamic Law and Ethics · X Women, Marriage, Family and Sexuality · XI Society, Politics and History · XII Dawah, Doubts and Conversion · XIII Christianity: God and Jesus · XIV The Bible · XV Judaism and Other Religions · XVI Atheism, Secularism and Other Worldviews · XVII Other Remarks (greetings, announcements, logistics).

## 1. Files per folder and per type

| Folder | SOLO | CONVERSATION | REACTION | MIXED | ARTICLE | Total |
|---|---|---|---|---|---|---|
| The Muslim Lantern/transcripts | 13 | 384 | 27 | 0 | — | 424 |
| Farid Responds/transcripts | 71 | 29 | 226 | 24 | — | 350 |
| Farid Responds (PDF files) | — | — | — | — | 8 | 8 |
| **Total** | 84 | 413 | 253 | 24 | 8 | **782** |

Full table: `work/classification.csv` (type, confidence, evidence per file).

## 2. Non-.txt files

8 non-.txt files were found, all PDFs in `Farid Responds/` (no others). They were first set aside as the instructions say, then — at your explicit request — included as ARTICLE: each one's original pages are embedded unaltered (vector, sha256-verified) under the label `Farid Responds:` with `Source: Farid Responds, article "<title>"`:
A Critical Analysis: Jay Smith's Claims About the Qur'an · A Critique of Shady Nasser's Treatment of the Hadith of Seven Ahruf · Isnad_Tree_Seven_Ahruf (one very wide page, shown in 6 landscape slices) · On the Status of Zurārah · The Distortions of al-Kulaynī · The Identity of Dhū al-Qarnayn and a Response to Alleged Alexander Parallels · The Insignificance of "Corrections" in Early Qur'ān Manuscripts · The Variants of the ʿUthmānic Maṣāḥif.
Authorship note: the first article carries the byline "Ijaz Ahmad"; the seventh is signed by Mansur Ahmed and Farid with an introduction by Ijaz Ahmad. Both are kept as published on the Farid Responds channel (attribution doubt).

## 3. Low-confidence classifications (30)

FR068 REACTION (two-line meme teaser) · FR127 CONVERSATION · FR140 MIXED · FR143 CONVERSATION (no turn markers) · FR173 CONVERSATION · FR191 CONVERSATION (teaser montage) · FR226 REACTION · FR227 MIXED (host and friend Ali comment together) · FR255 SOLO (captions are scattered nonsense words) · FR259 SOLO (four one-word fragments) · FR262 CONVERSATION · FR280 CONVERSATION (garbled recording) · FR300 REACTION (leaked audio, host does not speak) · FR316 REACTION · FR326 MIXED (guest video by Yusef) · FR355 REACTION (English mis-captioned as Dutch) · FR362 CONVERSATION · FR364 REACTION · FR371 REACTION · FR396, FR397, FR410, FR411, FR412 MIXED (2019 Apostate Prophet series co-presented with Emin/Gibran) · FR398 SOLO (captions mis-recognized as gibberish) · ML242, ML275, ML344, ML372, ML409 CONVERSATION (unpunctuated auto-captions, no turn markers).
333 further files are medium confidence (mostly auto-captioned conversations); 419 are high.

## 4. Attribution doubts

5,504 doubtful passages in 680 files, all listed with title, segment range, reason and the verbatim start of the passage in `attribution_doubts.md` (88 of them are "host recording" doubts: a recording of a host played inside another video, kept under the host's label). The main categories:
- auto-captioned videos with no punctuation and no turn markers, where the speaker changes mid-caption: each caption was given to the speaker who says most of it (e.g. ML133, ML139, ML143, ML146, ML149, ML158, ML164, ML167, ML169, ML172, ML174, ML177, ML180, ML184, ML186, ML187, ML189, ML191, ML199, ML203, ML216, ML224, ML226, ML228, ML230, ML232, ML235, ML238, ML242, ML249, ML273, ML275, ML281, ML287, ML291, ML380, ML409);
- fast dash-marked exchanges where short turns ("OK", "Yeah", "Absolutely", goodbyes) could belong to either speaker;
- several guests who could not be told apart and share one label (couples, groups of students, passers-by: e.g. ML167, ML172, ML228, ML235, ML275, ML281, ML333, ML337, ML364, ML374, ML388/389, ML394, ML403, ML412, ML422);
- names taken from a single mention or from the video title (ML137 "Jeong Lee", ML248 "Sheikh Uthman", ML240 "Sneako", ML233 interviewer unnamed, ML322 "Jake" never spoken); the same caller spelled "Hayden" (ML417) and "Ayden" (ML418), "Liam"/"Lian" (ML141), "Jushua" (ML331), "Dawn"/"Don" (ML147) kept as written;
- shahada lines where the host's prompt and the convert's repetition are captioned once (ML163, ML239, ML308, ML311, ML359);
- Farid Responds files with no host speech at all (posted recordings of other people, e.g. FR055, FR068, FR072, FR090, FR162, FR164, FR165, FR181, FR187, FR243, FR284, FR300, FR305, FR309, FR321, FR326, FR338, FR348, FR352, FR359, FR363, FR371, FR380, FR382, FR404, FR408, FR409) and the 2019 Apostate Prophet series co-narrated by Gibran/Emin;
- the sound bite "You asked me excellent, excellent question" (8 files) labeled Clip.

## 5. Reference texts

Added: **1,581 citations → 1,492 reference boxes in the book** (a box is printed after every excerpt that cites it; a reference cited twice in one excerpt is printed once):
- Quran (quran.com, Saheeh International): 1,569 citations, 771 distinct verses/ranges;
- Hadith (sunnah.com): 12 citations, 12 distinct hadiths (Sahih al-Bukhari 2685, 3219, 3336, 3448, 4110, 6114, 6464; Sahih Muslim 650, 819, 2667, 2816c; Mishkat al-Masabih 1630);
- Classical books (shamela.ws): 0.

Could not be retrieved: none (every accepted reference was fetched).

Skipped (185, full list with reasons in `skipped_references.md`):
- 102 Bible references (never added, as instructed);
- 13 conflicting locators, where the surah/verse written in the captions does not match the verse the host quotes (e.g. ML090 "(anNisa5:171)", ML204 "(anNoor 24:3)", ML216 "chapter 6:8", ML279 "(Annahl16:24)", ML286 "(Annisa4:175)", ML294 "(AlFatiha:1)", ML311 "(Quran7:162-163)", ML314 "(Quran4:150-151)", ML335 "(Quran4:60)", ML340 "(Quran3:94)", ML347 "(Quran4:155)" and "(Quran9:45)", ML403 "(arRum29:69)");
- classical-book page references whose edition or volume is not named, so the passage cannot be located on shamela.ws with certainty: FR254 Maqtal al-Husayn p. 70 and p. 77, al-Bidayah wa al-Nihayah p. 565; FR312 Fath al-Bari (5 volume/page citations); FR367 al-Tafsir al-Kabir vol. 19 p. 131; FR172 Tahdhib (garbled title); ML136 al-Irshad p. 63 and Majma al-Bayan vol. 5 p. 118; ML354 Asas al-Taqdis p. 221;
- modern or non-classical books (al-Albani's Silsilah, S. Nasser, The Sealed Nectar, Ahmadi literature, Christian books, PDF page numbers), negated citations ("That's not (2:82)"), hadith numbers without the collection named (FR091 "Hadith number 666/17"), garbled or ambiguous digit strings (ML057 "3109", ML164 "17:1 15", "867, 661, and 81", "2118"), and regex duplicates of citations already decided for the same segment.

## 6. Verification (details in `checks.md`)

| Check | Result |
|---|---|
| A Fidelity (every turn = exact source segments; dashes removed only at speaker changes; articles sha256-identical) | PASS |
| B Coverage (248,116 host segments, each exactly once; 8/8 articles) | PASS |
| C Attribution (labels and styles match the label files) | PASS |
| D Join (segments re-join to the normalized transcripts, 774/774 files) | PASS |
| E Visual (501 distinct characters all covered by the fonts; 24 sample pages inspected) | PASS |
| F References (1,492 boxes identical to the saved site texts, cited by a host segment of the excerpt above, never inside speaker text) | PASS |

## Notes

- Git: every stage and batch was committed locally on `claude/upbeat-ptolemy-ph4o7a`; every push was refused (403: this session has no GitHub access). Reconnect GitHub and push the branch. The PDF itself is git-ignored because it exceeds GitHub's 100 MB per-file limit; it is delivered directly.
- Nothing was typed by hand into the book: all speaker text is moved by code from the segment files; the only non-verbatim text in the book is the structure (titles), the source lines, the legend page and the reference boxes fetched from quran.com / sunnah.com.
