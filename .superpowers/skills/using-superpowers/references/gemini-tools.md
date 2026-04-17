# Gemini CLI 工具映射

技能正文使用 Claude Code 的工具名。当你在技能中遇到下列名称时，请使用你平台上的等价工具：

| 技能中的引用 | Gemini CLI 等价 |
|-------------|----------------|
| `Read`（读文件） | `read_file` |
| `Write`（创建文件） | `write_file` |
| `Edit`（编辑文件） | `replace` |
| `Bash`（运行命令） | `run_shell_command` |
| `Grep`（搜索文件内容） | `grep_search` |
| `Glob`（按文件名搜索） | `glob` |
| `TodoWrite`（任务跟踪） | `write_todos` |
| `Skill` 工具（加载技能） | `activate_skill` |
| `WebSearch` | `google_web_search` |
| `WebFetch` | `web_fetch` |
| `Task` 工具（派发子代理） | 无等价——Gemini CLI 不支持子代理 |

## 无子代理支持

Gemini CLI 没有与 Claude Code `Task` 工具等价的机制。依赖子代理派发的技能（`subagent-driven-development`、`dispatching-parallel-agents`）将回退为通过 `executing-plans` 在单会话中执行。

## 其他 Gemini CLI 工具

下列工具在 Gemini CLI 中可用，但 Claude Code 无直接对应：

| 工具 | 用途 |
|------|------|
| `list_directory` | 列出文件与子目录 |
| `save_memory` | 将事实持久化到跨会话的 GEMINI.md |
| `ask_user` | 向用户请求结构化输入 |
| `tracker_create_task` | 丰富任务管理（创建、更新、列表、可视化） |
| `enter_plan_mode` / `exit_plan_mode` | 在修改前切换到只读调研模式 |
