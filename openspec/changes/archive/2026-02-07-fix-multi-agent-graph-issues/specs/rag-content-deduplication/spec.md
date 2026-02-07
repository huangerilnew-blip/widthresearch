## ADDED Requirements

### Requirement: RAG 内容相似度去重
系统 SHALL 在 RAG 后处理阶段对检索节点进行内容相似度去重，阈值使用 `Config.DOC_FILTER`。

#### Scenario: 相似度超过阈值时去重
- **WHEN** 两个或多个检索节点的内容相似度 >= `Config.DOC_FILTER`
- **THEN** 系统 SHALL 仅保留分数最高的节点
- **AND** SHALL 丢弃其余相似节点

#### Scenario: 相似度低于阈值时保留
- **WHEN** 检索节点之间的内容相似度 < `Config.DOC_FILTER`
- **THEN** 系统 SHALL 保留所有节点

### Requirement: 去重顺序与评分保留
系统 SHALL 在 rerank 之后执行内容相似度去重，并保持最终结果按分数降序排序。

#### Scenario: 先 rerank 再去重
- **WHEN** 完成检索 rerank 与阈值过滤
- **THEN** 系统 SHALL 基于 rerank 分数执行内容相似度去重

#### Scenario: 去重后排序
- **WHEN** 内容相似度去重完成
- **THEN** 系统 SHALL 按分数从高到低排序输出节点
