# Reason Cavalier（本仓库）代理说明

本仓库是 **Reason Cavalier Harness** 能力与约定的来源之一（Cursor / Claude Code / Codex 等宿主可引用其中的 skills、commands、hooks）。在此工作时，请把 **`docs/`** 视为正式、可评审的知识与蓝图；执行态与任务持久化在消费该 Harness 的工程里通常落在 **`.ai/tasks/`**、**`.ai/workflows/`**（以及建议的 **`.ai/memory/`**），与本仓库的 `docs/` 分工一致。

## 优先阅读

- 架构与状态机、门禁语义：[`docs/index.md`](docs/index.md)
- 任务驱动与 Coordinator 协议：[`skills/call-reason-cavalier/SKILL.md`](skills/call-reason-cavalier/SKILL.md)（加载后按其指引继续读 `workflow-protocol` / `task-protocol`）
- **外部业务工程**接入 Harness 的就绪检查与可选脚手架：**Harnessing（驾驭化）** [`skills/harnessing/SKILL.md`](skills/harnessing/SKILL.md)；检测脚本为 `skills/harnessing/scripts/harness_check.py`；除技能中「仅阻塞 `.ai` 目录」窄豁免外，其余写盘前务必 dry-run 且需用户明确同意后再使用 `harness_init.py --apply`。

## 工作方式（与 Harness 对齐）

1. **阶段与 workflow**：推进、回流路径以 workflow 模板与策略为准，不在此随意发明隐式阶段。
2. **证据与验证**：关键结论与门禁结果应能指向可追溯材料；无证据则不应宣称阶段已完成或通过验证。
3. **续跑与一致性**：涉及 `task_id`、checkpoint、策略快照时，以协议与 `docs/` 中的边界说明为准，避免与正式文档语义冲突。

若用户指令与本文件或 `docs/` 冲突，以用户当前任务约束为准，并在必要时提示风险。
