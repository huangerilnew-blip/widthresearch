## ADDED Requirements

### Requirement: question_pool 仅通过 messages 传递
系统 SHALL 通过 `state["messages"]` 传递 `question_pool`，不再在 `MultiAgentState` 中持久化该字段。

#### Scenario: rag_retrieve 写入问题池
- **WHEN** `_rag_retrieve_node` 完成问题池构建
- **THEN** 系统 SHALL 向 `state["messages"]` 写入包含 `question_pool` 的 `SystemMessage`
- **AND** SHALL 不在 `MultiAgentState` 中保留 `question_pool` 字段

### Requirement: correct_context 标记问题池有效性
系统 SHALL 在状态中维护 `correct_context` 字段，用于标记问题池是否有效。

#### Scenario: 有效问题池
- **WHEN** `_rag_retrieve_node` 收集 `meta["questions_this_excerpt_can_answer"]` 形成的 list 非空
- **THEN** 系统 SHALL 设置 `correct_context=True`

#### Scenario: 无有效问题池
- **WHEN** 收集到的 `meta["questions_this_excerpt_can_answer"]` list 为空
- **THEN** 系统 SHALL 设置 `correct_context=False`

## MODIFIED Requirements

### Requirement: question_pool 类型为字符串列表
系统 SHALL 将 `question_pool` 维护为 `List[str]`，并作为 `SystemMessage` 内容写入 `state["messages"]`。

#### Scenario: rag_retrieve 构建问题池
- **WHEN** `_rag_retrieve_node` 从检索到的 BaseNode 中提取 `questions_this_excerpt_can_answer`
- **THEN** 系统 SHALL 生成 `List[str]` 类型的 `question_pool`
- **AND** SHALL 将该列表写入 `state["messages"]`

### Requirement: question_pool 保序去重合并
系统 SHALL 按检索节点出现顺序合并 `questions_this_excerpt_can_answer`，对重复问题进行保序去重。

#### Scenario: 检索节点问题去重
- **WHEN** 多个检索节点包含重复问题
- **THEN** `question_pool` SHALL 仅保留第一次出现的条目

### Requirement: question_pool 允许为空列表
系统 SHALL 在未提取到任何问题时返回空列表，并标记 `correct_context=False`。

#### Scenario: 无可用问题
- **WHEN** 所有检索节点的 `questions_this_excerpt_can_answer` 为空或缺失
- **THEN** `question_pool` SHALL 为 `[]`
- **AND** SHALL 设置 `correct_context=False`

## REMOVED Requirements

### Requirement: 构建完成后返回列表
**Reason**: 问题池构建已由 `_rag_retrieve_node` 完成并写入 `state["messages"]`，不再依赖 `build_question_pool` 节点。
**Migration**: 使用 `_rag_retrieve_node` 写入的 `SystemMessage` 中的 `question_pool` 列表。
