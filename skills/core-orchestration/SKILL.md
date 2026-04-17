---
name: core-orchestration
description: Drives task stages via Coordinator semantics—routing workflow skills, evaluating gates G1–G4 from persisted evidence, and choosing recovery (retry, replan, rollback). Use when orchestrating SPEC→PLAN→IMPLEMENT→VERIFY→COMPLETE, resolving gate outcomes, or coordinating Task transitions without embedding storage details.
---

# 核心编排（L1）

## 定位

- **运行时内核技能**：不承载具体业务实现，只做**调度、阶段推进、门禁判定与异常恢复**。
- **统一入口**：由编排视角驱动推进；本技能描述的是**编排侧行为契约**，不替代宿主里的真实状态机实现。
- **依赖边界**：仅依赖 **任务管理** 暴露的统一任务接口（读/写状态、证据、checkpoint）；**不**依赖具体存储介质。

## 对齐模型

- 与项目蓝图一致：`Coordinator` + `Task` + `Workflow`。
- **L2 Workflow 技能**负责阶段能力；本层负责把阶段产出**收敛为可判定证据**，并产出**下一步决策**。
- **门禁外置语义**：`G1~G4` 的绑定规则不在各 Workflow Skill 内实现；由本编排层依据**已持久化的证据**统一判定是否满足过门条件。

## 契约

### 输入（概念）

| 字段 | 说明 |
| --- | --- |
| `task_id` | 当前任务标识 |
| `workflow_template` | 工作流模板或阶段图引用 |
| `policy` | 重试上限、是否允许 replan、回滚策略等 |
| `stage_context` | 当前阶段、上一阶段输出摘要、外部信号（如 CI） |

### 输出（概念）

| 字段 | 说明 |
| --- | --- |
| `next_step_decision` | 继续当前阶段 / 进入下一阶段 / 调用某 Workflow 能力 / 暂停等待输入 |
| `stage_transition` | 合法阶段迁移意图（须由任务层原子落盘） |
| `gate_result` | 对 G1~G4 的判定结论：**pass / fail / insufficient_evidence** |
| `recovery_action` | `retry` → `replan` → `rollback` 之一及参数（与 policy 一致） |

### 证据与追溯

- 关键编排决策必须能追溯到：**读了哪些任务状态/证据**、**判定的依据摘要**、**写回了哪些 `evidence_ref`**。
- **禁止**在无法引用证据引用的情况下声明 gate 为 `pass`。

### 失败策略

1. **retry**：可恢复错误（瞬时 IO、可重试外部调用），在 policy 允许范围内递增退避。
2. **replan**：阶段目标不变但执行路径失效；生成新的计划意图并写入任务证据链。
3. **rollback**：破坏一致性时回到最近 **checkpoint**；回滚结果必须落盘并索引。

## 执行要点

1. **先读任务再决策**：通过任务管理接口加载 `task_state`、证据索引与 checkpoint。
2. **Workflow 路由**：按阶段目标选择 L2 技能；技能**不反向绑定**角色名，仅按契约消费/产出。
3. **质量内建默认**：在 IMPLEMENT 相关阶段，编排层应要求计划中存在可验证的 **SDD + TDD** 证据链占位（具体执行由 L2 技能完成）；**证据不足则 `gate_result` 不得为 pass**（对齐设计文档对 G2 的叙述）。
4. **可恢复**：任何失败路径须写入任务证据链，便于续跑与审计。

## 反模式

- 在 Skill 文本中**硬编码**「某 Workflow 必须通过 G2」之类绑定；应改为「依据已存证据判定 G2」。
- 绕过任务管理接口直接改任意落盘格式（破坏存储适配器边界）。
- 无证据的「完成封账」。

## 相关文档

- 体系目标与分层：`docs/skills/index.md`
