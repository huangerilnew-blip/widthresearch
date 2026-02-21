import asyncio
import os

import httpx

# 用于测试 vLLM rerank 接口的返回结果结构和内容，确保接口正常工作并返回预期的数据格式。
# 期望返回 OpenAI 兼容的 /v1/rerank 响应 JSON。


TEST_CASES = [
    {
        "query": "LangGraph 条件边的实现方式",
        "docs": [
            "LangGraph 支持条件边用于动态路由。",
            "这是一个无关的句子。",
            "条件边允许工作流根据状态选择路径。",
        ],
    },
    {
        "query": "RAG 系统中重排序的作用",
        "docs": [
            "重排序可以提升检索质量。",
            "Rerank 会对候选文档评分。",
            "今天是晴天。",
        ],
    },
    {
        "query": "bge-rerank 使用方法",
        "docs": [
            "bge-rerank 是一个 reranker 模型。",
            "TEI 提供 /rerank 接口。",
            "Embedding 模型用于向量化。",
        ],
    },
]


RERANK_URL = os.getenv("RERANK_URL", "http://localhost:8100")
RERANK_MODEL = os.getenv("RERANK_MODEL", "")


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


async def main() -> None:
    async with httpx.AsyncClient(base_url=RERANK_URL, timeout=60.0) as client:
        model_id = await resolve_model_id(client)
        print(f"Using model: {model_id}")
        for idx, case in enumerate(TEST_CASES, 1):
            print(f"\n=== CASE {idx} ===")
            response = await client.post(
                "/v1/rerank",
                json={
                    "model": model_id,
                    "query": case["query"],
                    "documents": case["docs"],
                },
            )
            response.raise_for_status()
            result = response.json()
            print("type(result):", type(result))
            print("result keys:", list(result.keys()))
            for attr in ["results", "data", "items", "output"]:
                value = result.get(attr)
                if value is None:
                    continue
                print(f"result.{attr} type:", type(value))
                print(f"result.{attr}:", value)
                if isinstance(value, list) and value:
                    print(f"first {attr} element type:", type(value[0]))
                    print(f"first {attr} element:", value[0])
                break



if __name__ == "__main__":
    asyncio.run(main())
