---
name: using-git-worktrees
description: 在开始需要与当前工作区隔离的功能工作之前，或在执行实现计划之前使用——通过智能目录选择与安全检查创建隔离的 git worktree。
---

# 使用 Git Worktree

## 概述

Git worktree 在共享同一仓库的前提下创建隔离工作区，让你可同时工作在多个分支而无需频繁切换。

**核心原则：** 系统化目录选择 + 安全验证 = 可靠隔离。

**开始时宣告：**「我正在使用 using-git-worktrees 技能来建立隔离工作区。」

## 目录选择流程

按以下优先级：

### 1. 检查已有目录

```bash
ls -d .worktrees 2>/dev/null     # 优先（隐藏）
ls -d worktrees 2>/dev/null      # 备选
```

**若存在：** 使用该目录。若两者都在，`.worktrees` 优先。

### 2. 检查 CLAUDE.md

```bash
grep -i "worktree.*director" CLAUDE.md 2>/dev/null
```

**若写明偏好：** 直接使用，无需再问。

### 3. 询问用户

若既无目录也无 CLAUDE.md 偏好：

```
未找到 worktree 目录。我应在何处创建 worktrees？

1. .worktrees/（项目内、隐藏）
2. ~/.config/superpowers/worktrees/<项目名>/（全局位置）

你更倾向哪一个？
```

## 安全验证

### 对项目本地目录（.worktrees 或 worktrees）

**创建 worktree 前必须验证目录已被忽略：**

```bash
git check-ignore -q .worktrees 2>/dev/null || git check-ignore -q worktrees 2>/dev/null
```

**若未被忽略：**

按 Jesse 的规则「坏了就立刻修」：
1. 向 .gitignore 添加合适规则  
2. 提交该变更  
3. 继续创建 worktree  

**为何关键：** 防止误将 worktree 内容提交进仓库。

### 全局目录（~/.config/superpowers/worktrees）

完全在项目外，无需 .gitignore 验证。

## 创建步骤

### 1. 检测项目名

```bash
project=$(basename "$(git rev-parse --show-toplevel)")
```

### 2. 创建 Worktree

```bash
case $LOCATION in
  .worktrees|worktrees)
    path="$LOCATION/$BRANCH_NAME"
    ;;
  ~/.config/superpowers/worktrees/*)
    path="~/.config/superpowers/worktrees/$project/$BRANCH_NAME"
    ;;
esac

git worktree add "$path" -b "$BRANCH_NAME"
cd "$path"
```

### 3. 运行项目安装

自动检测并运行合适安装：

```bash
if [ -f package.json ]; then npm install; fi
if [ -f Cargo.toml ]; then cargo build; fi
if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
if [ -f pyproject.toml ]; then poetry install; fi
if [ -f go.mod ]; then go mod download; fi
```

### 4. 验证干净基线

运行测试确保 worktree 从干净状态开始：

```bash
npm test
cargo test
pytest
go test ./...
```

**若失败：** 报告失败，询问是否继续或调查。

**若通过：** 报告就绪。

### 5. 报告位置

```
Worktree 就绪：<full-path>
测试通过（<N> 个测试，0 失败）
准备实现 <feature-name>
```

## 速查

| 情况 | 动作 |
|------|------|
| 存在 `.worktrees/` | 使用（验证已忽略） |
| 存在 `worktrees/` | 使用（验证已忽略） |
| 两者都存在 | 使用 `.worktrees/` |
| 都不存在 | 查 CLAUDE.md → 问用户 |
| 目录未忽略 | 加 .gitignore 并提交 |
| 基线测试失败 | 报告失败 + 询问 |
| 无 package.json/Cargo.toml | 跳过依赖安装 |

## 常见错误

**跳过忽略验证** → worktree 内容被跟踪、污染 `git status` → 创建前始终 `git check-ignore`

**假设目录位置** → 不一致、违反项目约定 → 遵循：已有 > CLAUDE.md > 询问

**测试失败仍继续** → 无法区分新 bug 与既有问题 → 报告失败并取得明确许可再继续

**硬编码安装命令** → 不同工具链项目会坏 → 从项目文件自动检测

## 危险信号

**绝不：** 未验证忽略就创建项目本地 worktree；跳过基线测试验证；测试失败未询问就继续；位置有歧义时自作主张；跳过 CLAUDE.md 检查。

**务必：** 遵循目录优先级；项目本地必须验证忽略；自动检测并运行安装；验证干净测试基线。

## 集成

**调用方：**
- **brainstorming**（第 4 阶段）— 设计批准且将开始实现时 **必需**  
- **subagent-driven-development** — 执行任何任务前 **必需**  
- **executing-plans** — 执行任何任务前 **必需**  
- 任何需要隔离工作区的技能  

**搭配：**
- **finishing-a-development-branch** — 工作完成后 **必需** 清理 worktree  
