## ADDED Requirements

### Requirement: 检索结果为空时重试
系统 SHALL 在 `retrieved_nodes` 为空时触发重试，并使用 `retrieved_epoch` 记录重试次数。

#### Scenario: 检索为空触发重试
- **WHEN** `retrieved_nodes` 为空
- **THEN** 系统 SHALL 增加 `retrieved_epoch` 计数 +1
- **AND** SHALL 路由回检索节点重试

#### Scenario: 检索重试达到上限
- **WHEN** `retrieved_nodes` 为空
- **AND** `retrieved_epoch` 达到 `Config.GENER_EPOCH`
- **THEN** 系统 SHALL 路由到 `END`
- **AND** SHALL 返回“系统错误，无法正确回答”作为最终答案

### Requirement: 问题池为空时重试
系统 SHALL 在 `question_pool` 为空时触发重试，并使用 `set_ques_pool_epoch` 记录重试次数。

#### Scenario: 问题池为空触发重试
- **WHEN** `question_pool` 为空
- **THEN** 系统 SHALL 增加 `set_ques_pool_epoch` 计数 +1
- **AND** SHALL 路由回问题池构建节点重试

#### Scenario: 问题池重试达到上限
- **WHEN** `question_pool` 为空
- **AND** `set_ques_pool_epoch` 达到 `Config.GENER_EPOCH`
- **THEN** 系统 SHALL 路由到 `END`
- **AND** SHALL 返回“系统错误，无法正确回答”作为最终答案

### Requirement: 重试计数初始化
系统 SHALL 在初始化状态时设置 `retrieved_epoch=0` 与 `set_ques_pool_epoch=0`。

#### Scenario: 初始状态设置计数
- **WHEN** `run` 方法创建初始状态
- **THEN** SHALL 设置 `retrieved_epoch=0`
- **AND** SHALL 设置 `set_ques_pool_epoch=0`
