#!/usr/bin/env python3
"""Check a DOCX for common privacy and template-quality risks."""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


PATTERNS = {
    "long_digit_sequences": re.compile(r"\b\d{8,}\b"),
    "credit_code_like": re.compile(r"\b[0-9A-Z]{15,20}\b"),
    "mainland_mobile": re.compile(r"\b1[3-9]\d{9}\b"),
    "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "company_suffix": re.compile(r"[\u4e00-\u9fff]{2,}(?:有限责任公司|股份有限公司|有限公司|合伙企业|个体工商户)"),
}


def extract_text_from_xml(data: bytes) -> str:
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return ""
    parts = []
    for node in root.findall(".//w:t", NS):
        if node.text:
            parts.append(node.text)
    return "".join(parts)


def read_all_word_text(docx: Path) -> tuple[str, list[str], bool]:
    texts = []
    media = []
    rsid_left = False
    with zipfile.ZipFile(docx, "r") as zf:
        for name in zf.namelist():
            if name.startswith("word/media/"):
                media.append(name)
            if name.startswith("word/") and name.endswith(".xml"):
                data = zf.read(name)
                if b"rsid" in data:
                    rsid_left = True
                texts.append(extract_text_from_xml(data))
    return "\n".join(texts), media, rsid_left


def load_source_terms(paths: list[Path]) -> list[str]:
    terms: list[str] = []
    for path in paths:
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            term = line.strip()
            if term and not term.startswith("#"):
                terms.append(term)
    return terms


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docx", type=Path)
    parser.add_argument("--source-terms-file", action="append", type=Path, default=[], help="UTF-8 file with one known sensitive source term per line")
    parser.add_argument("--no-fail", action="store_true", help="Print report but always exit 0")
    args = parser.parse_args()

    if not args.docx.exists():
        print(f"DOCX not found: {args.docx}", file=sys.stderr)
        return 2

    text, media, rsid_left = read_all_word_text(args.docx)
    source_terms = load_source_terms(args.source_terms_file)

    pattern_hits = {name: len(pattern.findall(text)) for name, pattern in PATTERNS.items()}
    source_hits = {term: text.count(term) for term in source_terms if term in text}
    placeholder_count = len(re.findall(r"\[[^\[\]]+\]", text))

    report = {
        "file": str(args.docx),
        "visible_chars": len(text),
        "placeholder_count": placeholder_count,
        "media_files": len(media),
        "rsid_left": rsid_left,
        "pattern_hits": pattern_hits,
        "source_term_hits": source_hits,
        "media_paths": media[:20],
    }

    print(json.dumps(report, ensure_ascii=False, indent=2))

    has_risk = bool(media or rsid_left or source_hits or any(pattern_hits.values()))
    if has_risk and not args.no_fail:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
