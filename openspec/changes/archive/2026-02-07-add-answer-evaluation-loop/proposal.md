## Why

当前 `multi_agent_graph.py` 中的 `_generate_answer_node` 完成后直接返回结果，缺少对生成答案质量的自检机制。这可能导致回答维度不合理或证据标注存在问题，但没有反馈循环来改进答案质量。

## What Changes

- 在 `MultiAgentState` 中添加 `epoch` 字段，用于追踪生成-评估迭代次数
- 在 `Config` 中添加 `GENER_EPOCH` 配置，控制最大迭代次数
- 创建新的 `eval_node` 节点，用于评估 `_generate_answer_node` 生成的回复
- 评估使用 `Config.LLM_MUTI_AGENT` 指定的大模型
- 评估维度包括：
  - 回答维度是否合理（逻辑结构、回答边界）
  - 证据标注是否存在问题（来源准确性、信息充分性）
- 添加条件路由：评估通过则结束，不通过则回到 `_generate_answer_node` 基于建议修改
- 在初始状态中初始化 `epoch=0`、`last_answer=""`、`last_evaluation=None`
- 通过 `state["messages"]` 传递 SystemMessage（系统 prompt）和 HumanMessage（用户查询）
- 评估节点从 `state["messages"][-1]` 获取最近一次生成的答案
- 评估节点返回结构化结果：`{"passed": bool, "suggestions": List[str]}`
- 生成节点从 `state["messages"]` 读取对话历史，不内部构建 prompt
- 生成节点支持首次生成（无历史建议）和迭代修改（基于 `last_evaluation` 建议）两种模式

## Capabilities

### New Capabilities
- `answer-evaluation-loop`: 答案生成与评估循环能力，通过迭代评估提高答案质量

### Modified Capabilities
<!-- 无现有规范变更，这是新增功能 -->

## Impact

- `agents/multi_agent_graph.py`:
  - `MultiAgentState`: 添加 `epoch: int` 字段
  - `MultiAgentState`: 添加 `last_answer: str` 字段（存储上一次答案）
  - `MultiAgentState`: 添加 `last_evaluation: Optional[Dict]` 字段（存储上一次评估结果）
  - `Config`: 添加 `GENER_EPOCH` 配置项（已存在）
  - `run` 方法: 添加 `SystemMessage` 到 `state["messages"]`，包含生成系统 prompt
  - `_generate_answer_node`: 修改为从 `state["messages"]` 读取对话历史，不内部构建 prompt
  - `_eval_answer_node`: 从 `state["messages"][-1]` 获取最近一次答案，实现评估逻辑
  - 新增 `_should_continue_generation` 条件路由方法
  - `_build_graph`: 修改图结构，添加 `eval_answer` 节点和条件路由
