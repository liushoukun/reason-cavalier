"""
Shared Harness readiness rules (stdlib only). Used by harness_check / harness_init.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final

# 目录：阻塞项（最小可写入运行时）
BLOCKING_DIRS: Final[tuple[str, ...]] = (".ai", ".ai/tasks", ".ai/workflows")

# 建议项（不阻塞「最小可运转」结论）
RECOMMENDED_DIRS: Final[tuple[str, ...]] = (".ai/memory",)

DOCS_DIR: Final[str] = "docs"
# 可导航入口：任一存在即视为满足
DOCS_INDEX_CANDIDATES: Final[tuple[str, ...]] = (
    "docs/index.md",
    "docs/README.md",
    "docs/readme.md",
)

AGENTS_BASENAME: Final[str] = "AGENTS.md"

# 内容：过短或缺少锚点词则记为缺失/需补全
MIN_AGENTS_CHARS: Final[int] = 120
# 至少命中若干「Harness 语义」锚点（小写比较）
AGENTS_HINT_TERMS: Final[tuple[str, ...]] = (
    ".ai",
    "tasks",
    "workflow",
    "docs",
    "验证",
    "证据",
    "harness",
)

ROUND1_MARKER: Final[str] = "<!-- reason-cavalier-harness-round1 -->"

GITKEEP: Final[str] = ".gitkeep"


@dataclass(frozen=True)
class Paths:
    root: Path

    def rel(self, *parts: str) -> Path:
        return self.root.joinpath(*parts)


def normalize_root(path: str | Path) -> Path:
    p = Path(path).expanduser().resolve()
    if not p.is_dir():
        raise FileNotFoundError(f"项目根目录不存在或不是目录: {p}")
    return p
