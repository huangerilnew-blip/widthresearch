ExecutorAgent state read/write summary

Nodes and state fields

search (_search_node)
- Reads: sub_query
- Writes: search_results

llm_chat (_llm_chat_node)
- Reads: executor_messages, sub_query, user_query, optional_search_results
- Writes: executor_messages, sub_query (when empty)

optional_tool_node (_optional_tool_node)
- Reads: executor_messages
- Writes: optional_search_results, executor_messages

clean (_clean_node)
- Reads: search_results, optional_search_results, sub_url_pool, user_query, sub_query
- Writes: deduplicated_results, sub_url_pool
- Note: when no results, returns url_pool (does not match state key)

download (_download_node)
- Reads: deduplicated_results, optional_search_results
- Writes: downloaded_papers
