---
name: requesting-code-review
description: 在完成任务、实现主要功能或合并前验证工作是否符合要求时使用。
---

# 请求代码评审

派发 superpowers:code-reviewer 子代理，在问题扩散前拦截。评审者获得**精心裁剪**的评估上下文——永远不要塞入你完整会话历史。这让评审专注工作产物而非你的思路，也为你保留上下文以继续工作。

**核心原则：** 早评审、常评审。

## 何时请求评审

**必须：**
- subagent-driven-development 中每个任务之后  
- 完成主要功能之后  
- 合并到 main 之前  

**可选但很有价值：**
- 卡住时（新视角）  
- 重构前（基线检查）  
- 修复复杂 bug 之后  

## 如何请求

**1. 获取 git SHA：**
```bash
BASE_SHA=$(git rev-parse HEAD~1)  # 或 origin/main
HEAD_SHA=$(git rev-parse HEAD)
```

**2. 派发 code-reviewer 子代理：**

使用 Task 工具，类型为 superpowers:code-reviewer，按 `code-reviewer.md` 模板填写。

**占位符：**
- `{WHAT_WAS_IMPLEMENTED}` — 你刚构建的内容  
- `{PLAN_OR_REQUIREMENTS}` — 应该达成什么  
- `{BASE_SHA}` — 起始提交  
- `{HEAD_SHA}` — 结束提交  
- `{DESCRIPTION}` — 简短摘要  

**3. 处理反馈：**
- 严重问题立即修  
- 重要问题在继续前修  
- 轻微问题可记下稍后  
- 若评审错误则反驳（附理由）  

## 示例

```
[刚完成任务 2：添加校验函数]

你：在继续前先请求代码评审。

BASE_SHA=$(git log --oneline | grep "Task 1" | head -1 | awk '{print $1}')
HEAD_SHA=$(git rev-parse HEAD)

[派发 superpowers:code-reviewer 子代理]
  WHAT_WAS_IMPLEMENTED: 对话索引的校验与修复函数
  PLAN_OR_REQUIREMENTS: docs/superpowers/plans/deployment-plan.md 中的任务 2
  BASE_SHA: a7981ec
  HEAD_SHA: 3df7661
  DESCRIPTION: 新增 verifyIndex() 与 repairIndex()，覆盖 4 类问题

[子代理返回]：
  优点：架构清晰、有真实测试
  问题：
    重要：缺少进度指示
    轻微：上报间隔魔数 100
  评估：可继续

你：[修复进度指示]
[继续任务 3]
```

## 与工作流集成

**子代理驱动开发：**
- **每个**任务后评审  
- 在问题叠加前拦截  
- 进入下一任务前修复  

**执行计划：**
- 每批（3 个任务）后评审  
- 获取反馈、应用、继续  

**临时开发：**
- 合并前评审  
- 卡住时评审  

## 危险信号

**绝不：**
- 因「很简单」跳过评审  
- 忽略严重问题  
- 未修复重要问题就继续  
- 与有效技术反馈争辩  

**若评审错误：**
- 以技术理由反驳  
- 用代码/测试证明可行  
- 请求澄清  

模板见：`requesting-code-review/code-reviewer.md`
