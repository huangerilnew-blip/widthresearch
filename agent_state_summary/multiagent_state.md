MultiAgentGraph state read/write summary

Nodes and state fields

init_vector_store (_init_vector_store_node)
- Reads: none
- Writes: vector_store_initialized, inited_vector_index, flags

plan_query (_plan_query_node)
- Reads: original_query, thread_id, user_id
- Writes: sub_questions, flags

execute_first (_execute_first_node)
- Reads: sub_questions, thread_id, user_id, original_query
- Writes: first_executor_results, url_pool, flags

execute_second (_execute_second_node)
- Reads: sub_questions, thread_id, user_id, original_query, url_pool
- Writes: second_executor_results, url_pool, flags

collect_first (_collect_first_node)
- Reads: first_executor_results
- Writes: first_all_documents, first_processed_file_paths, flags

collect_second (_collect_second_node)
- Reads: second_executor_results, first_processed_file_paths
- Writes: second_all_documents, second_processed_file_paths, flags

process_first_documents (_process_first_documents_node)
- Reads: first_all_documents, first_llama_docs
- Writes: first_llama_docs, flags

process_second_documents (_process_second_documents_node)
- Reads: second_all_documents, second_llama_docs
- Writes: second_llama_docs, flags

vectorize_documents (_vectorize_documents_node)
- Reads: inited_vector_index, first_llama_docs, second_llama_docs
- Writes: flags

rag_retrieve (_rag_retrieve_node)
- Reads: sub_questions, retrieved_epoch
- Writes: retrieved_nodes, retrieved_epoch, correct_context, messages, flags

generate_answer (_generate_answer_node)
- Reads: epoch, messages
- Writes: epoch, messages, flags

eval_answer (_eval_answer_node)
- Reads: messages, retrieved_nodes, final_answer
- Writes: last_evaluation, flags

terminal_error (_terminal_error_node)
- Reads: retrieved_epoch
- Writes: final_answer, flags

Routing helpers
- _should_continue_generation reads: last_evaluation, epoch
- _route_after_retrieve reads: retrieved_nodes, correct_context, retrieved_epoch
