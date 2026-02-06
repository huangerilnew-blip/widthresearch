# PROJECT KNOWLEDGE BASE

**Generated:** 2025-02-03
**Commit:** unknown
**Branch:** main

## OVERVIEW

Multi-agent deep search system for literature retrieval and Q&A. Uses hierarchical agents (Planner → Executor) with RAG pipeline for high-quality answers.

**Tech Stack:** Python 3.10+, FastAPI, LangGraph, PostgreSQL, ChromaDB, vLLM (embeddings), TEI (reranker)

## STRUCTURE

```
widthresearch/
├── agents/          # Multi-agent orchestration (Planner, Executor, MultiAgent)
├── tools/
│   ├── core_tools/  # MCP server tools (search)
│   └── normal_tools/# Paper search/download (arxiv, semantic_scholar, etc.)
├── core/
│   ├── rag/         # RAG preprocessing, postprocessing, reranking
│   ├── mcp/         # MCP servers (grep, search_tool, context7_grep)
│   └── config/      # Central configuration
├── api/             # FastAPI routes
├── data/            # Downloads and crunchbase data
└── main.py          # FastAPI entry point
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Agent orchestration | `agents/` | Planner splits queries, Executors execute sub-questions |
| Tool implementations | `tools/` | `core_tools/` = MCP tools, `normal_tools/` = search/download |
| RAG pipeline | `core/rag/` | Vector store, reranking, document processing |
| MCP servers | `core/mcp/` | grep, search_tool, context7_grep integration |
| Configuration | `core/config/config.py` | All constants, LLM types, paths |
| API endpoints | `api/routes.py` | Query submission endpoint |

## CONVENTIONS

**Agent Patterns:**
- All agents use LangGraph StateGraph with TypedDict state
- Memory via AsyncPostgresSaver with thread_id
- Async throughout (async/await)

**Tool Output Format:**
```python
{
  "source_tool": "<tool_name>",
  "result_type": "papers",
  "papers": [...],
  "count": <int>
}
```

**Paper Data Model:**
- Standardized via `tools/core_tools/paper.py` and `tools/normal_tools/paper.py`
- `paper.extra["saved_path"]` for downloaded file path

**Executor Flow (ReAct):**
1. LLM decides if optional tools needed
2. Parallel required search (wikipedia, openalex, semantic_scholar, tavily)
3. Clean + deduplicate results
4. Download papers
5. Return structured results

## ANTI-PATTERNS (THIS PROJECT)

- **DO NOT** modify `core/config/config.py` without explicit instruction
- **NEVER** guess - always verify before making changes (per existing docs)
- **AVOID** downloading PDFs from arXiv - use HTML (ArXiv5) instead (10-20x faster, no anti-crawl)
- **DO NOT** break async patterns - use `asyncio.gather` with `return_exceptions=True`

## UNIQUE STYLES

**Multi-Agent Pattern:**
- PlannerAgent: Splits query into 3+ sub-questions (v2.0 - no DAG dependencies)
- ExecutorAgent Pool: 3 agents by default, concurrent execution
- MultiAgentGraph: 9-node LangGraph pipeline (init_vector_store → plan → execute → collect → process → vectorize → retrieve → question_pool → generate)

**RAG Pipeline:**
1. PDF → Markdown via MinerU service
2. Chunk (MAX_CHUNK_SIZE=1000)
3. Vectorize (BAAI/bge-large-zh-v1.5, 1024-dim)
4. Retrieve (TOP_K=5)
5. Rerank (BAAI/bge-reranker-v2-m3, threshold=0.5, top_n=20)

**Data Source Classification:**
- **Required** (always): wikipedia, openalex, semantic_scholar, tavily
- **Optional** (LLM decides): sec_edgar, akshare
- **Base data** (RAG): crunchbase

## COMMANDS

```bash
# Environment setup
conda create -n agent_backend python=3.10 -y
conda activate agent_backend
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# Dev server
python main.py
# or
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Production
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Build vector store
python core/build_base_vector_store.py

# Tests
bash run_tests.sh
```

## NOTES

**Configuration:**
- LLM providers: OpenAI, Qwen, OneAPI, Ollama
- Default: LLM_TYPE="qwen"
- Config in `core/config/config.py` + `.env` (DB_URI, OPENAI_API_KEY, etc.)

**Critical Paths:**
- `DOC_SAVE_PATH="/home/qinshan/widthresearch/data/downloads"` - downloaded papers
- `VECTOR_STORE_PATH="vector_storage"` - ChromaDB
- `LOG_FILE="logfile/app.log"` - concurrent rotating log (5MB, 3 backups)

**ExecutorAgent Observation Cropping:**
- To reduce token usage, only keeps title, source, preview
- Full JSON stored in state for clean/download
