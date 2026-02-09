## Why

当前 get_nodes 假定传入 documents 具有一致的字段，但实际来源是下载工具输出与去重逻辑，字段混杂且 metadata 只需保留 source/title/url，导致文档来源与标题信息不稳定。需要明确 documents 的结构与 metadata 规范，避免后续检索/展示误用。

## What Changes

- 明确 get_nodes 期望的 documents 字段集合（来自下载结果 + 去重流程），并约束 metadata 只写入 source、title、url。
- 统一从 documents 中提取 source/title/url 的规则，避免 doc_title、local_path 等非需求字段进入 Document.metadata。

## Capabilities

### New Capabilities
- `document-metadata-normalization`: 定义 documents 结构与 Document.metadata 的规范化提取规则（source/title/url）。

### Modified Capabilities

## Impact

- `core/rag/document_processor.py` 中 get_nodes 的元数据构建逻辑。
- `agents/multi_agent_graph.py` 文档去重与路径提取依赖的 documents 字段说明。
- 下载工具输出（downloaded_papers）的字段约束与日志说明。
