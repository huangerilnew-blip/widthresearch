## Context

get_nodes 的入参 documents 来自 `agents/executoragent.py` 的下载结果 `downloaded_papers`，再由 `agents/multi_agent_graph.py` 去重后传入。当前代码对字段的假设不一致：路径字段在 `extra.saved_path` / `local_path` / `file_path` / `path` 之间切换，metadata 里又塞入 `doc_title`、`local_path` 等非需求字段。需求侧只需要 `source`、`title`、`url` 三个字段，且 MarkdownReader 返回 `List[Document]`，需要统一对每个 Document 的 metadata 写入方式。

## Goals / Non-Goals

**Goals:**
- 明确 documents 字段来源与优先级（路径、来源、标题、链接）。
- 在 get_nodes 中只写入 `source`、`title`、`url` 到 `Document.metadata`。
- 保持 PDF/Markdown 两条路径一致的 metadata 规则。

**Non-Goals:**
- 不改动下载工具输出结构或去重策略。
- 不新增新的 metadata 字段（如 local_path、doc_id）。
- 不改变切分/抽题流程（IngestionPipeline）。

## Decisions

- **统一 documents 结构解析来源**：以 `agents/multi_agent_graph.py` 现有 `_get_document_path` 规则为主，路径解析顺序为 `extra.saved_path` → `local_path` → `file_path` → `path`。理由：去重与日志已经依赖该顺序，保持一致避免不一致的路径导致丢失或重复。
- **metadata 只保留三字段**：`source`、`title`、`url`。理由：需求明确且减少向量索引噪声，避免 doc_title/local_path 混入。
- **标题/链接提取策略**：优先从 documents 自带字段取值（例如 `title` / `url`），缺失时可回退到文件名（`Path(path).stem`）和本地路径构造 `file://` 链接。理由：满足最小可用性，同时不引入新字段。
- **MarkdownReader 返回值约束**：对 `MarkdownReader.load_data` 的 `List[Document]` 逐个更新 `metadata`，不替换 Document 对象。理由：保证 reader 内部已填充的 metadata 不丢失。

## Risks / Trade-offs

- 标题缺失时使用文件名可能不符合业务预期 → 通过明确优先级和日志提示降低不可控性。
- url 可能不是公网可访问链接（例如 file://） → 保持兼容，后续如需规范化可在调用层处理。
