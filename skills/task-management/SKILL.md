---
name: task-management
description: Provides a storage-agnostic task interface—load/save task state, append evidence with stable refs, checkpoints, and restore context—for core orchestration. Use when persisting or recovering Task artifacts, indexing evidence, or implementing adapters over files/DB/KV without embedding orchestration or gate rules.
---

# 任务管理（L1）

## 定位

- **运行时内核技能**：负责任务**状态读取、持久化、checkpoint、证据索引与恢复点**的统一访问面。
- **被调用方**：供 **核心编排** 与经编排授权的 Workflow 使用；**不**负责阶段路由、门禁规则或「是否放行」的业务裁决。
- **存储适配器原则**：具体介质（文件、数据库、KV 等）必须在 **adapter** 内封装；本技能描述的是**接口契约与一致性要求**，不固定目录结构（宿主可约定 `.ai/tasks/` 等，见 Harness 文档）。

## 对齐模型

- 核心对象：**Task**（状态 + 证据 + checkpoint）。
- 与 `Coordinator + Task + Workflow` 一致：任务层**只保证可审计的持久化与可恢复**，不耦合 Workflow 名称。

## 契约

### 输入（概念）

| 字段 | 说明 |
| --- | --- |
| `task_context` | 任务 ID、租户/空间隔离键、并发控制 token（如 etag） |
| `evidence_item` | 证据载荷：命令/输出摘要、产物路径、`gate` 标签（仅作索引，**不做判定**）、时间戳 |
| `checkpoint` | 一致点标签与可选元数据 |
| `storage_adapter` | 注入的存储实现（读/写/列举证据） |

### 输出（概念）

| 字段 | 说明 |
| --- | --- |
| `task_state` | 阶段、状态机字段、最近迁移版本等 |
| `persistence_result` | 成功 / 冲突 / 不可恢复错误 |
| `evidence_ref` | 稳定引用（可用于编排层引用与追溯） |
| `restore_context` | 从 checkpoint 或证据链恢复出的执行续跑上下文 |

### 证据闭环

- 写入证据时：**原子追加**或等价机制，避免半条记录；返回 `evidence_ref`。
- 读取时：支持按 `task_id` 列举、按 ref 定点取、按时间/阶段过滤（能力以 adapter 为准，但接口语义保持一致）。
- **证据索引**与正文分离时，须保证 ref 可解析到实际内容或明确 `missing`。

### 失败策略

- **冲突**：返回冲突，由编排层决定 retry（带新 token）或 replan。
- **损坏**：返回明确错误类型，**不**静默修补；由编排层选择 rollback 到 checkpoint。
- **部分写**：禁止；使用事务或写临时再提交等模式由 adapter 保证。

## 执行要点

1. **幂等与版本**：状态写建议带版本或 CAS，支持编排层重试。
2. **checkpoint**：在编排层请求时创建；记录阶段、关键 ref 列表、可选摘要哈希。
3. **不内嵌门禁**：不在本层实现 G1~G4 规则；仅存储与检索供编排层消费的证据。
4. **可扩展**：新增字段须**向后兼容**（可选字段、版本号），避免破坏已有流程语义。

## 反模式

- 在任务管理逻辑里写死「某阶段必须过 Gx」。
- 让 Workflow 直接绕过统一接口写散落文件且不可索引。
- 无 ref、无时间戳的「口头完成」式记录。

## 相关文档

- 体系目标与分层：`docs/skills/index.md`
