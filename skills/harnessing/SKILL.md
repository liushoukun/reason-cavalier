---
name: harnessing
description: Harnessing (驾驭化) audits an external application repository for Reason Cavalier Harness adoption readiness using stdlib Python scripts under skills/harnessing/scripts (.ai runtime dirs, Harness-oriented AGENTS.md, persistent docs/), proposes fixes, and can idempotently create blocking `.ai` dirs in one command via `harness_check.py --ensure-blocking-dirs` without user confirmation; other scaffolding and content passes still require explicit user confirmation. Use when an external project wires in or runs against this harness, onboards to Harness engineering, or asks for readiness checks and optional bootstrap.
---

# Harnessing（驾驭化）

> **驾驭化**：把外部工程纳入 Harness 可治理、可续跑、可证据化的落盘与文档约束；本技能在仓库内路径为 `skills/harnessing/`，技能代号为 **`harnessing`**（原 `harness` 目录已迁移至此）。

## 定位（必读）

- **Reason Cavalier 本仓库**是供**外部业务工程**引用的 Harness 能力与约定来源；被检查的通常是**外部项目根目录**，不是「给本仓库装插件」。
- 本技能回答：外部工程是否具备**按 Harness 运转的最小落盘结构**与**代理可读规范**；缺什么、怎么补、是否值得优化。
- **推荐流程**：`harness_check.py` 检测 → 向用户展示结论 → **阻塞项 `.ai` 三件套**（`.ai/`、`.ai/tasks/`、`.ai/workflows/`）可用**一条命令**幂等补齐（见下节 `--ensure-blocking-dirs`，**无需**用户再次确认）→ 其余写盘（`AGENTS.md` / `docs` / `.ai/memory` / `--content-round1` 等）仍须在用户明确同意后再执行 `harness_init.py`（可先 dry-run）→ 最后再跑 `harness_check.py` 复查。

## 0. 自动化脚本（本插件仓库）

路径（相对本仓库根）：`skills/harnessing/scripts/`。无第三方依赖，需 **Python 3**。

| 脚本 | 作用 |
|------|------|
| `harness_check.py` | 检测目录与 `AGENTS.md` / `docs` 入口及内容锚点；可加 `--ensure-blocking-dirs` **单次幂等**创建阻塞项 `.ai` 目录树 |
| `harness_init.py` | 创建目录树、骨架 `AGENTS.md`、`docs/index.md`；可选一轮内容补全（除「仅阻塞 `.ai`」窄豁免外，默认需用户确认后再 `--apply`） |
| `harness_spec.py` | 规则常量（被上述脚本引用，勿单独对用户强调） |

**检测（只读）**（将 `<ROOT>` 换为外部工程根目录的绝对路径）：

```bash
python skills/harnessing/scripts/harness_check.py <ROOT>
python skills/harnessing/scripts/harness_check.py <ROOT> --json <ROOT>/.ai/harness-check.json
```

**一条命令补齐阻塞项 `.ai` 目录树**（创建 `.ai/`、`.ai/tasks/`、`.ai/workflows/` 及 `.gitkeep`，**不含** `.ai/memory`、`AGENTS.md`、`docs/`；幂等、可重复执行）：

```bash
python skills/harnessing/scripts/harness_check.py <ROOT> --ensure-blocking-dirs
```

- 退出码：`0` 无阻塞；`1` 存在阻塞项；`2` 仅有建议/警告（无阻塞）。
- 代理应在执行后**读取终端输出或 `--json`**，再向用户给出结论表。
- **`--json` 路径父目录不存在时会自动创建**（便于写到 `<ROOT>/.ai/harness-check.json`）。

**初始化与一轮内容补全（写盘）**：默认不加 `--apply` 时为 **dry-run**，仅打印将执行的动作。

```bash
python skills/harnessing/scripts/harness_init.py <ROOT>
python skills/harnessing/scripts/harness_init.py <ROOT> --apply --scope all --content-round1
```

- 与 `--ensure-blocking-dirs` **等价写盘范围**的替代写法（同样**无需**为「仅目录」额外索要用户确认）：`python skills/harnessing/scripts/harness_init.py <ROOT> --apply --scope ai-only`（仅 `BLOCKING_DIRS`，不含 `.ai/memory`）。
- `--scope`：`all`（默认，含 `.ai` 阻塞项 + `.ai/memory` 建议项 + `docs/` + 缺省则写 `AGENTS.md` 骨架）、`ai-only`、`agents`、`docs`。
- `--content-round1`：在**不覆盖**既有正文的前提下，对偏弱的 `AGENTS.md` **追加**带标记段落；若缺 `docs/index.md` 则补最小入口。
- `--force-agents`：**慎用**，在 `--scope agents` 或 `all` 时允许覆盖已有 `AGENTS.md`。
- 成功写盘且复查**无阻塞**时进程退出 `0`（仅有警告也视为 `0`，便于链式脚本）。

**门禁（更新）**：

- **窄豁免（无需用户再次确认）**：仅为创建 **`harness_spec.py` 中 `BLOCKING_DIRS`**（`.ai/`、`.ai/tasks/`、`.ai/workflows/`）及占位 `.gitkeep` 时，代理可直接执行 **`harness_check.py <ROOT> --ensure-blocking-dirs`**，或 **`harness_init.py <ROOT> --apply --scope ai-only`**。不得顺带改写 `AGENTS.md`、`docs/` 正文，不得使用 `--force-agents` / `--content-round1` / `--scope all`（除非用户已明确同意相应范围）。
- **其余写盘**：在用户明确说出同意补齐（如「是」「按建议执行」）并尽量限定范围之前，代理**不得**调用会写入 `AGENTS.md`、`docs/`、`.ai/memory` 或覆盖正文的 `harness_init.py --apply` 组合，也不得手工批量改外部仓库。

