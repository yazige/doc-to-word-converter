#!/usr/bin/env python3
"""Report and persist doc-to-word conversion workspace status."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


QUEUE_DIRS = ("TBD", "Done", "New")
STATE_DIR = ".doc-to-word-converter"
STATUS_FILE = "status.json"


def list_queue_files(path: Path) -> list[str]:
    if not path.exists():
        return []
    return sorted(item.name for item in path.iterdir() if item.is_file() and not item.name.startswith("."))


def build_status(workspace: Path) -> dict[str, object]:
    workspace = workspace.expanduser().resolve()
    done_files = list_queue_files(workspace / "Done")
    new_files = list_queue_files(workspace / "New")
    tbd_files = list_queue_files(workspace / "TBD")
    return {
        "workspace": str(workspace),
        "processed_count": len(done_files),
        "new_count": len(new_files),
        "remaining_count": len(tbd_files),
        "done_files": done_files,
        "new_files": new_files,
        "remaining_files": tbd_files,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def write_status(workspace: Path, status: dict[str, object]) -> Path:
    state_dir = workspace.expanduser().resolve() / STATE_DIR
    state_dir.mkdir(exist_ok=True)
    status_path = state_dir / STATUS_FILE
    status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return status_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", nargs="?", default=".")
    parser.add_argument("--json", action="store_true", help="Print JSON only.")
    args = parser.parse_args()

    workspace = Path(args.workspace).expanduser().resolve()
    for name in QUEUE_DIRS:
        (workspace / name).mkdir(parents=True, exist_ok=True)

    status = build_status(workspace)
    status_path = write_status(workspace, status)
    if args.json:
        print(json.dumps(status, ensure_ascii=False, indent=2))
    else:
        print(f"Workspace: {status['workspace']}")
        print(f"Processed source files: {status['processed_count']}")
        print(f"New Word files: {status['new_count']}")
        print(f"Remaining TBD files: {status['remaining_count']}")
        print(f"Status file: {status_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
