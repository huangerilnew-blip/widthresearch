# widthresearch

`widthresearch` 是一个面向研究场景的多智能体系统，核心目标是把“问题拆解-证据检索-答案生成-质量评估”做成可复用的工程流水线。

本文档从企业落地常用的 6 个能力维度介绍项目，而非仅描述单个 Agent 功能。

## 1) 智能体编排能力（Agent Orchestration）

- 采用 `LangGraph StateGraph` 构建多节点流水线，覆盖初始化、规划、两阶段执行、文档处理、向量化、检索、生成、评估。
- 在全局编排层统一管理 Planner + Executor Pool + RAG 组件，形成可扩展的多 Agent 协同框架。
- 支持条件路由与分支汇合（如检索后路由、向量化前 join），具备流程级控制能力。

关键实现证据：
- `agents/multi_agent_graph.py`
- `agents/planneragent.py`
- `agents/executoragent.py`
- `agents/executor_pool.py`

## 2) 知识与 RAG 能力（Knowledge & RAG Engineering）

- 内置文档处理链路：PDF/Markdown/JSON 统一转为可检索节点，并补充可回答问题元数据。
- 基于 Chroma + LlamaIndex 的向量库管理，支持基础知识库加载与增量节点写入。
- 提供检索后处理：重排序、阈值过滤、节点去重、问题池构建，提升回答相关性和可解释性。

关键实现证据：
- `core/rag/document_processor.py`
- `core/rag/rag_preprocess_module.py`
- `core/rag/rag_postprocess_module.py`
- `core/rag/reranker.py`

## 3) 外部工具与协议集成能力（Tool/Protocol Integration）

- 通过 MCP 客户端统一接入外部能力，已覆盖 Context7 与 Grep 这类检索工具。
- Planner/Executor 均支持工具调用路径，工具结果通过标准消息结构回流到图状态。
- 保留“必需工具 + 可选工具”混合机制，兼顾稳定召回与动态探索。

关键实现证据：
- `core/mcp/context7_grep.py`
- `core/mcp/AGENTS.md`
- `agents/planneragent.py`
- `agents/executoragent.py`

## 4) 模型工程能力（ModelOps / Multi-LLM Abstraction）

- 统一模型工厂封装 chat 与 embedding 初始化，支持多供应侧配置与默认回退策略。
- 在不同任务层使用差异化模型（规划、执行、评估、Embedding）以平衡质量与成本。
- 配置集中在 `Config`，包含模型选择、重排参数、检索参数、服务地址等关键运行参数。

关键实现证据：
- `core/llms.py`
- `core/config/config.py`
- `agents/multi_agent_graph.py`

## 5) 评估与可观测能力（Evaluation & Observability）

- 生成后引入评估节点（`eval_answer`），支持“生成-评估-再生成”闭环。
- 全流程节点均带结构化日志与状态标记，便于问题定位与运行追踪。
- 通过 `thread_id/user_id` 与 checkpoint 机制，支撑会话级上下文追踪与恢复。

关键实现证据：
- `agents/multi_agent_graph.py`
- `openspec/changes/archive/2026-02-07-add-answer-evaluation-loop/proposal.md`
- `main.py`

## 6) 治理与可靠性能力（Governance & Reliability）

- Executor Pool 为单 Agent 引入串行锁，避免同一 Agent 并发复用导致状态竞态。
- 广泛采用 `asyncio.gather(..., return_exceptions=True)`，避免单点失败拖垮整批任务。
- 通过 OpenSpec 变更档案保留关键可靠性设计意图，支撑工程治理与演进审计。

关键实现证据：
- `agents/executor_pool.py`
- `test_code/test_executor_pool_serialization.py`
- `openspec/changes/archive/2026-02-09-fix-executor-pool-queue/specs/executor-pool-queueing/spec.md`
- `openspec/changes/archive/2026-02-09-fix-executor-pool-queue/design.md`

---

## 当前边界说明

- 项目当前重点是“研究流程与多 Agent 工程化”，并非完整企业 SaaS（如组织/租户/计费/权限门户）产品。
- 但在编排、RAG、工具协议、评估追踪、可靠性控制这 6 个核心能力上，已经具备可继续产品化的技术底座。
