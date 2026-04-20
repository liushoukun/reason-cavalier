#!/usr/bin/env python3
"""
在用户确认后：补齐 Harness 最小目录树，并可做一轮非破坏性的内容补全。

默认 --dry-run 仅打印将执行的动作；需显式传入 --apply 才会写盘。
无第三方依赖。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable

from harness_spec import (
    AGENTS_BASENAME,
    AGENTS_HINT_TERMS,
    BLOCKING_DIRS,
    DOCS_DIR,
    DOCS_INDEX_CANDIDATES,
    GITKEEP,
    MIN_AGENTS_CHARS,
    RECOMMENDED_DIRS,
    ROUND1_MARKER,
    normalize_root,
)

# 延迟导入，避免 harness_check 与 argparse 顶层副作用
def _audit(root: Path):
    from harness_check import audit, exit_code_for

    rows = audit(root)
    return rows, exit_code_for(rows)


def _read_package_scripts(root: Path) -> dict[str, str]:
    p = root / "package.json"
    if not p.is_file():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        scripts = data.get("scripts")
        return scripts if isinstance(scripts, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _agents_path(root: Path) -> Path:
    return root / AGENTS_BASENAME


def _docs_index_path(root: Path) -> Path | None:
    for rel in DOCS_INDEX_CANDIDATES:
        p = root / rel
        if p.is_file():
            return p
    return None


def _hint_hits(text: str) -> int:
    low = text.lower()
    return sum(1 for t in AGENTS_HINT_TERMS if t.lower() in low)


def _ensure_dir_with_gitkeep(path: Path, *, dry_run: bool) -> bool:
    """若目录已存在则返回 False（视为未变更）；否则创建并写入 .gitkeep。"""
    if path.is_dir():
        gitkeep = path / GITKEEP
        if not gitkeep.is_file():
            if dry_run:
                print(f"[DRY] 写入 {gitkeep.as_posix()}")
            else:
                gitkeep.write_text("", encoding="utf-8")
            return True
        return False
    if dry_run:
        print(f"[DRY] mkdir {path.as_posix()} + {GITKEEP}")
    else:
        path.mkdir(parents=True, exist_ok=True)
        (path / GITKEEP).write_text("", encoding="utf-8")
    return True


def build_agents_skeleton(root: Path) -> str:
    scripts = _read_package_scripts(root)
    lines: list[str] = [
        "# 代理工作区说明（Harness）",
        "",
        "本文件用于指导代理在本仓库内如何落盘任务、工作流与文档；**请以仓库真实脚本与路径为准**，勿编造命令。",
        "",
        "## 持久化与目录分工",
        "",
        "- 任务与执行上下文：`.ai/tasks/`",
        "- 工作流模板或运行期落盘：`.ai/workflows/`",
        "- 可选执行记忆（与正式文档区分）：`.ai/memory/`",
        "- 正式知识、归档与文档治理：`docs/`（建议入口 `docs/index.md`）",
        "",
        "## 验证与证据",
        "",
        "在声称完成、修复或通过前，应运行仓库内已有验证命令并保留输出证据；不要凭空调用不存在的脚本名。",
        "",
    ]
    if scripts:
        lines.extend(
            [
                "## package.json scripts（摘录，仅列出现有键名）",
                "",
            ]
        )
        for k in sorted(scripts.keys()):
            lines.append(f"- `{k}`")
        lines.append("")
    lines.extend(
        [
            "## 与 Reason Cavalier / Harness 对齐",
            "",
            "多会话续跑时优先读取 `.ai/tasks/` 下任务快照与 `docs/` 中权威说明；执行态中间产物放在 `.ai/` 下合适子目录，避免与 `docs/` 混放。",
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def build_round1_agents_append(root: Path) -> str:
    scripts = _read_package_scripts(root)
    script_line = ""
    if scripts:
        keys = ", ".join(f"`{k}`" for k in sorted(scripts.keys())[:12])
        if len(scripts) > 12:
            keys += "，…"
        script_line = f"\n\n当前 `package.json` 中已有脚本键名包括：{keys}；执行前请核对真实存在。"
    return (
        f"\n\n{ROUND1_MARKER}\n\n"
        "## Harness 自动补全段（一轮）\n\n"
        "以下段落由 `harness_init.py --content-round1` 在检测到 `AGENTS.md` 内容偏弱时**追加**，不覆盖上文。\n\n"
        "### 最低分工锚点\n\n"
        "- `.ai/tasks/`：任务快照与续跑上下文\n"
        "- `.ai/workflows/`：工作流落盘\n"
        "- `docs/`：人类可读权威文档与归档入口\n\n"
        "### 代理可执行要求\n\n"
        "变更前后应能指出证据路径；验证命令仅使用仓库内已声明脚本或工具。"
        f"{script_line}\n"
    )


def build_docs_index_minimal() -> str:
    return (
        "# 文档索引\n\n"
        "本目录用于**正式**、可评审、可版本化的项目知识；执行过程态请放在 `.ai/` 下（如 `.ai/memory/`）。\n\n"
        "## 待补充\n\n"
        "- 将权威规格、运行手册与归档类文档归类到此树并在此处链接。\n"
    )


def scaffold_dirs(
    root: Path,
    *,
    scope: str,
    dry_run: bool,
) -> list[str]:
    changed: list[str] = []
    dirs: Iterable[str]
    if scope == "ai-only":
        dirs = list(BLOCKING_DIRS)
    elif scope == "all":
        dirs = list(BLOCKING_DIRS) + list(RECOMMENDED_DIRS)
    else:
        dirs = ()

    for rel in dirs:
        p = root.joinpath(*rel.split("/"))
        if _ensure_dir_with_gitkeep(p, dry_run=dry_run):
            changed.append(p.as_posix())

    if scope in {"all", "docs"}:
        d = root / DOCS_DIR
        if not d.is_dir():
            if dry_run:
                print(f"[DRY] mkdir {d.as_posix()}")
            else:
                d.mkdir(parents=True, exist_ok=True)
            changed.append(d.as_posix())
    return changed


def scaffold_agents(root: Path, *, dry_run: bool, force: bool) -> list[str]:
    changed: list[str] = []
    p = _agents_path(root)
    if p.is_file() and not force:
        return changed
    body = build_agents_skeleton(root)
    mode = "覆盖" if p.is_file() and force else "新建"
    if dry_run:
        print(f"[DRY] 写入 {p.as_posix()}（{mode}）")
    else:
        p.write_text(body, encoding="utf-8", newline="\n")
    changed.append(p.as_posix())
    return changed


def scaffold_docs_index(root: Path, *, dry_run: bool) -> list[str]:
    changed: list[str] = []
    if _docs_index_path(root):
        return changed
    d = root / DOCS_DIR
    target = d / "index.md"
    if dry_run:
        print(f"[DRY] 写入 {target.as_posix()}")
    else:
        d.mkdir(parents=True, exist_ok=True)
        target.write_text(build_docs_index_minimal(), encoding="utf-8", newline="\n")
    changed.append(target.as_posix())
    return changed


def content_round1(root: Path, *, dry_run: bool) -> list[str]:
    """非破坏：仅在偏弱时追加 AGENTS 段落；仅在缺入口时写 docs/index.md。"""
    changed: list[str] = []
    ap = _agents_path(root)
    if ap.is_file():
        text = ap.read_text(encoding="utf-8", errors="replace")
        weak = (
            ROUND1_MARKER not in text
            and (
                len(text.strip()) < MIN_AGENTS_CHARS
                or _hint_hits(text) < 2
            )
        )
        if weak:
            append = build_round1_agents_append(root)
            if dry_run:
                print(f"[DRY] 追加内容到 {ap.as_posix()}（含 {ROUND1_MARKER}）")
            else:
                ap.write_text(text.rstrip() + append, encoding="utf-8", newline="\n")
            changed.append(ap.as_posix())
    else:
        # 无文件时与新建骨架一致，视为一轮补全
        changed.extend(scaffold_agents(root, dry_run=dry_run, force=False))

    if not _docs_index_path(root):
        changed.extend(scaffold_docs_index(root, dry_run=dry_run))

    return changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Harness 目录初始化与一轮内容补全")
    parser.add_argument("root", nargs="?", default=".", help="外部工程根目录")
    parser.add_argument(
        "--scope",
        choices=("all", "ai-only", "agents", "docs"),
        default="all",
        help="补齐范围：all=目录树+建议 memory+docs；ai-only=仅 .ai；agents/docs 见名知意",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="实际写盘；省略时仅 dry-run",
    )
    parser.add_argument(
        "--content-round1",
        action="store_true",
        help="在结构就绪后，对偏弱 AGENTS / 缺 docs 入口做一轮非破坏补全",
    )
    parser.add_argument(
        "--force-agents",
        action="store_true",
        help="与 --scope agents|all 联用：若已存在 AGENTS.md 仍覆盖写入骨架（慎用）",
    )
    args = parser.parse_args(argv)

    try:
        root = normalize_root(args.root)
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 1

    dry_run = not args.apply
    if dry_run:
        print("当前为 dry-run；若确认无误请追加 --apply 写盘。\n")

    all_changed: list[str] = []

    if args.scope in {"all", "ai-only"}:
        all_changed.extend(scaffold_dirs(root, scope=args.scope, dry_run=dry_run))
    if args.scope in {"all", "agents"}:
        all_changed.extend(scaffold_agents(root, dry_run=dry_run, force=args.force_agents))
    if args.scope in {"all", "docs"}:
        all_changed.extend(scaffold_docs_index(root, dry_run=dry_run))

    if args.content_round1:
        all_changed.extend(content_round1(root, dry_run=dry_run))

    if not all_changed and dry_run:
        print("[DRY] 无可执行变更（可能已满足）")

    rows, code = _audit(root)
    print("\n--- harness_check 复查 ---")
    for r in rows:
        print(f"[{r.severity.upper():8}] {r.id}: {r.detail}")
    print(f"\n复查退出码: {code}（0=无阻塞，1=有阻塞，2=仅有建议/警告）")
    # 写盘成功后：仅有警告时不以非零码失败，便于脚本链式调用
    if args.apply:
        return 0 if code != 1 else 1
    return code


if __name__ == "__main__":
    raise SystemExit(main())
