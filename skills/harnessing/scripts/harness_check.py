#!/usr/bin/env python3
"""
检测外部工程是否满足 Harness 最小目录与 AGENTS/docs 约定。

默认只读；若传入 ``--ensure-blocking-dirs``，会幂等地创建阻塞项 ``.ai`` 目录树
（``.ai/``、``.ai/tasks/``、``.ai/workflows/``）并写入 ``.gitkeep``，再执行检测。

无第三方依赖。退出码：0 无阻塞项；1 存在阻塞项；2 仅存在建议/警告（无阻塞）。
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from harness_spec import (
    AGENTS_BASENAME,
    AGENTS_HINT_TERMS,
    BLOCKING_DIRS,
    DOCS_DIR,
    DOCS_INDEX_CANDIDATES,
    GITKEEP,
    MIN_AGENTS_CHARS,
    RECOMMENDED_DIRS,
    Paths,
    normalize_root,
)


@dataclass
class Row:
    id: str
    severity: str  # "blocking" | "warn" | "ok"
    detail: str


def _agents_path(root: Path) -> Path:
    return root / AGENTS_BASENAME


def _wrong_case_agents(root: Path) -> str | None:
    """在大小写不敏感文件系统上，避免把规范的 ``AGENTS.md`` 误判为「小写 agents.md」。"""
    try:
        for p in root.iterdir():
            if not p.is_file():
                continue
            if p.name.lower() == AGENTS_BASENAME.lower() and p.name != AGENTS_BASENAME:
                return str(p)
    except OSError:
        return None
    return None


def _agents_text(root: Path) -> tuple[bool, str]:
    p = _agents_path(root)
    if not p.is_file():
        return False, ""
    try:
        return True, p.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        return True, f"<读取失败: {e}>"


def _hint_hits(text: str) -> int:
    low = text.lower()
    n = 0
    for t in AGENTS_HINT_TERMS:
        if t.lower() in low:
            n += 1
    return n


def _docs_index_ok(root: Path) -> tuple[bool, str]:
    for rel in DOCS_INDEX_CANDIDATES:
        p = root / rel
        if p.is_file():
            return True, rel
    return False, "（无 index.md / README.md）"


def audit(root: Path) -> list[Row]:
    rows: list[Row] = []
    paths = Paths(root=root)

    for rel in BLOCKING_DIRS:
        p = paths.rel(*rel.split("/"))
        if p.is_dir():
            rows.append(Row(id=f"dir:{rel}", severity="ok", detail=str(p)))
        else:
            rows.append(Row(id=f"dir:{rel}", severity="blocking", detail="不存在或不是目录"))

    for rel in RECOMMENDED_DIRS:
        p = paths.rel(*rel.split("/"))
        if p.is_dir():
            rows.append(Row(id=f"dir:{rel}", severity="ok", detail=str(p)))
        else:
            rows.append(Row(id=f"dir:{rel}", severity="warn", detail="建议创建"))

    docs = paths.rel(DOCS_DIR)
    if docs.is_dir():
        rows.append(Row(id="dir:docs", severity="ok", detail=str(docs)))
        ok, ev = _docs_index_ok(root)
        if ok:
            rows.append(Row(id="docs:entry", severity="ok", detail=ev))
        else:
            rows.append(Row(id="docs:entry", severity="warn", detail=ev))
    else:
        rows.append(Row(id="dir:docs", severity="warn", detail="docs/ 不存在（建议）"))

    wrong = _wrong_case_agents(root)
    if wrong:
        rows.append(
            Row(
                id="agents:case",
                severity="warn",
                detail=f"存在非规范文件名（建议改为 {AGENTS_BASENAME}）: {wrong}",
            )
        )

    exists, text = _agents_text(root)
    ap = _agents_path(root)
    if not exists:
        rows.append(Row(id="agents:file", severity="blocking", detail=f"缺少 {AGENTS_BASENAME}"))
    elif not text.strip():
        rows.append(Row(id="agents:empty", severity="blocking", detail=f"{AGENTS_BASENAME} 为空"))
    elif len(text.strip()) < MIN_AGENTS_CHARS:
        rows.append(
            Row(
                id="agents:short",
                severity="blocking",
                detail=f"{AGENTS_BASENAME} 过短（<{MIN_AGENTS_CHARS} 有效字符量级），不足以指导代理",
            )
        )
    elif _hint_hits(text) < 2:
        rows.append(
            Row(
                id="agents:hints",
                severity="blocking",
                detail="缺少与 Harness 分工相关的锚点（建议包含 .ai / tasks / workflows / docs / 验证或证据 等）",
            )
        )
    else:
        rows.append(Row(id="agents:content", severity="ok", detail=str(ap)))

    return rows


def exit_code_for(rows: list[Row]) -> int:
    if any(r.severity == "blocking" for r in rows):
        return 1
    if any(r.severity == "warn" for r in rows):
        return 2
    return 0


def rows_to_json(rows: list[Row]) -> dict[str, Any]:
    return {
        "rows": [asdict(r) for r in rows],
        "exit": exit_code_for(rows),
    }


def _ensure_dir_with_gitkeep_write(path: Path) -> bool:
    """创建目录并保证存在 ``.gitkeep``；若已满足则返回 False。与 harness_init 语义对齐。"""
    if path.is_dir():
        gitkeep = path / GITKEEP
        if not gitkeep.is_file():
            gitkeep.write_text("", encoding="utf-8")
            return True
        return False
    path.mkdir(parents=True, exist_ok=True)
    (path / GITKEEP).write_text("", encoding="utf-8")
    return True


def ensure_blocking_dir_tree(root: Path) -> list[str]:
    """幂等创建 ``BLOCKING_DIRS``；返回本次发生写盘的路径（posix）列表。"""
    changed: list[str] = []
    for rel in BLOCKING_DIRS:
        p = root.joinpath(*rel.split("/"))
        if _ensure_dir_with_gitkeep_write(p):
            changed.append(p.as_posix())
    return changed


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Harness 目录与文档检测（可选补齐阻塞 .ai 目录）")
    p.add_argument(
        "root",
        nargs="?",
        default=".",
        help="外部工程根目录（默认当前目录）",
    )
    p.add_argument("--json", metavar="FILE", help="将结果写入 JSON 文件")
    p.add_argument(
        "--ensure-blocking-dirs",
        action="store_true",
        help="若缺阻塞项 .ai 目录树则创建并写入 .gitkeep，然后检测；幂等；不含 .ai/memory/agents/docs",
    )
    args = p.parse_args(argv)

    try:
        root = normalize_root(args.root)
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 1

    if args.ensure_blocking_dirs:
        touched = ensure_blocking_dir_tree(root)
        if touched:
            print("已补齐阻塞项目录（.gitkeep）：")
            for s in touched:
                print(f"  - {s}")
        else:
            print("阻塞项 .ai 目录树已存在，无需写盘。")

    rows = audit(root)
    code = exit_code_for(rows)

    for r in rows:
        print(f"[{r.severity.upper():8}] {r.id}: {r.detail}")

    if args.json:
        json_path = Path(args.json)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(
            json.dumps(rows_to_json(rows), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    print(f"\n结论退出码: {code}（0=无阻塞，1=有阻塞，2=仅有建议/警告）")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
