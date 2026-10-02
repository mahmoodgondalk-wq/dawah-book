#!/usr/bin/env python3
"""Stage 1+2: NORMALIZE and SEGMENT every .txt file of the two input folders.

Allowed technical changes only (INSTRUCTIONS section 2):
  - remove timestamps "[mm:ss]" / "[h:mm:ss]" at the start of caption lines;
  - remove auto-caption sound annotations ([Music], [laughter], [snorts], ...);
  - remove the caption turn-change marker ">>" (its position is kept as metadata);
  - join caption lines and collapse whitespace.
Everything else is kept verbatim (including dashes, which are only dropped at
assembly time when they are converted into a speaker label).

Output: work/segments/<file_id>.json, work/files.csv, work/view/<file_id>.txt
"""
import csv
import glob
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
WORK = os.path.join(ROOT, "output_final", "work")
FOLDERS = [
    ("The Muslim Lantern/transcripts", "The Muslim Lantern", "ML"),
    ("Farid Responds", "Farid Responds", "FR"),
]

TS_RE = re.compile(r"^\[\d{1,2}:\d{2}(?::\d{2})?\]\s?")
SOUND_WORDS = r"(?:music|música|applause|laughter|snorts|clears throat|cough|heavy sigh|screaming)"
SOUND_RE = re.compile(r"\[" + SOUND_WORDS + r"(?:\s+and\s+" + SOUND_WORDS + r")*\]", re.IGNORECASE)
SENT_END_RE = re.compile(r"[.!?…][\"'”’)\]]*$")
ABBREV = {"mr.", "mrs.", "ms.", "dr.", "st.", "vs.", "e.g.", "i.e.", "etc.", "no.", "prof.", "sr.", "jr.", "v.", "vol.", "p.", "pp.", "ch.", "cf."}
LONG_SENTENCE_WORDS = 40
MIN_CHUNK_WORDS = 12


def ws(s):
    return re.sub(r"\s+", " ", s).strip()


def parse_file(path):
    raw = open(path, encoding="utf-8").read()
    lines = raw.split("\n")
    title = None
    url = None
    body_lines = []
    for i, line in enumerate(lines):
        if i == 0 and line.startswith("# "):
            title = line[2:].strip()
            continue
        if i == 1 and line.startswith("# http"):
            url = line[2:].strip()
            continue
        if not line.strip():
            continue
        body_lines.append(line)
    if not title:
        title = os.path.splitext(os.path.basename(path))[0]
    return title, url, body_lines


def caption_texts(body_lines):
    """Return list of (text, marker_offsets, trailing_marker) per caption line.
    marker_offsets = offsets in the cleaned line where text follows a removed '>>';
    trailing_marker = a '>>' with no text after it on that line (applies to the next line)."""
    out = []
    for line in body_lines:
        t = TS_RE.sub("", line)
        t = SOUND_RE.sub(" ", t)
        parts = t.split(">>")
        text = ""
        offs = []
        pending = False
        for k, p in enumerate(parts):
            if k > 0:
                pending = True
            p = ws(p)
            if not p:
                continue
            start = len(text) + (1 if text else 0)
            text = (text + " " + p) if text else p
            if pending:
                offs.append(start)
                pending = False
        out.append((text, offs, pending))
    return out


def file_mode(lines_text):
    words = sum(len(t.split()) for t in lines_text)
    body = " ".join(lines_text)
    punct = len(re.findall(r"[.?!]", body)) / max(words, 1) * 100
    nonempty = [t for t in lines_text if t]
    up = sum(1 for t in nonempty if t[:1].isupper() or t[:1] in "-–\"(") / max(len(nonempty), 1)
    return ("line" if (punct < 2 or up > 0.6) else "sentence"), round(punct, 2), round(up, 2)


