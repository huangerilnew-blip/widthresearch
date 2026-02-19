## ADDED Requirements

### Requirement: 提供框架化 LLM 获取接口
系统 MUST 提供 `llama_llm` 与 `lang_llm` 两类获取接口，分别返回 LlamaIndex 与 LangChain 对应的 LLM/Embedding 实例。

#### Scenario: LlamaIndex 获取接口
- **WHEN** 调用 `llama_llm` 获取模型
- **THEN** 返回类型为 `OpenAILike` 与 `OpenAILikeEmbedding`，用于 LlamaIndex 链路

#### Scenario: LangChain 获取接口
- **WHEN** 调用 `lang_llm` 获取模型
- **THEN** 返回类型为 `ChatOpenAI` 与 `OpenAIEmbeddings`，用于 LangChain/LangGraph 链路

## MODIFIED Requirements

### Requirement: 配置字段统一
每个模型配置 MUST 仅包含 `base_url`、`api_key`、`model_name` 三个字段，用于初始化对应的 `ChatOpenAI`/`OpenAIEmbeddings` 或 `OpenAILike`/`OpenAILikeEmbedding`。

#### Scenario: 初始化字段映射
- **WHEN** 通过 `llama_llm` 或 `lang_llm` 初始化 chat 或 embedding 模型
- **THEN** 分别使用 `model_name` 映射到 LangChain 的 `model` 参数或 LlamaIndex 的 `model_name` 参数

### Requirement: 初始化参数校验
系统 MUST 校验 `chat_name` 与 `embedding_name` 是否属于对应配置集合，若不存在 MUST 记录可读错误信息并使用默认值重试；若默认值仍失败 MUST 抛出异常。

#### Scenario: 非法模型名称
- **WHEN** 传入的 `chat_name` 或 `embedding_name` 不在对应配置集合中
- **THEN** 记录包含可用名称列表的错误信息并切换到默认值重试

#### Scenario: 默认配置仍失败
- **WHEN** 默认的 `chat_name` 与 `embedding_name` 初始化失败
- **THEN** 初始化流程必须抛出错误并终止
