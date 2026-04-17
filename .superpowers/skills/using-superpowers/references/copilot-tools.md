# Copilot CLI 工具映射

技能正文使用 Claude Code 的工具名。当你在技能中遇到下列名称时，请使用你平台上的等价工具：

| 技能中的引用 | Copilot CLI 等价 |
|-------------|------------------|
| `Read`（读文件） | `view` |
| `Write`（创建文件） | `create` |
| `Edit`（编辑文件） | `edit` |
| `Bash`（运行命令） | `bash` |
| `Grep`（搜索文件内容） | `grep` |
| `Glob`（按文件名搜索） | `glob` |
| `Skill` 工具（加载技能） | `skill` |
| `WebFetch` | `web_fetch` |
| `Task` 工具（派发子代理） | `task`（参见下文「代理类型」） |
| 多次并行 `Task` 调用 | 多次 `task` 调用 |
| 任务状态/输出 | `read_agent`、`list_agents` |
| `TodoWrite`（任务跟踪） | 使用内置 `todos` 表的 `sql` |
| `WebSearch` | 无直接等价——可用 `web_fetch` 访问搜索引擎 URL |
| `EnterPlanMode` / `ExitPlanMode` | 无等价——留在主会话中 |

## 代理类型

Copilot CLI 的 `task` 工具接受 `agent_type` 参数：

| Claude Code 代理 | Copilot CLI 等价 |
|-----------------|------------------|
| `general-purpose` | `"general-purpose"` |
| `Explore` | `"explore"` |
| 命名插件代理（如 `superpowers:code-reviewer`） | 从已安装插件自动发现 |

## 异步 Shell 会话

Copilot CLI 支持持久异步 shell 会话，Claude Code 无直接等价：

| 工具 | 用途 |
|------|------|
| `async: true` 的 `bash` | 在后台启动长时间运行的命令 |
| `write_bash` | 向正在运行的异步会话发送输入 |
| `read_bash` | 读取异步会话输出 |
| `stop_bash` | 终止异步会话 |
| `list_bash` | 列出所有活动 shell 会话 |

## 其他 Copilot CLI 工具

| 工具 | 用途 |
|------|------|
| `store_memory` | 持久保存关于代码库的事实供未来会话使用 |
| `report_intent` | 用当前意图更新 UI 状态行 |
| `sql` | 查询会话的 SQLite 数据库（待办、元数据等） |
| `fetch_copilot_cli_documentation` | 查阅 Copilot CLI 文档 |
| GitHub MCP 工具（`github-mcp-server-*`） | 原生 GitHub API（议题、PR、代码搜索等） |
