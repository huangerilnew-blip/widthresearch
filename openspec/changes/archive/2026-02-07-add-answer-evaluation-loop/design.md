## Context

当前 `multi_agent_graph.py` 中的 `_generate_answer_node` 完成后直接返回到 `END`，没有对生成答案质量的验证机制。这可能导致：
- 回答维度不合理（如逻辑结构混乱、偏离原始问题）
- 证据标注存在问题（如来源不准确、信息不足未说明）
- 没有机会自动改进低质量答案

项目配置中已存在相关配置项：
- `Config.LLM_MUTI_AGENT`: 评估大模型
- `Config.GENER_EPOCH`: 最大生成迭代次数（默认 3）

约束：
- 使用 LangGraph 的条件路由实现循环
- 必须防止无限循环
- 评估节点应独立于生成节点
- 状态需要在节点间传递 `epoch`、`last_answer`、`last_evaluation` 信息
- 评估节点需返回结构化结果（pass/fail + 具体建议）

## Goals / Non-Goals

**Goals:**
- 实现答案生成后的自动评估机制
- 根据评估结果决定是否重新生成
- 防止无限循环（通过 `GENER_EPOCH` 控制）
- 使用独立的大模型进行评估，避免生成模型自我肯定

**Non-Goals:**
- 修改 RAG 检索逻辑
- 改变最终答案的输出格式
- 添加人工审核流程
- 修改生成节点的 prompt（保持现有 prompt 不变）

## Decisions

### Decision 1: 使用条件边实现循环而非递归调用

**选择:** 使用 LangGraph 的条件边（conditional edges）在 `generate_answer` 和 `eval_answer` 之间路由

**理由:**
- LangGraph 的状态机设计更适合这种循环模式
- 条件边清晰表达路由逻辑（基于状态判断）
- 递归调用会增加栈深度，难以调试
- 条件边符合 LangGraph 最佳实践

**备选方案:**
- 在 `_generate_answer_node` 内部递归调用自己 → 被拒绝，因为会隐藏循环逻辑，难以追踪

### Decision 2: 评估节点独立于生成节点

**选择:** 创建独立的 `_eval_answer_node` 节点，使用不同的 LLM 实例

**理由:**
- 避免生成模型自我评估产生的偏差
- 可以使用更强的模型进行评估（`Config.LLM_MUTI_AGENT` 可能与生成模型不同）
- 分离关注点：生成负责内容创造，评估负责质量把关
- 便于未来单独优化评估 prompt

### Decision 3: 评估维度分为合理性和证据标注

**选择:** 两个独立评估维度：
1. **合理性检查**：
   - 是否围绕原始问题回答
   - 逻辑结构是否清晰
   - 是否存在明显矛盾或幻觉
2. **证据标注检查**：
   - 是否所有关键结论都有来源标注
   - 证据是否准确对应检索内容
   - 是否明确说明信息不足的部分

**理由:**
- 分离评估维度更清晰，便于后续调整
- 两个维度对应原始 prompt 的两个核心要求
- 可以为不同维度设置不同权重

### Decision 4: State 中使用 epoch 计数器

**选择:** 在 `MultiAgentState` 中添加 `epoch: int` 字段，每次迭代 +1

**理由:**
- 简单直接，状态清晰可见
- 方便调试和日志追踪
- 符合 LangGraph 的状态传递模式

**备选方案:**
- 使用状态中的 `messages` 长度推断 → 被拒绝，不够明确
- 使用外部计数器 → 被拒绝，应该保持在 LangGraph 状态机内

### Decision 5: 使用 Messages 字段传递 prompt 和答案历史

**选择:** 通过 `state["messages"]` 字段传递系统 prompt 和对话历史，而不是在 `_generate_answer_node` 内部构建 prompt

