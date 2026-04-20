---
name: rc.init
description: 插件启动准备：按固定顺序依次加载并执行多个初始化技能；当前第 1 步为 harnessing（外部工程 Harness 就绪检测与窄豁免补齐）。
---

你正在执行 **Reason Cavalier：初始化（init）**。目标是完成**插件侧约定的启动准备**，通过**严格顺序**的多技能链执行；**未完成前一步不得进入下一步**。

## 0. 执行顺序（总览）

| 顺序 | 技能代号 | 技能路径（相对本插件仓库根） | 说明 |
|------|-----------|------------------------------|------|
| 1 | `harnessing` | `skills/harnessing/SKILL.md` | 对外部工程根目录做 Harness 就绪检测；窄豁免下可幂等补齐 `.ai` 阻塞三件套 |
| 2+ | *预留* | （后续版本在此表追加） | 在未声明前**不得**自行发明「第 2 步技能」或跳过表内顺序 |

**硬性规则**：每一步必须先 **Read** 对应 `SKILL.md` 全文并按该技能执行；本 Command 仅编排顺序与共用输入，**不替代**技能正文中的门禁与写盘约定。

## 1. 共用输入

### 1.1 外部工程根 `<ROOT>`

- 若用户消息中已给出**绝对路径**的工程根目录，以其为 `<ROOT>`。
- 否则：将**当前 Cursor 工作区根目录**（用户打开的单根或多根工作区中，用户明示的那一个；单根则即该根）作为 `<ROOT>`，并在回复中写明假定路径请用户确认。
- `<ROOT>` 必须指向**被治理的业务工程**（外部应用仓库），不是本插件 `reason-cavalier` 仓库根，除非用户明确要对插件仓库自身做 harness 审计。

### 1.2 插件仓库根 `PLUGIN_ROOT`（用于运行脚本）

`skills/harnessing/scripts/*.py` 的路径**相对 Reason Cavalier 插件安装目录**（本仓库根），与 `<ROOT>` 无关。执行检测/补齐命令时：

- 先将 shell 当前目录切换到 **`PLUGIN_ROOT`**（含 `skills/`、`commands/` 的该插件根）；或
- 使用 `PLUGIN_ROOT` 的绝对路径调用解释器与脚本，例如：  
  `python "<PLUGIN_ROOT>/skills/harnessing/scripts/harness_check.py" <ROOT>`

定位 `PLUGIN_ROOT`：本文件位于 `<PLUGIN_ROOT>/commands/init.md`；从已打开的该文件路径向上解析父目录即可。

## 2. 第 1 步：`harnessing`

1. **Read** `skills/harnessing/SKILL.md`（本插件仓库内路径）。
2. 按该技能「0. 自动化脚本」与「门禁」执行对 `<ROOT>` 的操作，至少包括：
   - 在 **`PLUGIN_ROOT`** 下执行只读检测（`<ROOT>` 为被检查的外部工程绝对路径）：
     ```bash
     python skills/harnessing/scripts/harness_check.py <ROOT>
     ```
   - 根据技能窄豁免约定，在需要且技能允许时执行：
     ```bash
     python skills/harnessing/scripts/harness_check.py <ROOT> --ensure-blocking-dirs
     ```
   - 可选：按技能说明将结果写入 `<ROOT>/.ai/harness-check.json`（`--json`）。
3. 按 `harnessing` 技能第 2 节「输出格式（给用户）」向用户汇报：**结论**、**检查结果表**、**优化建议**；对超出窄豁免的写盘**必须先征得用户明确同意**后再执行 `harness_init.py` 等（详见该技能）。

## 3. 第 2 步及以后

- 当本文件「0. 执行顺序」表中**尚未**列出第 2 步技能时：在完成第 1 步汇报后，向用户说明「初始化链当前仅包含 harnessing；后续步骤将在插件更新中加入」，**结束**本次 init。
- 当表中已追加第 2 行及以后：对上一步输出与用户状态做必要确认后，**从第 2 行起依次** Read 并执行对应 `SKILL.md`，规则同第 1 步。

## 4. 完成后向用户汇报

- 已执行的步骤序号与技能代号
- `PLUGIN_ROOT` 与 `<ROOT>` 最终采用的路径
- `harnessing` 的退出码含义（若已运行脚本）与是否已执行 `--ensure-blocking-dirs`
- 若初始化链在表内已无后续步骤：明确告知「当前链已跑完」
