## ADDED Requirements

### Requirement: 单个 ExecutorAgent 串行执行
ExecutorAgentPool SHALL ensure any single ExecutorAgent processes at most one question concurrently, and additional questions assigned to the same agent MUST wait until the current question finishes.

#### Scenario: 超过池大小时按 agent 排队执行
- **WHEN** questions 数量大于 pool_size 并触发复用同一 ExecutorAgent
- **THEN** 该 ExecutorAgent 的后续问题必须等待当前问题完成后再开始

### Requirement: execute_questions 接口保持兼容
ExecutorAgentPool MUST keep the execute_questions signature and return structure unchanged, returning a results list and updated_url_pool that align with current callers.

#### Scenario: 现有调用保持可用
- **WHEN** multi_agent_graph 调用 execute_questions 并传入 questions、base_thread_id、user_id、url_pool、user_query
- **THEN** 返回值必须包含与输入 questions 等长的结果列表与去重后的 updated_url_pool

### Requirement: 多 agent 并发能力保留
ExecutorAgentPool SHALL allow multiple ExecutorAgent instances to run in parallel up to pool_size while enforcing per-agent serialization.

#### Scenario: 多个 agent 并行执行
- **WHEN** pool_size 大于 1 且存在多个待处理问题
- **THEN** 至少可并行执行多个 agent 的问题，而非全局串行
