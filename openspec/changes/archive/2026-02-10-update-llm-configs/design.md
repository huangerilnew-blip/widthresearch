## Context

当前 `core/llms.py` 通过单一 `MODEL_CONFIGS` 和 `llm_type` 选择模型，chat 与 embedding 混用同一配置层级，且 `embedding_model` 缺失时会在初始化阶段报错。调用方主要集中在 `agents/*` 与 `core/config/config.py`，需要统一更新签名与配置结构。

## Goals / Non-Goals

**Goals:**
- 以 `chat` 与 `embedding` 两类配置明确区分模型配置来源。
- 每个模型配置统一字段：`base_url`、`api_key`、`model_name`。
- 初始化接口改为 `chat_name` 与 `embedding_name`，并做合法性校验与默认值回退。

**Non-Goals:**
- 不新增新的模型提供方或引入额外依赖。
- 不改变 ChatOpenAI/OpenAIEmbeddings 的运行参数行为（如 temperature、timeout、重试策略）。

## Decisions

- **配置结构调整**：将 `MODEL_CONFIGS` 变为 `{"chat": {...}, "embedding": {...}}` 的两层结构，内部按 `qwen` 等模型名索引，避免 chat/embedding 混配。
- **字段统一**：统一使用 `base_url`/`api_key`/`model_name`，在初始化时映射为 LangChain 的 `model` 参数，保持接口一致性。
- **接口签名变更**：`initialize_llm` 与 `get_llm` 改为 `chat_name` 与 `embedding_name`，并在函数内校验是否属于对应配置集合。
- **调用方更新**：`agents/*` 与 `core/config/config.py` 传参改为新的签名，允许 chat/embedding 独立指定或使用默认配置。

## Risks / Trade-offs

- **调用方不一致** → 若遗漏更新会导致运行时参数缺失；通过集中搜索与统一替换降低风险。
- **环境变量缺失** → 新结构仍依赖环境变量，配置不完整会导致初始化失败；在初始化阶段增加清晰错误提示。
- **向后兼容性** → 旧 `llm_type` 入口不再适用；通过变更说明和调用方同步修改来缓解。
