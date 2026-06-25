from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON = os.environ.get("PYTHON", sys.executable)


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [PYTHON, *args],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )


class CodexAdaptationTests(unittest.TestCase):
    def test_skill_frontmatter_is_codex_valid(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        frontmatter = re.match(r"^---\n(.*?)\n---", text, re.S)
        self.assertIsNotNone(frontmatter, "SKILL.md must start with YAML frontmatter")
        assert frontmatter is not None
        keys = {
            line.split(":", 1)[0].strip()
            for line in frontmatter.group(1).splitlines()
            if ":" in line and not line.startswith(" ")
        }
        self.assertLessEqual(keys, {"name", "description", "license", "allowed-tools", "metadata"})
        self.assertNotIn("agent_created", keys)

    def test_skill_documents_codex_context_handoff_rules(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        required = [
            "Quality-first batching",
            "Context handoff",
            "processed_count",
            "remaining_count",
            "new Codex conversation",
            "TBD",
            "Done",
            "New",
        ]
        for phrase in required:
            self.assertIn(phrase, text)

        forbidden = ["WorkBuddy", "Agent tool", "general-purpose agent"]
        for phrase in forbidden:
            self.assertNotIn(phrase, text)

    def test_init_workspace_creates_queue_dirs_and_status(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            script = ROOT / "scripts" / "init_workspace.py"
            run_script(str(script), str(tmp_path))

            for name in ("TBD", "Done", "New"):
                self.assertTrue((tmp_path / name).is_dir())

            status_path = tmp_path / ".doc-to-word-converter" / "status.json"
            status = json.loads(status_path.read_text(encoding="utf-8"))
            self.assertEqual(status["workspace"], str(tmp_path.resolve()))
            self.assertEqual(status["processed_count"], 0)
            self.assertEqual(status["remaining_count"], 0)

    def test_status_report_counts_done_new_and_tbd(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            run_script(str(ROOT / "scripts" / "init_workspace.py"), str(tmp_path))
            (tmp_path / "TBD" / "a.pdf").write_text("todo", encoding="utf-8")
            (tmp_path / "TBD" / "b.docx").write_text("todo", encoding="utf-8")
            (tmp_path / "Done" / "old.pdf").write_text("done", encoding="utf-8")
            (tmp_path / "New" / "old.docx").write_text("new", encoding="utf-8")

            result = run_script(
                str(ROOT / "scripts" / "status_report.py"),
                str(tmp_path),
                "--json",
            )
            status = json.loads(result.stdout)
            self.assertEqual(status["processed_count"], 1)
            self.assertEqual(status["new_count"], 1)
            self.assertEqual(status["remaining_count"], 2)

    def test_template_builder_supports_landscape_and_narrow_margins(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            input_text = tmp_path / "input.txt"
            output_docx = tmp_path / "output.docx"
            input_text.write_text(
                "测试合同模板\n第一条 合作内容\n双方应按约定完成交付。\n",
                encoding="utf-8",
            )

            run_script(
                str(ROOT / "scripts" / "template_text_to_docx.py"),
                str(input_text),
                str(output_docx),
                "--title-lines",
                "1",
                "--orientation",
                "landscape",
                "--margin-cm",
                "1.27",
            )

            from docx import Document

            doc = Document(str(output_docx))
            section = doc.sections[0]
            self.assertGreater(section.page_width.cm, section.page_height.cm)
            for margin in (
                section.left_margin.cm,
                section.right_margin.cm,
                section.top_margin.cm,
                section.bottom_margin.cm,
            ):
                self.assertLess(abs(margin - 1.27), 0.05)

    def test_template_builder_default_is_portrait_fallback_not_landscape(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            input_text = tmp_path / "input.txt"
            output_docx = tmp_path / "output.docx"
            input_text.write_text("普通竖版文档\n第一条 内容\n", encoding="utf-8")

            run_script(
                str(ROOT / "scripts" / "template_text_to_docx.py"),
                str(input_text),
                str(output_docx),
            )

            from docx import Document

            doc = Document(str(output_docx))
            section = doc.sections[0]
            self.assertLess(section.page_width.cm, section.page_height.cm)


if __name__ == "__main__":
    unittest.main()
