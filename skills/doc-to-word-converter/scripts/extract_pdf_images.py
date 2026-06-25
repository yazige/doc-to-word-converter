#!/usr/bin/env python3
"""Extract embedded page images from a scanned PDF."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def safe_suffix(name: str | None) -> str:
    if not name:
        return ".bin"
    suffix = Path(name).suffix.lower()
    if re.fullmatch(r"\.[a-z0-9]{2,5}", suffix or ""):
        return suffix
    return ".bin"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path, help="PDF file to inspect")
    parser.add_argument("output_dir", type=Path, help="Directory for extracted images")
    args = parser.parse_args()

    try:
        from pypdf import PdfReader
    except ImportError:
        print("Missing dependency: pypdf. Install pypdf or use an environment that provides it.", file=sys.stderr)
        return 2

    if not args.pdf.exists():
        print(f"PDF not found: {args.pdf}", file=sys.stderr)
        return 2

    args.output_dir.mkdir(parents=True, exist_ok=True)
    reader = PdfReader(str(args.pdf))
    written = 0

    for page_number, page in enumerate(reader.pages, start=1):
        try:
            images = list(page.images)
        except Exception as exc:
            print(f"page {page_number}: could not read images: {exc}", file=sys.stderr)
            continue

        for image_number, image in enumerate(images, start=1):
            name = getattr(image, "name", None)
            suffix = safe_suffix(name)
            out_path = args.output_dir / f"page-{page_number:02d}-image-{image_number:02d}{suffix}"
            out_path.write_bytes(image.data)
            written += 1
            print(out_path)

    print(f"extracted_images={written}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
