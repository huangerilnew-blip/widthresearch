# AGENTS MODULE

Multi-agent orchestration using LangGraph StateGraph with async/await.

## STRUCTURE

```
agents/
├── planneragent.py      # Splits queries into 3+ sub-questions
├── executoragent.py     # ReAct pattern: search → clean → download
├── executor_pool.py     # Manages pool of ExecutorAgent instances
└── multi_agent_graph.py # 9-node pipeline orchestrator
```

## WHERE TO LOOK

| Task | File | Notes |
|------|------|-------|
| Query planning | planneragent.py | PlannerAgent v2.0: no DAG dependencies |
| Sub-question execution | executoragent.py | ReAct: LLM decides optional tools |
| Concurrent execution | executor_pool.py | Default 3 agents, pool management |
| Full pipeline | multi_agent_graph.py | init → plan → execute → collect → process → vectorize → retrieve → generate |

## CONVENTIONS

- All agents use LangGraph StateGraph with TypedDict state
- Memory via AsyncPostgresSaver with thread_id for persistence
- Async throughout (asyncio.gather with return_exceptions=True)
- LLM providers: Qwen (default), OpenAI, OneAPI, Ollama

**ExecutorAgent Flow:**
1. llm_decision_node: LLM decides if optional tools needed
2. optional_tool_node (optional): Call sec_edgar, akshare if needed
3. search_node: Parallel required tools (wikipedia, openalex, semantic_scholar, tavily)
4. clean_node: Deduplicate results
5. download_node: Download papers from collected URLs

## ANTI-PATTERNS

- **NEVER** use asyncio.gather without return_exceptions=True
- **DO NOT** break LangGraph TypedDict state patterns
- **AVOID** modifying PlannerAgent/ExecutorAgent state structure without understanding flow
- **NEVER** skip observation cropping - ExecutorAgent._crop_observation saves tokens
