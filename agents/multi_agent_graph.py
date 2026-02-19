#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MultiAgent 协调器 - LangGraph 版本
使用 LangGraph 构建状态图，实现清晰的流程编排

相比原版 multi_agent.py 的优势：
1. 状态流转清晰可见
2. 易于调试和可视化
3. 支持检查点和状态恢复
4. 更符合 LangGraph 的设计理念
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import ast
import logging
from typing import Dict, Any, List, Optional, TypedDict, Annotated, Union, Set
from psycopg_pool import AsyncConnectionPool
from concurrent_log_handler import ConcurrentRotatingFileHandler
from llama_index.core import Settings
from agents.planneragent import PlannerAgent
from agents.executor_pool import ExecutorAgentPool
from core.rag.rag_preprocess_module import VectorStoreManager
from core.rag.document_processor import DocumentProcessor
from core.rag.rag_postprocess_module import RAGPostProcessModule as RAGModule
from core.rag.models import BGERerankNodePostprocessor
from core.config.config import Config
from core.llms import lang_llm, llama_llm
from core.rag.reranker import BGEReranker
from core.file_deduplicator import FileDeduplicator
from core.log_config import setup_logger

# LangGraph 相关导入
from langgraph.graph import StateGraph, START, END, add_messages
from langchain_core.messages import AnyMessage, AIMessage, HumanMessage, SystemMessage
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

# 设置日志
logger = setup_logger(__name__)

NODE_FLAG_KEYS = [
    "init_vector_store",
    "plan_query",
    "execute_first",
    "collect_first",
    "process_first_documents",
    "execute_second",
    "collect_second",
    "process_second_documents",
    "vectorize_documents",
    "rag_retrieve",
    "generate_answer",
    "eval_answer",
    "terminal_error"
]

# process_first_documents / process_second_documents 的 flags
# 用于 vectorize_documents 判断阶段是否已完成


def merge_flags(
    left: Optional[Dict[str, Union[bool, str]]],
    right: Optional[Dict[str, Union[bool, str]]]
) -> Dict[str, Union[bool, str]]:
    merged = dict(left or {})
    merged.update(right or {})
    return merged


# ============================================================================
# State 定义
# ============================================================================

class MultiAgentState(TypedDict):
    """MultiAgent 的状态定义

    包含整个处理流程中的所有状态信息
    """
    # 消息流（用于 LangGraph 的 add_messages 机制）
    messages: Annotated[list[AnyMessage], add_messages]

    # 输入
    original_query: str  # 用户原始查询
    thread_id: str  # 跨节点传播的唯一会话标识
    user_id: str  # 用户标识，用于权限和日志

    # Planner 阶段
    sub_questions: List[str]  # Planner 生成的子问题

    # Executor 阶段
    first_executor_results: List[Dict]  # 第一阶段执行结果
    second_executor_results: List[Dict]  # 第二阶段执行结果
    url_pool: List[str]  # 全局去重后的 URL 列表

    # 文档处理阶段
    first_all_documents: List[Dict]  # 第一阶段收集的文档
    second_all_documents: List[Dict]  # 第二阶段收集的文档
    first_processed_file_paths: List[Dict]  # 第一阶段去重后的文件路径元数据
    second_processed_file_paths: List[Dict]  # 第二阶段去重后的文件路径元数据
    first_llama_docs: List  # 第一阶段处理后的文档片段
    second_llama_docs: List  # 第二阶段处理后的文档片段

    # RAG 阶段
    retrieved_nodes: List  # RAG 检索结果
    retrieved_epoch: int  # 检索重试次数
    correct_context: bool  # 上下文与问题池是否有效

    # 输出
    final_answer: str  # 最终答案

    # 内部状态
    vector_store_initialized: bool  # 向量库是否已初始化
    inited_vector_index: bool  # 向量索引是否已初始化
    flags: Annotated[Dict[str, Union[bool, str]], merge_flags]  # 节点执行状态
    epoch: int  # 生成答案迭代次数
    last_answer: str  # 上一次生成的答案
    last_evaluation: Optional[Dict[str, Any]]  # 上一次评估结果


# ============================================================================
# MultiAgentGraph - LangGraph 版本
# ============================================================================

