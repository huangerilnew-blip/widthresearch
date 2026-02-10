## 1. State & Node Cleanup

- [x] 1.1 移除 `MultiAgentState.question_pool` 与 `set_ques_pool_epoch` 字段，新增 `correct_context`
- [x] 1.2 更新 `NODE_FLAG_KEYS` 与 `run` 汇总逻辑，移除 `build_question_pool` 节点
- [x] 1.3 删除 `_build_question_pool_node` 与 `_route_after_question_pool` 实现

## 2. RAG 检索与路由调整

- [x] 2.1 校验 `_rag_retrieve_node` 已构造 `question_pool` 并写入 `state["messages"]`（包含上下文）
- [x] 2.2 在 `_rag_retrieve_node` 设置 `correct_context`（NodeWithScore 为空或问题池为空即为 False）
- [x] 2.3 调整 `_route_after_retrieve`：基于 `retrieved_nodes` 与 `correct_context` 统一重试逻辑

## 3. 生成节点简化与图结构更新

- [x] 3.1 简化 `_generate_answer_node`，仅调用 `self.llm.ainvoke(state["messages"])`
- [x] 3.2 更新 `StateGraph` 节点注册与 conditional edges，移除 `build_question_pool`

## 4. Specs 对齐

- [x] 4.1 更新 `graph-error-propagation` delta：仅使用 `retrieved_epoch`，移除 `set_ques_pool_epoch`
- [x] 4.2 更新 `message-write-scope` delta：移除 `build_question_pool` 写入许可
