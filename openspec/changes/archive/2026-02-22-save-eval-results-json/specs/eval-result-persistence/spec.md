## ADDED Requirements

### Requirement: 评估通过时追加写入观测数据
系统 MUST 在 `last_evaluation.passed == true` 时，将观测数据追加写入项目根目录的 `observational_data.json`。

#### Scenario: 评估通过后追加写入
- **WHEN** `run` 读取到 `last_evaluation.passed == true`
- **THEN** 系统 MUST 调用持久化函数写入一条 JSON Lines 记录

#### Scenario: 评估未通过不写入
- **WHEN** `run` 读取到 `last_evaluation.passed != true`
- **THEN** 系统 MUST NOT 写入 `observational_data.json`

### Requirement: 观测数据的字段结构
系统 MUST 以 `instruction`、`input`、`output` 字段保存观测数据。

#### Scenario: instruction 字段来源
- **WHEN** 持久化观测数据
- **THEN** `instruction` MUST 使用 `state.original_query`

#### Scenario: input 字段结构
- **WHEN** 持久化观测数据
- **THEN** `input` MUST 为 `list[dict]`
- **AND** 每个元素 MUST 包含 `content` 与 `questions`
- **AND** `content` MUST 来自 `retrieved_nodes_score` 中 `node.get_content()`
- **AND** `questions` MUST 来自 `node.metadata["questions_this_excerpt_can_answer"]`

#### Scenario: output 字段来源
- **WHEN** 持久化观测数据
- **THEN** `output` MUST 使用最终回答内容

### Requirement: observational_data.json 文件创建与追加
系统 MUST 以追加写入的方式保存观测数据，文件不存在时 MUST 创建。

#### Scenario: 文件不存在则创建
- **WHEN** 项目根目录的 `observational_data.json` 不存在
- **THEN** 系统 MUST 创建文件并写入首条记录

#### Scenario: 文件存在则追加
- **WHEN** 项目根目录的 `observational_data.json` 已存在
- **THEN** 系统 MUST 追加写入新记录
