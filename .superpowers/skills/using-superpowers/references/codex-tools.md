# Codex 工具映射

技能正文使用 Claude Code 的工具名。当你在技能中遇到下列名称时，请使用你平台上的等价工具：

| 技能中的引用 | Codex 等价 |
|-------------|-----------|
| `Task` 工具（派发子代理） | `spawn_agent`（参见下文「命名代理派发」） |
| 多次并行 `Task` 调用 | 多次 `spawn_agent` 调用 |
| 任务返回结果 | `wait` |
| 任务自动完成 | `close_agent` 释放槽位 |
| `TodoWrite`（任务跟踪） | `update_plan` |
| `Skill` 工具（加载技能） | 技能原生加载——直接遵循说明即可 |
| `Read`、`Write`、`Edit`（文件） | 使用你环境原生的文件工具 |
| `Bash`（运行命令） | 使用你环境原生的 shell 工具 |

## 子代理派发需要多代理支持

在 Codex 配置（`~/.codex/config.toml`）中加入：

```toml
[features]
multi_agent = true
```

以启用 `spawn_agent`、`wait`、`close_agent`，供 `dispatching-parallel-agents`、`subagent-driven-development` 等技能使用。

## 命名代理派发

Claude Code 技能会引用诸如 `superpowers:code-reviewer` 的命名代理类型。  
Codex 没有命名代理注册表——`spawn_agent` 使用内置角色（`default`、`explorer`、`worker`）创建通用代理。

当技能要求派发命名代理类型时：

1. 找到代理的提示文件（例如 `agents/code-reviewer.md` 或技能内模板如 `code-quality-reviewer-prompt.md`）  
2. 读取提示内容  
3. 填写模板占位符（`{BASE_SHA}`、`{WHAT_WAS_IMPLEMENTED}` 等）  
4. 以填充后的内容作为 `message` 派发 `worker` 代理  

| 技能中的指令 | Codex 等价 |
|-------------|-----------|
| `Task tool (superpowers:code-reviewer)` | `spawn_agent(agent_type="worker", message=...)`，message 为 `code-reviewer.md` 内容 |
| `Task tool (general-purpose)` 与行内提示 | `spawn_agent(message=...)`，message 与提示相同 |

### 消息框架

`message` 参数是用户级输入，不是系统提示。为最大化遵循度，建议结构：

```
Your task is to perform the following. Follow the instructions below exactly.

<agent-instructions>
[来自代理 .md 文件的已填充提示内容]
</agent-instructions>

Execute this now. Output ONLY the structured response following the format
specified in the instructions above.
```

- 使用任务委派式措辞（「Your task is...」）而非人设式（「You are...」）  
- 用 XML 标签包裹指令——模型通常将带标签块视为权威  
- 以明确执行指令结尾，避免模型只总结指令而不执行  

### 何时可移除此变通

该做法用于弥补 Codex 插件系统尚不支持 `plugin.json` 中 `agents` 字段。当 `RawPluginManifest` 支持 `agents` 后，插件可像现有 `skills/` 一样 symlink 到 `agents/`，技能即可直接派发命名代理类型。

## 环境检测

创建 worktree 或结束分支的技能应先以只读 git 命令检测环境：

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
BRANCH=$(git branch --show-current)
```

- `GIT_DIR != GIT_COMMON` → 已在链接的 worktree 中（跳过创建）  
- `BRANCH` 为空 → 分离 HEAD（沙箱中无法从该状态分支/推送/开 PR）  

各技能如何解读这些信号，见 `using-git-worktrees` 与 `finishing-a-development-branch` 的相关步骤。

## Codex App 收尾

当沙箱阻止分支/推送操作（外部托管 worktree 中的分离 HEAD）时，代理应提交全部工作并提示用户使用 App 原生控件：

- **「Create branch」**——命名分支后，通过 App UI 进行提交/推送/PR  
- **「Hand off to local」**——将工作转移到用户本地检出  

代理仍可运行测试、暂存文件，并输出建议的分支名、提交说明与 PR 描述供用户复制。
