import asyncio

from tei_client import HttpClient
# 用于测试bge-rerank接口的返回结果结构和内容，确保接口正常工作并返回预期的数据格式。
#返回的数据结构是[RerankScore(score=..., index=0, text=None), ...]


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


async def main() -> None:
    client = HttpClient(url="http://localhost:8100")
    for idx, case in enumerate(TEST_CASES, 1):
        print(f"\n=== CASE {idx} ===")
        result = await client.async_rerank(query=case["query"], texts=case["docs"])
        print("type(result):", type(result))
        print("dir(result) contains:", [name for name in dir(result) if not name.startswith("_")])
        if hasattr(result, "__dict__"):
            print("result.__dict__:", result.__dict__)
        for attr in ["results", "ranks", "scores", "data", "items", "output"]:
            if hasattr(result, attr):
                value = getattr(result, attr)
                print(f"result.{attr} type:", type(value))
                print(f"result.{attr}:", value)
                if isinstance(value, list) and value:
                    print(f"first {attr} element type:", type(value[0]))
                    print(f"first {attr} element:", value[0])
                break



if __name__ == "__main__":
    asyncio.run(main())
