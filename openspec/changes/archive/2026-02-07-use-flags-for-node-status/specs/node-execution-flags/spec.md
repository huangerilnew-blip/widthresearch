## ADDED Requirements

### Requirement: Graph state includes node execution flags
系统 SHALL 在 `MultiAgentState` 中新增 `flags` 字段，类型为字典，key 为节点名称，value 为 `true/false/error` 之一。

#### Scenario: 初始化 flags 字段
- **WHEN** `run` 方法创建初始状态
- **THEN** 系统 SHALL 初始化 `flags` 为包含所有节点名称的字典
- **AND** 每个节点的初始值 SHALL 为 `false`

### Requirement: 节点执行结果写入 flags
系统 SHALL 在每个节点执行完成时更新对应的 `flags` 值以反映执行结果。

#### Scenario: 节点成功执行
- **WHEN** 节点逻辑执行成功且返回正常结果
- **THEN** 系统 SHALL 将 `flags["<node>"]` 设置为 `true`

#### Scenario: 节点执行失败
- **WHEN** 节点发生异常并进入错误处理逻辑
- **THEN** 系统 SHALL 将 `flags["<node>"]` 设置为 `error`

#### Scenario: 节点未满足前置条件
- **WHEN** 节点因缺少输入数据而跳过实际处理
- **THEN** 系统 SHALL 将 `flags["<node>"]` 保持为 `false`

### Requirement: run 汇总节点执行状态
系统 SHALL 在 `run` 完成后基于 `flags` 评估各节点是否成功执行，并在返回结果中携带对应状态信息。

#### Scenario: 汇总成功状态
- **WHEN** `flags` 中所有节点均为 `true`
- **THEN** 系统 SHALL 标记本次执行为成功

#### Scenario: 汇总错误状态
- **WHEN** `flags` 中存在 `error`
- **THEN** 系统 SHALL 标记本次执行为失败并记录失败节点
