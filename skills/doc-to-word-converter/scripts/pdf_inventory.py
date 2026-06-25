#!/usr/bin/env python3
"""Inspect a PDF for page count, text layer size, and embedded images."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


def image_count(page) -> int:
    try:
        return len(page.images)
    except Exception:
        pass

    try:
        resources = page.get("/Resources") or {}
        xobjects = resources.get("/XObject") or {}
        count = 0
        for obj in xobjects.values():
            resolved = obj.get_object()
            if resolved.get("/Subtype") == "/Image":
                count += 1
        return count
    except Exception:
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path, help="PDF file to inspect")
    args = parser.parse_args()

    try:
        from pypdf import PdfReader
    except ImportError:
        print("Missing dependency: pypdf. Install pypdf or use an environment that provides it.", file=sys.stderr)
        return 2

    if not args.pdf.exists():
        print(f"PDF not found: {args.pdf}", file=sys.stderr)
        return 2

    reader = PdfReader(str(args.pdf))
    rows = []
    total_chars = 0
    total_images = 0

    for index, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        chars = len(text.strip())
        images = image_count(page)
        total_chars += chars
        total_images += images
        
        # 检测页面版式
        try:
            mediabox = page.mediabox
            w, h = float(mediabox.width), float(mediabox.height)
            orientation = "landscape" if w > h else "portrait"
        except Exception:
            w, h, orientation = 0, 0, "unknown"
        
        rows.append({
            "page": index,
            "text_chars": chars,
            "images": images,
            "width_pt": round(w, 1),
            "height_pt": round(h, 1),
            "orientation": orientation
        })

    writer = csv.DictWriter(sys.stdout, fieldnames=["page", "text_chars", "images", "width_pt", "height_pt", "orientation"])
    writer.writeheader()
    writer.writerows(rows)
    print()
    print(f"pages={len(reader.pages)}")
    print(f"total_text_chars={total_chars}")
    print(f"total_images={total_images}")
    # 汇总版式：多数页面的朝向
    orientations = [r["orientation"] for r in rows if r["orientation"] != "unknown"]
    if orientations:
        from collections import Counter
        dominant = Counter(orientations).most_common(1)[0][0]
        print(f"orientation={dominant}")
    if total_chars == 0 and total_images > 0:
        print("assessment=scanned_pdf_no_text_layer")
    elif total_chars > 0:
        print("assessment=has_text_layer")
    else:
        print("assessment=no_text_or_images_detected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