**实现方式:**
- 在 `run` 方法中添加 `SystemMessage`（包含生成系统 prompt）到 `messages`
- 保持 `HumanMessage` 包含用户原始查询
- `_generate_answer_node` 从 `state["messages"]` 读取对话历史
- `_generate_answer_node` 不再内部构建 prompt，直接使用 messages
- `eval_node` 从 `state["messages"][-1]` 获取最近一次生成的答案（AIMessage）

**理由:**
- 符合 LangGraph 的状态传递和消息管理设计理念
- 系统提示词集中管理，便于维护和调整
- 支持完整的对话历史追踪
- 评估节点自然访问之前的答案（通过 messages 历史）
- 代码结构更清晰，prompt 构建逻辑与节点实现分离

**备选方案:**
- 在每个节点内部构建 prompt → 被拒绝，因为：
  - 重复的 prompt 构建逻辑
  - 难以追踪完整的对话历史
  - 不符合 LangGraph 最佳实践

### Decision 6: 评估失败时基于建议增量修改答案

**选择:** 评估不通过时，将评估建议反馈给 `_generate_answer_node`，基于之前的答案和建议进行修改

**理由:**
- 基于反馈的迭代修改比完全重新生成更高效
- 保留之前答案的有效部分，只修改有问题的地方
- 评估节点返回具体建议（如"缺少证据标注"、"逻辑混乱"），引导 LLM 精确改进
- 类似于人工审阅的工作流程：生成 → 反馈 → 修改 → 再评估

**工作流程:**
- 首次生成：`_generate_answer_node` 基于检索内容生成初始答案（AIMessage1）
- 评估：`_eval_answer_node` 评估答案，返回修改建议（AIMessage2）
- 迭代修改：`_generate_answer_node` 接收（AIMessage1 + AIMessage2）生成修改后答案（AIMessage3）
- 循环：直到评估通过或达到 `GENER_EPOCH` 限制

**State 传递:**
- `last_answer`: 上一次生成的答案
- `last_evaluation`: 上一次的评估结果（包含具体问题和建议）
- `final_answer`: 当前最终答案（每次迭代更新）

**风险:** 修改后的答案可能引入新问题，但评估循环会持续捕捉

## Risks / Trade-offs

### Risk 1: 评估节点可能误判

**风险**: 评估 LLM 可能误判高质量答案为不合格，导致不必要的重生成

**缓解**:
- 在评估 prompt 中明确评分标准
- 可以设置评估结果的置信度阈值，低于阈值时不判定为不通过
- 日志中记录每次评估的详细结果，便于分析

### Risk 2: 最大迭代次数后仍无合格答案

**风险**: 达到 `GENER_EPOCH` 限制后仍无法生成合格答案，但系统会使用最后一次生成的答案

**缓解**:
- 记录所有迭代历史，便于后续分析
- 在最终答案中附加警告信息（如"已迭代 3 次，答案可能不完美"）
- 可以考虑增加一个降级策略：多次失败后返回简化版本

### Trade-off: 额外的 LLM 调用成本

**权衡**: 每次迭代增加一次评估 LLM 调用，增加延迟和成本

**理由**:
- 质量提升带来的价值超过额外成本
- 用户期望的准确性和可靠性更高
- 可以通过 `GENER_EPOCH` 控制成本上限

### Risk 3: System prompt 构建位置设计

**风险**: 如果系统 prompt 构建在错误的位置（如每个节点内部），可能导致不一致或难以维护

**缓解**:
- 将系统 prompt 集中在 `run` 方法中，通过 `SystemMessage` 传递
- 使用 LangGraph 的 messages 管理机制，保持对话历史
- `_generate_answer_node` 只负责处理 messages，不构建 prompt

### Risk 4: 评估 prompt 设计不当导致评估不准确

**风险**: 如果评估 prompt 设计不清晰，评估结果可能不可靠

**缓解**:
- 提供明确的具体判断标准
- 使用 WHEN/THEN 格式的评估条件
- 初始阶段可以用人工验证评估结果，调整 prompt
