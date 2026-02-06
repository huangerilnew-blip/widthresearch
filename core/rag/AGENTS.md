# RAG PIPELINE

Retrieval-Augmented Generation: preprocessing, vectorization, retrieval, reranking.

## STRUCTURE

```
rag/
├── rag_preprocess_module.py   # VectorStoreManager, document indexing
├── rag_postprocess_module.py  # RAGPostProcessModule, retrieval pipeline
├── reranker.py              # BGEReranker wrapper (TEI service)
├── models.py                # QuestionsPool, BGERerankNodePostprocessor
└── document_processor.py     # PDF → Markdown, chunking, embedding
```

## WHERE TO LOOK

| Task | File | Notes |
|------|------|-------|
| Vector store | rag_preprocess_module.py | ChromaDB + vLLM embeddings |
| Reranking | reranker.py | TEI BGE-reranker-v2-m3 service |
| Document processing | document_processor.py | MinerU: PDF → Markdown |
| Retrieval | rag_postprocess_module.py | Top-K retrieval + deduplication |

## CONVENTIONS

**RAG Pipeline:**
1. PDF → Markdown via MinerU service (localhost:8080)
2. Chunk documents (MAX_CHUNK_SIZE=1000 chars)
3. Vectorize (BAAI/bge-large-zh-v1.5, 1024-dim, vLLM at localhost:8081)
4. Retrieve (TOP_K=5)
5. Rerank (threshold=0.5, top_n=20)

**Configuration:**
- RERANK_MODEL: BAAI/bge-reranker-v2-m3
- RERANK_THRESHOLD: 0.5
- RERANK_TOP_N: 20
- RERANK_BATCH_SIZE: 32
- MAX_CONCURRENT: 5

**QuestionsPool:**
- Combines original sub-questions (Planner) + extracted questions (from retrieved nodes)
- Used for multi-vector retrieval

## ANTI-PATTERNS

- **NEVER** change embedding model without rebuilding vector store
- **DO NOT** set RERANK_THRESHOLD too low (<0.3) - returns irrelevant docs
- **AVOID** MAX_CHUNK_SIZE > 2000 - reduces retrieval precision
