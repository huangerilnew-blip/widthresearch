## Context

当前 `MultiAgentGraph` 的问题池来自 `_rag_retrieve_node`：从检索得到的 BaseNode 提取 metadata 中的 `questions_this_excerpt_can_answer`，去重后写入 `state["messages"]`，并与检索上下文一并记录（`multi_agent_graph.py` 764-765）。`_generate_answer_node` 理论上只需 `self.llm.ainvoke(state["messages"])` 即可使用系统提示词 + 上下文 + 问题池生成答案。此时 `_build_question_pool_node` 再次构造问题池属于重复路径，导致路由与重试机制复杂化。

相关约束与规范：
- `question-pool-state` 要求 `question_pool` 为 `List[str]` 且保序去重
- `graph-error-propagation` 定义 `retrieved_epoch` / `set_ques_pool_epoch` 的重试规则
- `message-write-scope` 限制可写入 `messages` 的节点集合
- `answer-evaluation-loop` 要求 `generate_answer` 从 `messages` 读取 prompt 而非内部拼接

## Goals / Non-Goals

**Goals:**
- 将问题池构建集中到 `_rag_retrieve_node`，确保检索结果与问题池同生命周期、同步存在
- 删除 `_build_question_pool_node` 并简化路由，保持检索/问题池的重试与终止语义
- 以 `questions_this_excerpt_can_answer` 为唯一问题池来源，与 `_rag_retrieve_node` 行为一致
- 明确修改范围：`agents/multi_agent_graph.py` 的节点与路由、相关 specs 的适配
 - 节点级改动范围仅限 `_build_question_pool_node`、`_rag_retrieve_node`、`_generate_answer_node` 及其直接调用的辅助函数

**Non-Goals:**
- 不调整检索、重排序、向量化、评估算法
- 不引入新依赖或改变外部接口
- 不改动 Planner/Executor Agent 的职责

## Decisions

- **统一问题池构建点**：在 `_rag_retrieve_node` 已经完成 `question_pool` 构建，同时将其写入 `state["messages"]`（`multi_agent_graph.py` 764-765），随后由路由判断是否进入生成阶段。`question_pool` 作为 state 字段随 `_build_question_pool_node` 删除。

- **问题池构建规则**：
  - 仅在 `_rag_retrieve_node` 从检索出的 BaseNode 的 `questions_this_excerpt_can_answer` 提取问题并去重。
  - 问题池不再由 `sub_questions` 补齐，避免双路构造导致的不一致。
  - 结果以 SystemMessage 写入 `state["messages"]`，与上下文内容保持同一次检索结果。

- **路由与重试整合**：
  - `_route_after_retrieve` 承担双重判断：`retrieved_nodes` 为空时走检索重试；同时检查 `state["messages"]` 是否已写入检索上下文与问题池（`multi_agent_graph.py` 764-765）。
  - 在 state 中新增 `correct_context` 字段：当 `_rag_retrieve_node` 成功获取 BaseNode 且尝试将所有 BaseNode 的 `meta["questions_this_excerpt_can_answer"]` 收集为 list，只要该 list 非空，就将 `correct_context` 置为 `True`。
  - 若检索得到的 NodeWithScore 数量为 0，则 `correct_context=False`。
  - 若所有节点的 `questions_this_excerpt_can_answer` 为空或缺失，则 `correct_context=False`，路由回 `_rag_retrieve_node` 重试。
  - 仅使用 `retrieved_epoch` 计数，删除 `set_ques_pool_epoch`，超过 `Config.GENER_EPOCH` 进入 `terminal_error`。
  - `build_question_pool` 相关节点与 conditional edges 从图中移除，`rag_retrieve → generate_answer` 成为主路径。

- **删除节点后的连带修改**：
  - 移除 `NODE_FLAG_KEYS` 中的 `build_question_pool`，并同步更新 `run` 汇总逻辑中的节点集合与统计。
  - 删除 `_build_question_pool_node` 与 `_route_after_question_pool`，更新 `StateGraph` 中的节点注册与 conditional edges。
  - 更新 `MultiAgentState`：移除 `question_pool` ,`set_ques_pool_epoch`字段，问题池仅通过 `state["messages"]` 传递。
  - `_generate_answer_node` 仅调用 `self.llm.ainvoke(state["messages"])`，依赖消息链路获取问题池与上下文。

- **生成节点简化**：`_generate_answer_node` 只调用 `self.llm.ainvoke(state["messages"])`，不再重复拼接问题池与上下文，确保消息链路即事实来源。

- **规范同步范围**：
  - `question-pool-state`：更新“构建节点”描述为 `rag_retrieve`。
  - `graph-error-propagation`：问题池重试的路由节点由 `build_question_pool` 调整为 `rag_retrieve`。
  - `message-write-scope`：移除 `build_question_pool` 的写入许可。

## Risks / Trade-offs

- **元数据缺失导致重试** → 如果检索节点缺少 `questions_this_excerpt_can_answer`，问题池可能为空并触发额外重试；缓解方式：明确检索节点构造保证该字段写入。
- **规范同步遗漏** → 若未同步更新 `graph-error-propagation` 与 `message-write-scope`，实现与 specs 不一致；缓解方式：在 specs 阶段明确变更并更新。
- **行为变化对日志/监控** → 删除节点后 flags 与日志节点名变化；缓解方式：更新 `NODE_FLAG_KEYS` 与 run 汇总逻辑的节点集合。
