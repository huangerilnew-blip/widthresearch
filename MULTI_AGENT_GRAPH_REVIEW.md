# MultiAgentGraph 修改建议评估（基于新版 PlannerAgent）

以下建议基于当前 `agents/multi_agent_graph.py` 与你已修改的 `agents/planneragent.py` 进行对齐分析，不涉及任何代码修改，仅提供方案。

## 1. 依赖源切换（必做）

- 当前仍使用 `agents/agents.py` 的 `PlannerAgent`，与“废弃 agents.py”冲突。
- 建议改为使用 `agents/planneragent.py` 和 `agents/executoragent.py` 的实现，并确保 `ExecutorAgentPool` 同样切换到新版 ExecutorAgent。

## 2. Planner 调用方式与协议对齐

- 新版 `PlannerAgent.invoke()` 需要 `user_query/thread_id/user_id`，并自动注入 `SystemMessage(prompt)`。
- `multi_agent_graph._plan_query_node()` 仍在调用 `planner_agent.graph.ainvoke(initial_state)`，没有 user_id，也没有 prompt。
- 建议改为直接调用 `PlannerAgent.invoke()`，并传入 `user_id`。
- Planner 结果虽然已被解析为 dict，这里我们可以做一下多情况的判断： string（dict）时才 `json.loads`。然后判断dict 是否包含 `tasks`键，同时做好日志处理。

## 3. Executor 调用协议补齐

- 新版 `ExecutorAgent.invoke()` 需要 `user_id/sub_url_pool/user_query`。
- `ExecutorAgentPool` 当前没有传递这些字段，建议统一封装并补齐。
- 建议在 `MultiAgentState` 中加入 `user_id`、`thread_id`、`url_pool`（传递给executoragent的sub_url_pool） 的传递与落地。multiAgentstate 初始化时，"url_pool"设置为空（作为multiagentstate的属性而不是其state的）。

## 4. 输出契约变更：改为从 DOC_SAVE_PATH 采集文件路径

- 你指定“从 `Config.DOC_SAVE_PATH` 中提取完整 file_path（路径 + 文件名）”。
- 因此 `collect_documents` 不应再依赖 `executor_results[i]["downloaded_papers"]`，而是从Config.DOC_SAVE_PATH中获取list[file_path]。
- 建议流程：
  - PlannerAgent执行完之后，分两次调用ExecutorAgent（从而使用所有PlannerAgent生成的子查询("tasks"对应的list中的元素)都被executoragent执行），第一次执行完扫描 `Config.DOC_SAVE_PATH`，先对文档进行去重，去重之后生成将list[file_path]并传入到DocumentProcessor中进行处理。
  - 只保留 `*.md` ,`*.json`和*.pdf`（虽然不太会用到，但是可以加入这个功能）。
  - 输出为绝对路径列表（或 dict：`{"file_path": "..."}`）。
  - 第一次调用ExecutorAgent后立即构建"url_pool"（对第一次使用ExecutorAgent（可以调用多个）返回的"sub_url_pool"进行去重），第一次调用ExecutorAgent 中sub_url_pool参数为空
  - 第二次ExecutorAgent（可以是多个）调用，sub_url_pool参数使用构建好的MultiAgentState的url_pool（第一次调用ExecutorAgent后创建）
  - 特殊情况处理1：Executoragent执行之后在Config.DOC_SAVE_PATH下有可能会出现空文档，需要进行删除。
  - 特殊情况2：多个Executoragent执行之后在Config.DOC_SAVE_PATH下极有可能会保存相似度非常高的文本文件，需要对其进行去重。（两次调用ExecutorAgent，每一次调用完后，先去重然后再进入DocumentProcessor）。去重策略：保留其中一个即可。第二次去重-去除掉第二次新的文档，如果重复文档都是第二次新增的，那保留其中一个即可。


## 5. 并行 fan-in 风险处理（必须明确）

当前流程：`START` 同时进入 `init_vector_store` 与 `plan_query`，二者都指向 `execute_subquestions`，存在竞态与重复执行风险。在document_process之后（所有planneragent生成的自问题全部保存到Config.DOC_SAVE_PATH，且Config.DOC_SAVE_PATH文件全部被document_processor 处理完之后），这时确保init_vector_store完成即可。可以使用加barrier节点这样的方案。

3. 条件路由
   - 这里你提出一个修改方案。

## 6. MultiAgentState 建议补充字段

- `thread_id`、`user_id`、`url_pool` 建议作为状态字段显式传递，避免节点内通过默认值补偿。
- 有助于 Executor/Planner 的一致性与后续日志追踪。

## 7.Config.DOC_SAVE_DOC去重
- 使用两次去重，Executoragent执行完一次就进行一次去重。
- 去重建议，使用scikit—learn包来对文件进行去重
- 去重保留原则，随便保留一个即可
- 阈值：使用Config.DOC_FILTER