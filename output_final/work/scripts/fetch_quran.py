#!/usr/bin/env python3
"""Fetch Quran verses (Saheeh International, translation id 20) from quran.com pages.

Usage: python3 fetch_quran.py 4:124 50:38-39 ...
Saves output_final/work/references/quran_SSS_VVV[-WWW].json

The text is taken from the page's embedded JSON (__NEXT_DATA__) exactly as served.
The only processing: footnote-marker tags <sup foot_note=...>n</sup> (links to quran.com
footnotes, not part of the translation sentence) are removed in "text"; the untouched
string is kept in "raw".
"""
import datetime
import json
import os
import re
import subprocess
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
REFDIR = os.path.join(ROOT, "output_final", "work", "references")
SUP_RE = re.compile(r"<sup foot_note=[^>]*>\d+</sup>")


def get(url):
    for attempt in range(4):
        r = subprocess.run(["curl", "-sS", "-L", "-m", "60", "-A", "Mozilla/5.0", url], capture_output=True)
        if r.returncode == 0 and b"__NEXT_DATA__" in r.stdout:
            return r.stdout.decode("utf-8")
        time.sleep(2 ** (attempt + 1))
    raise RuntimeError(f"cannot fetch {url}")


def verses_from_page(html):
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.S)
    d = json.loads(m.group(1))
    found = {}

    def walk(o):
        if isinstance(o, dict):
            if "verseKey" in o and "translations" in o and isinstance(o["translations"], list):
                for t in o["translations"]:
                    if t.get("resourceId") == 20 or t.get("resource_id") == 20:
                        found[o["verseKey"]] = (t.get("text"), t.get("resourceName"))
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(d)
    return found


def fetch(ref):
    s, vv = ref.split(":")
    s = int(s)
    if "-" in vv:
        a, b = (int(x) for x in vv.split("-"))
    else:
        a = b = int(vv)
    fname = f"quran_{s:03d}_{a:03d}" + (f"-{b:03d}" if b != a else "") + ".json"
    path = os.path.join(REFDIR, fname)
    if os.path.exists(path):
        return path, "exists"
    url = f"https://quran.com/{s}/{a}" + (f"-{b}" if b != a else "") + "?translations=20"
    html = get(url)
    found = verses_from_page(html)
    verses = []
    urls = [url]
    for v in range(a, b + 1):
        key = f"{s}:{v}"
        if key not in found:
            vurl = f"https://quran.com/{s}/{v}?translations=20"
            more = verses_from_page(get(vurl))
            urls.append(vurl)
            found.update(more)
        if key not in found:
            raise RuntimeError(f"verse {key} not found on quran.com")
        raw, rname = found[key]
        verses.append({"key": key, "raw": raw, "text": SUP_RE.sub("", raw), "resource_name": rname})
    if any("<" in v["text"] for v in verses):
        raise RuntimeError(f"unexpected markup left in {ref}: {[v['text'] for v in verses]}")
    label_ref = f"{s}:{a}" + (f"-{b}" if b != a else "")
    doc = {
        "kind": "quran",
        "ref": label_ref,
        "label": f"Reference text: Quran {label_ref}, quran.com (Saheeh International)",
        "source": "quran.com, Saheeh International (translation id 20)",
        "url": url,
        "urls_fetched": urls,
        "retrieved_utc": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "processing": "footnote-marker tags <sup foot_note=...>n</sup> removed from 'text'; 'raw' is the string as served",
        "verses": verses,
    }
    os.makedirs(REFDIR, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    return path, "fetched"


def main():
    for ref in sys.argv[1:]:
        try:
            p, st = fetch(ref)
            print(ref, st, os.path.basename(p))
        except Exception as e:
            print(ref, "FAILED", e)
        time.sleep(0.5)


if __name__ == "__main__":
    main()
