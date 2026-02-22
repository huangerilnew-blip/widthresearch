## 1. State 扩展与检索结果保存

- [x] 1.1 在 `MultiAgentState` 增加 `retrieved_nodes_score` 字段定义
- [x] 1.2 更新 `_rag_retrieve_node` 写入 `retrieved_nodes_score`（保留原有 `retrieved_nodes`）
- [x] 1.3 校验新增字段不会影响现有流程日志与路由

## 2. 观测数据构建与持久化

- [x] 2.1 新增 `_persist_observation` 函数，负责追加写入项目根目录 `observational_data.json`
- [x] 2.2 在 `run` 中基于 `last_evaluation.passed` 调用 `_persist_observation`
- [x] 2.3 实现 `instruction/input/output` 组装逻辑，解析 `retrieved_nodes_score` 填充 `content` 与 `questions`
- [x] 2.4 处理文件不存在场景，首次写入时创建 `observational_data.json`

## 3. 校验与自检

- [x] 3.1 运行静态检查或 LSP 诊断，确保新增字段与函数无类型错误
- [ ] 3.2 通过本地用例验证评估通过时追加写入，未通过时不写入
