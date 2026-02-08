## Context

`MultiAgentGraph` 的 `state["question_pool"]` 目前使用自定义 `QuestionsPool` 类，但下游统计与部分访问逻辑按 `List[str]` 处理，存在类型不一致与序列化隐患。LangGraph 状态持久化更适合使用可序列化的基础类型，简化为列表可以降低维护成本。

## Goals / Non-Goals

**Goals:**
- 将 `question_pool` 统一为 `List[str]`，保证状态可序列化且访问一致。
- 保留问题去重逻辑与现有流程行为（构建、路由、生成答案）。
- 移除 `QuestionsPool` 定义与相关调用，减少冗余抽象。

**Non-Goals:**
- 不调整检索/改写问题的算法与质量策略。
- 不引入新的依赖或改变 RAG 模块接口。
- 不做跨模块的大规模重构。

## Decisions

- 使用 `List[str]` 作为 `question_pool` 的唯一形态，并在构建节点中完成去重与合并。
- 保留原有问题顺序（先原始问题，再改写问题），去重采用“保序去重”策略，避免 set 直接打乱顺序。
- `QuestionsPool` 类删除，调用点改为列表操作（`extend` + 去重）。
- 统计字段若需要区分原始/改写数量，在合并前计算并缓存；如无强需求，统一使用总量。

## Risks / Trade-offs

- 问题来源区分丢失 → 如需要统计改写问题数量，在合并前计算并保留计数。
- 去重实现不当可能改变排序 → 使用保序去重逻辑（遍历 + set 记录）。
- 旧代码隐式依赖 `QuestionsPool` 方法 → 全量替换并通过静态搜索确认无遗留调用。

## Migration Plan

- 更新 `MultiAgentState` 类型与相关字段注释。
- 将 `_build_question_pool_node` 等逻辑改为列表合并与保序去重。
- 移除 `core/rag/models.py` 中 `QuestionsPool` 及其导入引用。
- 更新文档（如 `multiagent结构.md`）的类型描述。

## Open Questions

- 是否需要保留“原始问题数量 / 改写问题数量”的独立统计字段？
