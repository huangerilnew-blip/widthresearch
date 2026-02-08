## 1. Document Processing Refactor

- [x] 1.1 将现有 `_process_documents_node` 逻辑抽取为类方法（如 `_process_documents`），支持传入文档集合并返回处理后的节点列表
- [x] 1.2 新增 `_process_first_documents_node`，在第一次去重后调用新方法并更新 `llama_docs`
- [x] 1.3 新增 `_process_second_documents_node`，在第二次去重后调用新方法并更新 `llama_docs`

## 2. Graph Wiring & State Updates

- [x] 2.1 更新 `MultiAgentState` 与节点标记，记录新的处理节点执行状态
- [x] 2.2 调整图构建流程：`collect_first -> process_first_documents -> execute_second`，`collect_second -> process_second_documents -> vectorize_documents`
- [x] 2.3 确认向量化节点继续等待 `init_vector_store` 与第二次处理节点完成

## 3. Validation

- [x] 3.1 运行 LSP 诊断或最小化运行流程，确认新节点可正常更新 `llama_docs`
- [x] 3.2 验证日志与状态标记输出符合预期
