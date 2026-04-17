---
name: call-reason-cavalier
description: 统一编排 Reason Cavalier 任务生命周期。SKILL 保留简要执行说明，workflow 协议细节见技能内独立规范文档。
---

# Call Reason Cavalier

## 用途

当请求满足以下任一条件时使用本技能：

- 需要分阶段推进任务
- 需要门禁判定与证据约束
- 需要失败恢复（`retry/replan/rollback`）

## 最小执行流程

1. 绑定 `task_id` 并选择 workflow
2. 按 schema 校验 workflow
3. 执行当前阶段，记录输入/产出与证据
4. 执行门禁判定，决定迁移或恢复
5. 输出 `complete` 或 `blocked` 结论

## 强制约束

- 禁止跳过 workflow 校验直接执行
- 禁止无证据通过门禁
- 禁止绕过 coordinator 直接推进阶段
- 恢复顺序固定：`retry -> replan -> rollback`

## 协议规范（详细）

详细 workflow 字段、约束、Stage/Step/Transition/Gate 定义请遵循：

- `skills/call-reason-cavalier/workflow-protocol.md`

## 示例模板

参考：

- `skills/call-reason-cavalier/workflows/dev.workflow.yaml`
