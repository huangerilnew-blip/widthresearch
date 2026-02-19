## 1. 核心 LLM 工厂拆分

- [x] 1.1 在 `core/llms.py` 实现 `llama_llm`，返回 `OpenAILike` 与 `OpenAILikeEmbedding`
- [x] 1.2 在 `core/llms.py` 实现 `lang_llm`，返回 `ChatOpenAI` 与 `OpenAIEmbeddings`
- [x] 1.3 保留 `MODEL_CONFIGS` 与默认回退逻辑，确保 `DEFAULT_CHAT_NAME = "qwen"`、`DEFAULT_EMBEDDING_NAME = "bge"` 作为默认初始化值
- [x] 1.4 移除 `get_llm` 并更新 `__main__` 示例改用新接口

## 2. 调用方按框架改造

- [x] 2.1 更新 `agents/multi_agent_graph.py`：LangChain/LangGraph 主流程与评估使用 `lang_llm`
- [x] 2.2 更新 `agents/multi_agent_graph.py`：LlamaIndex 文档处理、`Settings.embed_model`、`VectorStoreManager` 使用 `llama_llm`
- [x] 2.3 更新 `agents/executoragent.py` 使用 `lang_llm` 获取 Chat 模型
- [x] 2.4 更新 `agents/planneragent.py` 使用 `lang_llm` 获取 Chat 模型

## 3. 校验与收敛

- [x] 3.1 运行 `lsp_diagnostics` 或等效检查，确认所有 `get_llm` 引用已移除
- [x] 3.2 复核日志输出仍包含默认回退与配置错误提示
