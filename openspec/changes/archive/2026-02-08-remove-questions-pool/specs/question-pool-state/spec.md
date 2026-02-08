## ADDED Requirements

### Requirement: question_pool 类型为字符串列表
系统 SHALL 将 `state["question_pool"]` 维护为 `List[str]`，不再存放自定义对象。

#### Scenario: 构建完成后返回列表
- **WHEN** `build_question_pool` 节点执行完成
- **THEN** 系统 SHALL 返回 `question_pool` 为字符串列表

### Requirement: question_pool 保序去重合并
系统 SHALL 以“先原始问题、后改写问题”的顺序合并问题池，并对重复问题进行保序去重。

#### Scenario: 原始与改写问题去重
- **WHEN** `sub_questions` 与检索改写问题存在重复项
- **THEN** `question_pool` SHALL 仅保留第一次出现的条目
- **AND** SHALL 保持原始问题在改写问题之前

### Requirement: question_pool 允许为空列表
系统 SHALL 在没有可用问题时返回空列表，而不是 `None`。

#### Scenario: 无可用问题
- **WHEN** 未生成 `sub_questions` 且未提取到改写问题
- **THEN** `question_pool` SHALL 为 `[]`
