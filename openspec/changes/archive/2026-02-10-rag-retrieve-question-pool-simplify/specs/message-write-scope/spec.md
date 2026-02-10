## MODIFIED Requirements

### Requirement: 限定 messages 写入节点范围
系统 MUST 仅允许在 `rag_retrieve`、`generate_answer`、`eval_answer` 三个节点向 `state["messages"]` 写入消息。

#### Scenario: 允许的节点写入消息
- **WHEN** `rag_retrieve` 或 `generate_answer` 或 `eval_answer` 节点执行完成
- **THEN** 允许该节点返回 `messages` 并追加新的消息
