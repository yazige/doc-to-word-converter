---
name: doc-to-word-converter
description: Use when converting PDF, PPT/PPTX, Excel/CSV, image, scanned, or DOCX files into clean editable Word templates; batch-processing files from TBD; anonymizing sensitive document content; preserving source orientation and layout; or continuing a document-conversion batch in Codex.
---

# Doc-to-Word Converter

Convert source documents into clean, editable, anonymized Word `.docx` templates. This Codex version is quality-first: preserve source orientation, reduce context load before quality degrades, and continue large batches through explicit handoffs.

## Workspace

Use a conversion workspace that contains these folders:

| Folder | Purpose |
|---|---|
| `TBD/` | Files waiting to be converted. |
| `Done/` | Source files after successful conversion. |
| `New/` | Finished Word files. |

Ask the user to confirm the conversion workspace. In examples below, replace `<workspace>` with the real folder path.

```bash
<workspace>
```

Initialize or verify the workspace before processing:

```bash
python scripts/init_workspace.py "<workspace>"
```

The script creates `TBD`, `Done`, and `New`, then writes `.doc-to-word-converter/status.json`.

## Quality-first batching

Always run complexity assessment before converting files:

```bash
python scripts/assess_batch_complexity.py --tbd-dir "<workspace>/TBD" --json
```

Use the assessment to choose the next batch. The goal is not speed; the goal is usable Word output.

| Situation | Batch choice |
|---|---|
| Fresh context, simple files | Up to 12 complexity points. |
| Medium context, mixed files | Up to 8 complexity points. |
| Long context, error logs, OCR output, or uncertainty | 1 file only. |
| Very-complex file or failed assessment | 1 file only. |

Process fewer files whenever unsure. A slow good conversion is better than a fast unusable document.

## Orientation Rule

Do not default to landscape. Do not blindly default to portrait except as a fallback after failed detection.

1. Detect the source document's structure first.
2. Use the detected orientation for the output:
   - source portrait -> output portrait
   - source landscape -> output landscape
3. If detection fails, use portrait as the safe fallback and report: `版式检测失败，已按竖版保守处理`.

The complexity script returns `orientation`, `page_width_pt`, and `page_height_pt`. Pass the detected value into the builder:

```bash
python scripts/template_text_to_docx.py clean_text.txt output.docx --orientation portrait --margin-cm 1.27
python scripts/template_text_to_docx.py clean_text.txt output.docx --orientation landscape --margin-cm 1.27
```

## Context handoff

Large batches must not be forced through one long Codex conversation.

After each file, run:

```bash
python scripts/status_report.py "<workspace>" --json
```

Use `processed_count`, `new_count`, and `remaining_count` in the user-facing progress report.

Ask the user to continue in a new Codex conversation when any of these are true:

- the planned batch is complete and `remaining_count > 0`;
- the current conversation contains long OCR text, repeated errors, or large script/log output;
- visual reading, table reconstruction, or redaction quality starts becoming shallow;
- you feel tempted to process "just one more" complex file in a crowded context.

Use this exact handoff message:

```text
已经处理 {processed_count} 个原文件，已生成 {new_count} 个 Word 文件，TBD 里还剩 {remaining_count} 个文件。
当前对话上下文已经变长。为了保证转出的质量，建议新建一个 Codex 对话继续处理。
是否新建对话继续转化？如果继续，新对话请使用下面这段提示词：

继续使用 doc-to-word-converter skill 处理 <workspace>/TBD 里的文件。
先运行 scripts/status_report.py 查看 processed_count 和 remaining_count，再运行 scripts/assess_batch_complexity.py 选择下一批。
质量第一：根据当前上下文和文件复杂度选择合适的信息密度，复杂或不确定文件一律单独处理。
每个文件完成后，把原文件放入 Done，把新 Word 放入 New，并重新报告 processed_count、new_count、remaining_count。
直到 TBD 为空再结束。
```

If Codex thread-management tools are available and the user says yes, create or hand off to a new Codex thread. If those tools are not available, give the continuation prompt above and wait.

## Standard Workflow

1. **Initialize workspace**
   - Confirm the target folder.
   - Run `scripts/init_workspace.py`.
   - Never delete or overwrite source files.

