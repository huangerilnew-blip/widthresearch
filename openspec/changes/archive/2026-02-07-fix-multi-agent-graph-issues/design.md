## Context

MultiAgentGraph 目前以无条件边串联节点，错误仅以 `MultiAgentState.error` 单字段存储且会被后续节点覆盖。评估节点仅接收最终答案，无法核验证据与检索内容一致性。RAG 后处理仅按 `node_id` 去重，存在内容重复但 id 不同的污染风险。现有检索上下文已在 `_generate_answer_node` 中构造，但未复用于评估阶段。

## Goals / Non-Goals

**Goals:**
- 让评估阶段可访问检索上下文，并据此核验证据一致性。
- 明确错误传播与终止路径，避免失败继续进入生成环节。
- 在 RAG 后处理阶段补充内容级去重策略。

**Non-Goals:**
- 不改动 Planner/Executor 的核心逻辑或工具调用策略。
- 不引入新的外部依赖或重写向量检索流程。
- 不改变答案生成的整体输出格式。

## Decisions

- **评估输入扩展**：复用 `_generate_answer_node` 的上下文拼接逻辑，将检索片段格式化为 `retrieved_contexts`，并传入 `_build_eval_messages`，让评估模型能核对证据与来源。
  - 备选方案：重新检索一次用于评估。否决原因：成本高、容易与生成阶段上下文不一致。

- **错误传播与重试策略**：在图中引入基于检索与问题池状态的条件路由。
  - 当 `retrieved_nodes` 或 `question_pool` 为空时，触发重试；分别使用 `retrieved_epoch` 和 `set_ques_pool_epoch` 计数。
  - 当对应计数达到 `Config.GENER_EPOCH` 仍未获取成功时，直接终止到 END，并返回“系统错误，无法正确回答”。
  - 备选方案：仅在 `run()` 外层捕获异常。否决原因：节点内错误被吞并、无法阻断后续节点。

- **内容级去重**：在 `RAGPostProcessModule` 中使用 TF-IDF + 余弦相似度进行去重，重合度高于 `Config.DOC_FILTER` 时保留分数最高节点。
  - 备选方案：基于文本 hash 去重。否决原因：无法识别近似重复片段。

## Risks / Trade-offs

- **误判去重** → 过度规范化可能合并语义不同但文本相似的片段 → 限制规范化范围（去空白、大小写、标点）并保留高分节点。
- **错误早停影响可用性** → 某些可恢复错误会提前终止 → 通过分级错误或节点内可恢复异常继续返回默认值。
- **评估提示变长** → 评估输入变大增加成本 → 对检索片段长度做 500 字符截断并保持 Top-K 限制。

## Migration Plan

- 无需数据迁移。
- 修改节点与状态字段后，回归测试主流程；若有问题可通过回滚单个模块恢复。

## Open Questions

- 是否需要为错误类型分级（fatal vs recoverable）以决定是否中止？
- 内容级去重采用 hash 还是轻量相似度（如 SimHash）更合适？
