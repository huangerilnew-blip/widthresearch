## Why

当前问题池构建分散在 `_rag_retrieve_node` 和 `_build_question_pool_node` 两处，导致状态一致性弱，检索结果与问题池可能不匹配，重试逻辑也变得脆弱。需要把问题池构建集中到检索节点并补齐条件边，提升容错与可维护性。

## What Changes

- 在 `_rag_retrieve_node` 内完成检索结果与 `question_pool` 的统一构造（已完成），并保证两者同步存在。
- 增加条件边/路由逻辑，确保只有在检索结果与问题池齐备时才进入生成答案。
- 移除冗余的 `_build_question_pool_node` 及其路由重试路径（保留必要的重试与终止机制）。
- 精简 `_generate_answer_node` 中对问题池与上下文的重复拼装逻辑，仅依赖消息链路中的系统提示与检索结果。
- 分析 `_build_question_pool_node`的删除，哪些地方需要做必然的修改

## Capabilities

### New Capabilities
- （无）

### Modified Capabilities
- `question-pool-state`: 问题池生成节点与路由条件变更，要求与检索结果同生命周期

## Impact

- `agents/multi_agent_graph.py` 的节点实现与图路由（rag_retrieve、build_question_pool、generate_answer）
- 可能影响与问题池相关的日志与重试策略
- 无新增外部依赖
