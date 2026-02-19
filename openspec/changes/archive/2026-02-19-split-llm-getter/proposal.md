## Why

当前系统同时使用 LlamaIndex 与 LangChain/LangGraph 两套框架，但它们对 LLM 与 embedding 模型的类型要求不同，导致共享的 `get_llm` 返回值在两侧不兼容，引发运行时问题与维护成本。需要拆分获取逻辑以避免类型冲突并提升可维护性。

## What Changes

- 将 `core/llms.py` 中的 `get_llm` 拆分为面向 LlamaIndex 的 `llama_llm` 和面向 LangChain 的 `lang_llm`。
- LlamaIndex 路径返回 `OpenAILike` 与 `OpenAILikeEmbedding`。
- LangChain 路径返回 `ChatOpenAI` 与 `OpenAIEmbeddings`。
- 更新 `agents/multi_agent_graph.py`、`agents/planneragent.py`、`agents/executoragent.py` 等调用方使用对应方法。

## Capabilities

### New Capabilities
- 无

### Modified Capabilities
- `llm-config-management`: LLM 初始化与获取接口从单一 `get_llm` 拆分为按框架区分的获取方法，并明确返回类型。

## Impact

- 代码：`core/llms.py` 与各 agent 初始化逻辑。
- API：内部 LLM 初始化接口变更（调用方需要调整）。
- 依赖：继续使用现有 LlamaIndex/LangChain 模型类，无新增依赖。
