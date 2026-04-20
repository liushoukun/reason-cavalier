#!/usr/bin/env python3
"""
Create `.ai/tasks/<task_id>/task.yaml` (Reason Cavalier task snapshot).

No third-party deps (stdlib only). Canonical task_id rules: ../SKILL.md
(section「task_id 命名规范」). This script assigns UTC-day serial and uid.
"""

from __future__ import annotations

import argparse
import re
import secrets
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
TASK_TYPES = frozenset({"feat", "bug", "refactor", "test", "doc", "chore"})
HOST_APPS = frozenset({"cursor", "codex", "claude_code", "other"})
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DIR_RE_TMPL = r"^{}-{}(\d{{3}})-.+$"


def yaml_single_quoted(s: str) -> str:
    if s is None:
        return "''"
    return "'" + s.replace("'", "''") + "'"


def title_to_kebab_slug(title: str) -> str:
    t = title.strip().lower()
    t = re.sub(r"\s+", "-", t)
    t = re.sub(r"[^a-z0-9-]+", "-", t)
    t = re.sub(r"-{2,}", "-", t).strip("-")
    return t or "task"


def new_ulid() -> str:
    ms = int(time.time() * 1000)
    chars = [""] * 26
    m = ms
    for i in range(9, -1, -1):
        chars[i] = CROCKFORD[m % 32]
        m //= 32

    rand = secrets.token_bytes(10)
    bi = int.from_bytes(rand, "big")
    for i in range(25, 9, -1):
        digit = bi % 32
        chars[i] = CROCKFORD[digit]
        bi //= 32
    return "".join(chars)


def next_daily_serial(tasks_dir: Path, task_type: str, yy_mm_dd: str) -> int:
    pattern = re.compile(DIR_RE_TMPL.format(re.escape(task_type), re.escape(yy_mm_dd)))
    max_n = 0
    if not tasks_dir.is_dir():
        return 1
    for child in tasks_dir.iterdir():
        if not child.is_dir():
            continue
        m = pattern.fullmatch(child.name)
        if m:
            n = int(m.group(1))
            if n > max_n:
                max_n = n
    return max_n + 1


def build_task_yaml(
    *,
    task_id: str,
    uid: str,
    task_type: str,
    title: str,
    intent: str,
    host_app: str,
    workflow: str,
    now_iso: str,
    notes: str,
) -> str:
    title_y = yaml_single_quoted(title)
    intent_y = yaml_single_quoted(intent)
    notes_y = yaml_single_quoted(notes)
    lines = [
        "schema_version: 1.0.0",
        f"task_id: {task_id}",
        f"uid: {uid}",
        f"type: {task_type}",
        f"title: {title_y}",
        f"intent: {intent_y}",
        f"host_app: {host_app}",
        "status: todo",
        "owner: user",
        f"workflow: {workflow}",
        "stages:",
        "  - name: SPEC",
        "    status: todo",
        "    artifacts: []",
        "  - name: PLAN",
        "    status: todo",
        "    artifacts: []",
        "  - name: IMPLEMENT",
        "    status: todo",
        "    artifacts: []",
        "  - name: VERIFY",
        "    status: todo",
        "    artifacts: []",
        "  - name: COMPLETE",
        "    status: todo",
        "    artifacts: []",
        f"created_at: {now_iso}",
        f"updated_at: {now_iso}",
        "updated_by: user",
        f"notes: {notes_y}",
    ]
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Create .ai/tasks/<task_id>/task.yaml")
    p.add_argument("--type", required=True, choices=sorted(TASK_TYPES), help="Task type")
    p.add_argument("--title", required=True, help="Human title (UTF-8 ok)")
    p.add_argument("--slug", default="", help="kebab-case suffix; default derived from title")
    p.add_argument(
        "--repo-root",
        default=".",
        type=Path,
        help="Repository root (default: current directory)",
    )
    p.add_argument("--host-app", default="cursor", choices=sorted(HOST_APPS))
    p.add_argument(
        "--workflow",
        default="dev",
        help="Must match task.yaml `workflow` and bundled workflow file id (default: dev)",
    )
    p.add_argument("--dry-run", action="store_true", help="Print paths only; do not write")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    tasks_dir = repo_root / ".ai" / "tasks"

    slug = args.slug.strip() or title_to_kebab_slug(args.title)
    if not SLUG_RE.fullmatch(slug):
        print(f"Slug must be kebab-case (a-z, 0-9, hyphens): {slug!r}", file=sys.stderr)
        return 2

    yy_mm_dd = datetime.now(timezone.utc).strftime("%y%m%d")
    serial = next_daily_serial(tasks_dir, args.type, yy_mm_dd)
    serial_str = f"{serial:03d}"
    task_id = f"{args.type}-{yy_mm_dd}{serial_str}-{slug}"
    task_dir = tasks_dir / task_id
    task_file = task_dir / "task.yaml"

    if task_dir.exists():
        print(f"Target directory already exists: {task_dir}", file=sys.stderr)
        return 3

    uid = new_ulid()
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    notes = (
        "Initialized by skills/call-reason-cavalier/scripts/new-task.py. "
        "Update per task-protocol when execution starts."
    )
    yaml_text = build_task_yaml(
        task_id=task_id,
        uid=uid,
        task_type=args.type,
        title=args.title,
        intent=args.title,
        host_app=args.host_app,
        workflow=args.workflow,
        now_iso=now_iso,
        notes=notes,
    )

    print(f"task_id: {task_id}")
    print(f"path:    {task_file}")

    if args.dry_run:
        print("(dry-run) no files written.")
        return 0

    tasks_dir.mkdir(parents=True, exist_ok=True)
    task_dir.mkdir(parents=False, exist_ok=False)
    tmp = task_file.with_suffix(task_file.suffix + ".tmp")
    tmp.write_text(yaml_text, encoding="utf-8", newline="\n")
    tmp.replace(task_file)
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
