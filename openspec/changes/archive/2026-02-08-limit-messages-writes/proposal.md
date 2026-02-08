## Why

当前在多个节点写入 `state["messages"]`，导致消息流被大量进度/状态信息污染，影响上下文质量与可读性，也增加评估与调试的噪声。需要收敛写入范围，确保消息流只包含对 RAG 与答案生成真正有价值的内容。

## What Changes

- 限制 `state["messages"]` 的写入范围，仅允许在 `rag_retrieve`、`build_question_pool`、`generate_answer`、`eval_answer` 四个节点写入。
- 其他节点不再向 `messages` 写入状态/进度信息，改用日志或现有 flag 机制保留执行状态。

## Capabilities

### New Capabilities
- `message-write-scope`: 定义并约束 LangGraph 主流程中 `messages` 的写入范围，确保消息流只承载检索与回答相关内容。

### Modified Capabilities


## Impact

- 代码：`agents/multi_agent_graph.py` 中各节点的返回结构
- 系统：LangGraph 状态合并逻辑（`add_messages`）的使用方式
