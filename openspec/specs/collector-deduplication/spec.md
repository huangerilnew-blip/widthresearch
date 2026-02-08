# collector-deduplication Specification

## Purpose
TBD - collected from change fix-collector-dedup. Update Purpose after archive.

## Requirements
### Requirement: 第一阶段文档相似度去重
系统 SHALL 仅基于 `execute_first` 产生的文档集合执行 TF-IDF 余弦相似度去重，阈值使用 `Config.DOC_FILTER`，并仅输出非重复结果而不删除重复文档。

#### Scenario: 第一阶段相似度超过阈值时去重
- **WHEN** 第一阶段文档集合中任意两份文档的相似度 >= `Config.DOC_FILTER`
- **THEN** 系统 SHALL 仅输出其中任意一份文档
- **AND** SHALL 记录未被输出的重复文档

#### Scenario: 第一阶段相似度低于阈值时保留
- **WHEN** 第一阶段文档集合中任意两份文档的相似度 < `Config.DOC_FILTER`
- **THEN** 系统 SHALL 保留所有文档

### Requirement: 第二阶段内部相似度去重
系统 SHALL 在第二阶段先对 `execute_second` 产生的文档集合执行 TF-IDF 余弦相似度去重，阈值使用 `Config.DOC_FILTER`，并仅输出非重复结果而不删除重复文档。

#### Scenario: 第二阶段内部相似度超过阈值时去重
- **WHEN** 第二阶段文档集合中任意两份文档的相似度 >= `Config.DOC_FILTER`
- **THEN** 系统 SHALL 仅输出其中任意一份文档
- **AND** SHALL 记录未被输出的重复文档

#### Scenario: 第二阶段内部相似度低于阈值时保留
- **WHEN** 第二阶段文档集合中任意两份文档的相似度 < `Config.DOC_FILTER`
- **THEN** 系统 SHALL 保留所有文档

### Requirement: 跨阶段去重优先级
系统 SHALL 在第二阶段内部去重完成后，将其结果与第一阶段保留结果进行相似度比对；当判定为重复时，必须仅输出第一阶段结果而不删除第二阶段文档。

#### Scenario: 第二阶段与第一阶段重复时删除第二阶段
- **WHEN** 第二阶段去重后的任意文档与第一阶段保留文档相似度 >= `Config.DOC_FILTER`
- **THEN** 系统 SHALL 仅输出对应的第一阶段文档
- **AND** SHALL 不输出该第二阶段文档

#### Scenario: 第二阶段与第一阶段不重复时保留
- **WHEN** 第二阶段去重后的任意文档与第一阶段保留文档相似度 < `Config.DOC_FILTER`
- **THEN** 系统 SHALL 保留该第二阶段文档
