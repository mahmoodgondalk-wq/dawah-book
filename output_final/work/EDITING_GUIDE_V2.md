# EDITING GUIDE v2 (Stage 8: from spoken words to a readable book, without repetitions)

You turn the spoken words of two YouTube hosts (The Muslim Lantern, Farid Responds) into clean written prose
for a book that presents their arguments by topic, **once each, without repetitions**. The book must contain THEIR
words, not yours: **the only operation allowed is deletion.** You remove what is superfluous; you never add,
replace or reorder words.

## Input
`output_final/work/edit/in/<BATCH>.txt`. It is a sequence of sub-chapters and passages:
```
## SUB-CHAPTER <id> — <title>   (chapter: ...; part: ...)
### <PASSAGE_ID> | <host> | "<video title>"
<the host's words, exactly as transcribed from the video>
```
Inside a passage the marker `⟦…⟧` shows where another person spoke (a caller, a guest, a clip); their words are
not given and must not appear in the book. The passages of a sub-chapter are already in reading order, and in the
book they will be printed one after another as one continuous section (each with a footnote naming its video).

## Step 1 — clean every passage (deletion only)
Delete:
- fillers and tics: um, uh, you know, like (as a filler), I mean, look, OK so, right?, basically, literally, kind of, sort of, obviously (when empty);
- repetitions, stutters, false starts and self-corrections (keep only the final, corrected wording);
- words addressed to the interlocutor or the audience: "brother", "my friend", "sir", "listen", "let me ask you", "do you agree?", "can you hear me?", "let me share my screen", "guys", "as you can see";
- stream and video logistics, greetings, thanks, jokes with the caller, references to the chat, to the camera, to "this video";
- questions that only prompt the other speaker, and fragments that only make sense as a reply to the deleted words of the other person;
- half-sentences that cannot be completed by deletion alone (delete the whole fragment rather than add a word).

## Step 2 — remove repetitions across the passages of a sub-chapter (deletion only)
The same argument, story, example, study, verse or explanation is often told in many videos. In the book each point
must be told ONCE, in its fullest and clearest telling:
- Before editing a sub-chapter, read all its passages and note its points. For each point choose the passage where it
  is told most completely and clearly, and keep it there.
- In the other passages delete the sentences that only repeat that point (the same argument in other words, the same
  story told again, the same study or verse quoted again). Keep only what is NEW in them: an additional detail,
  example, objection and answer, nuance or source that has not been given yet.
- A passage that, after this, contains nothing new is left out: write `[omitted: repeats points made above]`
  (or `... made below` when its point is kept in a later passage).
- What remains of a passage must read well on its own: whole sentences, no dangling "this"/"he" without a referent
  (if needed keep the sentence that introduces the referent), no fragments.
Expect a large reduction: in many sub-chapters only a third of the words, or less, will remain, because the same
points come back again and again. But never delete a point, a detail or a nuance that is said only once — the book
must be complete in its arguments, it must only not repeat them. Repetition across different sub-chapters is not your
concern; work within each sub-chapter.

## What you may and may not do
You may freely: change punctuation and capitalization, split or join sentences, create paragraphs (a blank line
between paragraphs; aim for 60-150 words per paragraph), and drop a dash at the start of a line.

You may NOT: add any word (not even "the", "and", "is", "that"), change a word (no tense, number, spelling or synonym
changes; keep caption spellings such as "Muhammedﷺ", "Mathew12:25-26", "Quran4:124"), reorder words or sentences,
move text from one passage to another, summarize, paraphrase, write transitions, headings, notes or comments, translate
or transliterate Arabic. The checker verifies that the words of your output, in order, are a sub-sequence of the words
of the input passage (case and punctuation ignored). Any added or changed word is an error.

One exception, for obvious transcription errors only: when the captions garbled a word (for example "f" or "fitra" for
*fitrah*, "Quan" for Quran, a mangled name or Arabic term), you may replace it with the correct word **in square
brackets**: "the [fitrah] is there". Use this only where the garbled word would make the sentence unreadable; at most
4 words per bracket and at most 2% of the words of a passage (always at least 3 words allowed). Never use brackets to
add content, explanations or missing words.

A passage that is only greetings, logistics, banter, or an answer that is meaningless without the other person's words
is also left out: `[omitted: <short reason>]`.

## Output: `output_final/work/edit/out/<BATCH>.txt`
```
### <PASSAGE_ID>
<edited prose, paragraphs separated by a blank line>

### <PASSAGE_ID>
[omitted: repeats points made above]
```
One block per passage of the input, same ids, same order; nothing else in the file (no sub-chapter lines, no markers,
no comments). Then run `cd /home/user/dawah-book && python3 output_final/work/scripts/check_edit.py <BATCH>` and fix
every ERROR until it prints OK. Do not modify any other file. Do not run git.
