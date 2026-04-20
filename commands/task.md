---
name: rc.task.new
description: 在 .ai/tasks 下创建新任务目录，写入符合 task-protocol 的 task.yaml，并落盘与 workflow-protocol 语义对齐的 workflow.yaml（默认复用 dev.workflow.yaml）
---

你正在执行 **Reason Cavalier：新建任务存储**。目标是在仓库根下创建 `.ai/tasks/<task_id>/`，形成可被 `call-reason-cavalier` 技能消费的**最小任务存储**。

## 0. 必须先读（不可跳过）

1. **`skills/call-reason-cavalier/SKILL.md`** —— 编排约束、协议加载范围、`task.yaml` 须由脚本生成。
2. `skills/call-reason-cavalier/task-protocol.md` —— `task.yaml` 字段、目录、`uid`、原子写约定（`task_id` 命名仅见 `SKILL.md`）。
3. `skills/call-reason-cavalier/workflow-protocol.md` —— 工作流根对象、Stage/Step/Gate 语义与顺序约束。
4. `skills/call-reason-cavalier/workflows/dev.workflow.yaml` —— 默认绑定的工作流**机读模板**（与 `docs/workflow/workflow-definition.schema.json` 一致；落盘以本文件结构为准）。

**硬性规则**：已 Read `SKILL.md`；`task.yaml` 仅允许由第 2 节脚本生成；禁止手写流水号与 `uid`（见 `SKILL.md`「task_id 命名规范」）。

## 1. 向用户确认或补全的输入

若用户消息中未给全，先**简短追问**一次；仍缺省则按默认值：

| 字段 | 说明 | 默认 |
|------|------|------|
| `type` | `feat\|bug\|refactor\|test\|doc\|chore` | 由用户说明推断，无法推断则用 `chore` |
| `title` | 任务标题 | 必填（若缺则追问） |
| `intent` | 目标陈述 | 可与 title 同义补全或追问 |
| `name` | 对应脚本的尾段（`--slug`）；规则见 `SKILL.md`「task_id 命名规范」 | 由 title 转写、用户约定，或传 `--slug` |
| `host_app` | `cursor\|codex\|claude_code\|other` | `cursor` |

## 2. 生成 `task.yaml`（必须用脚本）

在**仓库根目录**执行（参数与用户输入对齐；**禁止**手算流水号或手写 ULID，命名规则见 `SKILL.md`「task_id 命名规范」）：

```bash
python skills/call-reason-cavalier/scripts/new-task.py --type <type> --title "<title>" [--slug <kebab-name>] [--host-app cursor] [--workflow dev]
```

- 未传 `--slug` 时由标题生成 kebab；与用户约定的 `name` 不一致时用 `--slug` 显式指定。
- **`--workflow` 默认为 `dev`**，须与同目录即将写入的 `workflow.yaml`（来自 `dev.workflow.yaml`，根字段 `id: dev`）一致。
- 需要仅预览路径时加 `--dry-run`。
- **禁止**自行推算流水号或手写 ULID；`task_id` / `uid` 以脚本输出为准（与 `SKILL.md` 一致）。

## 3. 写入 `workflow.yaml`

- 将 `skills/call-reason-cavalier/workflows/dev.workflow.yaml` 的**完整内容**复制到 `.ai/tasks/<task_id>/workflow.yaml`（UTF-8，不删减）。
- `task.yaml` 已由脚本创建；若需在 `notes` 中补充「工作流见同目录 workflow.yaml」，可再按 `task-protocol.md` 原子更新规则编辑（非必填）。

## 4. 目录与文件结果

```text
.ai/tasks/<task_id>/
  task.yaml      # 由 new-task.py 生成
  workflow.yaml  # 自 dev.workflow.yaml 复制
```

## 5. 写入约定

脚本对 `task.yaml` 使用临时文件再替换；复制 `workflow.yaml` 时须**临时文件 → 替换目标**，符合 `task-protocol.md` 原子写约定。

## 6. 完成后向用户汇报

- 新目录路径与 `task_id`
- 提醒后续编排应加载 **`call-reason-cavalier`** 技能（或 Read `SKILL.md`），并**校验** `workflow.yaml` 后再进入执行态（与 `workflow-protocol.md` 第 6 节一致）
