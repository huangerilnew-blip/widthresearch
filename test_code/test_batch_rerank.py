import asyncio
import os
import time
from typing import List, Tuple, TypedDict

import httpx

from core.config import Config

RERANK_URL = os.getenv("RERANK_URL", Config.RERANK_BASE_URL)
RERANK_MODEL = os.getenv("RERANK_MODEL", "")
TOTAL_CASES = int(os.getenv("BATCH_CASES", "30"))
DOCS_PER_CASE = int(os.getenv("DOCS_PER_CASE", "50"))
DOC_LEN = int(os.getenv("DOC_LEN", "400"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", str(Config.RERANK_BATCH_SIZE)))
MAX_CONCURRENT = int(os.getenv("MAX_CONCURRENT", str(Config.RERANK_MAX_CONCURRENT)))


def build_docs(count: int, doc_len: int) -> List[str]:
    filler = ("lorem ipsum " * ((doc_len // 12) + 1))[:doc_len]
    return [f"Document {i}: {filler}" for i in range(count)]


class RerankCase(TypedDict):
    query: str
    docs: List[str]


def build_cases(total_cases: int, docs_per_case: int, doc_len: int) -> List[RerankCase]:
    docs = build_docs(docs_per_case, doc_len)
    return [
        {
            "query": f"batch rerank query {i}",
            "docs": docs,
        }
        for i in range(total_cases)
    ]


async def resolve_model_id(client: httpx.AsyncClient) -> str:
    if RERANK_MODEL:
        return RERANK_MODEL
    response = await client.get("/v1/models")
    response.raise_for_status()
    payload = response.json()
    data = payload.get("data", [])
    if not data:
        raise RuntimeError(f"No models returned from {RERANK_URL}/v1/models: {payload}")
    return data[0].get("id", "")


async def run_case(
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    case_id: int,
    query: str,
    docs: List[str],
    model_id: str,
) -> Tuple[int, bool, float, str, int]:
    async with sem:
        start = time.perf_counter()
        try:
            response = await client.post(
                "/v1/rerank",
                json={
                    "model": model_id,
                    "query": query,
                    "documents": docs,
                },
            )
            response.raise_for_status()
            result = response.json()
            ranks = result.get("results", [])
            duration = time.perf_counter() - start
            return case_id, True, duration, "", len(ranks)
        except Exception as exc:
            duration = time.perf_counter() - start
            return case_id, False, duration, repr(exc), 0


async def run_batch(
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    batch_id: int,
    batch_cases: List[RerankCase],
    model_id: str,
) -> List[Tuple[int, bool, float, str, int]]:
    tasks = [
        run_case(client, sem, batch_id * 1000 + idx, case["query"], case["docs"], model_id)
        for idx, case in enumerate(batch_cases)
    ]
    results = await asyncio.gather(*tasks, return_exceptions=False)
    ok_count = sum(1 for _, ok, _, _, _ in results if ok)
    print(f"batch {batch_id}: ok={ok_count}/{len(results)}")
    return results


async def main() -> None:
    print("Batch rerank test settings:")
    settings = f"  url={RERANK_URL} cases={TOTAL_CASES} docs_per_case={DOCS_PER_CASE} doc_len={DOC_LEN} batch_size={BATCH_SIZE} max_concurrent={MAX_CONCURRENT}"
    print(settings)

    sem = asyncio.Semaphore(MAX_CONCURRENT)
    cases = build_cases(TOTAL_CASES, DOCS_PER_CASE, DOC_LEN)

    async with httpx.AsyncClient(base_url=RERANK_URL, timeout=120.0) as client:
        model_id = await resolve_model_id(client)
        print(f"  model={model_id}")
        all_results: List[Tuple[int, bool, float, str, int]] = []
        for batch_id, offset in enumerate(range(0, len(cases), BATCH_SIZE), 1):
            batch_cases = cases[offset : offset + BATCH_SIZE]
            batch_results = await run_batch(client, sem, batch_id, batch_cases, model_id)
            all_results.extend(batch_results)

        failures = [item for item in all_results if not item[1]]
        durations = [item[2] for item in all_results]
        avg_duration = sum(durations) / len(durations) if durations else 0.0

        print("\nSummary:")
        print(f"  total={len(all_results)} ok={len(all_results) - len(failures)} fail={len(failures)}")
        print(f"  avg_duration={avg_duration:.3f}s")
        if failures:
            print("  failures (first 5):")
            for case_id, _, duration, error, _ in failures[:5]:
                print(f"    case={case_id} duration={duration:.3f}s error={error}")


if __name__ == "__main__":
    asyncio.run(main())
