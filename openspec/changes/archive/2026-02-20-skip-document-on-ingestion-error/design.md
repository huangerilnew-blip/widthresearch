## Context

当前文档处理逻辑位于 `core/rag/document_processor.py`，在 `get_nodes` 中先构建 `docs_for_pipeline`，随后对每个 `Document` 调用 `self.ingestion_pipeline.run`。已有 try/except 捕获异常并继续，但路径字段依赖 `doc.metadata`，存在路径为空或未按统一字段命名的问题，且仍有 `raise` 类语义残留的预期。我们需要在异常时稳定记录触发文档路径，并确保失败文档被跳过。

## Goals / Non-Goals

**Goals:**
- 明确文档路径的获取策略（优先 `metadata["path"]`，其次回退到 `title` 或其他可识别字段）。
- 在 `IngestionPipeline` 执行异常时记录路径并跳过该文档，保证流程不中断。
- 通过代码分析明确路径在各类文档（PDF/Markdown/JSON）中的来源与可用性。

**Non-Goals:**
- 不修改外部接口或新增依赖。
- 不重构文档处理流程或引入新的并发模型。

## Decisions

- **统一路径字段来源**：在构建 `Document`/`TextNode` 时写入 `metadata["path"]`，并在异常日志中优先读取 `path`，其次读取 `title` 或可替代字段。
  - 备选：只记录 `doc.doc_id`。放弃原因：可追溯性差，无法快速定位文件。
- **异常处理策略**：在 `for doc in docs_for_pipeline` 的调用处 catch 异常，记录路径与错误信息后 `continue`。
  - 备选：在 `IngestionPipeline` 内部修改或自定义 TransformComponent。放弃原因：范围更大、侵入性高。
- **日志内容**：明确记录 `doc_path` 和异常 `e`，确保错误可定位。

## Risks / Trade-offs

- **路径缺失** → 仍可能记录为 `unknown`。缓解：在构建 Document 时确保 `metadata["path"]` 写入，并在日志中增加 `title` 作为兜底。
- **误判路径来源** → 不同文档类型字段不一致。缓解：在代码中集中定义路径提取逻辑，避免分散获取。