def build(path, channel, file_id, folder_rel):
    title, url, body_lines = parse_file(path)
    caps = caption_texts(body_lines)
    mode, punct, up = file_mode([c[0] for c in caps])

    # Build normalized text and boundary sets
    text = ""
    line_starts = set()
    marker_pos = set()
    carry = False
    for ctext, offs, trailing in caps:
        if not ctext:
            carry = carry or trailing
            continue
        start = len(text) + (1 if text else 0)
        text = (text + " " + ctext) if text else ctext
        line_starts.add(start)
        if carry:
            marker_pos.add(start)
        for o in offs:
            marker_pos.add(start + o)
        carry = trailing
    assert text == ws(text)

    # candidate cut positions (index of first char of a new segment; must follow a space)
    cuts = set()
    cuts |= {p for p in marker_pos if 0 < p < len(text)}
    # dash markers: "– " / "- " at line start, or " – " / " - " mid line
    for m in re.finditer(r"(?<= )[–-](?= )", text):
        cuts.add(m.start())
    # sentence ends
    for m in re.finditer(r"\S+", text):
        tok = m.group(0)
        end = m.end()
        if end < len(text) and SENT_END_RE.search(tok) and tok.lower() not in ABBREV:
            cuts.add(end + 1)
    if mode == "line":
        cuts |= {p for p in line_starts if p > 0}
    cuts = sorted(c for c in cuts if 0 < c < len(text) and text[c - 1] == " ")

    def split_at(cut_list):
        segs = []
        prev = 0
        for c in cut_list:
            segs.append((prev, c - 1))
            prev = c
        segs.append((prev, len(text)))
        return segs

    spans = split_at(cuts)
    if mode == "sentence":
        # split long sentences at caption line boundaries
        new_cuts = set(cuts)
        for a, b in spans:
            seg = text[a:b]
            if len(seg.split()) > LONG_SENTENCE_WORDS:
                inner = sorted(p for p in line_starts if a < p < b)
                last = a
                for p in inner:
                    if len(text[last:p].split()) >= MIN_CHUNK_WORDS and len(text[p:b].split()) >= MIN_CHUNK_WORDS:
                        new_cuts.add(p)
                        last = p
        cuts = sorted(new_cuts)
        spans = split_at(cuts)

    segments = []
    for n, (a, b) in enumerate(spans, 1):
        seg_text = text[a:b]
        assert seg_text and seg_text == seg_text.strip(), (file_id, n, seg_text)
        marker = None
        if a in marker_pos:
            marker = ">>"
        elif re.match(r"[–-] ", seg_text):
            marker = "dash"
        segments.append({
            "id": f"{file_id}-{n:04d}",
            "text": seg_text,
            "marker": marker,
        })
    joined = " ".join(s["text"] for s in segments)
    assert joined == text, file_id
    return {
        "file_id": file_id,
        "channel": channel,
        "folder": folder_rel,
        "file_name": os.path.basename(path),
        "title": title,
        "url": url,
        "chapters": [],
        "mode": mode,
        "punct_per_100_words": punct,
        "upper_line_start_ratio": up,
        "n_words": len(text.split()),
        "normalized_text": text,
        "segments": segments,
    }


def dump_doc(doc):
    """Compact JSON, one segment per line."""
    head = {k: v for k, v in doc.items() if k != "segments"}
    s = json.dumps(head, ensure_ascii=False, separators=(",", ":"))[:-1]
    lines = [json.dumps(seg, ensure_ascii=False, separators=(",", ":")) for seg in doc["segments"]]
    return s + ',"segments":[\n' + ",\n".join(lines) + "\n]}\n"


def write_view(doc, path):
    """Reading view for labelers: line k == segment k (no header). '» ' marks a raw '>>' before the segment."""
    with open(path, "w", encoding="utf-8") as f:
        for s in doc["segments"]:
            mark = "» " if s["marker"] == ">>" else ""
            f.write(f"{mark}{s['text']}\n")


def main():
    files = []
    ignored = []
    for folder_rel, channel, prefix in FOLDERS:
        base = os.path.join(ROOT, folder_rel)
        for dirpath, dirnames, filenames in os.walk(base):
            for fn in sorted(filenames):
                p = os.path.join(dirpath, fn)
                if fn.lower().endswith(".txt"):
                    files.append((p, channel, prefix))
                else:
                    ignored.append(os.path.relpath(p, ROOT))
    seen = {}
    rows = []
    for p, channel, prefix in sorted(files):
        fn = os.path.basename(p)
        m = re.match(r"^(\d{3}) - ", fn)
        num = m.group(1) if m else "000"
        fid = prefix + num
        if fid in seen:
            raise SystemExit(f"duplicate id {fid}: {p} / {seen[fid]}")
        seen[fid] = p
        folder_rel = os.path.relpath(os.path.dirname(p), ROOT)
        doc = build(p, channel, fid, folder_rel)
        with open(os.path.join(WORK, "segments", fid + ".json"), "w", encoding="utf-8") as f:
            f.write(dump_doc(doc))
        write_view(doc, os.path.join(WORK, "view", fid + ".txt"))
        rows.append([fid, doc["channel"], doc["folder"], doc["file_name"], doc["title"], doc["url"] or "",
                     doc["mode"], len(doc["segments"]), doc["n_words"]])
    rows.sort(key=lambda r: r[0])
    with open(os.path.join(WORK, "files.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["file_id", "channel", "folder", "file_name", "title", "url", "seg_mode", "n_segments", "n_words"])
        w.writerows(rows)
    with open(os.path.join(WORK, "ignored_files.txt"), "w", encoding="utf-8") as f:
        for p in sorted(ignored):
            f.write(p + "\n")
    print(f"files: {len(rows)}  ignored non-txt: {len(ignored)}")
    print("segments:", sum(r[7] for r in rows), "words:", sum(r[8] for r in rows))


if __name__ == "__main__":
    main()
