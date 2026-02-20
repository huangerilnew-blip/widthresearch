## Why

当前文档处理管道在单个文档解析失败时会中断或遗漏错误上下文，缺少明确的失败文档路径记录，导致排查与恢复成本高。需要在异常发生时完整记录触发文档路径，并保证流程跳过失败文档继续处理。

## What Changes

- 明确文档处理环节的异常处理策略：记录失败文档路径并跳过，避免单个文档影响整体处理。
- 强化对文档路径的获取与传递，确保异常日志包含可追溯的文件路径信息。
- 在处理链路中补齐对路径缺失场景的兜底逻辑，避免日志出现空路径。

## Capabilities

### New Capabilities
- `document-ingestion-error-handling`: 规定文档处理异常时的路径记录与跳过策略。

### Modified Capabilities

## Impact

- 影响文件：`core/rag/document_processor.py`（IngestionPipeline 异常处理与日志）。
- 影响日志：异常日志将包含触发文档的路径或可替代标识。
- 不引入新依赖，不改变外部接口，仅完善处理行为与可观测性。
