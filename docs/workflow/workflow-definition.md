# 工作流定义（YAML）与 Schema

本文定义 workflow 的机读结构，口径与 [`index.md`](index.md) 保持一致。  
人读方法正文见 [`SDD/SDD.md`](SDD/SDD.md)，机读校验规则见 [`workflow-definition.schema.json`](workflow-definition.schema.json)。

---

## 1. 定义原则

- `Workflow` 负责流程语义，不负责执行与存储
- 模板稳定优先：运行期不改写阶段语义
- 证据驱动门禁：门禁结果必须可追溯到交付物/证据
- 兼容优先：Schema 保留历史字段，同时给出新字段规范

---

## 2. 根对象字段

| 字段 | 必填 | 说明 |
|------|------|------|
| `id` / `version` / `name` | 是 | 工作流标识与版本 |
| `description` / `methodology` / `documentation` | 否 | 说明与文档链接 |
| `template_id` | 否（建议） | 模板标识，建议与运行期模板目录对齐 |
| `stages[]` | 是 | 阶段定义数组 |
| `transitions[]` | 否 | 主链路阶段迁移与门禁 |
| `exceptions[]` | 否 | 异常回流路径 |
| `gates[]` | 否（建议） | 全局门禁定义（如 G1~G4） |
| `required_artifacts[]` | 否（建议） | 全局必备交付物 |
| `fallback_policy` | 否（建议） | 失败回退策略（`retry/replan/rollback`） |
| `agent_roles[]` / `agent_pipeline` | 否 | Agent 角色对齐与调用拓扑 |

---

## 3. Stage 字段

| 字段 | 必填 | 说明 |
|------|------|------|
| `id` / `key` / `title` / `purpose` / `exit_criteria` | 是 | 阶段标识、键、名称、目的、出口条件 |
| `entry_criteria` | 否（建议） | 阶段进入条件 |
| `inputs[]` | 否 | 阶段依赖输入 |
| `outputs[]` | 否 | 阶段约定产出（非 stdout） |
| `artifacts[]` | 否（兼容） | 旧字段；新定义优先 `outputs` |
| `agents[]` | 否 | 参与阶段的 Agent（可带 `role`） |
| `steps[]` | 否 | 阶段内子步骤 |
| `next_step_decision` | 否（建议） | 阶段结束后建议动作 |
| `principles[]` / `activities[]` | 否 | 阶段补充说明 |

`next_step_decision` 推荐值：

- `CONTINUE`
- `ASK_USER`
- `DISPATCH_AGENT`
- `REPLAN`
- `STOP`

---

## 4. Gate 与 Transition

支持两种表达方式：

1. **迁移内联门禁**：`transitions[].gate` 直接写门禁要点  
2. **全局门禁对象**：`gates[]` 定义 `id/type/criteria`，迁移按 `gate_id` 引用

推荐同时保留迁移文本门禁与全局门禁对象，便于人读与机判共存。

---

## 5. Fallback Policy

`fallback_policy` 推荐结构：

- `retry.max_attempts`
- `retry.backoff`
- `replan.target_stage`
- `rollback.strategy`

其语义需与 `index.md` 的恢复模型一致：`retry -> replan -> rollback`。

---

## 6. 示例与校验

- 示例文件：`docs/workflow/SDD/sdd.workflow.yaml`
- 校验文件：`docs/workflow/workflow-definition.schema.json`

校验方式（示例）：

```bash
npx ajv-cli validate -s docs/workflow/workflow-definition.schema.json -d docs/workflow/SDD/sdd.workflow.yaml
```
