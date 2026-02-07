## ADDED Requirements

### Requirement: 评估提示包含检索上下文并截断
系统 SHALL 在构建评估提示时包含检索上下文，并对每条检索内容进行 500 字符截断。

#### Scenario: 评估提示加入检索内容
- **WHEN** `_eval_answer_node` 构建评估提示
- **THEN** SHALL 将检索上下文加入评估提示
- **AND** SHALL 保持检索内容数量与 Top-K 限制一致

#### Scenario: 检索内容截断
- **WHEN** 单条检索内容长度超过 500 字符
- **THEN** 系统 SHALL 截断为 500 字符并追加省略标记

## MODIFIED Requirements

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
