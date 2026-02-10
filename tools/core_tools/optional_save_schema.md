query-docs 记录（_build_query_docs_records）：
- text
- metadata 内新增：
  - tool: "query-docs"
  - source: "context7_query_docs"
  - library_id（来自 library_id 或 libraryId）
  - query（来自 tool_args["query"]）
grep_query 记录（_build_grep_query_records，有 results_by_repository 时）：
- text
- metadata 内新增：
  - tool: "grep_query"
  - source: "grep"
  - repository
  - file_path
  - branch
  - line_numbers
  - language
  - total_matches
  - query（来自返回体或 tool_args["query"]）