import asyncio
from typing import Any

from psycopg_pool import AsyncConnectionPool

from agents.multi_agent_graph import MultiAgentGraph
from core.config import Config

SUPER_QUESTIONS_PATH = "super_questions.md"
THREAD_ID = "batch_thread_001"
USER_ID = "batch_user_001"


async def run_from_super_questions() -> None:
    pool: Any = AsyncConnectionPool(
        conninfo=Config.CHECKPOINT_URL,
        min_size=3,
        max_size=6,
        open=False,
        kwargs={"autocommit": True},
    )
    agent = MultiAgentGraph(pool)  # type: ignore[reportArgumentType]

    try:
        open_result = pool.open()
        if asyncio.iscoroutine(open_result):
            await open_result
        await agent.memory.setup()

        consecutive_failures = 0
        with open(SUPER_QUESTIONS_PATH, "r", encoding="utf-8") as file:
            for line in file:
                if not line.startswith("- "):
                    continue
                query = line[2:].strip("\n")
                if not query:
                    continue

                result = await agent.run(query, THREAD_ID, USER_ID)
                status = result.get("status", "fail")

                if status == "pass":
                    consecutive_failures = 0
                else:
                    consecutive_failures += 1
                    if consecutive_failures >= 2:
                        print("========================================")
                        print("!!! STOPPED: 2 CONSECUTIVE FAILURES !!!")
                        print("========================================")
                        break
    finally:
        close_result = pool.close()
        if asyncio.iscoroutine(close_result):
            await close_result


if __name__ == "__main__":
    asyncio.run(run_from_super_questions())
