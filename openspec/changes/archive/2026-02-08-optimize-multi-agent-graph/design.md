## Context

当前 MultiAgentGraph 采用两阶段流程：第一阶段执行与收集后进入第一阶段文档处理，再进入第二阶段执行、收集与处理。需要将 `collect_first` 之后的 `process_first_documents` 与 `execute_second` 并行化，以缩短关键路径。同时向量化需在 `init_vector_store` 完成后启动，并通过 `state["flags"]` 动态检测第一、二阶段处理完成情况，按完成先后进行增量入库。

LangGraph 并发分支写同一状态 key 需要 reducer。为避免第一、二阶段处理并发写入同一列表导致 `InvalidUpdateError`，需要将 `llama_docs` 拆分为 `first_llama_docs` 与 `second_llama_docs`，由对应节点写入，并在 `vectorize_documents` 中按完成顺序入库。

## Goals / Non-Goals

**Goals:**
- 让第二阶段执行与第一阶段文档处理并行，缩短关键路径。
- 明确向量化同步屏障，在`init_vector_store`、`process_first_documents`都完成的情况下执行（state["flags"]可以提供参考）。
- 保持单次向量化入库路径，将`llama_docs` 拆分为`first_llama_docs`和`second_llama_docs`  。
-  process_first_documents 执行完成将结果保存由 `llama_docs`改为`first_llama_docs`
- process_second_documents 执行完成将结果保存由 `llama_docs`改为`second_llama_docs`

**Non-Goals:**
- 不改动文档处理逻辑（PDF 解析、切分、改写等）。
- 不引入新的向量库或外部依赖。
- 不调整 Executor/Planner 的行为和状态结构。
- 不修复 `need_fix.md` 中未被本变更涉及的其他问题。

## Decisions

1) **并行化第一阶段处理与第二阶段执行**
- 方案：`collect_first` 同时指向 `process_first_documents` 与 `execute_second`。
- 理由：`execute_second` 只依赖 `url_pool` 与 `sub_questions`，不必等待第一阶段处理结束。
- 备选方案：保持现状串行；被否决，因为无法提升并行度。

2) **拆分处理结果字段以支持并行**
- 方案：将 `llama_docs` 拆分为 `first_llama_docs` 与 `second_llama_docs`，分别由 `process_first_documents` 与 `process_second_documents` 写入。
- 理由：避免并发写同一 key，降低 LangGraph 更新冲突风险，同时满足并行执行目标。
- 备选方案：为 `llama_docs` 增加 reducer 以允许并发；被否决，增加状态合并复杂度且不保证顺序。

3) **动态向量化触发与重复检查**
- 方案：`vectorize_documents` 依赖 `init_vector_store` 后启动，通过 `state["flags"]` 动态判断 `process_first_documents` 与 `process_second_documents` 的完成状态。任一阶段完成即立刻对对应的 `first_llama_docs` 或 `second_llama_docs` 入库；入库后再次检查另一阶段状态，若已完成则立即补入。
- 理由：最大化缩短关键路径，避免等待未完成阶段，同时确保两阶段结果都能入库。
- 备选方案：固定等待 `process_first_documents` 或 `process_second_documents`；被否决，不符合动态入库目标。

4) **保持单节点入库与增量处理**
- 方案：继续复用 `vectorize_documents` 单节点，内部按完成顺序增量入库，不新增额外节点。
- 理由：保持结构稳定，配合动态检测满足快速入库。
- 备选方案：新增 `vectorize_first_documents` 与 `vectorize_second_documents`；被否决，扩大变更面。

## Risks / Trade-offs

- **[并行度受限于 process_first_documents]** → 通过让 `execute_second` 并行执行，仍能降低总体延迟。
- **[阶段完成检测不一致]** → 以 `state["flags"]` 作为唯一完成判定，并在每次入库后重新检查另一阶段状态。
- **[重复入库风险]** → 在 `vectorize_documents` 内部记录已入库阶段，避免重复写入。
- **[未覆盖其他竞态风险]** → 明确本变更不处理 `rag_retrieve` 对 `vector_store_index` 的潜在竞态，后续单独跟踪。

## Migration Plan

- 调整 `agents/multi_agent_graph.py` 中的 LangGraph 依赖关系，使 `vectorize_documents` 仅依赖 `init_vector_store`。
- 将 `llama_docs` 拆分为 `first_llama_docs` 与 `second_llama_docs`，并更新对应节点写入逻辑。
- 在 `vectorize_documents` 中增加动态检测与入库逻辑，基于 `state["flags"]` 触发分阶段入库，并记录已入库阶段。
- 使用现有测试或最小化运行样例验证节点顺序与日志输出。
- 回滚策略：恢复原有依赖边配置。

## Open Questions

- 是否需要为 `llama_docs` 增加 reducer，以支持未来进一步并行化？ 答：`llama_docs`被`first_llama_docs`和`second_llama_docs`替代，删除`llama_docs`。state增加`first_llama_docs`和`second_llama_docs`
- 若后续性能仍不足，是否拆分为两次向量化节点？暂不考虑后期性能不足的问题
- 是否需要在 `rag_retrieve` 前显式加入对 `init_vector_store` 的依赖以增强健壮性？需要，添加一个判断，确保`vectorize_documents`必须先完成
