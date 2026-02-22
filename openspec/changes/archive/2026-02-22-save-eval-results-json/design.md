## Context

当前 MultiAgentGraph 的 run 流程在评估通过时不会落盘保存最终的 instruction/input/output。检索结果会在部分格式化流程中被截断（例如 `_format_retrieved_contexts` 的 500 字限制），导致保存上下文无法完整复现。系统需要在评估通过时输出可追溯的 JSON 结果，并统一追加写入 `observational_data.json`。

## Goals / Non-Goals

**Goals:**
- 评估通过时统一写入 `observational_data.json`，采用追加写入，不删除历史数据。
- `input` 为 `list[dict]`，每个元素包含 `content` 与 `questions` 字段。
- `questions` 取自检索结果的 `questions_this_excerpt_can_answer`，`content` 取自 `node.get_content()`。
- 避免检索结果在保存链路被截断，确保 `content` 为完整原文。

**Non-Goals:**
- 不修改评估逻辑本身的判定标准。
- 不调整 RAG 检索/重排算法或文档处理链路。
- 不引入新的存储后端或外部依赖。

## Decisions

- 在 `_rag_retrieve_node` 中新增 `retrieved_nodes_score` 字段，直接保存 `await rag_module.retrieve_postprecess` 的原始结果（包含 score 与 node）。
- 保持现有 `retrieved_nodes` 不变。
- 在 `run` 中读取 `retrieved_nodes_score` 解析出 `instruction`、`input`、`output` 并写入项目根目录的 `observational_data.json`（追加写入，JSON Lines）。

**instruction/input/output 构建方式**
- `instruction`: 使用 `state.original_query`（用户原始问题）。
- `input`: `list[dict]`，遍历 `retrieved_nodes_score`，每个元素包含 `content` 与 `questions` 两个字段。
  - `content`: `node.get_content()` 的完整文本。
  - `questions`: `node.metadata.get("questions_this_excerpt_can_answer", [])`。
- `output`: 使用最终回答（优先 `state.final_answer`，否则取最后一条 AIMessage 的内容）。

**保存前提与通过依据**
- 仅当 `last_evaluation.passed == true` 时才写入 `observational_data.json`。
- `last_evaluation` 由 `eval_node` 写入，来源于评估模型返回的 JSON 结果。
- `eval_node` 的通过依据：评估模型返回 `{"passed": true, "suggestions": []}`，且其评估对象为 `generate_answer` 生成的最新回答内容。

**保存实现约束**
- 将写入项目根目录 `observational_data.json` 的逻辑封装为独立函数（例如 `_persist_observation`）。
- 在 `run` 中调用该函数完成写入。
- 若 `observational_data.json` 不存在则创建后写入（追加写入模式）。

**代码修改方案（草案）**
- `agents/multi_agent_graph.py`:
  - `_rag_retrieve_node`: 保持现有 `retrieved_nodes = await rag_module.retrieve_postprecess(...)`，并新增 `retrieved_nodes_score` 字段，将 `retrieved_nodes` 原始结果写入该字段。
  - `run`: 在评估通过后解析 `retrieved_nodes_score`，组装 `instruction/input/output`，追加写入项目根目录的 `observational_data.json`。
  - 文件写入方式：`with open(path, "a", encoding="utf-8") as f: f.write(json.dumps(record, ensure_ascii=False) + "\n")`。

**_rag_retrieve_node 改动说明**
- 保持现有的检索与重排序流程不变，仅在 state 中新增 `retrieved_nodes_score` 字段保存原始检索结果（含 score 与 node）。
- 原有 `retrieved_nodes` 继续用于生成提示与后续逻辑，不影响现有输出。

**run 改动方案**
- 在 `run` 中读取 `last_evaluation` 判断是否通过。
- 通过时调用保存函数（如 `_persist_observation`），使用 `retrieved_nodes_score` 解析 `input`，并落盘到 `observational_data.json`。

## Risks / Trade-offs

- 不截断检索结果会增加状态大小 → 仅在保存字段使用完整内容，避免过度传递到 LLM 消息流。
