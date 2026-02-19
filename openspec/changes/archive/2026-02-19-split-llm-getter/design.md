## Context

当前 `core/llms.py` 通过 `get_llm` 统一返回 `ChatOpenAI` 与 `OpenAILikeEmbedding` 的元组，调用方以解包或索引方式取用。系统同时使用 LlamaIndex 与 LangChain/LangGraph，两者对 LLM 与 embedding 类型要求不同，导致返回值在框架边界不兼容。需要在不破坏现有配置与默认回退逻辑的前提下，将 LLM 获取接口按框架拆分。

## Goals / Non-Goals

**Goals:**
- 提供面向 LlamaIndex 的 `llama_llm`（返回 `OpenAILike` 与 `OpenAILikeEmbedding`）与面向 LangChain 的 `lang_llm`（返回 `ChatOpenAI` 与 `OpenAIEmbeddings`）。
- 保持现有模型配置结构与默认回退策略不变，`DEFAULT_CHAT_NAME = "qwen"`、`DEFAULT_EMBEDDING_NAME = "bge"` 继续作为默认初始化值。
- 明确调用方按框架选择接口，避免不兼容类型被误用。

**Non-Goals:**
- 不新增新的模型供应商或配置项。
- 不改变现有业务流程（Planner/Executor/RAG 逻辑）。
- 不调整向量存储或 RAG 的算法行为。

## Decisions

- **拆分接口而非扩展参数**：采用两个显式方法（`llama_llm`、`lang_llm`）替代单一 `get_llm` 的模式，避免调用方自行判断框架类型而引入分支。
- **复用配置与校验逻辑**：沿用 `MODEL_CONFIGS` 与默认回退机制，内部只改变对象实例化类型。
  - 备选方案：分别维护两套配置字典。该方案会造成配置重复与漂移。
- **调用方按职责选择接口**：
  - LlamaIndex 相关（Settings.embed_model、VectorStoreManager、DocumentProcessor）使用 `llama_llm`。
  - LangChain/LangGraph 相关（Planner/Executor、eval）使用 `lang_llm`。
  - MultiAgent 相关（`agents/multi_agent_graph.py`）：
    - `lang_llm`：用于主流程的对话生成与评估（`self.llm`、`self.eval_llm`），保持 LangGraph/LangChain 的消息与调用方式。
    - `llama_llm`：仅用于 LlamaIndex 文档处理链路（`DocumentProcessor` 等）与向量相关初始化；embedding 始终从 `llama_llm` 获取并继续写入 `Settings.embed_model` 与 `VectorStoreManager`。
  - `agents/executoragent.py` 与 `agents/planneragent.py`：仅需 LangChain 聊天模型，改为调用 `lang_llm` 获取 `ChatOpenAI`，不再依赖 embedding 返回值。
- **移除旧接口**：`get_llm` 从 `core/llms.py` 中移除，所有调用点统一切换到 `llama_llm` 或 `lang_llm`。

## Risks / Trade-offs

- **风险**：调用方误用接口导致类型不匹配 → **缓解**：在命名上强调框架（`llama_`/`lang_`），并在代码中集中替换调用点。
- **风险**：拆分后接口数量增加导致维护成本上升 → **缓解**：共用配置与初始化校验，确保修改点仍集中在 `core/llms.py`。
- **权衡**：保留默认回退逻辑可能掩盖配置错误 → **缓解**：保留现有行为以避免破坏性变更，并记录日志提示。
