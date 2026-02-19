# pyright: reportArgumentType=false
# pyright: reportPrivateUsage=false

import asyncio
import asyncio
import os
from typing import Any

from psycopg_pool import AsyncConnectionPool

from agents.multi_agent_graph import MultiAgentGraph
from core.config import Config

QUERY = "langgraph 高阶技巧有哪些？"
THREAD_ID = "test_thread_001"
USER_ID = "test_user_001"
RUN_FULL = True # 用于控制multiagent是否执行完成


async def run_multiagent() -> None:
    pool: Any = AsyncConnectionPool(
        conninfo=Config.CHECKPOINT_URL,
        min_size=3,
        max_size=6,
        open=False,
        kwargs={"autocommit": True},
    )
    agent = MultiAgentGraph(pool)  # type: ignore[reportArgumentType]
    try:
        if RUN_FULL:
            open_result = pool.open()
            if asyncio.iscoroutine(open_result):
                await open_result
            await agent.memory.setup()
            result = await agent.run(QUERY, THREAD_ID, USER_ID)
            print(result)
        else:
            print(
                "MultiAgentGraph initialized. Set RUN_MULTIAGENT_FULL=1 to run the full pipeline."
            )
    finally:
        close_result = pool.close()
        if asyncio.iscoroutine(close_result):
            await close_result


if __name__ == "__main__":
    asyncio.run(run_multiagent())
