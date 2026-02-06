# NORMAL TOOLS - PAPER SEARCH & DOWNLOAD

Paper search and download tools for academic databases.

## STRUCTURE

```
normal_tools/
├── arxiv.py, arxiv_fixed.py    # arXiv paper search
├── semantic_scholar.py          # AI-enhanced paper search
├── pubmed.py                   # Medical literature
├── openalex*.py               # OpenAlex multiple versions
├── biorxiv.py, medrxiv.py     # Preprint servers
├── tavily.py, exa.py          # Web search
├── crunchbase.py              # Company info
├── paper.py                   # Paper data model
└── searcher.py                # Searcher base class
```

## WHERE TO LOOK

| Task | File | Notes |
|------|------|-------|
| arXiv search | arxiv_fixed.py | HTML download (not PDF) - 10-20x faster |
| Academic search | semantic_scholar.py, openalex.py | Used for reranking |
| Preprints | biorxiv.py, medrxiv.py | PubMed Central integration |
| Companies | crunchbase.py | Base data for RAG |

## CONVENTIONS

**arXiv HTML Download:**
- URL: https://arxiv.org/html/{id} (not pdf/{id}.pdf)
- Download delay: random.uniform(0.5, 1.0) for HTML
- File extension: .html (not .pdf)
- Content-Type check: text/html

**Searcher Pattern:**
- All searchers inherit from searcher.py base class
- Output format matches core_tools specification
- Use paper.py for consistent data structures

**Tool Output Format:**
```python
{
  "source_tool": "<tool_name>",
  "result_type": "papers",
  "papers": [...],
  "count": <int>
}
```

## ANTI-PATTERNS

- **NEVER** download PDFs from arXiv - use HTML (ArXiv5) instead
- **AVOID** long download delays for HTML (0.5-1.0s is sufficient)
- **DO NOT** break paper.py data structure
