## Context

当前 ExecutorAgentPool 在 `execute_questions` 中采用轮询分配并一次性 `asyncio.gather` 并发执行。当 questions 数量超过 pool_size 时，同一个 ExecutorAgent 会被并发复用，导致 agent 内部状态初始化或资源使用出现竞态。该变更要求保持 `execute_questions` 的调用接口不变，并兼容 multi_agent_graph 的两阶段调用流程。

## Goals / Non-Goals

**Goals:**
- 单个 ExecutorAgent 在任何时刻只处理一个 question，按分配顺序串行执行。
- 不改变 `execute_questions` 的对外接口和返回结构，保持 multi_agent_graph 调用兼容。
- 保持多个 agent 之间的并行能力，避免整体吞吐下降到单线程。

**Non-Goals:**
- 不调整 PlannerAgent/ExecutorAgent 的业务逻辑与状态结构。
- 不引入新的外部依赖或跨模块重构。
- 不改变 URL pool 的合并与去重策略。

## Decisions

1. **在 ExecutorAgentPool 内为每个 agent 增加串行控制**
   - 方案：为每个 ExecutorAgent 维护一个 `asyncio.Lock`（或 `asyncio.Semaphore(1)`），调用 `_invoke_agent_with_message` 前先获取该 lock，完成后释放。
   - 理由：实现简单、侵入性低，既能保证单 agent 串行，又保留多 agent 并行。
   - 备选方案：为每个 agent 建立 `asyncio.Queue` + worker 协程，按队列顺序消费任务。
   - 选择理由：锁方案改动最小，不引入后台 worker 生命周期管理。

2. **保持线程 ID 与结果聚合逻辑不变**
   - 继续使用 `thread_id = f"{base_thread_id}_executor_{i}"`，保证 AsyncPostgresSaver 的兼容性。
   - 保持 `asyncio.gather(..., return_exceptions=True)` 的结果收集方式与 URL pool 合并流程。

## Risks / Trade-offs

- **并发度下降** → 仅限制单 agent 内并发，多 agent 仍并行，整体吞吐影响可控。
- **任务等待时间增加** → 当 questions 数量显著超过 pool_size 时，同一 agent 上的排队时间增加；但这是为了消除竞态的必要代价。
- **锁使用不当导致死锁** → 避免在 lock 内再等待同一 agent 的其他任务；锁范围限定在单次 `_invoke_agent_with_message` 调用。
