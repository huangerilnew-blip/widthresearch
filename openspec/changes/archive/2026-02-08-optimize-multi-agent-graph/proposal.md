## Why

当前图的依赖关系会导致第一阶段文档处理无法与第二阶段执行并行，且向量化可能在第一阶段处理完成前启动，影响吞吐与完整性。需要明确同步屏障和并行路径，以减少总耗时并保证全部文档进入向量库。

## What Changes

- 调整 `collect_first` 的后继依赖，使其同时触发 `execute_second` 与 `process_first_documents`，提高并行度。
- 扩展 `vectorize_documents` 的同步屏障，确保等待 `init_vector_store`、`process_first_documents`、全部完成第一次入库，`process_second_documents` 完成后进行第二次入库。

## Capabilities

### New Capabilities
<!-- 无新增能力 -->

### Modified Capabilities

- `staged-document-processing`: 明确向量化需等待两阶段文档处理完成

## Impact

- 影响 `agents/multi_agent_graph.py` 的 LangGraph 依赖关系与执行时序。
- 无外部 API 变更；运行时并行度提升，整体延迟降低。
