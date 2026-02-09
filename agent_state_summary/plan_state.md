PlannerAgent state read/write summary

Nodes and state fields

llm_chat (_llm_chat)
- Reads: planner_messages, epoch
- Writes: planner_messages, epoch

tool_node (_tool_node)
- Reads: planner_messages
- Writes: planner_messages

persist_result (_persist_result)
- Reads: planner_messages
- Writes: planner_result

condition_router (_condition_router)
- Reads: planner_messages, epoch
- Writes: planner_result (when epoch max)
