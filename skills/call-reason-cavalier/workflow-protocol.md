# Call Reason Cavalier - Workflow 协议规范

本文是 `call-reason-cavalier` 技能执行时使用的 workflow 协议规范。  
本规范为技能自包含协议，不依赖外部 `docs/` 目录。

## 1. 目标与边界

- 目标：用统一 workflow 协议驱动任务阶段推进、门禁判定、恢复动作
- 边界：本协议只定义流程语义与判定口径，不定义具体实现细节

## 2. Workflow 根对象

必须支持以下字段：

- `id`：工作流唯一标识（kebab-case）
- `version`：定义版本
- `name`：工作流名称
- `description`：说明（可选）
- `stages[]`：阶段列表（至少 1 项）
- `gates[]`：门禁定义（可选）

## 3. Stage/Step 协议

### 3.1 Stage

每个阶段包含：

- `id`（必填）
- `key`（必填）
- `title`（必填）
- `purpose`（必填）
- `inputs[]`（可选）
- `outputs[]`（可选）
- `steps[]`（可选）

### 3.2 Step

每个步骤包含：

- `id`（必填）
- `title`（必填）
- `purpose`（必填）
- `agents[]`（选填）
- `inputs[]`（可选）
- `outputs[]`（可选）

## 4. Stage 顺序与 Gate 协议

### 4.1 Stage 顺序

主流程按 `stages[]` 声明顺序执行：

- 默认迁移关系：`stages[i] -> stages[i+1]`
- 不再定义独立 `transitions[]` 连边对象
- 若存在需求变更或异常恢复，使用任务级恢复策略处理，不在同一 workflow 内引入回流边

### 4.2 Gate

每个门禁包含：

- `id`（必填）
- `type`（必填，`STARTUP|IMPLEMENTATION|SUBMISSION|DELIVERY|CUSTOM`）
- `criteria[]`（必填，至少 1 条）
- `notes`（可选）

## 5. 一致性约束

- `stages[]` 必须按执行顺序声明
- `gates[].id` 应全局唯一，供执行期门禁判定引用
- 未通过 schema 校验的 workflow，不得进入执行态

## 6. 技能执行规则

`call-reason-cavalier` 调用时必须遵循：

1. 先选定 workflow（任务显式指定优先，否则按意图匹配）
2. 再校验 workflow schema
3. 按阶段执行并产出证据
4. 按门禁判定是否进入下一顺位阶段或触发恢复（`retry -> replan -> rollback`）
5. 完成后输出交付结论或阻塞结论

## 7. 参考

- `skills/call-reason-cavalier/workflows/dev.workflow.yaml`
