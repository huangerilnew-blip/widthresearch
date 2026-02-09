#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ExecutorAgent Pool
管理多个 ExecutorAgent 实例，支持并发执行
"""

import asyncio
import logging
from typing import List, Dict
from psycopg_pool import AsyncConnectionPool
from concurrent_log_handler import ConcurrentRotatingFileHandler

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.executoragent import ExecutorAgent
from core.config import Config
from langchain_core.messages import HumanMessage
from core.log_config import setup_logger

# 设置日志
logger = setup_logger(__name__)


class ExecutorAgentPool:
    """ExecutorAgent 池
    
    管理多个 ExecutorAgent 实例，支持并发执行多个子问题
    """
    
    def __init__(
        self,
        pool: AsyncConnectionPool,
        pool_size: int,
        model: str = Config.LLM_EXECUTOR
    ):
        """初始化 ExecutorAgent Pool
        
        Args:
            pool: PostgreSQL 连接池
            pool_size: 池大小
            model: 使用的模型
        """
        self.pool = pool
        self.pool_size = pool_size
        self.model = model
        self.agents: List[ExecutorAgent] = []
        self.agent_locks: List[asyncio.Lock] = []
        
        self._initialize_agents()
        
        logger.info(f"初始化 ExecutorAgentPool: pool_size={pool_size}, model={model}")
    
    def _initialize_agents(self):
        """创建指定数量的 ExecutorAgent 实例"""
        for i in range(self.pool_size):
            agent = ExecutorAgent(self.pool, self.model)
            self.agents.append(agent)
            self.agent_locks.append(asyncio.Lock())
            logger.debug(f"创建 ExecutorAgent {i+1}/{self.pool_size}")
        
        logger.info(f"成功创建 {len(self.agents)} 个 ExecutorAgent 实例")
    
    async def execute_questions(
        self,
        questions: List[str],
        user_query: str ,
        base_thread_id: str,
        user_id: str ,
        url_pool: List[str],
        
    ) -> tuple[List[Dict], List[str]]:
        """并发执行多个子问题

        Args:
            questions: 子问题列表
            base_thread_id: 基础线程 ID
            user_id: 用户标识
            url_pool: 全局 URL 池（用于去重）
            user_query: 用户原始查询

        Returns:
            tuple[List[Dict], List[str]]: (所有 ExecutorAgent 的结果列表, 更新后的 URL 池)
        """
        if not questions:
            logger.warning("没有子问题需要执行，planer 可能没有正确分解问题，或者所有子问题都被过滤掉了")
            return [], url_pool or []

        if url_pool is None:
            url_pool = []
            logger.warning("未提供 URL 池，使用空列表作为初始 URL 池,如果是第一次executor，这是正常的；如果是第二次executor，原则上来讲不应该为空")
        logger.info(f"开始并发执行 {len(questions)} 个子问题 (user_id={user_id}, url_pool_size={len(url_pool)})")

        # 创建任务列表
        tasks = []
        for i, question in enumerate(questions):
            # 使用轮询方式分配 Agent
            agent = self.agents[i % self.pool_size]
            agent_lock = self.agent_locks[i % self.pool_size]
            thread_id = f"{base_thread_id}_executor_{i}"

            # 创建异步任务（传递新参数）
            task = self._invoke_agent_with_message(
                agent, agent_lock, question, thread_id, user_id, url_pool, user_query
            )
            tasks.append(task)

            logger.debug(f"分配子问题 {i+1} 到 Agent {i % self.pool_size}")

        # 并发执行所有任务，使用 return_exceptions=True 确保单个失败不影响其他
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理结果
        valid_results = [] # 结构是[{"sub_url_pool": ..., "downloaded_papers": ...}...]
        all_sub_url_pools = []
        failed_count = 0

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"子问题 {i+1} 执行失败: {result}")
                failed_count += 1
            else:
                valid_results.append(result)
                # 收集每个 Agent 返回的 sub_url_pool
                if isinstance(result, dict) and "sub_url_pool" in result:
                    all_sub_url_pools.extend(result["sub_url_pool"])
                logger.debug(f"子问题 {i+1} 执行成功")

        # 全局去重合并 URL 池
        updated_url_pool = list(set(url_pool + all_sub_url_pools))

        logger.info(f"并发执行完成: 成功 {len(valid_results)}/{len(questions)}, 失败 {failed_count}")
        logger.info(f"URL 池更新: {len(url_pool)} -> {len(updated_url_pool)} 个 URL")

        return valid_results, updated_url_pool

    async def _invoke_agent_with_message(
        self,
        agent: ExecutorAgent,
        agent_lock: asyncio.Lock,
        question: str,
        thread_id: str,
        user_id: str,
        url_pool: List[str],
        user_query: str
    ) -> Dict:
        """执行单个 ExecutorAgent，正确初始化 executor_messages

        Args:
            agent: ExecutorAgent 实例
            question: 子问题（字符串）
            thread_id: 线程 ID
            user_id: 用户标识
            url_pool: 全局 URL 池
            user_query: 用户原始查询

        Returns:
            执行结果（包含 sub_url_pool）
        """
        async with agent_lock:
            # 确保异步资源已初始化 self.agents 中的每个 Agent 都已正确初始化
            await agent._ensure_initialized()

            try:
                logger.info(f"executor_pool开始处理子问题 '{question}' (user_id={user_id}, thread_id={thread_id})")
                result = await agent.ainvoke(query=question, thread_id=thread_id,user_id=user_id, sub_url_pool=list(url_pool),user_query=user_query )
                logger.info(f"executor 完成子问题 '{question}' 的处理")
                sub_url_pool = result.get("sub_url_pool", [])
                downloaded_papers = result.get("downloaded_papers", [])
                if not sub_url_pool:
                    logger.warning(f"executor_pool中 完成{question}后sub_url_pool 为空")
                else:
                    logger.info(f"executor_pool中 完成{question}后 sub_url_pool 包含 {len(sub_url_pool)} 个 URL")
                if not downloaded_papers:
                    logger.warning(f"executor_pool中 完成{question}后 downloaded_papers 为空")
                else:
                    logger.info(f"executor_pool中 完成{question}后 downloaded_papers 包含 {len(downloaded_papers)} 个结果")

                # 返回完整结果，包括 sub_url_pool
                return {
                    "sub_url_pool":sub_url_pool,
                    "downloaded_papers": downloaded_papers
                }
            except Exception as e:
                logger.error(f"executor 处理子问题 '{question}' 时出错: {e}")
                import traceback
                traceback.print_exc()
                raise e
    
    async def cleanup(self):
        """清理所有 Agent 资源"""
        logger.info("开始清理 ExecutorAgentPool 资源")
        
        cleanup_tasks = []
        for i, agent in enumerate(self.agents):
            task = agent._clean()
            cleanup_tasks.append(task)
        
        # 并发清理所有 Agent
        await asyncio.gather(*cleanup_tasks, return_exceptions=True)
        
        logger.info(f"成功清理 {len(self.agents)} 个 ExecutorAgent")
    
    def __len__(self) -> int:
        """返回池中 Agent 的数量"""
        return len(self.agents)
    
    def __repr__(self) -> str:
        return f"ExecutorAgentPool(size={len(self.agents)}, model={self.model})"


# 测试代码
if __name__ == "__main__":
    import sys
    sys.path.insert(0, '.')
    
    async def test_executor_pool():
        print("=" * 60)
        print("ExecutorAgentPool 测试")
        print("=" * 60)
        
        # 创建模拟的连接池（实际使用时需要真实的 PostgreSQL 连接）
        from psycopg_pool import AsyncConnectionPool
        
        try:
            # 尝试创建连接池
            pool = AsyncConnectionPool(
                conninfo=Config.DB_URI,
                min_size=1,
                max_size=2,
                open=False  # 不立即打开连接
            )
            
            # 创建 ExecutorAgentPool
            executor_pool = ExecutorAgentPool(
                pool=pool,
                pool_size=3
            )
            
            print(f"\n✓ ExecutorAgentPool 创建成功")
            print(f"  - 池大小: {len(executor_pool)}")
            print(f"  - 模型: {executor_pool.model}")
            print(f"  - {executor_pool}")
            
            # 测试方法存在性
            print("\n✓ 测试方法存在性:")
            methods = ['_initialize_agents', 'execute_questions', 'cleanup']
            for method in methods:
                if hasattr(executor_pool, method):
                    print(f"  ✓ {method}")
                else:
                    print(f"  ✗ {method} 不存在")
            
            print("\n" + "=" * 60)
            print("基础测试通过！")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n✗ 测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    # 运行测试
    asyncio.run(test_executor_pool())
