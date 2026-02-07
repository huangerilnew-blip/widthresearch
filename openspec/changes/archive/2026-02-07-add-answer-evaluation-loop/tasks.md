## 1. State 和配置准备

- [ ] 1.1 在 `MultiAgentState` 中添加 `epoch: int` 字段
- [ ] 1.2 在 `MultiAgentState` 中添加 `last_answer: str` 字段（存储上一次答案）
- [ ] 1.3 在 `MultiAgentState` 中添加 `last_evaluation: Optional[Dict]` 字段（存储上一次评估结果）
- [ ] 1.4 在 `run` 方法的初始状态中初始化 `epoch=0`、`last_answer=""`、`last_evaluation=None`

## 2. Messages 传递机制改造

- [ ] 2.1 在 `run` 方法中添加 `SystemMessage`（包含生成系统 prompt）
- [ ] 2.2 将 `SystemMessage` 和 `HumanMessage` 一起放入 `state["messages"]`
- [ ] 2.3 修改 `_generate_answer_node` 从 `state["messages"]` 读取，不内部构建 prompt
- [ ] 2.4 修改 `eval_node` 从 `state["messages"][-1]` 获取最近一次生成的答案

## 3. 评估节点实现

- [ ] 3.1 在 `MultiAgentGraph.__init__` 中创建评估 LLM 实例（使用 `Config.LLM_MUTI_AGENT`）
- [ ] 3.2 设计评估 prompt，包含合理性和证据标注两个维度
- [ ] 3.3 实现 `_eval_answer_node` 方法，包含评估逻辑
- [ ] 3.4 实现 JSON 格式的评估结果解析：`{"passed": bool, "suggestions": List[str]}`
- [ ] 3.5 在 state 中更新 `last_evaluation` 为评估结果

## 4. 生成节点修改

- [ ] 4.1 在 `_generate_answer_node` 中从 `state["messages"]` 读取对话历史
- [ ] 4.2 在 `_generate_answer_node` 中读取当前 `epoch` 值
- [ ] 4.3 实现条件分支：首次生成（`last_evaluation` 为 None）vs 迭代修改（`last_evaluation` 不为 None）
- [ ] 4.4 首次生成：直接调用 LLM，使用 `state["messages"]` 中的 System 和 Human messages
- [ ] 4.5 迭代修改：在 messages 中添加评估建议，调用 LLM 基于历史生成新答案
- [ ] 4.6 在 `_generate_answer_node` 完成后返回 `epoch + 1` 和更新后的 `final_answer`

## 5. 条件路由实现

- [ ] 5.1 实现 `_should_continue_generation` 条件路由方法
- [ ] 5.2 路由逻辑：评估通过（`passed=True`）→ END
- [ ] 5.3 路由逻辑：评估不通过（`passed=False`）且 epoch < GENER_EPOCH → generate_answer
- [ ] 5.4 路由逻辑：评估不通过且 epoch 达到 GENER_EPOCH → END（使用警告日志）

## 6. 图构建修改

- [ ] 6.1 在 `_build_graph` 中添加 `eval_answer` 节点
- [ ] 6.2 修改 `generate_answer` 的边，路由到 `eval_answer` 而非 `END`
- [ ] 6.3 添加条件边：`eval_answer` 根据评估结果路由
- [ ] 6.4 更新流程图注释说明新的循环结构

## 7. 验证

- [ ] 7.1 运行测试查询，验证评估循环正常工作
- [ ] 7.2 检查日志中 epoch 计数正确
- [ ] 7.3 验证达到 GENER_EPOCH 后正确结束
- [ ] 7.4 验证评估不通过时正确重新生成
- [ ] 7.5 验证 `last_answer` 和 `last_evaluation` 在节点间正确传递
- [ ] 7.6 验证 `state["messages"]` 正确传递 System 和 Human messages
- [ ] 7.7 验证基于建议修改时答案质量逐步改善
