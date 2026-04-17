---
name: harness
description: Audits an external application repository for Reason Cavalier Harness adoption readiness (.ai runtime dirs, Harness-oriented AGENTS.md, persistent docs/ for archival and cleanup), proposes fixes, and applies scaffolding only after explicit user confirmation. Use when an external project wires in or runs against this harness, onboards to Harness engineering, or asks for readiness checks and optional bootstrap.
---

# Harness 外部工程就绪检查与补齐

## 定位（必读）

- **Reason Cavalier 本仓库**是供**外部业务工程**引用的 Harness 能力与约定来源；被检查的通常是**外部项目根目录**，不是「给本仓库装插件」。
- 本技能回答：外部工程是否具备**按 Harness 运转的最小落盘结构**与**代理可读规范**；缺什么、怎么补、是否值得优化。
- 流程：**只读检查 → 结论与建议 → 仅在用户明确要求「优化/补齐」时再改文件或建目录**。

## 1. 检查清单（只读）

逐项记录 **OK / 缺失 / 警告**，并附一行证据（路径或「不存在」）。

### 1.1 `.ai/` 运行时目录（Harness 常见必备）

以「是否存在且可被代理与工具稳定写入」为准（具体子目录以当前 Harness 蓝图为锚；缺蓝图时按下述最小集判断）：

- `.ai/` 根目录是否存在。
- `.ai/tasks/`：任务与执行上下文的持久化（如 `task.yaml` 等）。
- `.ai/workflows/`：工作流模板或运行期工作流落盘占位。
- **建议项**（与多数蓝图一致时标为建议而非阻塞）：`.ai/memory/`（执行记忆、可消费中间态；与正式 `docs/` 区分）。

若外部工程文档中规定了额外子路径（如审计、策略快照目录），一并核对并标为「契约项」或「建议项」。

### 1.2 Harness 向的代理说明（仓库根）

- **规范文件名**：`AGENTS.md`（若仅有 `agents.md` 或其它变体，记**警告**并建议改为 `AGENTS.md`，避免宿主工具识别失败）。勿与误写的 `AGENT.MD` 混淆。
- 内容是否**非空**且对代理**可执行**：工作区规则优先级、任务/工作流与 `.ai/` 的对应关系、验证与证据要求、与 `docs/` 的引用关系等；空壳或一句话占位记为**缺失**。
- 是否与 **Harness 工程**语义一致（能支撑多会话续跑、文档与 `.ai` 分工、门禁/证据等叙述之一即可；不必照抄本仓库全文）。

### 1.3 `docs/` 项目文档持久化区

`docs/` 的定位：**正式知识、归档、文档治理与清理结果的持久化存储**（人类可读、可评审、可版本化），与 `.ai/memory/` 等执行态区分。

检查：

- `docs/` 是否存在。
- 是否有**可导航入口**（如 `docs/index.md` 或等价总览），便于归档归类与后续清理时定位权威文档。
- 与 Harness 常见约定相关的子树是否在**该外部工程**中有落点

## 2. 输出格式（给用户）

1. **结论**：该外部工程是否满足「按 Harness 最小可运转」条件；阻塞项与可后补项分开写。
2. **检查结果表**：覆盖 1.1～1.3 各条。
3. **优化建议**：按 **阻塞 / 建议 / 可选** 排序，并说明每项对「续跑、归档、文档清理持久化」的影响。
4. **明确提问**：`是否需要我按建议自动补齐？请回复「是」并说明范围（例如仅 .ai 目录树、仅 AGENTS.md 骨架、或含 docs 最小入口等）。`

在用户确认前：**不要**创建目录、不要写/覆盖 `AGENTS.md`、不要批量改 `docs/`。

## 3. 用户确认后的「补齐」约定

仅在用户明确同意（如「是」「优化」「按建议执行」并限定范围）后执行：

1. **`.ai/`**：按确认范围创建缺失目录；空目录可用 `.gitkeep`（路径使用正斜杠，如 `.ai/workflows/.gitkeep`）。
2. **`AGENTS.md`**：写入与该外部工程一致的骨架（引用其真实 `package.json`/脚本、已有 `docs/` 链接）；**禁止**编造不存在的命令或路径。
3. **`docs/`**：在同意范围内补最小入口与指向已有章节的链接；**不**擅自大段覆盖已有规格/蓝图类正文。
4. 结束后给出**变更文件列表**与需人工补全的条目。

## 4. 自检

- `description` 为第三人称，含能力与触发场景。
- 术语统一：**外部工程**、**Harness**、**持久化**；路径统一正斜杠。
