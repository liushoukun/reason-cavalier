# Workflow 定义（简化版）

本文定义 workflow 的最小机读结构。  
人读方法正文见 [`SDD/SDD.md`](SDD/SDD.md)，机读校验规则见 [`workflow-definition.schema.json`](workflow-definition.schema.json)。

---

## 1. 设计目标

- 使用统一最小模型描述流程语义，不混入执行器细节
- 保留门禁抽象，保证阶段推进可被机器校验
- 删除历史扩展字段，降低维护与理解成本

---

## 2. 根对象（均衡核心）

根对象仅保留以下字段：

| 字段 | 必填 | 说明 |
|------|------|------|
| `id` | 是 | 工作流唯一标识（kebab-case） |
| `version` | 是 | 定义版本 |
| `name` | 是 | 人类可读名称 |
| `description` | 否 | 工作流总体说明 |
| `stages[]` | 是 | 阶段定义数组，至少 1 项 |
| `transitions[]` | 否 | 阶段迁移规则 |
| `gates[]` | 否 | 全局门禁定义，供迁移引用 |

---

## 3. Stage 定义

| 字段 | 必填 | 说明 |
|------|------|------|
| `id` | 是 | 阶段唯一标识（kebab-case） |
| `key` | 是 | 阶段键（用于迁移引用） |
| `title` | 是 | 阶段显示名 |
| `purpose` | 是 | 阶段目标 |
| `inputs[]` | 否 | 阶段输入项 |
| `outputs[]` | 否 | 阶段产出项 |
| `steps[]` | 否 | 阶段内步骤列表 |

### 3.1 Step 定义

| 字段 | 必填 | 说明 |
|------|------|------|
| `id` | 是 | 步骤唯一标识（kebab-case） |
| `title` | 是 | 步骤显示名 |
| `purpose` | 是 | 步骤目标 |
| `inputs[]` | 否 | 步骤输入项 |
| `outputs[]` | 否 | 步骤产出项 |

---

## 4. Transition 与 Gate

### 4.1 transitions[]

每条迁移包含：

- `from_key`：起始阶段 key
- `to_key`：目标阶段 key
- `gate_id`（可选）：引用 `gates[].id`
- `gate_note`（可选）：人读门禁说明

### 4.2 gates[]

每个门禁包含：

- `id`：门禁标识（如 `G1`）
- `type`：门禁类型（`STARTUP` / `IMPLEMENTATION` / `SUBMISSION` / `DELIVERY` / `CUSTOM`）
- `criteria[]`：门禁条件列表，至少 1 条

---

## 5. 约束说明

- `transitions[].from_key` 与 `to_key` 必须引用已定义的 `stages[].key`
- `transitions[].gate_id` 若存在，必须引用已定义的 `gates[].id`
- 文档字段仅用于说明，不参与流程控制
