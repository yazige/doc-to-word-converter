#!/usr/bin/env python3
"""Initialize a doc-to-word conversion workspace."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


QUEUE_DIRS = ("TBD", "Done", "New")
STATE_DIR = ".doc-to-word-converter"
STATUS_FILE = "status.json"


def count_files(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for item in path.iterdir() if item.is_file() and not item.name.startswith("."))


def build_status(workspace: Path) -> dict[str, object]:
    return {
        "workspace": str(workspace),
        "processed_count": count_files(workspace / "Done"),
        "new_count": count_files(workspace / "New"),
        "remaining_count": count_files(workspace / "TBD"),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "queue_dirs": list(QUEUE_DIRS),
    }


def init_workspace(workspace: Path) -> dict[str, object]:
    workspace = workspace.expanduser().resolve()
    workspace.mkdir(parents=True, exist_ok=True)
    for name in QUEUE_DIRS:
        (workspace / name).mkdir(exist_ok=True)

    state_dir = workspace / STATE_DIR
    state_dir.mkdir(exist_ok=True)
    status = build_status(workspace)
    (state_dir / STATUS_FILE).write_text(
        json.dumps(status, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return status


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "workspace",
        nargs="?",
        default=".",
        help="Conversion workspace that should contain TBD, Done, and New.",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable status.")
    args = parser.parse_args()

    status = init_workspace(Path(args.workspace))
    if args.json:
        print(json.dumps(status, ensure_ascii=False, indent=2))
    else:
        print(f"Workspace initialized: {status['workspace']}")
        print("Created or verified folders: TBD, Done, New")
        print(
            "Status: "
            f"processed_count={status['processed_count']}, "
            f"remaining_count={status['remaining_count']}, "
            f"new_count={status['new_count']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
