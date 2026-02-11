import asyncio

from agents.executoragent import ExecutorAgent

# langgraph的记忆管理 ，langgraph 使用技巧
# 人工智能的发展历史，人工智能的影响
QUERY = "langgraph的记忆管理 "
USER_QUERY = "langgraph 使用技巧"
THREAD_ID = "test_thread_001"
USER_ID = "user_001"


async def run_executor() -> None:
    agent = ExecutorAgent(None)
    try:
        result = await agent.ainvoke(query=QUERY, thread_id=THREAD_ID, user_id=USER_ID, user_query=USER_QUERY,sub_url_pool=[])
        print(result)
    finally:
        await agent._clean()


if __name__ == "__main__":
    state=asyncio.run(run_executor())
    