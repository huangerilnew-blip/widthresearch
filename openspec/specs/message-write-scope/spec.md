# message-write-scope Specification

## Purpose
TBD - created by archiving change limit-messages-writes. Update Purpose after archive.

## Requirements
### Requirement: 限定 messages 写入节点范围
系统 MUST 仅允许在 `rag_retrieve`、`generate_answer`、`eval_answer` 三个节点向 `state["messages"]` 写入消息。

#### Scenario: 允许的节点写入消息
- **WHEN** `rag_retrieve` 或 `generate_answer` 或 `eval_answer` 节点执行完成
- **THEN** 允许该节点返回 `messages` 并追加新的消息

### Requirement: 其他节点不得写入 messages
除上述四个节点外，所有节点 MUST NOT 返回 `messages` 字段或追加消息到 `state["messages"]`。

#### Scenario: 非允许节点不写入
- **WHEN** `plan_query`、`execute_first`、`collect_first`、`process_first_documents`、`execute_second`、`collect_second`、`process_second_documents`、`vectorize_documents`、`terminal_error` 任一节点执行完成
- **THEN** 该节点返回的状态中不包含 `messages` 字段

### Requirement: 不引入替代消息合并器
系统 MUST NOT 为上述非允许节点新增任何 `add_messages` 替代字段或额外消息流。

#### Scenario: 不新增替代消息字段
- **WHEN** 任何非允许节点需要记录进度
- **THEN** 仅使用日志或现有 `flags`，不新增消息字段
