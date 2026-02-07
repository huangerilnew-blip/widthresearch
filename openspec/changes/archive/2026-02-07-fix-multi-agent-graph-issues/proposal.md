## Why

当前评估节点无法访问检索上下文，证据一致性无法被验证；同时错误信息会被后续节点覆盖，失败仍进入生成环节并被“无信息”答案掩盖；RAG 仅按 node_id 去重导致重复内容污染上下文。这些问题会降低答案可信度并掩盖系统故障，需要尽快修复。

## What Changes

- 评估节点接收检索上下文与引用信息，用于核验证据一致性。
- 引入明确的错误传播与终止路径，避免失败继续进入生成环节。
- 在 RAG 后处理阶段增加内容级去重（非仅 node_id）。

## Capabilities

### New Capabilities
- `rag-content-deduplication`: 在检索后处理阶段基于内容指纹去重，避免重复片段污染上下文。
- `graph-error-propagation`: 节点失败时可被上游识别并阻断生成流程，错误信息可累计保留。

### Modified Capabilities
- `answer-evaluation-loop`: 评估阶段需基于检索上下文核验证据一致性，不仅检查格式与结构。

## Impact

- agents/multi_agent_graph.py
- core/rag/rag_postprocess_module.py
- core/rag/models.py
- 评估提示词与状态字段结构
