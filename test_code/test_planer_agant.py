import asyncio

from langchain_core.messages import HumanMessage

from agents.planneragent import PlannerAgent


QUERY = "人工智能在生活中的影响？"
THREAD_ID = "test_thread_001"
UESER_ID = "test_user_001"

async def run_planner() -> None:
    agent = PlannerAgent(None)
    try:
        result = await agent.invoke(user_query=QUERY, thread_id=THREAD_ID, user_id=UESER_ID)
        print(result)
    finally:
        await agent._clean()


if __name__ == "__main__":
    asyncio.run(run_planner())
