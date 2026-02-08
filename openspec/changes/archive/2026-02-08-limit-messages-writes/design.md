## Context

当前 `agents/multi_agent_graph.py` 中多数节点都会向 `state["messages"]` 追加状态/进度信息，导致消息流被噪声填充。业务上只需要在检索与回答相关节点保留消息，其它节点应只记录日志和使用现有 `flags`。

## Goals / Non-Goals

**Goals:**
- 仅保留 `rag_retrieve`、`build_question_pool`、`generate_answer`、`eval_answer` 对 `state["messages"]` 的写入。
- 其余节点完全移除 `messages` 写入，直接舍去，不用 `add_messages` 替代。
- 保持现有日志与 `flags` 作为进度追踪手段。

**Non-Goals:**
- 不改变 ExecutorAgent/PlannerAgent 的内部消息流（`executor_messages`/`planner_messages`）。
- 不调整 RAG 检索、问题池、答案生成的业务逻辑。

## Decisions

- **收敛写入点**：仅在四个 RAG/回答相关节点返回 `messages`。其余节点返回结构删除 `messages` 字段。
  - 备选方案：保留状态消息但改写为 `SystemMessage`。放弃原因：仍会污染消息流，不符合“直接舍去”的要求。
- **进度信息使用日志与 flags**：保持现有 `logger` 与 `flags` 更新，避免引入新的状态字段。
  - 备选方案：新增 `status_messages` 字段。放弃原因：超出范围，且增加状态复杂度。
- **不引入 `add_messages` 替代**：不为其它节点新增任何消息合并器或消息字段。

## Risks / Trade-offs

- **调试信息减少** → 依赖日志排查问题，必要时扩展日志级别。
- **上游节点消息缺失影响上下文** → 目前生成答案只需要系统/用户上下文与检索结果，影响可控。
