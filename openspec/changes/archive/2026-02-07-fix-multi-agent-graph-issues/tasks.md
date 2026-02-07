## 1. State & Routing Updates

- [x] 1.1 在 `MultiAgentState` 增加 `retrieved_epoch` 与 `set_ques_pool_epoch` 字段并初始化为 0
- [x] 1.2 在图中添加检索与问题池的条件路由逻辑（空结果触发重试，达到 `Config.GENER_EPOCH` 终止）
- [x] 1.3 终止分支返回"系统错误，无法正确回答"的最终答案

## 2. RAG 内容相似度去重

- [x] 2.1 在 `RAGPostProcessModule` 引入 TF-IDF + 余弦相似度去重逻辑
- [x] 2.2 以 `Config.DOC_FILTER` 为阈值，合并相似节点并保留高分节点
- [x] 2.3 保持 rerank 后去重、结果按分数降序输出

## 3. 评估提示上下文与截断

- [x] 3.1 复用检索上下文拼接逻辑，将 `retrieved_nodes` 提供给评估提示构建
- [x] 3.2 单条检索内容超过 500 字符时截断并追加省略标记
- [x] 3.3 确保评估提示保留 Top-K 限制

## 4. 回归与验证

- [x] 4.1 更新相关日志与错误提示，确保重试与终止路径可追踪
- [x] 4.2 运行必要的基本验证（lint/类型检查或最小运行路径）

