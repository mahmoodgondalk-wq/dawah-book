# EDITING GUIDE (Stage 8: from spoken words to a readable book)

You turn the spoken words of two YouTube hosts (The Muslim Lantern, Farid Responds) into clean written prose
for a book that presents their arguments by topic. The book must contain THEIR words, not yours:
**the only operation allowed is deletion.** You remove what is superfluous; you never add, replace or reorder.

## Input
`output_final/work/edit/in/<BATCH>.txt`. It is a sequence of sub-chapters and passages:
```
## SUB-CHAPTER <id> — <number and title>   (part/chapter titles follow)
### <PASSAGE_ID> | <host> | "<video title>"
<the host's words, exactly as transcribed from the video>
```
Inside a passage the marker `⟦…⟧` shows where another person spoke (a caller, a guest, a clip); their words are
not given and must not appear in the book. Passages of one sub-chapter are already in reading order.

## What to do with each passage
Produce the same passage as written prose, keeping the host's words in their original order and deleting:
- fillers and tics: um, uh, you know, like (as a filler), I mean, look, OK so, right?, basically, literally, kind of, sort of, obviously (when empty);
- repetitions, stutters, false starts and self-corrections (keep only the final, corrected wording);
- words addressed to the interlocutor or the audience: "brother", "my friend", "sir", "listen", "let me ask you", "do you agree?", "can you hear me?", "let me share my screen", "guys", "as you can see";
- stream and video logistics, greetings, thanks, jokes with the caller, references to the chat, to the camera, to "this video" or "the previous video" when they carry no argument;
- questions that only prompt the other speaker, and fragments that only make sense as a reply to the deleted words of the other person;
- half-sentences that cannot be completed by deletion alone (delete the whole fragment rather than add a word).
Keep EVERYTHING that is an argument, an explanation, an example, a story, a definition, a verse or hadith quoted, a name, a number, a date, an Arabic word or phrase, a qualification or a nuance. The book must be complete: every point the host makes stays, in his own words.

You may freely: change punctuation and capitalization, split or join sentences, create paragraphs (a blank line between paragraphs; aim for 60-150 words per paragraph), and drop a dash at the start of a line.

You may NOT: add any word (not even "the", "and", "is", "that"), change a word (no tense, number, spelling or synonym changes; keep caption spellings such as "Muhammedﷺ", "Mathew12:25-26", "Quran4:124"), reorder words or sentences, merge sentences from different passages, summarize, paraphrase, write transitions, headings, notes or comments, translate or transliterate Arabic.
The checker verifies that the words of your output, in order, are a sub-sequence of the words of the input (case and punctuation ignored). Any added or changed word is an error.

One exception, for obvious transcription errors only: when the captions garbled a word (for example "f" or "fitra" for *fitrah*, "Quan" for Quran, "koran", a mangled name or Arabic term), you may replace it with the correct word **in square brackets**: "the [fitrah] is there". The brackets show the reader that the word is an editorial correction. Use this only where the garbled word would make the sentence unreadable; at most 4 words per bracket and at most 2% of the words of a passage (always at least 3 words allowed). Never use brackets to add content, explanations or missing words.

If a whole passage is superfluous (only greetings, logistics, banter, or an answer that is meaningless without the other person's words), omit it: write `[omitted: <short reason>]` instead of text. Do this sparingly; a passage with any argument in it must be kept (edited).

## Output: `output_final/work/edit/out/<BATCH>.txt`
```
### <PASSAGE_ID>
<edited prose, paragraphs separated by a blank line>

### <PASSAGE_ID>
[omitted: greetings and stream logistics only]
```
One block per passage of the input, same ids, same order; nothing else in the file (no sub-chapter lines, no markers, no comments).
Then run `cd /home/user/dawah-book && python3 output_final/work/scripts/check_edit.py <BATCH>` and fix every ERROR until it prints OK.
Review the warnings: "low retention" means you may have deleted substance; "no change" means the passage was not edited.
Do not modify any other file. Do not run git.
