# CORE TOOLS - MCP SERVER TOOLS

MCP server implementations for web search and document retrieval.

## STRUCTURE

```
core_tools/
├── tavily.py              # Web search (required)
├── wikipedia_searcher.py   # Wikipedia search (required)
├── exa_context.py         # Context7 integration
├── paper.py              # Standardized Paper data model
├── sec_edgar.py          # SEC filings (optional)
├── akshare_searcher.py    # Financial data (optional)
└── __main__.py          # MCP server entry point
```

## WHERE TO LOOK

| Task | File | Notes |
|------|------|-------|
| Web search | tavily.py | TAVILY_NUM=10, TAVILY_FLOOR_SCORE=0.6 |
| Knowledge base | wikipedia_searcher.py | WIKI_NUM=3, respects Config.LANGUAGE |
| Paper model | paper.py | Paper.extra["saved_path"] stores file location |
| SEC filings | sec_edgar.py | Optional tool, SEC_NUM=3 |

## CONVENTIONS

**Tool Output Format:**
```python
{
  "source_tool": "<tool_name>",
  "result_type": "papers",
  "papers": [...],
  "count": <int>
}
```

**Paper Model:**
- Use paper.py for standardized paper structures
- Downloaded file path in paper.extra["saved_path"]
- Required fields: title, url, abstract (for papers)

**Tool Types:**
- **Required:** Always called by ExecutorAgent (wikipedia, openalex, semantic_scholar, tavily)
- **Optional:** LLM decides (sec_edgar, akshare)

## ANTI-PATTERNS

- **NEVER** return paper data without source_tool field
- **DO NOT** modify paper.py structure without considering downstream consumers
- **AVOID** adding new required tools without updating ExecutorAgent._get_required_tools()