## 1. 检查清单（与脚本一致；可人工复核）

逐项记录 **OK / 缺失 / 警告**，并附一行证据（路径或「不存在」）。

### 1.1 `.ai/` 运行时目录（Harness 常见必备）

以「是否存在且可被代理与工具稳定写入」为准（具体子目录以当前 Harness 蓝图为锚；缺蓝图时脚本按下述最小集判断）：

- `.ai/` 根目录是否存在。
- `.ai/tasks/`：任务与执行上下文的持久化（如 `task.yaml` 等）。
- `.ai/workflows/`：工作流模板或运行期工作流落盘占位。
- **建议项**：`.ai/memory/`（执行记忆、可消费中间态；与正式 `docs/` 区分）。

若外部工程文档中规定了额外子路径（如审计、策略快照目录），脚本未覆盖时由代理**额外**核对并标为「契约项」或「建议项」。

### 1.2 Harness 向的代理说明（仓库根）

- **规范文件名**：`AGENTS.md`（若目录中存在与 `AGENTS.md` 仅大小写不同的变体，记**警告**并建议统一为 `AGENTS.md`；在大小写不敏感系统上脚本会避免误报）。
- 内容是否**非空**、长度与锚点是否达到脚本阈值（过短或缺少 `.ai` / `tasks` / `workflows` / `docs` / 验证或证据等语义之一组，记**阻塞**）；空壳或一句话占位记为**缺失**。
- 是否与 **Harness 工程**语义一致（能支撑多会话续跑、文档与 `.ai` 分工、门禁/证据等叙述之一即可；不必照抄本仓库全文）。

### 1.3 `docs/` 项目文档持久化区

`docs/` 的定位：**正式知识、归档、文档治理与清理结果的持久化存储**（人类可读、可评审、可版本化），与 `.ai/memory/` 等执行态区分。

检查：

- `docs/` 是否存在（脚本层为建议/警告；代理可结合工程契约升为阻塞）。
- 是否有**可导航入口**（`docs/index.md` 或 `docs/README.md`）。
- 与 Harness 常见约定相关的子树是否在**该外部工程**中有落点。

## 2. 输出格式（给用户）

1. **结论**：该外部工程是否满足「按 Harness 最小可运转」条件；阻塞项与可后补项分开写（与 `harness_check.py` 退出码一致）。
2. **检查结果表**：覆盖 1.1～1.3；优先引用脚本输出或 `--json` 中的 `rows`。
3. **优化建议**：按 **阻塞 / 建议 / 可选** 排序，并说明每项对「续跑、归档、文档清理持久化」的影响。
4. **明确提问**（仅当需要 **超出**「阻塞项 `.ai` 三件套」的补齐时）：`是否需要我继续补齐？请回复「是」并说明范围（例如 .ai/memory、AGENTS.md 骨架、docs 最小入口、`--content-round1` 等）。`

在用户确认前：**不要**调用会写入 `AGENTS.md`、`docs/`、`.ai/memory` 或 `--content-round1` / `--force-agents` 的 `harness_init.py --apply`；**不要**手工写/覆盖 `AGENTS.md`、不要批量改 `docs/`。**允许**直接执行 `harness_check.py <ROOT> --ensure-blocking-dirs`（或等价的 `harness_init.py --apply --scope ai-only`）以创建阻塞项 `.ai` 目录树。

## 3. 用户确认后的「补齐」约定

**阻塞项 `.ai` 三件套**已可由第 0 节命令在无额外确认下完成。以下针对 **`.ai/memory`、`AGENTS.md`、`docs/`、内容轮次** 等超出窄豁免的写盘：

仅在用户明确同意（如「是」「优化」「按建议执行」并限定范围）后执行：

1. 先对外部根目录执行 `harness_init.py <ROOT>`（dry-run），与用户确认范围一致后再 `--apply`。
2. **`.ai/`**：按 `--scope` 创建缺失目录；空目录使用 `.gitkeep`（路径使用正斜杠描述，如 `.ai/workflows/.gitkeep`）。若仅需阻塞子集，优先用 `harness_check.py <ROOT> --ensure-blocking-dirs` 或 `--scope ai-only`。
3. **`AGENTS.md`**：由脚本写入与该外部工程一致的骨架（若存在 `package.json` 则**仅摘录已有 `scripts` 键名**）；**禁止**编造不存在的命令或路径。需要覆盖旧文件时必须有用户明确授权并使用 `--force-agents`。
4. **`docs/`**：在同意范围内补最小入口；**不**擅自大段覆盖已有规格/蓝图类正文。内容仍偏弱时，可再使用 `--content-round1` 追加带标记段落（**一轮**；重复执行会因标记存在而跳过追加）。
5. 结束后给出**变更文件列表**与需人工补全的条目，并再运行 `harness_check.py` 作为证据。

## 4. 自检

- `description` 为第三人称，含能力与触发场景。
- 术语统一：**外部工程**、**Harness**、**持久化**；路径统一正斜杠。
- 脚本与清单冲突时，以 `harness_spec.py` 与脚本实现为准，并**更新本技能**使二者一致。
