#!/usr/bin/env python3
"""Scrub DOCX author metadata, custom properties, and Word rsid traces."""

from __future__ import annotations

import argparse
import re
import shutil
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


RSID_ATTR_RE = re.compile(rb'\s+w:rsid\w+="[^"]*"')
RSIDS_BLOCK_RE = re.compile(rb"<w:rsids\b[^>]*>.*?</w:rsids>", re.DOTALL)
RSID_EMPTY_RE = re.compile(rb"<w:rsid\b[^>]*/>")


def scrub_word_xml(data: bytes) -> bytes:
    data = RSID_ATTR_RE.sub(b"", data)
    data = RSIDS_BLOCK_RE.sub(b"", data)
    data = RSID_EMPTY_RE.sub(b"", data)
    return data


def scrub_core_xml(data: bytes) -> bytes:
    try:
        ET.register_namespace("cp", "http://schemas.openxmlformats.org/package/2006/metadata/core-properties")
        ET.register_namespace("dc", "http://purl.org/dc/elements/1.1/")
        ET.register_namespace("dcterms", "http://purl.org/dc/terms/")
        ET.register_namespace("dcmitype", "http://purl.org/dc/dcmitype/")
        ET.register_namespace("xsi", "http://www.w3.org/2001/XMLSchema-instance")
        root = ET.fromstring(data)
    except ET.ParseError:
        return data

    text_tags = {
        "{http://purl.org/dc/elements/1.1/}creator",
        "{http://schemas.openxmlformats.org/package/2006/metadata/core-properties}lastModifiedBy",
        "{http://schemas.openxmlformats.org/package/2006/metadata/core-properties}revision",
        "{http://schemas.openxmlformats.org/package/2006/metadata/core-properties}keywords",
        "{http://purl.org/dc/elements/1.1/}subject",
        "{http://purl.org/dc/elements/1.1/}description",
    }
    date_tags = {
        "{http://purl.org/dc/terms/}created",
        "{http://purl.org/dc/terms/}modified",
    }

    for element in root.iter():
        if element.tag in text_tags:
            element.text = ""
        elif element.tag in date_tags:
            element.text = "2000-01-01T00:00:00Z"

    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def remove_custom_content_type(data: bytes) -> bytes:
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return data

    removed = False
    for child in list(root):
        if child.attrib.get("PartName") == "/docProps/custom.xml":
            root.remove(child)
            removed = True
    if not removed:
        return data
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def remove_custom_relationship(data: bytes) -> bytes:
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return data

    removed = False
    for child in list(root):
        if child.attrib.get("Target") == "docProps/custom.xml":
            root.remove(child)
            removed = True
    if not removed:
        return data
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def scrub_docx(input_docx: Path, output_docx: Path) -> dict[str, int]:
    stats = {"word_xml_scrubbed": 0, "core_props_scrubbed": 0, "custom_props_removed": 0}
    output_docx.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp_path = Path(tmp.name)

    try:
        with zipfile.ZipFile(input_docx, "r") as zin, zipfile.ZipFile(tmp_path, "w", zipfile.ZIP_DEFLATED) as zout:
            for info in zin.infolist():
                name = info.filename
                if name == "docProps/custom.xml":
                    stats["custom_props_removed"] += 1
                    continue

                data = zin.read(name)
                if name.startswith("word/") and name.endswith(".xml"):
                    new_data = scrub_word_xml(data)
                    if new_data != data:
                        stats["word_xml_scrubbed"] += 1
                    data = new_data
                elif name == "docProps/core.xml":
                    data = scrub_core_xml(data)
                    stats["core_props_scrubbed"] += 1
                elif name == "[Content_Types].xml":
                    data = remove_custom_content_type(data)
                elif name == "_rels/.rels":
                    data = remove_custom_relationship(data)

                zout.writestr(info, data)

        shutil.move(str(tmp_path), str(output_docx))
    finally:
        if tmp_path.exists():
            tmp_path.unlink()

    return stats


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_docx", type=Path)
    parser.add_argument("output_docx", type=Path)
    args = parser.parse_args()

    if not args.input_docx.exists():
        print(f"DOCX not found: {args.input_docx}")
        return 2

    stats = scrub_docx(args.input_docx, args.output_docx)
    print(args.output_docx)
    for key, value in stats.items():
        print(f"{key}={value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
