# 可视化伴侣指南

基于浏览器的可视化头脑风暴伴侣，用于展示线框图、示意图与选项。

## 何时使用

**逐题决策，而非按会话一刀切。** 检验标准：**用户是「看到」比「读到」更能理解吗？**

**用浏览器** — 当内容本身是视觉的：

- **UI 线框** — 线框、布局、导航结构、组件设计  
- **架构图** — 系统组件、数据流、关系图  
- **并排视觉对比** — 两种布局、配色、设计方向  
- **视觉打磨** — 关于观感、间距、视觉层级的问题  
- **空间关系** — 状态机、流程图、ER 图等以图呈现  

**用终端** — 当内容是文本或表格：

- **需求与范围** — 「X 在此语境指什么？」「哪些功能在范围内？」  
- **概念性 A/B/C** — 用文字描述的路径选择  
- **利弊列表** — 对比表  
- **技术决策** — API 设计、数据建模、架构取舍  
- **澄清问题** — 答案是文字而非视觉偏好  

*关于* UI 的问题**不自动**等于视觉问题。「想要哪种向导？」是概念题 —— 用终端。「这几种向导布局哪个更对？」是视觉题 —— 用浏览器。

## 原理

服务器监视目录中的 HTML 文件，将**最新**文件提供给浏览器。你把 HTML 写到 `screen_dir`，用户在浏览器查看并可点击选择；选择记录到 `state_dir/events`，你在下一轮读取。

**内容片段 vs 完整文档：** 若 HTML 以 `<!DOCTYPE` 或 `<html` 开头，服务器原样提供（仅注入辅助脚本）。否则服务器自动用 frame 模板包装 —— 加页眉、主题 CSS、选择指示与交互基础设施。**默认写内容片段。** 仅当你需要完全控制页面时才写完整文档。

## 启动会话

```bash
scripts/start-server.sh --project-dir /path/to/project
```

响应含 `port`、`url`、`screen_dir`、`state_dir`。保存 `screen_dir` 与 `state_dir`，请用户打开 URL。

**查找连接信息：** 启动 JSON 写入 `$STATE_DIR/server-info`。若服务器在后台启动且未捕获 stdout，读该文件获取 URL 与端口。使用 `--project-dir` 时，在 `<project>/.superpowers/brainstorm/` 下查找会话目录。

**注意：** 传入项目根作为 `--project-dir`，使 mockup 持久在 `.superpowers/brainstorm/` 并可在服务器重启后保留。不传则文件在 `/tmp` 可能被清理。若尚未忽略，提醒用户将 `.superpowers/` 加入 `.gitignore`。

**按平台启动：**  
- **Claude Code（macOS/Linux）：** 默认脚本会自行后台化服务器。  
- **Claude Code（Windows）：** 脚本以前台方式阻塞；调用 Bash 工具时设 `run_in_background: true`，下一轮读 `$STATE_DIR/server-info`。  
- **Codex：** 后台进程会被收割；脚本检测 `CODEX_CI` 并切前台；正常运行即可。  
- **Gemini CLI：** 使用 `--foreground` 且 shell 工具 `is_background: true`。  
- **其他环境：** 服务器必须在多轮对话间保持存活；若环境会收割 detached 进程，用 `--foreground` 加平台后台机制。

若 URL 在远程/容器内浏览器不可达，可绑定 `0.0.0.0` 并用 `--url-host` 控制打印在 JSON 里的主机名。

## 循环

1. **确认服务器存活**，然后向 `screen_dir` **写入新 HTML 文件**：  
   - 每次写入前确认 `$STATE_DIR/server-info` 存在；若不存在或存在 `$STATE_DIR/server-stopped`，服务器已退出 —— 用 `start-server.sh` 重启。无活动约 30 分钟服务器自动退出。  
   - 语义化文件名：`platform.html`、`layout.html`  
   - **永不复用文件名** —— 每屏新文件  
   - 使用 Write 工具 —— **不要用 cat/heredoc**（污染终端）  
   - 服务器按修改时间提供最新文件  

2. **告诉用户期待什么并结束本轮：**  
   - 每步提醒 URL（不只第一步）  
   - 简短文字描述屏幕内容  
   - 请用户在**终端**回应：「请查看并告诉我想法；可点击选择。」  

3. **下一轮** — 用户已在终端回应后：  
   - 若存在则读 `$STATE_DIR/events`（浏览器点击/选择的 JSONL）  
   - 与终端文字合并理解  
   - **终端消息是主反馈**；`events` 提供结构化交互数据  

4. **迭代或推进** — 若反馈要求改当前屏，写新文件（如 `layout-v2.html`）。仅当当前步骤被确认后再进入下一问题。  

5. **回到纯终端时卸载视觉** — 下一步不需要浏览器时，推一屏等待页，避免用户盯着已过时选择：  

   ```html
   <div style="display:flex;align-items:center;justify-content:center;min-height:60vh">
     <p class="subtitle">Continuing in terminal...</p>
   </div>
   ```  

   可将文案改为中文：「继续在终端中进行…」  

6. 重复直至完成。

## 写内容片段

只写放入页面的主体；frame 模板自动加页眉、主题、选择条等。

最小示例（选项 A/B）见英文版同文件；结构为 `h2` + `.subtitle` + `.options` > `.option[data-choice][onclick=toggleSelect(this)]`。

无需手写 `<html>`/大量 CSS/`<script>` —— 由服务器与模板提供。

## 可用 CSS 类（摘要）

- **`.options` / `.option`** — A/B/C；多选用容器属性 `data-multiselect`  
- **`.cards` / `.card`** — 卡片式视觉设计  
- **`.mockup` / `.mockup-header` / `.mockup-body`** — 预览容器  
- **`.split`** — 左右并排  
- **`.pros-cons`** — 利弊两栏  
- **`.mock-nav`、`.mock-sidebar`、`.mock-content`、`.mock-button`、`.mock-input`、`.placeholder`** — 线框积木  
- **排版：** `h2`、`h3`、`.subtitle`、`.section`、`.label`  

完整 HTML/CSS 参考仍以英文仓库 `skills/brainstorming/scripts/frame-template.html` 为准。

## 浏览器事件格式

`$STATE_DIR/events` 为 JSONL，每行一个对象；推新屏时文件会清空。字段含 `type`、`choice`、`text`、`timestamp` 等。若文件不存在，表示用户未在浏览器交互 —— 仅用终端文字。

## 设计建议

- **保真度匹配问题** — 布局用线框，打磨问题再提高完成度  
- **每页写清在问什么**  
- **确认后再进入下一题**  
- **每屏最多 2–4 个选项**  
- **该用真实内容时用真实内容**（如作品集用真实图）  
- **mockup 保持简单** — 聚焦结构与布局  

## 命名

语义名；永不复用；迭代用 `layout-v2.html` 等后缀；服务器以最新修改时间为准。

## 清理

```bash
scripts/stop-server.sh $SESSION_DIR
```

使用 `--project-dir` 时，文件保留在 `.superpowers/brainstorm/` 供日后参考；仅 `/tmp` 会话在 stop 时删除。

## 参考

- 框架模板（CSS）：`skills/brainstorming/scripts/frame-template.html`  
- 客户端脚本：`skills/brainstorming/scripts/helper.js`  
