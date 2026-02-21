import asyncio
import os
from typing import Dict, List

from core.rag.reranker import BGEReranker


QUERY = "RAG 系统中重排序的作用"
DOCUMENT_COUNT = 20
MIN_DOC_LENGTH = 1200


def build_document(base: str, min_length: int) -> str:
    if not base.strip():
        base = "占位文本"
    chunk = f"{base} "
    repeats = (min_length // len(chunk)) + 1
    return (chunk * repeats)[:min_length]


def build_documents() -> List[str]:
    documents: List[str] = []
    for idx in range(DOCUMENT_COUNT):
        if idx < 5:
            base = (
                "重排序用于提升 RAG 检索质量，通过相关性评分筛选候选文档，"
                "尤其在多源检索场景中能有效剔除噪音内容。"
            )
        elif idx < 15:
            base = (
                "检索系统会综合向量召回与关键词匹配，重排序有助于重新评估候选文档，"
                "同时需要考虑上下文一致性与答案覆盖度。"
            )
        else:
            base = (
                "今日天气晴朗，城市交通较为拥堵，适合室内活动，"
                "与检索系统或 RAG 无直接关联。"
            )
        documents.append(build_document(base, MIN_DOC_LENGTH))
    return documents


def assert_sorted_by_score(results: List[Dict[str, float]]) -> None:
    for idx in range(len(results) - 1):
        if results[idx]["score"] < results[idx + 1]["score"]:
            raise AssertionError("rerank 结果未按 score 降序排列")


async def main() -> None:
    if not os.getenv("VLLM_RERANK_MODEL_ID"):
        print("注意: 若使用 vLLM，需要设置 VLLM_RERANK_MODEL_ID")

    reranker = BGEReranker()
    documents = build_documents()

    results: List[Dict[str, float]] = await reranker.rerank_async(QUERY, documents)
    if not results:
        raise AssertionError("返回结果为空")

    for item in results:
        if "index" not in item or "score" not in item:
            raise AssertionError("结果项缺少 index 或 score")
        if not isinstance(item["index"], (int, float)):
            raise AssertionError("index 不是数字")
        if not isinstance(item["score"], float):
            raise AssertionError("score 不是 float")

    assert_sorted_by_score(results)

    print("Top 5 results:")
    for item in results[:5]:
        doc_index: int = int(item.get("index", 0))
        snippet = documents[doc_index][:60].replace("\n", " ")
        print(f"  index={doc_index} score={item['score']:.4f} text={snippet}...")

    await reranker.close()


if __name__ == "__main__":
    asyncio.run(main())
