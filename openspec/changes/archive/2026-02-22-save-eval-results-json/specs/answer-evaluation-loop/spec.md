## MODIFIED Requirements

### Requirement: 答案生成评估循环

系统 SHALL 在 `_generate_answer_node` 生成答案后进行评估，根据评估结果决定是否重新生成，并在评估通过后触发观测数据持久化。

#### Scenario: 首次生成与评估

- **WHEN** `_generate_answer_node` 首次生成最终答案
- **THEN** SHALL 传递答案到 `_eval_answer_node` 进行评估
- **AND** state 中的 `epoch` SHALL 为 0

#### Scenario: 评估通过直接结束

- **WHEN** `_eval_answer_node` 评估结果为通过
- **AND** 回答维度合理
- **AND** 证据标注正确
- **THEN** SHALL 路由到 `END`
- **AND** 使用当前 `final_answer` 作为最终结果

#### Scenario: 评估通过触发观测数据持久化

- **WHEN** `_eval_answer_node` 评估结果为通过
- **THEN** `run` MUST 使用 `retrieved_nodes_score` 解析观测数据并追加写入 `observational_data.json`

#### Scenario: 评估不通过且未达上限

- **WHEN** `_eval_answer_node` 评估结果为不通过
- **AND** `epoch` 小于 `Config.GENER_EPOCH`
- **THEN** SHALL 路由回 `_generate_answer_node`
- **AND** SHALL 增加 `epoch` 计数 +1
- **AND** SHALL 基于评估反馈重新生成答案

#### Scenario: 评估不通过且已达上限

- **WHEN** `_eval_answer_node` 评估结果为不通过
- **AND** `epoch` 等于 `Config.GENER_EPOCH`
- **THEN** SHALL 路由到 `END`
- **AND** SHALL 使用当前生成的答案作为最终结果
- **AND** SHALL 在日志中记录已达到最大迭代次数
