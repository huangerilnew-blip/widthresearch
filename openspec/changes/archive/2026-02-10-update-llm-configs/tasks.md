## 1. 配置结构调整

- [ ] 1.1 在 `core/llms.py` 重构 `MODEL_CONFIGS` 为 `chat`/`embedding` 两层结构并统一字段
- [ ] 1.2 更新默认配置常量，明确 chat 与 embedding 的默认名称

## 2. 初始化与校验逻辑

- [ ] 2.1 将 `initialize_llm`/`get_llm` 参数改为 `chat_name` 与 `embedding_name`
- [ ] 2.2 增加配置存在性校验与清晰的错误信息
- [ ] 2.3 保持 chat 与 embedding 初始化映射到 LangChain 的 `model` 字段

## 3. 调用方与配置接入

- [ ] 3.1 更新 `core/config/config.py` 中模型名称字段以适配新的双参数
- [ ] 3.2 更新 `agents/*` 中 `get_llm` 调用与默认值传递

## 4. 验证与清理

- [ ] 4.1 运行相关模块的 lsp_diagnostics 或最小运行路径验证改动
- [ ] 4.2 确认无遗留的 `llm_type` 旧参数调用点
