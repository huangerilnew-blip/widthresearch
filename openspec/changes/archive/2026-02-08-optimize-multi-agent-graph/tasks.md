## 1. Graph Wiring Updates

- [x] 1.1 更新 `agents/multi_agent_graph.py` 依赖关系，使 `collect_first` 同时指向 `process_first_documents` 与 `execute_second`
- [x] 1.2 调整 `vectorize_documents` 边，仅依赖 `init_vector_store`，并确保流程注释与新依赖一致
- [x] 1.3 在 `rag_retrieve` 之前增加对 `vectorize_documents` 已完成的判断或显式依赖

## 2. State Model Changes

- [x] 2.1 在 `MultiAgentState` 中新增 `first_llama_docs` 与 `second_llama_docs` 字段并初始化
- [x] 2.2 移除或废弃 `llama_docs` 的使用并更新读写逻辑
- [x] 2.3 更新 `NODE_FLAG_KEYS` 与相关节点 flags 写入说明以覆盖新流程

## 3. Node Logic Adjustments

- [x] 3.1 修改 `process_first_documents` 将处理结果写入 `first_llama_docs`
- [x] 3.2 修改 `process_second_documents` 将处理结果写入 `second_llama_docs`
- [x] 3.3 更新 `vectorize_documents`，根据 `state["flags"]` 动态判断阶段完成状态并增量入库
- [x] 3.4 在 `vectorize_documents` 内部记录已入库阶段，避免重复写入

## 4. Validation

- [ ] 4.1 运行最小化流程验证并发路径与入库顺序符合预期
- [ ] 4.2 检查日志与 flags，确认两阶段入库均可触发且无重复写入
