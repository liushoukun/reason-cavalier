---
name: rc.task.new
description: 在 .ai/tasks 下创建新任务目录，写入符合 task-protocol 的 task.yaml，并落盘与 workflow-protocol 语义对齐的 workflow.yaml（默认复用 dev.workflow.yaml）
---

你正在执行 **Reason Cavalier：新建任务存储**。目标是在仓库根下创建 `.ai/tasks/<task_id>/`，形成可被 `call-reason-cavalier` 技能消费的**最小任务存储**。

## 0. 必须先读（不可跳过）

1. `skills/call-reason-cavalier/task-protocol.md` —— `task.yaml` 字段、目录、`task_id` / `uid`、原子写约定。
2. `skills/call-reason-cavalier/workflow-protocol.md` —— 工作流根对象、Stage/Step/Gate 语义与顺序约束。
3. `skills/call-reason-cavalier/workflows/dev.workflow.yaml` —— 默认绑定的工作流**机读模板**（与 `docs/workflow/workflow-definition.schema.json` 一致；技能正文里 Stage 的 `id`/`key` 为抽象口径时，**落盘以本文件结构为准**）。

## 1. 向用户确认或补全的输入

若用户消息中未给全，先**简短追问**一次；仍缺省则按默认值：

| 字段 | 说明 | 默认 |
|------|------|------|
| `type` | `feat\|bug\|refactor\|test\|doc\|chore` | 由用户说明推断，无法推断则用 `chore` |
| `title` | 任务标题 | 必填（若缺则追问） |
| `intent` | 目标陈述 | 可与 title 同义补全或追问 |
| `name` | `task_id` 尾段，kebab-case，仅 `a-z0-9-` | 由 title 转写或追问 |
| `host_app` | `cursor\|codex\|claude_code\|other` | `cursor` |

## 2. 生成 `task_id` 与 `uid`

- `task_id` 必须符合 `task-protocol.md` 中的正则：  
  `^(feat|bug|refactor|test|doc|chore)-\d{9}-[a-z0-9]+(?:-[a-z0-9]+)*$`  
  其中 **9 位数字段**为 `YYMMDD`（6 位）+ 当日流水号 `XXX`（3 位，自 `001` 起）。
- **流水号**：枚举 `.ai/tasks/**/task.yaml`（或任务目录名），筛出与**今天**（按用户环境当日日期）相同 `YYMMDD` 且同 `type` 前缀的已占用 `XXX`，取最大 +1；若无则 `001`。
- `uid`：新生成的 **ULID**（26 字符 Crockford base32），保证与已有任务不重复。

## 3. 目录与文件

创建目录：

```text
.ai/tasks/<task_id>/
  task.yaml
  workflow.yaml
```

### 3.1 `workflow.yaml`

- 将 `skills/call-reason-cavalier/workflows/dev.workflow.yaml` 的**完整内容**写入 `.ai/tasks/<task_id>/workflow.yaml`。
- 不删减阶段、门禁与步骤；保持 UTF-8。该文件体现 `workflow-protocol.md` 中的：**根对象**、`stages[]` 顺序主链、**阶段内** `gates[]` 与 `steps[]`、Gate 的 `type` + `conditions[]` 等语义。

### 3.2 `task.yaml`

按 `task-protocol.md` 的**必填字段**构造任务**当前快照**（新建态）：

- `schema_version`: `1.0.0`
- `task_id` / `uid` / `type` / `title` / `intent` / `host_app`
- `status`: `todo`（新建）
- `owner`: `user`（若用户明确说由代理创建可写 `agent`）
- `workflow`: 与 `dev.workflow.yaml` 根字段 `id` 一致，即 **`dev`**
- `stages`: **5** 个阶段，与 SDD 主链及本仓库示例任务一致，**`name`** 依次为：`SPEC`、`PLAN`、`IMPLEMENT`、`VERIFY`、`COMPLETE`。每阶段：
  - `status`: 全为 `todo`
  - `artifacts`: `[]`
- `created_at` / `updated_at`: 当前 UTC，ISO-8601，形如 `2026-04-18T12:00:00Z`（按实际时刻）
- `updated_by`: `user` 或 `agent`（与 `owner` 首次写入策略一致即可）
- `notes`: 一句中文说明「任务已初始化，工作流见同目录 workflow.yaml」

## 4. 写入约定

遵循 `task-protocol.md`：**临时文件写入 → 再替换目标文件**，避免半截 YAML。

## 5. 完成后向用户汇报

- 新目录路径与 `task_id`
- 提醒后续编排应加载 `call-reason-cavalier` 技能，并**校验** `workflow.yaml` 后再进入执行态（与 `workflow-protocol.md` 第 6 节一致）
