# 基于条件的等待

## 概述

脆弱测试常用任意延迟猜时间，造成竞态：快机器过、负载或 CI 下失败。

**核心原则：** 等待你**真正关心的条件**，而不是猜需要多久。

## 何时使用

```dot
digraph when_to_use {
    "测试用 setTimeout/sleep？" [shape=diamond];
    "在测定时行为？" [shape=diamond];
    "记录为何需要超时" [shape=box];
    "使用基于条件的等待" [shape=box];

    "测试用 setTimeout/sleep？" -> "在测定时行为？" [label="是"];
    "在测定时行为？" -> "记录为何需要超时" [label="是"];
    "在测定时行为？" -> "使用基于条件的等待" [label="否"];
}
```

**适用于：**
- 测试含任意延迟（`setTimeout`、`sleep`、`time.sleep()`）  
- 测试不稳定（有时过、负载下失败）  
- 并行运行时超时  
- 等待异步操作完成  

**不适用于：**
- 测试**真实**定时行为（防抖、节流间隔）  
- 若必须用任意超时，**务必**记录原因  

## 核心模式

```typescript
// ❌ 之前：猜时间
await new Promise(r => setTimeout(r, 50));
const result = getResult();
expect(result).toBeDefined();

// ✅ 之后：等条件
await waitFor(() => getResult() !== undefined);
const result = getResult();
expect(result).toBeDefined();
```

## 速查模式

| 场景 | 模式 |
|------|------|
| 等事件 | `waitFor(() => events.find(e => e.type === 'DONE'))` |
| 等状态 | `waitFor(() => machine.state === 'ready')` |
| 等数量 | `waitFor(() => items.length >= 5)` |
| 等文件 | `waitFor(() => fs.existsSync(path))` |
| 复杂条件 | `waitFor(() => obj.ready && obj.value > 10)` |

## 实现

通用轮询：

```typescript
async function waitFor<T>(
  condition: () => T | undefined | null | false,
  description: string,
  timeoutMs = 5000
): Promise<T> {
  const startTime = Date.now();

  while (true) {
    const result = condition();
    if (result) return result;

    if (Date.now() - startTime > timeoutMs) {
      throw new Error(`Timeout waiting for ${description} after ${timeoutMs}ms`);
    }

    await new Promise(r => setTimeout(r, 10)); // 每 10ms 轮询
  }
}
```

完整实现与领域助手（`waitForEvent` 等）见本目录 `condition-based-waiting-example.ts`。

## 常见错误

**❌ 轮询过快：** `setTimeout(check, 1)` — 浪费 CPU  
**✅：** 每 10ms  

**❌ 无超时：** 条件永不满足则死循环  
**✅：** 始终含超时与清晰错误  

**❌ 陈旧数据：** 在循环外缓存状态  
**✅：** 在循环内调用 getter 取最新值  

## 何时任意超时才是对的

```typescript
await waitForEvent(manager, 'TOOL_STARTED'); // 先：等条件
await new Promise(r => setTimeout(r, 200));   // 再：等定时行为
// 200ms = 在 100ms tick 下等 2 次 —— 有注释与依据
```

**要求：**  
1. 先等触发条件  
2. 基于已知时序（非猜测）  
3. 注释说明**为何**  

## 实际影响

来自调试会话（2025-10-03）：
- 修复 3 个文件共 15 个脆弱测试  
- 通过率：60% → 100%  
- 执行时间：快约 40%  
- 消除竞态  
