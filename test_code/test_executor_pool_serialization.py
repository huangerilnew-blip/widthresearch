# -*- coding: utf-8 -*-
import asyncio
import os
import sys
from typing import Any, Dict, cast

from psycopg import AsyncConnection
from psycopg.rows import TupleRow
from psycopg_pool import AsyncConnectionPool

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.executor_pool import ExecutorAgentPool
from agents.executoragent import ExecutorAgent
from core.config import Config


class FakeAgent(ExecutorAgent):
    def __init__(self, agent_id: int, tracker: Dict[str, Dict[int, int]]):
        super().__init__(pool=None, modelname=cast(Any, Config.LLM_EXECUTOR))
        self.agent_id = agent_id
        self.tracker = tracker

    async def _ensure_initialized(self):
        return None

    async def ainvoke(self, query, thread_id, user_id, sub_url_pool, user_query):
        current = self.tracker["current"].get(self.agent_id, 0) + 1
        self.tracker["current"][self.agent_id] = current
        self.tracker["max"][self.agent_id] = max(
            self.tracker["max"].get(self.agent_id, 0),
            current,
        )
        await asyncio.sleep(0.05)
        self.tracker["current"][self.agent_id] -= 1
        return {
            "sub_url_pool": [f"url-{query}"],
            "downloaded_papers": [{"id": query}],
        }


class TestExecutorAgentPool(ExecutorAgentPool):
    def __init__(self, pool_size: int, tracker: Dict[str, Dict[int, int]]):
        self.tracker = tracker
        pool: AsyncConnectionPool[AsyncConnection[TupleRow]] = AsyncConnectionPool(
            conninfo=Config.DB_URI,
            min_size=1,
            max_size=1,
            open=False,
        )
        super().__init__(pool=cast(Any, pool), pool_size=pool_size, model=cast(Any, "dummy"))

    def _initialize_agents(self):
        self.agents = []
        self.agent_locks = []
        for i in range(self.pool_size):
            self.agents.append(cast(ExecutorAgent, FakeAgent(i, self.tracker)))
            self.agent_locks.append(asyncio.Lock())


async def run_serialization_test():
    tracker = {"current": {}, "max": {}}
    pool = TestExecutorAgentPool(pool_size=2, tracker=tracker)

    questions = [f"q{i}" for i in range(5)]
    results, updated_url_pool = await pool.execute_questions(
        questions=questions,
        user_query="test",
        base_thread_id="thread",
        user_id="user",
        url_pool=[],
    )

    assert len(results) == len(questions), "result length mismatch"
    assert len(updated_url_pool) == len(questions), "url pool merge mismatch"
    for agent_id, max_concurrent in tracker["max"].items():
        assert max_concurrent <= 1, f"agent {agent_id} ran concurrently"

    print("ExecutorAgentPool serialization test passed")


if __name__ == "__main__":
    asyncio.run(run_serialization_test())
