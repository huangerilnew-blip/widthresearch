## ADDED Requirements

### Requirement: Document metadata normalization
系统 SHALL 在 get_nodes 处理文档时，仅向 Document.metadata 写入 `source`、`title`、`url` 三个字段。

#### Scenario: 构建元数据
- **WHEN** get_nodes 接收到 documents 列表
- **THEN** 系统 SHALL 为每个 Document 写入且仅写入 `source`、`title`、`url` 字段

### Requirement: Document field extraction rules
系统 SHALL 依据 documents 中已有字段提取 `source`、`title`、`url`，并为缺失项提供可用的回退值。

#### Scenario: 字段优先级
- **WHEN** documents 中存在 `source`/`title`/`url` 字段
- **THEN** 系统 SHALL 直接使用这些字段

#### Scenario: 缺失字段回退
- **WHEN** documents 缺失 `title` 或 `url`
- **THEN** 系统 SHALL 使用文件名（Path(path).stem）作为 title，并使用 `file://<path>` 作为 url

### Requirement: Document path resolution consistency
系统 SHALL 采用统一路径解析顺序以保证与去重逻辑一致。

#### Scenario: 路径解析
- **WHEN** documents 包含 `extra.saved_path`、`local_path`、`file_path`、`path` 任一字段
- **THEN** 系统 SHALL 按 `extra.saved_path` → `local_path` → `file_path` → `path` 的顺序选择第一个可用路径
