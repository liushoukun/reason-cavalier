---
name: rc.task.new
description: 在 .ai/tasks 下创建新任务目录，写入符合 task-protocol 的 task.yaml，并落盘与 workflow-protocol 语义对齐的 workflow.yaml（默认复用 dev.workflow.yaml）
---

你正在执行 **Reason Cavalier：新建任务存储**。目标是在仓库根下创建 `.ai/tasks/<task_id>/`，形成可被 `call-reason-cavalier` 技能消费的**最小任务存储**。

## 命令语义（先判定上下文，再决定动作）

- 触发 `/task` 时，表示当前对话进入**任务上下文模式**，后续动作默认以指定任务为锚点执行。
- 若命令中附带 `{task}` 目录或可解析 `task_id`（例如 `/task .ai/tasks/feat-260420001-xxx`），表示**绑定已有任务**，优先按该任务当前进度推进，而不是新建任务。
- 若命令后追加其他技能（例如 `/task {task目录} /brainstorming`），其语义是：在该任务上下文内执行对应技能，产出需回流到同一 `task_id` 的状态与证据链。
- 仅当无法识别已有任务上下文，或用户明确要求“新建任务存储”时，才进入本文第 2~5 节的新建流程。

## 会话环境识别（必须先执行）

1. 检查用户输入与当前会话是否已指定任务上下文（`task_id`、`.ai/tasks/<task_id>/`、`task.yaml`）。
2. 若已绑定任务：
   - 读取该任务目录下 `task.yaml`（必要时同时读取 `workflow.yaml`）。
   - 按 `call-reason-cavalier` + `task-protocol.md` + `workflow-protocol.md` 继续当前阶段，不重复创建任务。
3. 若未绑定任务且用户意图为“创建任务存储”，执行后续新建流程（第 0~6 节）。
4. 若意图不明，先简短追问一次；仍不明确时默认按“新建任务存储”处理。

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
- 若本次是“绑定已有任务”而非新建：汇报当前绑定的任务目录、`task_id`、所处阶段与下一步建议动作

## 常见组合示例

```text
/task .ai/tasks/feat-260420001-add-login /brainstorming
```

含义：在 `feat-260420001-add-login` 任务上下文中执行 `brainstorming`，结果需回写同一任务的执行脉络（而非创建新任务）。