2. **Assess complexity**
   - Run `scripts/assess_batch_complexity.py --tbd-dir <workspace>/TBD --json`.
   - Choose a conservative batch using Quality-first batching.
   - If the assessment fails, process one file only.

3. **Inspect source and extract content**
   - PDF: run `scripts/pdf_inventory.py`. Use text layer when available.
   - PPT/PPTX: use `python-pptx` to extract slide text and notes.
   - Excel/CSV: use spreadsheet rows as Word tables.
   - DOCX: read editable text; inspect embedded images when present.
   - Images/scans: OCR only when Tesseract or visual transcription is available. If not, report the limitation instead of pretending OCR was done.

4. **Clean and anonymize**
   - Follow `references/redaction-rules.md`.
   - Former company identifiers -> `****`.
   - Other sensitive values -> role placeholders like `[乙方公司名称]`, `[自然人姓名]`, `[联系电话]`.
   - Keep uncertain replacements marked as `【待确认：...】`.

5. **Build Word**
   - Use the detected orientation.
   - Use 1.27 cm margins.
   - Preserve headings, clauses, tables, page breaks, and signature blocks as editable content.
   - Do not paste full-page screenshots as the final Word content.
   - For image-only forms, scorecards, checklists, and evaluation tables, reconstruct the visible grid as editable table rows.
   - Do not collapse multiple source rows into one large cell separated by line breaks. Each visible row or scoring item should become its own Word table row.
   - Preserve meaningful source merges. If the source table uses merged cells to show groups, categories, section numbers, scoring standards, result blocks, or remark blocks, keep those merged cells.
   - Do not remove all merges by default. The correct rule is: detail rows stay editable one row per item; grouping labels may be merged exactly where the source groups them.
   - Avoid only harmful merges: do not merge unrelated detail rows just to save work, and do not put many source rows into one text-only cell when the source shows separate grid rows.
   - Preserve complex table headers. If the source has diagonal corner headers, grouped column headers, or multi-row headers, rebuild that structure as editable Word table cells instead of flattening it into simple column names.
   - For diagonal header cells, use Word diagonal borders when practical; if the exact diagonal text placement is uncertain, keep both header labels in the same corner cell and report that the diagonal layout was approximated.
   - For grouped headers such as cost categories, reimbursement categories, scoring groups, or regional standards, keep the two-level header layout: group header row first, subcategory row second, then data rows.

6. **Scrub and validate**
   - Run:

```bash
python scripts/privacy_scrub_docx.py output.docx output_scrubbed.docx
python scripts/check_docx_privacy.py output_scrubbed.docx
python scripts/check_docx_quality.py output_scrubbed.docx
```

   - For table-heavy or image-only forms, also run a table-granularity check. Use `--no-merged-cells` only when the source table truly has no merged cells or the user explicitly requests independent cells:

```bash
python scripts/check_docx_table_granularity.py output_scrubbed.docx --min-rows 8 --max-newlines-per-cell 3
```

   - If a check fails, fix the document before moving it to `New`.

7. **Move files and report**
   - Move the source file to `Done/`.
   - Move the final `.docx` to `New/`.
   - Run `scripts/status_report.py`.
   - Report orientation, quality check result, redaction notes, unresolved `【待确认】`, `processed_count`, `new_count`, and `remaining_count`.

## Dependency Notes

Codex Desktop often provides `python-docx`, `python-pptx`, `openpyxl`, `pypdf`, and `Pillow`. `PyMuPDF/fitz`, `pytesseract`, and the Tesseract OCR engine may be missing.

If OCR dependencies are missing:

- text-layer PDF, DOCX, Excel, and PPT can still be processed;
- scanned PDF and image OCR are limited;
- tell the user what cannot be read automatically and suggest installing OCR support or processing those files one by one with visual transcription.

## Guardrails

- Quality first; never maximize batch size for speed.
- Never overwrite original files.
- Never claim OCR, visual QA, or privacy cleanup unless the corresponding step actually ran.
- Do not continue a crowded conversation just because files remain.
- Do not move a file to `Done` until the final Word passed quality and privacy checks.
- If a file cannot be processed safely, leave it in `TBD` and explain why.
