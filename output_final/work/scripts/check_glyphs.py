#!/usr/bin/env python3
"""Check E helper: every character used in the book source must be covered by one of the fonts in the
fallback list (otherwise it would print as an empty box). Prints uncovered characters, exits 1 if any."""
import glob
import os
import sys
import unicodedata

from fontTools.ttLib import TTCollection, TTFont

sys.path.insert(0, os.path.dirname(__file__))
from verify import parse_tstrings, BOOK, ROOT  # noqa: E402

FONT_DIR = os.path.join(ROOT, "output_final", "book", "fonts")  # shared by the compilation and the edited book

FONTS = [
    os.path.join(FONT_DIR, "SourceSerif4_400Regular.ttf"),
    os.path.join(FONT_DIR, "Amiri_400Regular.ttf"),
    os.path.join(FONT_DIR, "NotoNaskhArabic_400Regular.ttf"),
    os.path.join(FONT_DIR, "NotoSerifHebrew_400Regular.ttf"),
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
]
IGNORABLE = {0x200B, 0x200C, 0x200D, 0x200E, 0x200F, 0x2060, 0xFEFF, 0xFE0F, 0xFE0E, 0x202A, 0x202B, 0x202C,
             0x202D, 0x202E, 0x2066, 0x2067, 0x2068, 0x2069, 0x061C}


def cmaps():
    out = []
    for p in FONTS:
        if p.endswith(".ttc"):
            for f in TTCollection(p).fonts:
                out.append(set(f.getBestCmap().keys()))
        else:
            out.append(set(TTFont(p).getBestCmap().keys()))
    return out


def main():
    chars = {}
    files = glob.glob(os.path.join(BOOK, "content", "*.typ")) + [os.path.join(BOOK, "sources.typ")]
    for p in files:
        for line in open(p, encoding="utf-8"):
            if line.startswith("#") or line.startswith("="):
                for s in (parse_tstrings(line) if line.startswith("#") else [line]):
                    for ch in s:
                        chars[ch] = chars.get(ch, 0) + 1
    cms = cmaps()
    bad = []
    for ch, n in sorted(chars.items()):
        o = ord(ch)
        if o < 32 or o in IGNORABLE or unicodedata.category(ch) in ("Mn", "Cf") and any(o in c for c in cms):
            continue
        if not any(o in c for c in cms):
            if unicodedata.category(ch) == "Mn":
                bad.append((ch, o, n, unicodedata.name(ch, "?") + " (combining)"))
            else:
                bad.append((ch, o, n, unicodedata.name(ch, "?")))
    print(f"distinct characters: {len(chars)}; uncovered: {len(bad)}")
    for ch, o, n, name in bad:
        print(f"  U+{o:04X} x{n} {name}")
    import json
    name = "glyph_check.json" if os.path.basename(BOOK.rstrip("/")) == "book" else f"glyph_check_{os.path.basename(BOOK.rstrip('/'))}.json"
    with open(os.path.join(ROOT, "output_final", "work", name), "w", encoding="utf-8") as f:
        json.dump({"distinct_characters": len(chars), "uncovered": [f"U+{o:04X} {name} (x{n})" for ch, o, n, name in bad]}, f, indent=1)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
