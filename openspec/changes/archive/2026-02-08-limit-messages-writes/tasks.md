## 1. 移除非允许节点 messages 写入

- [x] 1.1 移除 `plan_query` 返回结构中的 `messages` 字段，仅保留必要状态与 flags
- [x] 1.2 移除 `execute_first`、`execute_second` 节点返回结构中的 `messages`
- [x] 1.3 移除 `collect_first`、`collect_second` 节点返回结构中的 `messages`
- [x] 1.4 移除 `process_first_documents`、`process_second_documents` 节点返回结构中的 `messages`
- [x] 1.5 移除 `vectorize_documents`、`terminal_error` 节点返回结构中的 `messages`

## 2. 保留允许节点 messages 写入

- [x] 2.1 确认 `rag_retrieve`、`build_question_pool` 保持 `messages` 返回
- [x] 2.2 确认 `generate_answer`、`eval_answer` 保持 `messages` 返回

## 3. 校验与回归

- [x] 3.1 运行静态检查或 LSP 诊断，确保无返回结构语法错误
- [x] 3.2 手动核对 `agents/multi_agent_graph.py` 中 `messages` 写入点仅剩四个允许节点
