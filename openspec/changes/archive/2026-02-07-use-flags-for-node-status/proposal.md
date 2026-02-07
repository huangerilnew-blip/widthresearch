## Why

当前多个节点通过 `state.error` 记录错误，缺乏统一的节点级执行状态，导致无法清晰判断每个节点是否成功完成。引入 `flags` 字典可以统一记录节点执行结果并提升可观测性。

## What Changes

- 在状态中新增 `flags: Dict[str, Union[true, false, error]]`，记录每个节点的执行状态。
- 各节点不再写入 `state.error`，改为设置 `state["flags"][<node>]` 为 `true/false/error`。
- `run` 方法基于 `flags` 评估节点执行是否成功，`inited_vector_index` 默认设置为 `false`。

## Capabilities

### New Capabilities
- `node-execution-flags`: 以 `flags` 统一记录图中各节点的执行结果与错误状态。

### Modified Capabilities

## Impact

- 影响 `agents/multi_agent_graph.py` 的状态定义与节点错误记录逻辑。
- 影响依赖 `state.error` 的诊断与日志行为，需要同步调整。
