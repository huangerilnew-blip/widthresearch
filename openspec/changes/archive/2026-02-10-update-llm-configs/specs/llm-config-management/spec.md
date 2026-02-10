## ADDED Requirements

### Requirement: 配置按 chat 与 embedding 分类
系统 MUST 将模型配置拆分为 `chat` 与 `embedding` 两类，并在各自类别下按模型名称（如 `qwen`）进行索引。

#### Scenario: 读取分类配置
- **WHEN** 读取 `MODEL_CONFIGS`
- **THEN** 可以分别通过 `MODEL_CONFIGS["chat"][<name>]` 与 `MODEL_CONFIGS["embedding"][<name>]` 获取对应配置

### Requirement: 配置字段统一
每个模型配置 MUST 仅包含 `base_url`、`api_key`、`model_name` 三个字段，用于初始化对应的 ChatOpenAI 或 OpenAIEmbeddings。

#### Scenario: 初始化字段映射
- **WHEN** 初始化 chat 或 embedding 模型
- **THEN** 分别使用 `model_name` 映射到 LangChain 的 `model` 参数

### Requirement: 初始化参数校验
系统 MUST 校验 `chat_name` 与 `embedding_name` 是否属于对应配置集合，若不存在 MUST 抛出可读错误信息并记录日志。

#### Scenario: 非法模型名称
- **WHEN** 传入的 `chat_name` 或 `embedding_name` 不在对应配置集合中
- **THEN** 初始化失败并输出包含可用名称列表的错误信息
