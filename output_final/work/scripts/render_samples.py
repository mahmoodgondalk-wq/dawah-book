#!/usr/bin/env python3
"""Check E helper: render selected PDF pages to PNG contact sheets for visual inspection.
Usage: render_samples.py <pdf> <outdir> <page,page,...> [dpi]"""
import os
import subprocess
import sys

from PIL import Image


def main():
    pdf, outdir, pages = sys.argv[1], sys.argv[2], [int(x) for x in sys.argv[3].split(",")]
    dpi = int(sys.argv[4]) if len(sys.argv) > 4 else 60
    os.makedirs(outdir, exist_ok=True)
    ims = []
    for p in pages:
        base = os.path.join(outdir, f"p{p:05d}")
        subprocess.run(["pdftoppm", "-r", str(dpi), "-f", str(p), "-l", str(p), "-png", "-singlefile", pdf, base], check=True)
        ims.append(Image.open(base + ".png"))
    w, h = ims[0].size
    cols = 4
    for s in range(0, len(ims), 8):
        chunk = ims[s:s + 8]
        rows = (len(chunk) + cols - 1) // cols
        sheet = Image.new("RGB", (w * cols, h * rows), "white")
        for i, im in enumerate(chunk):
            sheet.paste(im, ((i % cols) * w, (i // cols) * h))
        name = os.path.join(outdir, f"sheet_{pages[s]:05d}.png")
        sheet.save(name)
        print(name)


if __name__ == "__main__":
    main()
