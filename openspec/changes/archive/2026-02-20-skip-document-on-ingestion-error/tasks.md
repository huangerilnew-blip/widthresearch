## 1. 代码路径梳理与元数据规范化

- [x] 1.1 复核 `core/rag/document_processor.py` 中路径解析与 `metadata["path"]` 写入位置
- [x] 1.2 对比 `extra.saved_path`/`local_path`/`file_path`/`path` 的优先级实现是否一致
- [x] 1.3 明确异常日志使用的路径回退逻辑（`path` → `title` → 其他字段）

## 2. IngestionPipeline 异常处理改造

- [x] 2.1 在单文档 `self.ingestion_pipeline.run` 调用处补齐路径提取与兜底
- [x] 2.2 将异常处理改为记录路径并 `continue`，确保跳过失败文档
- [x] 2.3 校验错误日志包含路径与异常信息，避免空路径记录

## 3. 验证与回归检查

- [x] 3.1 对失败文档场景进行验证，确认后续文档仍被处理
- [x] 3.2 检查日志输出格式是否满足追踪需求
