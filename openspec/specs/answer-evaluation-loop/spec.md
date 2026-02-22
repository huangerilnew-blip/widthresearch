# answer-evaluation-loop Specification

## Purpose
TBD - created by archiving change add-answer-evaluation-loop. Update Purpose after archive.
## Requirements
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

### Requirement: 评估维度合理性

`_eval_answer_node` SHALL 评估回答的合理性，包括逻辑结构和回答边界。

#### Scenario: 合理性检查通过

- **WHEN** 评估 LLM 分析答案
- **AND** 回答围绕原始问题展开
- **AND** 逻辑结构清晰分层
- **AND** 无明显矛盾或幻觉
- **THEN** SHALL 判定为合理性通过

#### Scenario: 合理性检查失败

- **WHEN** 评估 LLM 分析答案
- **AND** 回答偏离原始问题
- **OR** 逻辑结构混乱
- **OR** 存在明显矛盾或幻觉
- **THEN** SHALL 判定为合理性不通过
- **AND** SHALL 在评估结果中说明具体问题

### Requirement: 评估提示包含检索上下文并截断

系统 SHALL 在构建评估提示时包含检索上下文，并对每条检索内容进行 500 字符截断。

#### Scenario: 评估提示加入检索内容

- **WHEN** `_eval_answer_node` 构建评估提示
- **THEN** SHALL 将检索上下文加入评估提示
- **AND** SHALL 保持检索内容数量与 Top-K 限制一致

#### Scenario: 检索内容截断

- **WHEN** 单条检索内容长度超过 500 字符
- **THEN** 系统 SHALL 截断为 500 字符并追加省略标记

### Requirement: 评估证据标注准确性

`_eval_answer_node` SHALL 基于检索上下文评估证据标注的准确性，包括来源和信息充分性。

#### Scenario: 证据标注检查通过

- **WHEN** 评估 LLM 检查证据标注
- **AND** 已提供检索上下文
- **AND** 所有关键结论都有明确的来源标注
- **AND** 证据准确对应检索内容
- **AND** 明确说明信息不足的部分
- **THEN** SHALL 判定为证据标注通过

#### Scenario: 证据标注检查失败

- **WHEN** 评估 LLM 检查证据标注
- **AND** 已提供检索上下文
- **AND** 存在关键结论缺少来源标注
- **OR** 证据与检索内容不匹配
- **OR** 信息不足部分未说明
- **THEN** SHALL 判定为证据标注不通过
- **AND** SHALL 在评估结果中说明具体问题

### Requirement: 防止无限循环

系统 SHALL 通过 epoch 计数器防止生成-评估循环无限进行。

#### Scenario: Epoch 初始化

- **WHEN** 查询处理开始（`run` 方法）
- **THEN** SHALL 初始化 `epoch=0` 在初始状态中

#### Scenario: Epoch 计数

- **WHEN** 进入 `_generate_answer_node`
- **THEN** SHALL 读取当前 `epoch` 值
- **WHEN** `_generate_answer_node` 完成
- **THEN** SHALL 增加 `epoch` +1

#### Scenario: Epoch 达到上限

- **WHEN** `epoch` 达到 `Config.GENER_EPOCH`
- **THEN** SHALL 停止循环
- **AND** SHALL 使用最后一次生成的答案
- **AND** SHALL 在日志中记录警告信息

### Requirement: 使用独立评估模型

`_eval_answer_node` SHALL 使用 `Config.LLM_MUTI_AGENT` 指定的大模型进行评估。

#### Scenario: 评估模型初始化

- **WHEN** 初始化 `MultiAgentGraph`
- **THEN** SHALL 创建评估 LLM 实例
- **AND** SHALL 使用 `Config.LLM_MUTI_AGENT` 配置

#### Scenario: 评估模型独立调用

- **WHEN** `_eval_answer_node` 执行评估
- **THEN** SHALL 使用独立的评估 LLM
- **AND** SHALL 不与生成 LLM 共享实例

### Requirement: 使用 Messages 字段传递 prompt 和对话历史

系统 SHALL 通过 `state["messages"]` 字段传递系统 prompt 和对话历史。

#### Scenario: 初始构建 SystemMessage 和 HumanMessage

- **WHEN** `run` 方法初始化查询
- **THEN** SHALL 创建 `SystemMessage`（包含生成系统 prompt）和 `HumanMessage`（包含用户查询）
- **AND** SHALL 放入 `state["messages"]`
- **AND** SHALL 设置 `messages: [SystemMessage(...), HumanMessage(...)]`

#### Scenario: 生成节点读取 messages

- **WHEN** `_generate_answer_node` 执行
- **THEN** SHALL 从 `state["messages"]` 读取完整对话历史
- **AND** SHALL 不在节点内部构建 prompt
- **AND** SHALL 直接调用 LLM，传入 messages

#### Scenario: 评估节点读取最近一次答案

- **WHEN** `_eval_answer_node` 执行
- **THEN** SHALL 从 `state["messages"][-1]` 获取最近一次生成的 `AIMessage`
- **AND** SHALL 评估 `AIMessage.content` 的质量

### Requirement: 评估节点返回结构化建议

`_eval_answer_node` SHALL 返回结构化的评估结果，包含 pass/fail 判断和具体的修改建议。

#### Scenario: 评估通过返回

- **WHEN** 评估结果为通过
- **THEN** SHALL 返回 `{"passed": true, "suggestions": []}`
- **AND** 不需要具体修改建议

#### Scenario: 评估不通过返回建议

- **WHEN** 评估结果为不通过
- **THEN** SHALL 返回 `{"passed": false, "suggestions": ["问题1", "问题2", ...]}`
- **AND** SHALL 为每个评估维度（合理性、证据标注）提供具体问题
- **AND** 建议 SHALL 具有可操作性（如"缺少关键结论的来源标注"而非"质量差"）

### Requirement: State 存储历史答案和评估

`MultiAgentState` SHALL 存储之前的答案和评估结果，支持增量修改。

#### Scenario: 首次生成前初始化

- **WHEN** 查询开始
- **THEN** SHALL 初始化 `last_answer=""` 和 `last_evaluation=None`
- **AND** SHALL 设置 `epoch=0`

#### Scenario: 评估后保存结果

- **WHEN** `_eval_answer_node` 完成
- **THEN** SHALL 更新 `last_evaluation` 为评估结果
- **AND** SHALL 保持 `last_answer` 不变

#### Scenario: 生成前读取历史

- **WHEN** `_generate_answer_node` 开始执行
- **THEN** SHALL 读取 `last_answer` 和 `last_evaluation`
- **AND** SHALL 判断是否有历史评估建议

### Requirement: 基于评估建议增量修改答案

`_generate_answer_node` SHALL 基于之前的答案和评估建议生成修改后的答案。

#### Scenario: 首次生成（无历史建议）

- **WHEN** `_generate_answer_node` 执行且 `last_evaluation` 为 None
- **THEN** SHALL 基于原始查询和检索内容生成初始答案
- **AND** SHALL 不参考评估建议（因为不存在）

#### Scenario: 基于建议修改答案

- **WHEN** `_generate_answer_node` 执行且 `last_evaluation` 不为 None
- **AND** `last_evaluation.suggestions` 包含具体建议
- **THEN** SHALL 在 prompt 中包含：
  - 原始查询
  - 检索内容
  - 之前生成的答案（`last_answer`）
  - 评估的具体建议（`last_evaluation.suggestions`）
- **AND** SHALL 要求 LLM 基于这些建议修改答案
- **AND** SHALL 保留答案的有效部分，只修改有问题的部分
