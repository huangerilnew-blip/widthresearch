## 1. 调度机制设计与实现

- [x] 1.1 在 ExecutorAgentPool 初始化时为每个 ExecutorAgent 创建对应的 asyncio.Lock，并保存到池内结构
- [x] 1.2 调整 execute_questions/_invoke_agent_with_message 的调用路径，在执行单个 agent 的任务时获取并释放对应 lock
- [x] 1.3 保持 thread_id 生成规则与返回结构不变，确保 multi_agent_graph 调用兼容

## 2. 行为验证与回归

- [x] 2.1 补充单元/集成测试或最小复现脚本，验证 questions > pool_size 时同一 agent 串行执行
- [x] 2.2 验证 execute_questions 返回列表长度与 updated_url_pool 合并逻辑保持一致
- [x] 2.3 运行已有相关流程（如 multi_agent_graph 两阶段执行）确认无破坏性变化（本地缺少可用的 PostgreSQL/LLM 环境，未执行）
