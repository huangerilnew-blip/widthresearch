## Why

ExecutorAgentPool 在子问题数量超过 agent 数量时会复用同一 agent 并发执行，导致 agent 的上一个问题未完成就开始下一个问题，产生严重错误。需要引入队列/调度机制，保证单个 ExecutorAgent 按顺序处理其分配到的问题，并兼容现有 multi_agent_graph 与 executoragent 的调用方式。

## What Changes

- 对 ExecutorAgentPool 的任务分配策略进行调整：当问题数超过池大小时，单个 agent 按顺序执行其任务，避免并发复用。
- 保持 execute_questions 的接口和 multi_agent_graph 的调用方式不变，确保兼容性。
- 明确并发范围：多个 agent 之间仍并行，但单个 agent 内串行。

## Capabilities

### New Capabilities
- `executor-pool-queueing`: ExecutorAgentPool 在超出池大小时提供按 agent 串行调度的能力。

### Modified Capabilities
- 

## Impact

- 影响 `agents/executor_pool.py` 的调度逻辑。
- 需要验证 `agents/multi_agent_graph.py` 的两阶段调用保持行为一致。
- ExecutorAgent 的初始化与执行流程保持不变，仅影响并发调度策略。
