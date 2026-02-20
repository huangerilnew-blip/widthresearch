# pyright: reportArgumentType=false
# pyright: reportPrivateUsage=false

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


async def reset_checkpoints(pool: AsyncConnectionPool) -> None:
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT tablename
                FROM pg_tables
                WHERE schemaname = 'public'
                  AND tablename LIKE 'checkpoint%';
                """
            )
            rows = await cur.fetchall()
            tables = [row[0] for row in rows]
            if not tables:
                return
            table_list = ", ".join(f'"{name}"' for name in tables)
            await cur.execute(f"TRUNCATE TABLE {table_list} CASCADE;")


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
            await reset_checkpoints(pool)
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
