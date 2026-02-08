## Why

当前 `state["question_pool"]` 在流程中作为自定义类使用，但下游与统计处又按 `List[str]` 访问，类型不一致导致潜在错误与序列化风险。将其收敛为简单列表可以降低复杂度，避免 LangGraph 状态持久化时的非必要对象。

## What Changes

- 将 `state["question_pool"]` 统一为 `List[str]`，不再依赖 `QuestionsPool` 类。
- 移除 `QuestionsPool` 的定义与引用，并在构建问题池时改为列表合并与去重。
- 更新相关文档/描述中 `question_pool` 的类型说明。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

（无）

## Impact

- 影响 `agents/multi_agent_graph.py` 中问题池构建、路由与统计逻辑。
- 影响 `core/rag/models.py` 的类型定义与导入依赖。

