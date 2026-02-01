import asyncio

from agents.executoragent import ExecutorAgent


QUERY = "langchain 中短期记忆管理的最佳实践是什么？"
USER_QUERY = "请提供有关 langchain 短期记忆管理的建议。"
THREAD_ID = "test_thread_001"
USER_ID = "user_001"


async def run_executor() -> None:
    agent = ExecutorAgent(None)
    try:
        result = await agent.invoke(query=QUERY, thread_id=THREAD_ID, user_id=USER_ID, user_query=USER_QUERY)
        print(result)
    finally:
        await agent._clean()


if __name__ == "__main__":
    state=asyncio.run(run_executor())
    