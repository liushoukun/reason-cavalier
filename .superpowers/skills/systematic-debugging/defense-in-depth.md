# 纵深防御校验

## 概述

当无效数据导致 bug 时，只在一处加校验往往感觉够了。但那条路径可能被不同代码路径、重构或 mock 绕过。

**核心原则：** 在数据经过的**每一层**都校验。让 bug **结构上不可能**。

## 为何要多层

单层校验：「我们修了 bug」  
多层校验：「我们让 bug 不可能再发生」  

不同层捕获不同情况：
- 入口校验捕获大多数问题  
- 业务逻辑捕获边界  
- 环境守卫防止特定上下文危险  
- 调试日志在其他层失效时帮助取证  

## 四层

### 第 1 层：入口校验
**目的：** 在 API 边界拒绝明显无效输入

```typescript
function createProject(name: string, workingDirectory: string) {
  if (!workingDirectory || workingDirectory.trim() === '') {
    throw new Error('workingDirectory cannot be empty');
  }
  if (!existsSync(workingDirectory)) {
    throw new Error(`workingDirectory does not exist: ${workingDirectory}`);
  }
  if (!statSync(workingDirectory).isDirectory()) {
    throw new Error(`workingDirectory is not a directory: ${workingDirectory}`);
  }
  // ... proceed
}
```

### 第 2 层：业务逻辑校验
**目的：** 确保数据对此操作有意义

```typescript
function initializeWorkspace(projectDir: string, sessionId: string) {
  if (!projectDir) {
    throw new Error('projectDir required for workspace initialization');
  }
  // ... proceed
}
```

### 第 3 层：环境守卫
**目的：** 在特定上下文中阻止危险操作

```typescript
async function gitInit(directory: string) {
  if (process.env.NODE_ENV === 'test') {
    const normalized = normalize(resolve(directory));
    const tmpDir = normalize(resolve(tmpdir()));

    if (!normalized.startsWith(tmpDir)) {
      throw new Error(
        `Refusing git init outside temp dir during tests: ${directory}`
      );
    }
  }
  // ... proceed
}
```

### 第 4 层：调试埋点
**目的：** 为取证保留上下文

```typescript
async function gitInit(directory: string) {
  const stack = new Error().stack;
  logger.debug('About to git init', {
    directory,
    cwd: process.cwd(),
    stack,
  });
  // ... proceed
}
```

## 应用模式

发现 bug 时：

1. **追踪数据流** — 坏值从哪来？在哪用？  
2. **映射所有检查点** — 列出数据经过的每一点  
3. **每层加校验** — 入口、业务、环境、调试  
4. **逐层测试** — 尝试绕过第 1 层，验证第 2 层能抓住  

## 会话示例

Bug：空 `projectDir` 导致在源码中 `git init`

**数据流：**
1. 测试 setup → 空串  
2. `Project.create(name, '')`  
3. `WorkspaceManager.createWorkspace('')`  
4. `git init` 在 `process.cwd()` 运行  

**增加四层：**
- 第 1 层：`Project.create()` 校验非空/存在/可写  
- 第 2 层：`WorkspaceManager` 校验 `projectDir` 非空  
- 第 3 层：`WorktreeManager` 在测试中拒绝 tmpdir 外 `git init`  
- 第 4 层：`git init` 前打栈日志  

**结果：** 全部 1847 测试通过，bug 无法再复现  

## 关键洞见

四层都必要。测试中每层抓到过其他层漏掉的问题：
- 不同路径绕过入口校验  
- Mock 绕过业务检查  
- 不同平台边界需要环境守卫  
- 调试日志发现结构性误用  

**不要停在一个校验点。** 在每一层都加检查。
