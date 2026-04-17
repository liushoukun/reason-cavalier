---
name: finishing-a-development-branch
description: 当实现已完成、测试均通过，且需要决定如何集成工作时使用——通过结构化选项指导完成合并、PR 或清理。
---

# 完成开发分支

## 概述

通过呈现清晰选项并执行所选工作流，指导开发工作收尾。

**核心原则：** 验证测试 → 呈现选项 → 执行选择 → 清理。

**开始时宣告：**「我正在使用 finishing-a-development-branch 技能来完成这项工作。」

## 流程

### 第 1 步：验证测试

**在呈现选项之前，验证测试通过：**

```bash
# 运行项目测试套件
npm test / cargo test / pytest / go test ./...
```

**若测试失败：**
```
测试失败（<N> 个）。必须先修复才能继续：

[展示失败信息]

在测试通过前不得进行合并/PR。
```

停止。不要进入第 2 步。

**若测试通过：** 继续第 2 步。

### 第 2 步：确定基础分支

```bash
# 尝试常见基础分支
git merge-base HEAD main 2>/dev/null || git merge-base HEAD master 2>/dev/null
```

或询问：「此分支从 main 分出——是否正确？」

### 第 3 步：呈现选项

**精确**呈现以下 4 个选项：

```
实现已完成。你希望接下来怎么做？

1. 在本地合并回 <base-branch>
2. 推送并创建 Pull Request
3. 保留分支现状（我稍后自行处理）
4. 丢弃此工作

请选择？
```

**不要附加长篇解释** — 保持选项简洁。

### 第 4 步：执行选择

#### 选项 1：本地合并

```bash
git checkout <base-branch>
git pull
git merge <feature-branch>
# 在合并结果上验证测试
<test command>
# 若通过
git branch -d <feature-branch>
```

然后：第 5 步清理 worktree

#### 选项 2：推送并创建 PR

```bash
git push -u origin <feature-branch>
gh pr create --title "<title>" --body "$(cat <<'EOF'
## 摘要
<2-3 条变更要点>

## 测试计划
- [ ] <验证步骤>
EOF
)"
```

然后：第 5 步清理 worktree

#### 选项 3：保持现状

汇报：「保留分支 <name>。Worktree 仍位于 <path>。」

**不要**清理 worktree。

#### 选项 4：丢弃

**先确认：**
```
将永久删除：
- 分支 <name>
- 所有提交：<commit-list>
- 位于 <path> 的 worktree

输入 discard 确认。
```

等待**精确**确认词。

若确认：
```bash
git checkout <base-branch>
git branch -D <feature-branch>
```

然后：第 5 步清理 worktree

### 第 5 步：清理 Worktree

**对选项 1、2、4：**

检查是否在 worktree 中：
```bash
git worktree list | grep $(git branch --show-current)
```

若是：
```bash
git worktree remove <worktree-path>
```

**对选项 3：** 保留 worktree。

## 速查

| 选项 | 合并 | 推送 | 保留 Worktree | 清理分支 |
|------|------|------|---------------|----------|
| 1. 本地合并 | ✓ | - | - | ✓ |
| 2. 创建 PR | - | ✓ | ✓ | - |
| 3. 保持现状 | - | - | ✓ | - |
| 4. 丢弃 | - | - | - | ✓（强制） |

## 常见错误

**跳过测试验证**
- **问题：** 合并坏代码、创建失败 PR  
- **修复：** 提供选项前始终验证测试  

**开放式提问**
- **问题：**「接下来做什么？」→ 含糊  
- **修复：** 精确给出上述 4 个结构化选项  

**自动清理 worktree**
- **问题：** 在仍需要时移除 worktree（选项 2、3）  
- **修复：** 仅对选项 1 和 4 清理  

**丢弃无确认**
- **问题：** 误删工作  
- **修复：** 选项 4 要求输入 `discard` 确认  

## 危险信号

**绝不：**
- 在测试失败时继续  
- 未在合并结果上验证测试就合并  
- 无确认就删除工作  
- 未经明确要求就 force-push  

**务必：**
- 提供选项前先验证测试  
- 精确呈现 4 个选项  
- 选项 4 需打字确认  
- 仅对选项 1 与 4 清理 worktree  

## 集成

**调用方：**
- **subagent-driven-development**（第 7 步）— 全部任务完成后  
- **executing-plans**（第 5 步）— 全部批次完成后  

**搭配：**
- **using-git-worktrees** — 清理由该技能创建的 worktree  
