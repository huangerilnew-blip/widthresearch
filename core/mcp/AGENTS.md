# MCP SERVERS

Model Context Protocol servers for code search and external integrations.

## STRUCTURE

```
mcp/
├── grep_mcp/             # Codebase grep/search tool
│   ├── server.py          # MCP server implementation
│   └── __main__.py      # Entry point
├── search_tool_mcp/       # Document/code search
│   ├── mcp_server.py
│   └── __main__.py
├── context7_grep.py       # Context7 integration
└── tools.py              # MCP tool definitions
```

## WHERE TO LOOK

| Task | File | Notes |
|------|------|-------|
| Code search | grep_mcp/ | Fast codebase grep via MCP |
| Document search | search_tool_mcp/ | Index-based document search |
| External code | context7_grep.py | Context7 API integration |

## CONVENTIONS

**MCP Protocol:**
- All servers implement MCP protocol
- Entry point via __main__.py
- Used by ExecutorAgent for code search capabilities

**Usage Pattern:**
- ExecutorAgent calls MCP tools through tool interface
- Results flow back as ToolMessages with standard format
- Async/await throughout

## ANTI-PATTERNS

- **NEVER** block MCP server startup - should be non-blocking
- **DO NOT** modify MCP protocol structure without understanding client expectations
- **AVOID** synchronous operations in MCP tool implementations
