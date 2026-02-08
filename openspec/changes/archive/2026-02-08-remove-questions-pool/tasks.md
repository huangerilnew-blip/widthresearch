## 1. 类型与结构调整

- [x] 1.1 将 `MultiAgentState` 中 `question_pool` 类型改为 `List[str]`
- [x] 1.2 移除 `QuestionsPool` 的导入与类定义（`core/rag/models.py`）

## 2. 问题池构建逻辑

- [x] 2.1 将 `_build_question_pool_node` 改为列表合并与保序去重
- [x] 2.2 更新 `_generate_answer_node` 与路由逻辑以适配列表

## 3. 输出与文档同步

- [x] 3.1 更新 `run` 返回结果的计数逻辑（如需要区分原始/改写数量）
- [x] 3.2 更新文档中 `question_pool` 类型说明（如 `multiagent结构.md`，用户确认无需修改）
