## Why

当前 collector_first 与 collector_second 共用同一套文件去重逻辑，无法区分两阶段的去重规则，导致第二阶段结果可能与第一阶段重复却未按优先级处理，重复文档仍会进入后续处理，影响精炼阶段质量与效率。

## What Changes

- 为 collector_first 引入“仅基于 execute_first 结果的 TF-IDF 相似度去重”，重复结果任意保留一个即可，重复项不做删除。
- 为 collector_second 引入“跨阶段优先级去重”：若与 collector_first 结果重复，仅保留第一阶段结果，execute_second 内部重复仅保留一个，重复项不做删除。
- 统一去重后元数据与日志输出，确保两阶段去重统计可追踪且不包含物理删除。

## Capabilities

### New Capabilities
- `collector-deduplication`: 定义两阶段收集流程中的去重规则与优先级（第一阶段 TF-IDF 相似度去重、第二阶段跨阶段优先级去重）。

### Modified Capabilities

## Impact

- `agents/multi_agent_graph.py` 中的 collector_first/collector_second 节点逻辑与返回结构。
- 可能新增或调整去重辅助函数（如 TF-IDF 相似度与跨阶段比对）及相关日志。
- 文档收集与处理流程的重复统计与输出信息。
