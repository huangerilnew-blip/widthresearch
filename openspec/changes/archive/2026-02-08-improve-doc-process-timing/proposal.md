## Why

当前流程在两次去重结束后才统一切割文档，导致大量重复内容进入后续处理，延长整体运行时间。应在每次去重后立刻处理文档，以减少无效处理并缩短等待时间。

## What Changes

- 在每次文档去重完成后立即调用文档处理逻辑，避免延迟切割。
- 将 `process_documents` 从节点调整为类方法，供两个新节点复用。
- 新增两个节点分别在第一次和第二次去重后调用文档处理。

## Capabilities

### New Capabilities
- `staged-document-processing`: 在多阶段去重后分段处理文档，降低重复处理成本并缩短总耗时。

### Modified Capabilities
- 无

## Impact

- `agents/multi_agent_graph.py` 的节点定义与流程顺序调整。
- 文档处理调用时机变化，可能影响向量化前的处理节奏与日志输出。
