## Purpose

TBD

## ADDED Requirements

### Requirement: 记录并跳过处理失败的文档
当单个文档在 IngestionPipeline 处理过程中触发异常时，系统 SHALL 记录该文档的路径信息并跳过该文档，处理流程 SHALL 继续处理后续文档。

#### Scenario: 单个文档触发异常
- **WHEN** 处理某个 Document 时发生异常
- **THEN** 系统 SHALL 在错误日志中记录该文档路径或可替代标识
- **AND** 系统 SHALL 跳过该文档并继续处理后续文档

### Requirement: 路径字段回退策略
系统 SHALL 在日志记录时优先使用文档元数据中的 `path` 字段，并在缺失时回退到可识别的替代字段以保证日志可追溯。

#### Scenario: 文档路径存在
- **WHEN** 文档元数据中包含 `path`
- **THEN** 系统 SHALL 在错误日志中使用该 `path`

#### Scenario: 文档路径缺失
- **WHEN** 文档元数据中缺失 `path`
- **THEN** 系统 SHALL 使用 `title` 或其他可识别字段作为路径替代值记录在日志中
