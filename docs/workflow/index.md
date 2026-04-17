# Workflow 核心概念

Workflow 是任务推进的标准化流程契约，用于在统一语义下约束流程结构、阶段迁移和判定口径，并提供稳定的机读定义基础。

Workflow 只定义流程语义，不承担运行时执行职责：

- 定义流程应如何推进
- 不定义执行主体调度策略
- 不承载运行时状态持久化

本文采用单一核心建模对象 `stages[]`：阶段按声明顺序形成主流程；门禁作为阶段内约束，通过 `gates[]` 与阶段绑定，不作为顶层独立集合。

---

## 1. 术语与模型

### 1.1 术语定义

在本规范中，**门禁即前置要求**，为同一约束在不同语境下的命名：

- 从流程控制语境，称为门禁（`gate item`）
- 从阶段准入语境，称为前置要求

统一规则：**进入阶段前必须通过该阶段门禁**。阶段入口约束由 `stage.gates[].entryCriteria[]` 表达。

### 1.2 stages（阶段）

`stages[]` 是流程节点集合，描述“做什么”，并承载阶段内结构与约束。

每个 `stage` 必须包含：

- `name`：阶段唯一标识（建议 kebab-case）
- `title`：阶段显示名
- `purpose`：阶段目标
- `gates[]`：阶段门禁集合（可定义多个门禁项）

可选字段：

- `inputs[]`：阶段输入
- `outputs[]`：阶段产出
- `steps[]`：阶段内步骤
- `agents[]`：阶段执行主体（用于编排提示）

### 1.3 gates（阶段门禁集合）

`stage.gates[]` 定义阶段的进入与离开条件。每个门禁项建议包含：

- `type`：门禁类型（`STARTUP` / `IMPLEMENTATION` / `SUBMISSION` / `DELIVERY` / `CUSTOM`）
- `entryCriteria[]`：阶段进入条件（前置要求，至少 1 条）
- `exitCriteria[]`：阶段离开条件（迁移要求，至少 1 条）

统一判定语义：

- `PASS`：允许迁移
- `SOFT_FAIL`：允许迁移并记录风险
- `HARD_FAIL`：禁止迁移并进入阻断/恢复处理

---

## 2. 流程推进规则（DAG）

Workflow 主流程由 `stages[]` 顺序直接确定：`stages[i] -> stages[i+1]`。

约束如下：

- `stages[]` 必须按执行顺序声明，且至少包含 1 个阶段
- 进入 `stages[i]` 前，必须满足该阶段所有必需门禁项的 `entryCriteria[]`
- 从 `stages[i]` 迁移到 `stages[i+1]` 前，必须满足该阶段所有必需门禁项的 `exitCriteria[]`
- 流程图保持 DAG 语义（无环），确保推进可预测、可恢复

```mermaid
flowchart LR
  SPEC[Spec] -->|G1| PLAN[Plan]
  PLAN -->|G2| IMPLEMENT[Implement]
  IMPLEMENT -->|G3| VERIFY[Verify]
  VERIFY -->|G4| COMPLETE[Complete]
```

需求变更通过新一轮 workflow（或新任务）重新进入上游阶段处理，不在单个 workflow 内引入回流边。

---

## 3. 运行边界

- `Workflow`：定义阶段与门禁语义
- `Coordinator`：按 `stages[]` 顺序推进，并执行阶段入口/出口门禁判定
- `Task`：保存运行时状态、证据和 checkpoint，不定义流程结构

---

## 4. 机读定义对齐

语义文档与机读定义保持一致：

- 字段说明：`docs/workflow/workflow-definition.md`
- Schema 校验：`docs/workflow/workflow-definition.schema.json`
- 方法正文：`docs/workflow/SDD/SDD.md`

最小根对象包含：

- `id`
- `version`
- `name`
- `stages[]`
