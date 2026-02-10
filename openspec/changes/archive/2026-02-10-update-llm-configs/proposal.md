## Why

当前 LLM 配置把 chat 与 embedding 混在同一层级，通过单一的 llm_type 进行选择，导致配置结构不清晰且缺少 embedding 字段时容易在初始化时报错。为支持更明确的模型类型划分和后续扩展，需要调整配置结构与初始化参数。

## What Changes

- 将 `MODEL_CONFIGS` 拆分为 `chat` 与 `embedding` 两类配置，每类下按 `qwen` 等名称管理，并统一使用 `base_url`/`api_key`/`model_name` 三个字段。
- 将 `initialize_llm` 与 `get_llm` 的 `llm_type` 参数改为 `chat_name` 与 `embedding_name`，并校验是否属于对应配置集合。
- 更新调用方以适配新的参数与配置结构。

## Capabilities

### New Capabilities
- `llm-config-management`: 以 chat/embedding 分类的 LLM 配置管理与选择。

### Modified Capabilities
- 

## Impact

- `core/llms.py` 的配置结构与初始化逻辑
- `agents/*` 与 `core/config/config.py` 的模型名称传参与默认值
- 相关环境变量的读取方式与含义
