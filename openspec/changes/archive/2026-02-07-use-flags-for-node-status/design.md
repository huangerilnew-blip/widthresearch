## Context

MultiAgentGraph 目前依赖 `state.error` 记录节点异常，无法区分每个节点是否成功完成，也无法表达“执行失败但可继续”的状态。需要一个统一的节点级执行状态记录，并让 `run` 对节点完成情况有明确判断。

## Goals / Non-Goals

**Goals:**
- 在 MultiAgentGraph 状态中引入 `flags`，以 `node -> true/false/error` 统一记录节点执行结果。
- 将节点的错误记录从 `state.error` 迁移到 `flags`，并在 `run` 汇总节点执行情况。
- `inited_vector_index` 在初始状态设为 `false`，避免默认误判为已初始化。

**Non-Goals:**
- 不调整节点的业务逻辑或执行顺序。
- 不引入新的外部依赖或改变 LangGraph 结构。
- 不修改 Executor/Planner 的内部错误处理策略。

## Decisions

- **状态结构**：在 `MultiAgentState` 中新增 `flags: Dict[str, Union[true, false, error]]`，以节点名为 key。
  - 替代方案：继续使用 `state.error`。拒绝原因：无法区分节点级执行情况，也无法表达成功/失败混合状态。
- **节点写入方式**：每个节点在成功时设置 `flags["<node>"]=true`，在可预期失败时设置为 `false`，异常捕获时设置为 `error`。
  - 替代方案：在节点内部抛出异常交由外层捕获。拒绝原因：无法保留节点级结果与可恢复失败。
- **run 聚合方式**：在 `run` 中基于 `flags` 判断各节点是否完成，将整体状态映射为最终结果元数据。
  - 替代方案：仅依赖 `graph.ainvoke` 返回值。拒绝原因：缺少节点级状态，无法对失败节点进行定位。

## Risks / Trade-offs

- `flags` 需要覆盖所有节点名称，若漏写会导致状态不完整 → 通过统一初始化和节点模板约束降低遗漏风险。
- 迁移期间仍可能出现 `state.error` 的残留引用 → 在代码修改时集中替换并加日志验证。
- `flags` 值域扩展后可能与现有监控冲突 → 明确只在 MultiAgentGraph 内部使用并在日志中区分。

## Migration Plan

- 在 `MultiAgentState` 与 `run` 初始化中新增 `flags` 与 `inited_vector_index=false`。
- 批量替换所有节点对 `state.error` 的写入为 `flags`。
- 如仍需全局错误输出，在 `run` 中从 `flags` 汇总后生成错误摘要。

## Open Questions

- `flags` 中 `false` 与 `error` 的语义边界是否需要更细粒度分类？