class MultiAgentGraph:
    """MultiAgent 协调器 - LangGraph 版本

    流程图：
        START → init_vector_store → plan_query → execute_subquestions
            → collect_documents → process_stage_documents → vectorize_documents
            → rag_retrieve → generate_answer → eval_answer → END

    每个节点负责一个具体任务，状态在节点间流转
    """

    def __init__(
        self,
        pool: AsyncConnectionPool,
        executor_pool_size: int = Config.EXECUTOR_POOL_SIZE,
        planner_model: str = Config.LLM_PLANNER,
        executor_model: str = Config.LLM_EXECUTOR
    ):
        """初始化 MultiAgentGraph

        Args:
            pool: PostgreSQL 连接池（用于短期记忆）
            executor_pool_size: ExecutorAgent 池大小
            planner_model: PlannerAgent 使用的模型
            executor_model: ExecutorAgent 使用的模型
        """
        self.pool = pool
        self.executor_pool_size = executor_pool_size
        self.planner_model = planner_model
        self.executor_model = executor_model

      

        # LLM 和 Reranker
        self.llm = lang_llm(
            chat_name=executor_model,
            embedding_name=Config.LLM_EMBEDDING
        )[0]
        self.llama_llm, self.embeding = llama_llm(
            chat_name=executor_model,
            embedding_name=Config.LLM_EMBEDDING
        )
        if self.embeding:
            Settings.embed_model = self.embeding
        self.eval_llm = lang_llm(
            chat_name=Config.LLM_MUTI_AGENT,
            embedding_name=Config.LLM_EMBEDDING
        )[0]
        self.answer_system_prompt = self._build_answer_system_prompt()
        self.reranker = BGEReranker()
        # 初始化组件
        self.planner_agent = PlannerAgent(pool, planner_model)
        self.executor_pool = ExecutorAgentPool(pool, executor_pool_size, executor_model)
        self.vector_store_manager = VectorStoreManager(embedding_model=self.embeding)
        # 创建 BGE Reranker 节点后处理器
        self.node_postprocessor = BGERerankNodePostprocessor(
            reranker=self.reranker,
            top_n=Config.RERANK_TOP_N,
            score_threshold=Config.RERANK_THRESHOLD
        )

        # 文档处理器
        self.document_processor = DocumentProcessor(
            embedding_model=self.vector_store_manager.embedding_model,
            llm=self.llama_llm
        )

        # 文档去重器
        self.file_deduplicator = FileDeduplicator(
            similarity_threshold=Config.DOC_FILTER
        )

        # 向量存储索引（延迟初始化）
        self.vector_store_index = None

        # 检查点存储器
        self.memory = AsyncPostgresSaver(pool)

        # 构建图
        self.graph = self._build_graph()

        logger.info(f"初始化 MultiAgentGraph: executor_pool_size={executor_pool_size}")

    # ========================================================================
    # 节点实现
    # ========================================================================

    async def _init_vector_store_node(self, state: MultiAgentState) -> Dict[str, Any]:
        """节点 1: 初始化向量存储

        加载基础向量库（公司信息等）
        """
        logger.info("[节点 1] 初始化向量存储")

        try:
            if self.vector_store_index is None:
                self.vector_store_index = self.vector_store_manager.load_or_build_index()
                logger.info("向量存储初始化完成")

            return {
                "vector_store_initialized": True,
                "inited_vector_index": True,
                **self._with_flag(state, "init_vector_store", True)
            }

        except Exception as e:
            logger.error(f"向量存储初始化失败: {e}")
            return {
                "vector_store_initialized": False,
                "inited_vector_index": False,
                **self._with_flag(state, "init_vector_store", "error")
            }

    async def _plan_query_node(self, state: MultiAgentState) -> Dict[str, Any]:
        """节点 2: 调用 PlannerAgent 拆解查询

        将用户查询拆解为多个子问题
        """
        logger.info("[节点 2] 调用 PlannerAgent 拆解查询")

        original_query = state.get("original_query", "")
        thread_id = state.get("thread_id", "default")
        user_id = state.get("user_id", "default_user")

        try:
            # 使用 PlannerAgent.invoke() 方法调用
            result = await self.planner_agent.invoke(
                user_query=original_query,
                thread_id=f"{thread_id}_planner",
                user_id=user_id
            )

            # result 可能是 dict 或 str (JSON 字符串)
            if isinstance(result, str):
                try:
                    data = json.loads(result)
                except json.JSONDecodeError:
                    logger.error(f"解析 JSON 失败: {result}")
                    return {
                        "sub_questions": [original_query],
                        **self._with_flag(state, "plan_query", "error")
                    }
            elif isinstance(result, dict):
                data = result
            else:
                logger.error(f"PlannerAgent 返回了非预期的类型: {type(result)}")
                return {
                    "sub_questions": [original_query],
                    **self._with_flag(state, "plan_query", "error")
                }

            # 提取 tasks
            tasks = data.get('tasks', [])

            if isinstance(tasks, list) and len(tasks) >= 3:
                logger.info(f"查询拆解完成，生成 {len(tasks)} 个子问题")
                return {
                    "sub_questions": tasks,
                    **self._with_flag(state, "plan_query", True)
                }
            elif isinstance(tasks, list) and len(tasks) <3:
                logger.warning(f"子问题数量不足: {len(tasks)}")
                return {
                    "sub_questions": tasks if tasks else [original_query],
                    **self._with_flag(state, "plan_query", True)
                }

        except Exception as e:
            logger.error(f"查询拆解失败: {e}")
            return {
                "sub_questions": [original_query],
                **self._with_flag(state, "plan_query", "error")
            }

    async def _execute_first_node(self, state: MultiAgentState) -> Dict[str, Any]:
        """节点 3a: 第一阶段执行 - 探索阶段 (Exploration)

        使用空 url_pool，让 ExecutorAgent 自由探索
        """
        logger.info("[节点 3a] 第一阶段执行 - 探索阶段（url_pool=[]）")
        
        sub_questions = state.get("sub_questions", [])
        if len(sub_questions) > 3:
            sub_questions = sub_questions[:3]
        if len(sub_questions) <=3:
            sub_questions = sub_questions[:2]
        if not sub_questions:
            logger.warning("没有子问题需要执行第一阶段")
            return {
                "first_executor_results": [],
                "url_pool": [],
                **self._with_flag(state, "execute_first", False)
            }
        thread_id = state.get("thread_id", "default")
        user_id = state.get("user_id", "default_user")
        user_query = state.get("original_query", "")

        try:
            # 第一阶段：url_pool=[] (探索)
            logger.info(f"第一阶段执行: {len(sub_questions)} 个子问题，初始 URL 池为空")
            executor_results, updated_url_pool = await self.executor_pool.execute_questions(
                qustions=sub_questions,
                user_query=user_query,
                base_thread_id=thread_id,
                user_id=user_id,
                url_pool=[],  # 空 url_pool
            )

            logger.info(f"第一阶段执行完成，完成{len(executor_results)} 个子问题的检索")
            logger.info(f"第一阶段收集到 {len(updated_url_pool)} 个 URL")

            return {
                "first_executor_results": executor_results, #结构是[{"sub_url_pool": ..., "downloaded_papers": ...}...]
                "url_pool": updated_url_pool,
                **self._with_flag(state, "execute_first", True)
            }

        except Exception as e:
            logger.error(f"第一阶段执行失败: {e}")
            return {
                "first_executor_results": [],
                "url_pool": [],
                **self._with_flag(state, "execute_first", "error")
            }

    async def _execute_second_node(self, state: MultiAgentState) -> Dict[str, Any]:
        """节点 3b: 第二阶段执行 - 精炼阶段 (Refinement)

        使用第一阶段收集的 url_pool，进行精准检索
        """
        logger.info("[节点 3b] 第二阶段执行 - 精炼阶段（使用第一阶段的 url_pool）")

        sub_questions = state.get("sub_questions", [])
        if len(sub_questions) > 3:
            sub_questions = sub_questions[3:]
        if len(sub_questions) <=3:
            sub_questions = sub_questions[2:]
        if not sub_questions:
            logger.warning("没有子问题需要执行第二阶段")
            return {
                "second_executor_results": [],
                **self._with_flag(state, "execute_second", False)
            }
        thread_id = state.get("thread_id", "default")
        user_id = state.get("user_id", "default_user")
        user_query = state.get("original_query", "")
        url_pool = state.get("url_pool", [])  # 来自第一阶段
        if not url_pool:
            logger.warning("第一阶段没有收集到任何 URL，第二阶段将无法执行url检索去重")
        try:
            # 第二阶段：使用第一阶段收集的 url_pool
            logger.info(f"第二阶段执行: {len(sub_questions)} 个子问题，使用第一阶段收集的 {len(url_pool)} 个 URL")
            executor_results, updated_url_pool = await self.executor_pool.execute_questions(
                qustions=sub_questions,
                base_thread_id=thread_id,
                user_id=user_id,
                url_pool=url_pool,  # 使用第一阶段的 url_pool
                user_query=user_query
            )

            logger.info(f"第二阶段执行完成，获得 {len(executor_results)} 个结果")
            logger.info(f"第二阶段 URL Pool: {len(url_pool)} -> {len(updated_url_pool)}")

            return {
                "second_executor_results": executor_results,
                "url_pool": updated_url_pool,
                **self._with_flag(state, "execute_second", True)
            }

        except Exception as e:
            logger.error(f"第二阶段执行失败: {e}")
            return {
                "second_executor_results": [],
                **self._with_flag(state, "execute_second", "error")
            }

    def _dedupe_preserve_order(self, items: List[str]) -> List[str]:
        """对列表进行去重但保持原有顺序"""
        seen = set()
        deduped = []
        for item in items:
            if item in seen:
                continue
            seen.add(item)
            deduped.append(item)
        return deduped

    def _get_document_path(self, doc: Dict) -> str:
        """从文档元数据中提取文件路径"""
        if not isinstance(doc, dict):
            return ""
        extra = doc.get("extra")
        if isinstance(extra, dict):
            saved_path = extra.get("saved_path")
            if saved_path:
                return saved_path
        return doc.get("local_path") or doc.get("file_path") or doc.get("path") or ""

    def _extract_document_paths(self, documents: List[Dict]) -> List[str]:
        paths: List[str] = []
        for doc in documents:
            path = self._get_document_path(doc)
            if path:
                paths.append(path)
        return self._dedupe_preserve_order(paths) #不适用list（set（））防止顺序被打乱

    def _filter_documents_by_paths(self, documents: List[Dict], allowed_paths: Set[str]) -> List[Dict]:
        filtered: List[Dict] = []
        seen_paths = set()
        for doc in documents:
            path = self._get_document_path(doc)
            if not path or path not in allowed_paths or path in seen_paths:
                continue
            seen_paths.add(path) #防止多个paper其path相同，可能导致重复的paper被保留
            filtered.append(doc)
        return filtered

    async def _collect_first_node(self, state: MultiAgentState) -> Dict[str, Any]:
        """节点 4a: 第一次文档收集与去重

        在第一阶段执行后，对下载的文档进行去重
        """
        logger.info("[节点 4a] 第一次文档收集与去重")

        executor_results = state.get("first_executor_results", [])

        try:
            # 从 executor_results 中提取 downloaded_papers
            all_documents = []
            for result in executor_results:
                if isinstance(result, dict):
                    downloaded_papers = result.get('downloaded_papers', [])
                    all_documents.extend(downloaded_papers)

            document_paths = self._extract_document_paths(all_documents)
            unique_files, duplicate_files = self.file_deduplicator.deduplicate_file_list(document_paths)
            unique_set = set(unique_files)
            unique_documents = self._filter_documents_by_paths(all_documents, unique_set)
            logger.info(
                f"第一次去重完成: 输入 {len(document_paths)} 个, 输出 {len(unique_files)} 个, "
                f"未输出 {len(duplicate_files)} 个"
            )

            # 构建文件元数据列表
            processed_file_paths = []
            for file_path in unique_files:
                if not os.path.exists(file_path):
                    logger.warning(f"文件不存在，跳过元数据构建: {file_path}")
                    continue
                file_info = {
                    "path": file_path,
                    "filename": os.path.basename(file_path),
                    "size": os.path.getsize(file_path),
                    "extension": os.path.splitext(file_path)[1]
                }
                processed_file_paths.append(file_info)

            logger.info(f"从第一阶段 executor_results 提取到 {len(all_documents)} 个文档元数据")

            return {
                "first_all_documents": unique_documents,
                "first_processed_file_paths": processed_file_paths,
                **self._with_flag(state, "collect_first", True)
            }

        except Exception as e:
            logger.error(f"第一次文档收集失败: {e}")
            import traceback
            traceback.print_exc()

            return {
                "first_all_documents": [],
                "first_processed_file_paths": [],
                **self._with_flag(state, "collect_first", "error")
            }

    async def _collect_second_node(self, state: MultiAgentState) -> Dict[str, Any]:
        """节点 4b: 第二次文档收集与去重

        在第二阶段执行后，对下载的文档进行第二次去重
        """
        logger.info("[节点 4b] 第二次文档收集与去重")

        executor_results = state.get("second_executor_results", [])
        previous_file_paths = state.get("first_processed_file_paths", [])

        try:
            # 从 executor_results 中提取 downloaded_papers
            all_documents = []
            for result in executor_results:
                if isinstance(result, dict):
                    downloaded_papers = result.get('downloaded_papers', [])
                    all_documents.extend(downloaded_papers)

            document_paths = self._extract_document_paths(all_documents)
            unique_files, duplicate_files = self.file_deduplicator.deduplicate_file_list(document_paths)

            reference_paths: List[str] = []
            for item in previous_file_paths:
                if not isinstance(item, dict):
                    continue
                path = item.get("path")
                if path:
                    reference_paths.append(path)
            if reference_paths:
                stage_unique_files, cross_stage_duplicates = self.file_deduplicator.deduplicate_against_reference(
                    reference_paths,
                    unique_files
                )
            else:
                stage_unique_files = unique_files
                cross_stage_duplicates = []

            unique_set = set(stage_unique_files)
            unique_documents = self._filter_documents_by_paths(all_documents, unique_set)

            logger.info(
                f"第二次去重完成: 输入 {len(document_paths)} 个, 输出 {len(unique_files)} 个, "
                f"未输出 {len(duplicate_files)} 个"
            )
            if cross_stage_duplicates:
                logger.info(f"跨阶段去重未输出 {len(cross_stage_duplicates)} 个文档")

            # 构建文件元数据列表
            processed_file_paths = []
            for file_path in stage_unique_files:
                if not os.path.exists(file_path):
                    logger.warning(f"文件不存在，跳过元数据构建: {file_path}")
                    continue
                file_info = {
                    "path": file_path,
                    "filename": os.path.basename(file_path),
                    "size": os.path.getsize(file_path),
                    "extension": os.path.splitext(file_path)[1]
                }
                processed_file_paths.append(file_info)

            logger.info(f"从第二阶段 executor_results 提取到 {len(all_documents)} 个文档元数据")
            logger.info(
                f"两阶段总计：{len(previous_file_paths)} + {len(processed_file_paths)} = "
                f"{len(stage_unique_files)} 个去重后的文档"
            )

            return {
                "second_all_documents": unique_documents,
                "second_processed_file_paths": processed_file_paths,
                **self._with_flag(state, "collect_second", True)
            }

        except Exception as e:
            logger.error(f"第二次文档收集失败: {e}")
            import traceback
            traceback.print_exc()

            return {
                "second_all_documents": [],
                "second_processed_file_paths": [],
                **self._with_flag(state, "collect_second", "error")
            }

    async def _process_documents(self, documents: List[Dict], stage_label: str) -> List:
        if not documents:
            logger.info(f"{stage_label}没有文档需要处理")
            return []

        llama_docs = await self.document_processor.get_nodes(documents)
        logger.info(f"{stage_label}文档处理完成: {len(llama_docs)} 个片段")
        return llama_docs

    async def _process_first_documents_node(self, state: MultiAgentState) -> Dict[str, Any]:
        """节点 5a: 第一阶段文档处理

        PDF 转 Markdown、切割、问题改写
        """
        logger.info("[节点 5a] 第一阶段文档处理（去重后）")

        documents = state.get("first_all_documents", [])
        existing_docs = state.get("first_llama_docs", [])

        if not documents and not existing_docs:
            logger.error("第一阶段没有文档需要切割处理")
            return {
                "first_llama_docs": existing_docs,
                **self._with_flag(state, "process_first_documents", False)
            }
        if not documents and existing_docs:
            logger.info("第一阶段已完成但无新文档需要切割处理")
            return {
                "first_llama_docs": existing_docs,
                **self._with_flag(state, "process_first_documents", True)
            }
        try:
            processed_docs = await self._process_documents(documents, "第一阶段")
            merged_docs = existing_docs + processed_docs
            return {
                "first_llama_docs": merged_docs,
                **self._with_flag(state, "process_first_documents", True)
            }
        except Exception as e:
            logger.error(f"第一阶段文档处理失败: {e}")
            return {
                "first_llama_docs": existing_docs,
                **self._with_flag(state, "process_first_documents", "error")
            }

    async def _process_second_documents_node(self, state: MultiAgentState) -> Dict[str, Any]:
        """节点 5b: 第二阶段文档处理

        PDF 转 Markdown、切割、问题改写
        """
        logger.info("[节点 5b] 第二阶段文档处理（去重后）")

        documents = state.get("second_all_documents", [])
        existing_docs = state.get("second_llama_docs", [])

        if not documents and not existing_docs:
            return {
                "second_llama_docs": existing_docs,
                **self._with_flag(state, "process_second_documents", False)
            }
        if not documents and existing_docs:
            logger.info("第二阶段已完成但无新文档需要切割处理")
            return {
                "second_llama_docs": existing_docs,
                **self._with_flag(state, "process_second_documents", True)
            }
        try:
            processed_docs = await self._process_documents(documents, "第二阶段")
            merged_docs = existing_docs + processed_docs
            return {
                "second_llama_docs": merged_docs,
                **self._with_flag(state, "process_second_documents", True)
            }
        except Exception as e:
            logger.error(f"第二阶段文档处理失败: {e}")
            return {
                "second_llama_docs": existing_docs,
                **self._with_flag(state, "process_second_documents", "error")
            }

    async def _vectorize_documents_node(self, state: MultiAgentState) -> Dict[str, Any]:
        """节点 6: 向量化文档并入库

        将处理后的文档向量化并存入向量库
        """
        logger.info("[节点 6] 向量化文档并入库")

        if not state.get("inited_vector_index", False):
            logger.info("向量库尚未初始化，跳过向量化")
            return {
                **self._with_flag(state, "vectorize_documents", False)
            }

        first_llama_docs = state.get("first_llama_docs", [])
        second_llama_docs = state.get("second_llama_docs", [])

        try:
            if first_llama_docs:
                self.vector_store_index.insert_nodes(first_llama_docs)
                logger.info(f"成功添加 {len(first_llama_docs)} 个第一阶段文档到向量库")
            
            if second_llama_docs:
                self.vector_store_index .add_nodes(second_llama_docs)
                logger.info(f"成功添加 {len(second_llama_docs)} 个第二阶段文档到向量库")

            if not first_llama_docs and not second_llama_docs:
                logger.info("阶段一和阶段二都没有新的BaseNodes需要向量化")
            if not second_llama_docs :
                logger.info("阶段二没有新的BaseNodes需要向量化，仅阶段一有文档被向量化")
            return {
                **self._with_flag(state, "vectorize_documents", True)
            }

        except Exception as e:
            logger.error(f"向量化失败: {e}")
            return {**self._with_flag(state, "vectorize_documents", "error")}

    async def _rag_retrieve_node(self, state: MultiAgentState) -> Dict[str, Any]:
        """节点 7: RAG 检索

        基于子问题进行向量检索和重排序
        """
        logger.info("[节点 7] RAG 检索")

        sub_questions = state.get("sub_questions", [])
        retrieved_epoch = state.get("retrieved_epoch", 0)

        if self.vector_store_index is None:
            logger.info("向量化尚未完成或索引为空，跳过检索")
            return {
                "retrieved_nodes": [],
                "retrieved_epoch": retrieved_epoch,
                "correct_context": False,
                "messages": [SystemMessage(content="初始向量化尚未完成，严重错误- 跳过检索")],
                **self._with_flag(state, "rag_retrieve", False)
            }

        try:
            # 创建检索器
            logger.info(f"尝试创建 RAG 检索器，使用 top_k={Config.TOP_K}")
            retriever = self.vector_store_index.as_retriever(similarity_top_k=Config.TOP_K)

            # 创建 RAG 模块
            rag_module = RAGModule(
                retriever=retriever,
                node_postprocessor=self.node_postprocessor,
                top_k=Config.TOP_K
            )

            # 执行检索，获取去重后的节点
            retrieved_nodes = await rag_module.retrieve_postprecess(
                planner_questions=sub_questions
            )

            logger.info(f"RAG 检索完成，获得 {len(retrieved_nodes)} 个节点")

            if not retrieved_nodes:
                updated_epoch = retrieved_epoch + 1
                logger.warning(
                    f"RAG 检索为空，准备重试: retrieved_epoch={updated_epoch}"
                )
                return {
                    "retrieved_nodes": [],
                    "retrieved_epoch": updated_epoch,
                    "correct_context": False,
                    **self._with_flag(state, "rag_retrieve", False)
                }
            contents=[]
            question_pool=[]
            num=0
            for score,node in retrieved_nodes:
                metadata = node.metadata
                content = node.get_content()
                source = metadata.get('url', metadata.get('source', '联网检索获得'))
                questions=metadata.get("questions_this_excerpt_can_answer",[])
                if not questions:
                    logger.warning(f"检索出的basenode缺少 'questions_this_excerpt_can_answer' 元数据，无法展示改写的问题") 
                else:
                    question_pool.extend(questions)
                    logger.info(f"已将检索已将basenode添加到question_pool到,问题个数: {len(questions)}")   
                num+=1
                logger.info(f"检索到节点，来源: {source}, 相似度得分: {score}")
                contents.append({"content": content, "source": source})
            questions_pool: List[str] = []
            seen_questions: Set[str] = set()
            for question in question_pool:
                if not isinstance(question, str):
                    continue
                cleaned = question.strip()
                if not cleaned or cleaned in seen_questions:
                    continue
                seen_questions.add(cleaned)
                questions_pool.append(cleaned)
            correct_context = len(questions_pool) > 0
            updated_epoch = retrieved_epoch + 1 
            logger.info(f"从全部检索结果中提取并去重后，问题池中共有 {len(questions_pool)} 个问题")
            return {
                "retrieved_nodes": contents,
                "retrieved_epoch": updated_epoch,
                "correct_context": correct_context,
                "messages": [
                    SystemMessage(
                        content=contents,
                        metadata={"num_retreved": f"累计检索到 {num} 个相关节点"}
                    ),
                    SystemMessage(
                        content=f"问题池:{questions_pool}",
                        metadata={"message_type": "question_pool"}
                    )
                ],
                **self._with_flag(state, "rag_retrieve", True)
            }

        except Exception as e:
            logger.error(f"RAG 检索失败: {e}")
            updated_epoch = retrieved_epoch + 1
            return {
                "retrieved_nodes": [],
                "retrieved_epoch": updated_epoch,
                "correct_context": False,
                **self._with_flag(state, "rag_retrieve", "error")
            }

    async def _generate_answer_node(self, state: MultiAgentState) -> Dict[str, Any]:
        """节点 9: 生成最终答案

        基于检索结果和问题池生成最终答案
        """
        logger.info("[节点 9] 尝试生成最终答案")
        epoch = state.get("epoch", 0)
        try:
            base_messages: List[AnyMessage] = state["messages"]

            # 调用 LLM 生成答案
            response = await self.llm.ainvoke(base_messages)

            logger.info(f"轮次：{epoch+1}答案生成完成(注:轮次从1开始计数)")

            return {
                "epoch": epoch + 1,
                "messages": [response],
                **self._with_flag(state, "generate_answer", True)
            }

        except Exception as e:
            logger.error(f"生成答案失败: {e}")
            return {
                "epoch": epoch + 1,
                **self._with_flag(state, "generate_answer", "error")
            }

    # ========================================================================
    # 辅助方法
    # ========================================================================

    def _init_flags(self) -> Dict[str, Union[bool, str]]:
        return {node_name: False for node_name in NODE_FLAG_KEYS}

    def _with_flag(
        self,
        state: MultiAgentState,
        node_name: str,
        status: Union[bool, str]
    ) -> Dict[str, Dict[str, Union[bool, str]]]:
        return {"flags": {node_name: status}}

    def _build_answer_system_prompt(self) -> str:
        """构建回答生成的系统提示词"""
        return (
            "你是一名严谨的知识整合与分析专家。\n"
            "你的任务是基于对话中提供的用户问题、改写问题和检索内容生成回答。\n\n"
            "========================\n"
            "【工作原则】\n"
            "1. 优先使用“检索内容”中的信息。\n"
            "2. 不得凭空补充事实。\n"
            "3. 若信息不足，应明确指出“不足以回答”。\n"
            "4. 回答必须围绕用户原始问题。\n"
            "5. 改写问题的作用是辅助理解与语义扩展，而不是替代原问题。\n"
            "6. 输出必须分层组织，并体现逻辑结构。\n"
            "7. 所有结论必须能够在检索内容中找到依据或合理推导路径。\n\n"
            "========================\n"
            "【思考步骤】\n"
            "第一步：问题对齐，明确最终要回答的边界。\n"
            "第二步：信息筛选，提取高度相关事实。\n"
            "第三步：结构化生成，先给核心结论，再展开支撑逻辑。\n"
            "第四步：证据标注，说明来源、推理与不足。\n\n"
            "========================\n"
            "【输出格式】\n"
            "————————————\n"
            "【问题理解】\n"
            "- 原始问题核心意图：\n"
            "- 改写问题的补充作用：\n"
            "- 最终回答边界：\n\n"
            "【关键信息提取】\n"
            "- 事实1：\n"
            "- 事实2：\n"
            "- 事实3：\n\n"
            "【结构化回答】\n"
            "一、核心结论（简洁回答原问题）\n"
            "二、关键支撑点\n"
            "1.\n2.\n3.\n"
            "三、详细解释（分层展开，逻辑清晰）\n\n"
            "【证据说明】\n"
            "- 直接来源：\n"
            "- 合理推断：\n"
            "- 信息不足部分（如有）：\n"
            "————————————\n"
            "请确保回答严格围绕用户原始问题展开。"
        )

    def _format_retrieved_contexts(self, retrieved_nodes: list) -> str:
        """构建检索上下文字符串"""
        retrieved_contexts = []
        for item in retrieved_nodes:
            if instance(item, dict):
                content = item.get("content", "")
                source = item.get("source", "联网检索")
            else:
                logger.warning(f"检索结果格式不正确，预期 dict 但得到 {type(item)}，跳过该项")
                continue

            if len(content) > 500:
                content = content[:500] + "..."

            retrieved_contexts.append(f"来源: {source}\n内容: {content}\n")

        return "\n".join(retrieved_contexts) if retrieved_contexts else "无"

    def _extract_question_pool_from_messages(self, messages: List[AnyMessage]) -> List[str]:
        for message in reversed(messages or []):
            if not isinstance(message, SystemMessage):
                continue
            metadata = getattr(message, "additional_kwargs", {}) or {}
            if metadata.get("message_type") != "question_pool":
                continue
            content = message.content
            if isinstance(content, str) and content.startswith("问题池:"):
                raw = content[len("问题池:"):]
                try:
                    parsed = ast.literal_eval(raw)
                except (ValueError, SyntaxError):
                    return []
                if isinstance(parsed, list):
                    return [str(item) for item in parsed]
                return []
        return []

    def _build_eval_messages(self, answer: str, contexts_str: str) -> List[AnyMessage]:
        """构建评估消息"""
        system_prompt = (
            "你是一名严格的答案评估器。\n"
            "请从两个维度评估答案质量：\n"
            "1) 回答维度是否合理（是否围绕原问题、结构清晰、无明显矛盾）。\n"
            "2) 证据标注是否准确（关键结论是否有来源标注、证据是否匹配、是否说明不足）。\n\n"
            "输出必须是 JSON，格式如下：\n"
            "{\"passed\": true/false, \"suggestions\": [\"问题1\", \"问题2\"]}\n"
            "若通过，suggestions 为空数组。若不通过，提供具体可操作建议。"
        )
        user_prompt = (
            "需要评估的答案如下：\n\n"
            f"{answer}\n\n"
            f"检索内容：\n{contexts_str}\n"
        )
        return [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]

    def _parse_eval_response(self, content: str) -> Dict[str, Any]:
        """解析评估结果"""
        cleaned = content.strip()
        if cleaned.startswith("```") and cleaned.endswith("```"):
            cleaned_lines = [
                line for line in cleaned.splitlines() if not line.strip().startswith("```")
            ]
            cleaned = "\n".join(cleaned_lines).strip()

        try:
            result = json.loads(cleaned)
            logger.info(f"评估结果解析成功: {result}")
        except json.JSONDecodeError:
            logger.warning(f"评估结果{content}解析失败，返回默认不通过")
            return {
                "passed": False,
                "suggestions": ["评估结果解析失败，请重新生成评估结果"]
            }

        passed = bool(result.get("passed", False))
        suggestions = result.get("suggestions", [])
        if not isinstance(suggestions, list):
            suggestions = [str(suggestions)]
        suggestions = [str(item) for item in suggestions if item]
        return {"passed": passed, "suggestions": suggestions}

    async def _eval_answer_node(self, state: MultiAgentState) -> Dict[str, Any]:
        """节点 10: 评估生成答案"""
        logger.info("[节点 10] 评估生成答案")

        messages = state.get("messages", [])
        retrieved_nodes = state.get("retrieved_nodes", [])
        last_message = messages[-1] if messages else None
        if isinstance(last_message, AIMessage):
            answer = str(last_message.content)
        else:
            answer = str(state.get("final_answer", ""))

        contexts_str = self._format_retrieved_contexts(retrieved_nodes)
        eval_messages = self._build_eval_messages(answer, contexts_str)
        try:
            response = await self.eval_llm.ainvoke(eval_messages)
            content = response.content 
            logger.info(f"评估模型原始输出: {content}")
            eval_result = self._parse_eval_response(content)
        except Exception as e:
            logger.error(f"评估答案失败: {e}")
            eval_result = {
                "passed": False,
                "suggestions": ["评估过程出错，请重新生成答案"]
            }
            return {
                "last_evaluation": eval_result,
                **self._with_flag(state, "eval_answer", "error")
            }
        if isinstance(content, str):
            logger.info(f"评估结果原始内容(str格式): {content}")
            return {
                "last_evaluation": eval_result, 
                **self._with_flag(state, "eval_answer", False)
            }
        elif isinstance(content, dict):
            logger.info(f"评估结果原始内容（dict格式）: {content}")
            return {
                "last_evaluation": eval_result,
                **self._with_flag(state, "eval_answer", True)
            }

    def _should_continue_generation(self, state: MultiAgentState) -> str:
        """根据评估结果决定是否继续生成"""
        evaluation = state.get("last_evaluation") or {}
        passed = bool(evaluation.get("passed", False))
        epoch = state.get("epoch", 0)

        if passed:
            return "end"
        if epoch >= Config.GENER_EPOCH:
            logger.warning(f"达到最大迭代次数 {Config.GENER_EPOCH}，结束生成")
            return "end"
        return "generate_answer"

    def _route_after_retrieve(self, state: MultiAgentState) -> str:
        if state.get("retrieved_nodes") and state.get("correct_context"):
            return "generate_answer"

        retrieved_epoch = state.get("retrieved_epoch", 0)
        if retrieved_epoch >= Config.GENER_EPOCH:
            logger.error(
                f"检索重试达到上限 {Config.GENER_EPOCH}/{Config.GENER_EPOCH}，终止流程"
            )
            return "terminal_error"

        logger.info(f"检索为空，继续重试 ({retrieved_epoch}/{Config.GENER_EPOCH})")
        return "rag_retrieve"

    async def _terminal_error_node(self, state: MultiAgentState) -> Dict[str, Any]:
        """终止节点: 返回系统错误回答"""
        error_message = "系统错误，无法正确回答"
        logger.error(
            f"流程终止: retrieved_epoch={state.get('retrieved_epoch', 0)}"
        )
        return {
            "final_answer": error_message,
            **self._with_flag(state, "terminal_error", "error")
        }

    # ========================================================================
    # 图构建
    # ========================================================================

    def _build_graph(self) -> StateGraph:
        """构建 MultiAgent 的状态图（两阶段执行版本）

        两阶段执行流程：
            START ├──> init_vector_store (异步，独立执行)
                  └──> plan_query → execute_first (探索, url_pool=[])
                        → collect_first (第一次去重)
                        ├──> process_first_documents (第一次文档处理)
                        └──> execute_second (精炼, url_pool=<从第一阶段>)
                              → collect_second (第二次去重)
                              → process_second_documents
                        → vectorize_documents (动态入库) → rag_retrieve
                        → generate_answer → eval_answer → END

        关键设计：
        - 两阶段执行：探索（空url_pool） + 精炼（使用第一阶段url_pool）
        - 每阶段后立即去重，避免重复下载
        - vectorize_documents 在 init_vector_store 后启动，按阶段完成状态增量入库
        """
        builder = StateGraph(MultiAgentState)

        # 添加节点
        builder.add_node("init_vector_store", self._init_vector_store_node)
        builder.add_node("plan_query", self._plan_query_node)
        builder.add_node("execute_first", self._execute_first_node)
        builder.add_node("collect_first", self._collect_first_node)
        builder.add_node("process_first_documents", self._process_first_documents_node)
        builder.add_node("execute_second", self._execute_second_node)
        builder.add_node("collect_second", self._collect_second_node)
        builder.add_node("process_second_documents", self._process_second_documents_node)
        builder.add_node("vectorize_documents", self._vectorize_documents_node)
        builder.add_node("rag_retrieve", self._rag_retrieve_node)
        builder.add_node("generate_answer", self._generate_answer_node)
        builder.add_node("eval_answer", self._eval_answer_node)
        builder.add_node("terminal_error", self._terminal_error_node)

        # 添加边（两阶段执行流程）
        # START 后并行执行 init_vector_store 和 plan_query
        builder.add_edge(START, "init_vector_store")
        builder.add_edge(START, "plan_query")

        # 两阶段执行流程
        builder.add_edge("plan_query", "execute_first")
        builder.add_edge("execute_first", "collect_first")
        builder.add_edge("collect_first", "process_first_documents")
        builder.add_edge("collect_first", "execute_second")
        builder.add_edge("execute_second", "collect_second")
        builder.add_edge("collect_second", "process_second_documents")

        # 动态入库：init_vector_store 完成后启动 vectorize_documents
        builder.add_edge("init_vector_store", "vectorize_documents")
        builder.add_edge("process_first_documents", "vectorize_documents")
        builder.add_edge("process_second_documents", "vectorize_documents")

        # 后续流程保持不变
        builder.add_edge("vectorize_documents", "rag_retrieve")
        builder.add_conditional_edges(
            "rag_retrieve",
            self._route_after_retrieve,
            {
                "generate_answer": "generate_answer",
                "rag_retrieve": "rag_retrieve",
                "terminal_error": "terminal_error"
            }
        )
        builder.add_edge("generate_answer", "eval_answer")
        builder.add_edge("terminal_error", END)
        builder.add_conditional_edges(
            "eval_answer",
            self._should_continue_generation,
            {
                "generate_answer": "generate_answer",
                "end": END
            }
        )

        # 编译图
        graph = builder.compile(checkpointer=self.memory)
        logger.info("MultiAgentGraph 构建完成（两阶段执行版本）")
        return graph

    # ========================================================================
    # 对外接口
    # ========================================================================

    async def run(self, user_query: str, thread_id: str, user_id: str = "default_user") -> Dict[str, Any]:
        """执行完整的查询处理流程

        Args:
            user_query: 用户查询
            thread_id: 会话线程 ID
            user_id: 用户标识（可选，默认为 "default_user"）

        Returns:
            包含最终回答和元数据的字典
        """
        logger.info(f"开始处理用户查询: {user_query} (user_id={user_id}, thread_id={thread_id})")

        config = {"configurable": {"thread_id": thread_id,"user_id": user_id}}

        # 初始状态（补充新增字段）
        initial_state: MultiAgentState = {
            "messages": [
                SystemMessage(content=self.answer_system_prompt),
                HumanMessage(content=user_query)
            ],
            "original_query": user_query,
            "thread_id": thread_id,
            "user_id": user_id,
            "sub_questions": [],
            "first_executor_results": [],
            "second_executor_results": [],
            "url_pool": [],
            "first_all_documents": [],
            "second_all_documents": [],
            "first_processed_file_paths": [],
            "second_processed_file_paths": [],
            "first_llama_docs": [],
            "second_llama_docs": [],
            "retrieved_nodes": [],
            "final_answer": "",
            "vector_store_initialized": False,
            "inited_vector_index": False,
            "flags": self._init_flags(),
            "epoch": 0,
            "last_answer": "",
            "last_evaluation": None,
            "retrieved_epoch": 0,
            "correct_context": False
        }

        try:
            # 运行图
            result = await self.graph.ainvoke(initial_state, config)

            # 构建返回结果
            flags = result.get("flags") or self._init_flags()
            failed_nodes = [
                node_name for node_name, status in flags.items() if status == "error"
            ]
            execution_succeeded = bool(flags) and all(
                status is True for status in flags.values()
            )
            logger.info(f"节点执行状态: {flags}")

            question_pool = self._extract_question_pool_from_messages(result.get("messages", []))
            final_result = {
                'query': user_query,
                'user_id': user_id,
                'thread_id': thread_id,
                'sub_questions': result.get('sub_questions', []),
                'rewritten_questions_count': len(question_pool),
                'total_questions': len(question_pool),
                'documents_processed': len(result.get('first_all_documents', []))
                + len(result.get('second_all_documents', [])),
                'url_pool_size': len(result.get('url_pool', [])),
                'answer': result.get('final_answer', ''),
                'metadata': {
                    'retrieved_count': len(result.get('retrieved_nodes', [])),
                    'unique_count': len(result.get('retrieved_nodes', [])),
                    'reranked_count': len(result.get('retrieved_nodes', [])),
                    'execution_succeeded': execution_succeeded,
                    'failed_nodes': failed_nodes,
                    'node_flags': flags
                }
            }

            logger.info("查询处理完成")
            return final_result

        except Exception as e:
            logger.error(f"处理查询失败: {e}")
            import traceback
            traceback.print_exc()

            return {
                'query': user_query,
                'user_id': user_id,
                'thread_id': thread_id,
                'error': str(e),
                'answer': f"抱歉，处理您的查询时出现错误: {str(e)}"
            }

    async def _cleanup(self):
        """清理资源"""
        logger.info("开始清理 MultiAgentGraph 资源")

        try:
            # 清理 PlannerAgent
            await self.planner_agent._clean()

            # 清理 ExecutorAgent Pool
            await self.executor_pool.cleanup()

            # 清理内存
            await self.memory.aclose()

            logger.info("MultiAgentGraph 资源清理完成")
        except Exception as e:
            logger.error(f"资源清理失败: {e}")


# ============================================================================
# 测试代码
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("MultiAgentGraph 测试")
    print("=" * 60)
    print("✓ MultiAgentGraph 模块导入成功")
    print("\n注意：完整测试需要 PostgreSQL 连接池")
