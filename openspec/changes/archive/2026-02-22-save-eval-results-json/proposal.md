## Why

评估通过后需要产出可追溯的结果，用于审计、调试和后续复用。目前运行流程在评估通过时不会落盘保存最终的 instruction/input/output，结果容易丢失，且检索上下文可能被截断。

## What Changes

- 在 `run` 起始处清空 `Config.DOC_SAVE_PATH`，避免旧数据污染。
- 当 `eval_node` 通过时，落盘保存包含 `instruction`、`input`、`output` 的 JSON 记录。
- 保留 state 中完整的检索结果（不截断），确保保存的 input 反映完整上下文。

## Capabilities

### New Capabilities
- `eval-result-persistence`: 将评估通过的结果以结构化 JSON 形式持久化保存。

### Modified Capabilities
- `answer-evaluation-loop`: 评估通过时触发 JSON 持久化，并使用未截断的检索上下文。

## Impact

- `agents/multi_agent_graph.py` 的 run 流程与评估节点行为。
- 状态持久化与检索上下文在内存/检查点的使用方。
- `Config.DOC_SAVE_PATH` 对应的文件系统输出。
