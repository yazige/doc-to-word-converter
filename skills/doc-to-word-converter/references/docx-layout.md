# DOCX Layout for Chinese Document Templates

Prefer a conservative legal/business document layout **matching the source file's original format**.

## Page Orientation — DETECT FIRST, BUILD SECOND

**CRITICAL: Always detect the source document's page orientation BEFORE building the output DOCX.**
Never assume portrait. A landscape source must produce a landscape output.

### Detection by file type

| Format | Detection method | Key API |
|--------|-----------------|---------|
| PDF | `page.rect.width > page.rect.height` → landscape | PyMuPDF `fitz` |
| DOCX | `section.orientation == WD_ORIENT.LANDSCAPE` | `python-docx` |
| PPTX | `slide_width > slide_height` → landscape (most PPTs) | `python-pptx` |
| Images | Compare pixel dimensions | PIL/Pillow |

### Setting orientation in python-docx

```python
from docx import Document
from docx.shared import Cm, Inches, Pt
from docx.enum.section import WD_ORIENT

doc = Document()
section = doc.sections[0]

# === Portrait (default) ===
section.orientation = WD_ORIENT.PORTRAIT
section.page_width  = Cm(21.0)   # A4 portrait
section.page_height = Cm(29.7)

# === Landscape ===
section.orientation = WD_ORIENT.LANDSCAPE
section.page_width  = Cm(29.7)   # A4 landscape
section.page_height = Cm(21.0)
```

**IMPORTANT:** When switching to landscape in python-docx, you MUST swap width and height **explicitly**. Simply setting `orientation = WD_ORIENT.LANDSCAPE` does NOT automatically swap the dimensions in all versions.

### Usable widths by orientation

| Orientation | Page size | Margin (each side) | Usable width |
|------------|-----------|-------------------|-------------|
| Portrait A4 | 21.0 cm | 1.27 cm | **18.46 cm** |
| Landscape A4 | 29.7 cm | 1.27 cm | **27.16 cm** |

```python
# Detect and apply dynamically
if orientation == "landscape":
    USABLE_WIDTH_CM = 27.16  # A4 landscape minus 2.54 cm margins
    section.orientation = WD_ORIENT.LANDSCAPE
    section.page_width  = Cm(29.7)
    section.page_height = Cm(21.0)
else:
    USABLE_WIDTH_CM = 18.46  # A4 portrait minus 2.54 cm margins
    section.orientation = WD_ORIENT.PORTRAIT
    section.page_width  = Cm(21.0)
    section.page_height = Cm(29.7)
```

## Page Setup

- **Paper size:** Match source document. Default to A4 portrait, override if source is landscape or different size.
- **Margins (narrow):** top = bottom = left = right = **1.27 cm** (unless source has clearly different margins).
- Body font: Chinese `SimSun` / `宋体`; Latin `Times New Roman`.
- Body size: 12 pt.
- Line spacing: 1.5.
- Body paragraphs: first-line indent ~2 Chinese characters.

### Setting Margins in python-docx

```python
from docx.shared import Cm
section = doc.sections[0]
section.top_margin    = Cm(1.27)
section.bottom_margin = Cm(1.27)
section.left_margin   = Cm(1.27)
section.right_margin  = Cm(1.27)
```

## Table Column Width Adjustment

With narrow margins, the usable text width on A4 is:

> 21.0 cm (A4 width) − 1.27 cm × 2 (left + right) = **18.46 cm**

When creating or rebuilding tables, set total table width to the orientation-appropriate usable width and distribute column widths proportionally to match the source layout.

```python
from docx.shared import Cm
from docx.enum.table import WD_TABLE_ALIGNMENT

# Use the orientation-appropriate USABLE_WIDTH_CM defined above (18.46 for portrait, 27.16 for landscape)

def set_table_width(table, col_ratios):
    """
    Set table to full usable width and distribute columns by ratio.
    col_ratios: list of relative widths, e.g. [1, 2, 1] for a 3-column table.
    """
    total = sum(col_ratios)
    usable = Cm(USABLE_WIDTH_CM)
    for i, cell in enumerate(table.columns):
        for c in cell.cells:
            c.width = int(usable * col_ratios[i] / total)
```

Verify that no cell content overflows after setting column widths.

## Titles

- Main title centered, bold, 16–18 pt.
- If the source has a subtitle, place it centered above the main title.
- Leave a modest blank line after the title block.

## Parties and Recitals

- Keep party blocks near the top, using either source-like paragraphs or a simple table.
- Use consistent placeholder labels and punctuation.
- Keep `鉴于` / recital paragraphs in the same order as the source.

## Clauses

- Preserve original numbering style: `第一条`, `1.1`, `(一)`.
- Bold top-level clause headings when useful.
- Do not renumber unless there is an obvious OCR error.
- Join clauses split across pages into normal editable paragraphs.

## Signature Pages

- Insert page breaks before signature pages when the source uses separate signing pages.
- Use editable text fields only:
  - `签署方：[主体名称]`
  - `签字/盖章：________________`
  - `日期：____年____月____日`
- Do not insert scanned signatures, stamps, or handwritten marks.

## Format Preservation Policy

The goal is to **reproduce the original document's layout as faithfully as possible** in clean, editable DOCX form. Follow this priority order:

### Tier 1 — Must Preserve (non-negotiable)

| Element | How to preserve |
|---------|----------------|
| **Page orientation** | Detect first (`portrait`/`landscape`), build output to match |
| **Table structure** | Same rows, columns, merged cell regions as source |
| **Section/clause numbering** | Original numbering style (`第一条`, `1.1`, `(一)`) |
| **Content order** | Same sequence of sections, clauses, appendices |

### Tier 2 — Should Preserve (make best effort)

| Element | How to preserve |
|---------|----------------|
| **Column widths in tables** | Recalculate proportionally for target page width |
| **Bold/italic emphasis** | Replicate where clearly intentional in source |
| **Page breaks** | Insert `doc.add_page_break()` at original break points |
| **Signature blocks** | Editable blank fields preserving original layout |

### Tier 3 — Modernize (acceptable deviation)

| Element | Approach |
|---------|----------|
| **Font** | Standardize to SimSun/Times New Roman for clean readability |
| **Margins** | Default to narrow 1.27cm unless source is clearly different |
| **Headers/footers** | Omit logos and branding; keep page numbers if present |
| **Colors** | Drop decorative colors; keep black + standard table borders |

### Decision flow

```
1. Detect orientation → portrait or landscape?
2. Detect page size → A4 / US Letter / other?
3. Build matching section setup in python-docx
4. Reconstruct content in original order
5. Verify tables fit within usable width
```

## Final QA

- Open the DOCX with a document reader if available; verify no text overflow.
- If rendering is unavailable, read the DOCX text and inspect internal package for images and hidden metadata.
- Confirm margins are 1.27 cm and all tables fit within the text area.
- **Verify orientation matches source:** If source was landscape, output section must be `WD_ORIENT.LANDSCAPE`.
- Confirm page breaks align with original document structure.
