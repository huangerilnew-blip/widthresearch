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
import logging
from typing import Dict, Any, List, Optional, TypedDict, Annotated
from psycopg_pool import AsyncConnectionPool
from concurrent_log_handler import ConcurrentRotatingFileHandler

from agents.planneragent import PlannerAgent
from agents.executor_pool import ExecutorAgentPool
from core.rag.rag_preprocess_module import VectorStoreManager
from core.rag.document_processor import DocumentProcessor
from core.rag.rag_postprocess_module import RAGPostProcessModule as RAGModule
from core.rag.models import QuestionsPool, BGERerankNodePostprocessor
from core.config.config import Config
from core.llms import get_llm
from core.rag.reranker import BGEReranker
from core.file_deduplicator import FileDeduplicator
from core.log_config import setup_logger

# LangGraph 相关导入
from langgraph.graph import StateGraph, START, END, add_messages
from langchain_core.messages import AnyMessage, AIMessage, HumanMessage
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langchain_core.messages import HumanMessage

# 设置日志
logger = setup_logger(__name__)


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
    executor_results: List[Dict]  # ExecutorAgent 执行结果
    url_pool: List[str]  # 全局去重后的 URL 列表

    # 文档处理阶段
    all_documents: List[Dict]  # 收集的所有文档
    processed_file_paths: List[Dict]  # 已扫描并准备处理的文件路径及其元数据
    llama_docs: List  # 处理后的文档片段

    # RAG 阶段
    retrieved_nodes: List  # RAG 检索结果
    question_pool: Optional[QuestionsPool]  # 问题池

    # 输出
    final_answer: str  # 最终答案

    # 内部状态
    vector_store_initialized: bool  # 向量库是否已初始化
    error: Optional[str]  # 错误信息


# ============================================================================
# MultiAgentGraph - LangGraph 版本
# ============================================================================

class MultiAgentGraph:
    """MultiAgent 协调器 - LangGraph 版本

    流程图：
        START → init_vector_store → plan_query → execute_subquestions
            → collect_documents → process_documents → vectorize_documents
            → rag_retrieve → build_question_pool → generate_answer → END

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

        # 初始化组件
        self.planner_agent = PlannerAgent(pool, planner_model)
        self.executor_pool = ExecutorAgentPool(pool, executor_pool_size, executor_model)
        self.vector_store_manager = VectorStoreManager()

        # LLM 和 Reranker
        self.llm = get_llm(executor_model)[0]
        self.reranker = BGEReranker()

        # 创建 BGE Reranker 节点后处理器
        self.node_postprocessor = BGERerankNodePostprocessor(
            reranker=self.reranker,
            top_n=Config.RERANK_TOP_N,
            score_threshold=Config.RERANK_THRESHOLD
        )

        # 文档处理器
        self.document_processor = DocumentProcessor(
            embedding_model=self.vector_store_manager.embedding_model,
            llm=self.llm
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
                self.vector_store_index = self.vector_store_manager.load_base_vector_store()
                logger.info("向量存储初始化完成")

            return {"vector_store_initialized": True}

        except Exception as e:
            logger.error(f"向量存储初始化失败: {e}")
            return {"error": str(e), "vector_store_initialized": False}

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
                        "messages": [AIMessage(content="JSON 解析失败，使用原始查询")]
                    }
            elif isinstance(result, dict):
                data = result
            else:
                logger.error(f"PlannerAgent 返回了非预期的类型: {type(result)}")
                return {
                    "sub_questions": [original_query],
                    "messages": [AIMessage(content="PlannerAgent 返回类型错误，使用原始查询")]
                }

            # 提取 tasks
            tasks = data.get('tasks', [])

            if isinstance(tasks, list) and len(tasks) >= 3:
                logger.info(f"查询拆解完成，生成 {len(tasks)} 个子问题")
                return {
                    "sub_questions": tasks,
                    "messages": [AIMessage(content=f"已生成 {len(tasks)} 个子问题")]
                }
            else:
                logger.warning(f"子问题数量不足: {len(tasks)}")
                return {
                    "sub_questions": tasks if tasks else [original_query],
                    "messages": [AIMessage(content=f"生成 {len(tasks)} 个子问题")]
                }

        except Exception as e:
            logger.error(f"查询拆解失败: {e}")
            return {
                "sub_questions": [original_query],
                "messages": [AIMessage(content=f"查询拆解失败: {str(e)}")]
            }

    async def _execute_first_node(self, state: MultiAgentState) -> Dict[str, Any]:
        """节点 3a: 第一阶段执行 - 探索阶段 (Exploration)

        使用空 url_pool，让 ExecutorAgent 自由探索
        """
        logger.info("[节点 3a] 第一阶段执行 - 探索阶段（url_pool=[]）")

        sub_questions = state.get("sub_questions", [])
        thread_id = state.get("thread_id", "default")
        user_id = state.get("user_id", "default_user")
        user_query = state.get("original_query", "")

        try:
            # 初始化 Questions Pool
            questions_pool = QuestionsPool()
            questions_pool.add_original_questions(sub_questions)

            # 第一阶段：url_pool=[] (探索)
            executor_results, updated_url_pool = await self.executor_pool.execute_questions(
                sub_questions,
                thread_id,
                user_id,
                [],  # 空 url_pool
                user_query
            )

            logger.info(f"第一阶段执行完成，获得 {len(executor_results)} 个结果")
            logger.info(f"第一阶段收集到 {len(updated_url_pool)} 个 URL")

            return {
                "executor_results": executor_results,
                "url_pool": updated_url_pool,
                "messages": [AIMessage(content=f"第一阶段完成 {len(executor_results)} 个子问题的执行")]
            }

        except Exception as e:
            logger.error(f"第一阶段执行失败: {e}")
            return {
                "executor_results": [],
                "url_pool": [],
                "error": str(e)
            }

    async def _execute_second_node(self, state: MultiAgentState) -> Dict[str, Any]:
        """节点 3b: 第二阶段执行 - 精炼阶段 (Refinement)

        使用第一阶段收集的 url_pool，进行精准检索
        """
        logger.info("[节点 3b] 第二阶段执行 - 精炼阶段（使用第一阶段的 url_pool）")

        sub_questions = state.get("sub_questions", [])
        thread_id = state.get("thread_id", "default")
        user_id = state.get("user_id", "default_user")
        user_query = state.get("original_query", "")
        url_pool = state.get("url_pool", [])  # 来自第一阶段

        try:
            # 第二阶段：使用第一阶段收集的 url_pool
            executor_results, updated_url_pool = await self.executor_pool.execute_questions(
                sub_questions,
                thread_id,
                user_id,
                url_pool,  # 使用第一阶段的 url_pool
                user_query
            )

            logger.info(f"第二阶段执行完成，获得 {len(executor_results)} 个结果")
            logger.info(f"第二阶段 URL Pool: {len(url_pool)} -> {len(updated_url_pool)}")

            return {
                "executor_results": executor_results,
                "url_pool": updated_url_pool,
                "messages": [AIMessage(content=f"第二阶段完成 {len(executor_results)} 个子问题的执行")]
            }

        except Exception as e:
            logger.error(f"第二阶段执行失败: {e}")
            return {
                "executor_results": [],
                "error": str(e)
            }

    async def _collect_first_node(self, state: MultiAgentState) -> Dict[str, Any]:
        """节点 4a: 第一次文档收集与去重

        在第一阶段执行后，对下载的文档进行去重
        """
        logger.info("[节点 4a] 第一次文档收集与去重")

        executor_results = state.get("executor_results", [])

        try:
            # 执行第一次文件去重
            unique_files, duplicate_files = self.file_deduplicator.deduplicate(
                directory=Config.DOC_SAVE_PATH,
                remove_duplicates=True  # 物理删除重复文件
            )

            logger.info(f"第一次去重完成: 保留 {len(unique_files)} 个, 删除 {len(duplicate_files)} 个")

            # 构建文件元数据列表
            processed_file_paths = []
            for file_path in unique_files:
                file_info = {
                    "path": file_path,
                    "filename": os.path.basename(file_path),
                    "size": os.path.getsize(file_path),
                    "extension": os.path.splitext(file_path)[1]
                }
                processed_file_paths.append(file_info)

            # 从 executor_results 中提取 downloaded_papers
            all_documents = []
            for result in executor_results:
                if isinstance(result, dict):
                    downloaded_papers = result.get('downloaded_papers', [])
                    all_documents.extend(downloaded_papers)

            logger.info(f"从第一阶段 executor_results 提取到 {len(all_documents)} 个文档元数据")

            return {
                "all_documents": all_documents,
                "processed_file_paths": processed_file_paths,
                "messages": [AIMessage(content=f"第一次收集到 {len(unique_files)} 个去重后的文档")]
            }

        except Exception as e:
            logger.error(f"第一次文档收集失败: {e}")
            import traceback
            traceback.print_exc()

            return {
                "all_documents": [],
                "processed_file_paths": [],
                "error": str(e)
            }

    async def _collect_second_node(self, state: MultiAgentState) -> Dict[str, Any]:
        """节点 4b: 第二次文档收集与去重

        在第二阶段执行后，对下载的文档进行第二次去重
        """
        logger.info("[节点 4b] 第二次文档收集与去重")

        executor_results = state.get("executor_results", [])
        previous_file_paths = state.get("processed_file_paths", [])

        try:
            # 执行第二次文件去重
            unique_files, duplicate_files = self.file_deduplicator.deduplicate(
                directory=Config.DOC_SAVE_PATH,
                remove_duplicates=True  # 物理删除重复文件
            )

            logger.info(f"第二次去重完成: 保留 {len(unique_files)} 个, 删除 {len(duplicate_files)} 个")

            # 构建文件元数据列表
            processed_file_paths = []
            for file_path in unique_files:
                file_info = {
                    "path": file_path,
                    "filename": os.path.basename(file_path),
                    "size": os.path.getsize(file_path),
                    "extension": os.path.splitext(file_path)[1]
                }
                processed_file_paths.append(file_info)

            # 从 executor_results 中提取 downloaded_papers
            all_documents = []
            for result in executor_results:
                if isinstance(result, dict):
                    downloaded_papers = result.get('downloaded_papers', [])
                    all_documents.extend(downloaded_papers)

            logger.info(f"从第二阶段 executor_results 提取到 {len(all_documents)} 个文档元数据")
            logger.info(f"两阶段总计：{len(previous_file_paths)} + {len(processed_file_paths)} = {len(unique_files)} 个去重后的文档")

            return {
                "all_documents": all_documents,
                "processed_file_paths": processed_file_paths,
                "messages": [AIMessage(content=f"第二次收集到 {len(unique_files)} 个去重后的文档")]
            }

        except Exception as e:
            logger.error(f"第二次文档收集失败: {e}")
            import traceback
            traceback.print_exc()

            return {
                "all_documents": [],
                "processed_file_paths": [],
                "error": str(e)
            }

    async def _process_documents_node(self, state: MultiAgentState) -> Dict[str, Any]:
        """节点 5: 处理文档

        PDF 转 Markdown、切割、问题改写
        """
        logger.info("[节点 5] 处理文档（PDF → Markdown → 切割）")

        all_documents = state.get("all_documents", [])

        if not all_documents:
            logger.info("没有文档需要处理")
            return {
                "llama_docs": [],
                "messages": [AIMessage(content="没有文档需要处理")]
            }

        try:
            llama_docs = await self.document_processor.get_nodes(all_documents)
            logger.info(f"文档处理完成: {len(llama_docs)} 个片段")

            return {
                "llama_docs": llama_docs,
                "messages": [AIMessage(content=f"处理完成，生成 {len(llama_docs)} 个文档片段")]
            }

        except Exception as e:
            logger.error(f"文档处理失败: {e}")
            return {
                "llama_docs": [],
                "error": str(e)
            }

    async def _vectorize_documents_node(self, state: MultiAgentState) -> Dict[str, Any]:
        """节点 6: 向量化文档并入库

        将处理后的文档向量化并存入向量库
        """
        logger.info("[节点 6] 向量化文档并入库")

        llama_docs = state.get("llama_docs", [])

        if not llama_docs:
            logger.info("没有文档需要向量化")
            return {"messages": [AIMessage(content="没有文档需要向量化")]}

        try:
            self.vector_store_manager.add_nodes(llama_docs)
            logger.info(f"成功添加 {len(llama_docs)} 个文档到向量库")

            return {"messages": [AIMessage(content=f"成功向量化 {len(llama_docs)} 个文档")]}

        except Exception as e:
            logger.error(f"向量化失败: {e}")
            return {"error": str(e)}

    async def _rag_retrieve_node(self, state: MultiAgentState) -> Dict[str, Any]:
        """节点 7: RAG 检索

        基于子问题进行向量检索和重排序
        """
        logger.info("[节点 7] RAG 检索")

        sub_questions = state.get("sub_questions", [])
        thread_id = state.get("thread_id", "default")

        try:
            # 创建检索器
            retriever = self.vector_store_index.as_retriever(similarity_top_k=Config.TOP_K)

            # 创建 RAG 模块
            rag_module = RAGModule(
                vector_store=self.vector_store_index,
                retriever=retriever,
                node_postprocessor=self.node_postprocessor,
                top_k=Config.TOP_K
            )

            # 执行检索，获取去重后的节点
            retrieved_nodes = await rag_module.retrieve_postprecess(
                planner_questions=sub_questions
            )

            logger.info(f"RAG 检索完成，获得 {len(retrieved_nodes)} 个节点")

            return {
                "retrieved_nodes": retrieved_nodes,
                "messages": [AIMessage(content=f"检索到 {len(retrieved_nodes)} 个相关节点")]
            }

        except Exception as e:
            logger.error(f"RAG 检索失败: {e}")
            return {
                "retrieved_nodes": [],
                "error": str(e)
            }

    async def _build_question_pool_node(self, state: MultiAgentState) -> Dict[str, Any]:
        """节点 8: 构建问题池

        合并原始子问题和从检索节点中提取的问题
        """
        logger.info("[节点 8] 构建问题池")

        sub_questions = state.get("sub_questions", [])
        retrieved_nodes = state.get("retrieved_nodes", [])

        try:
            # 从检索结果中提取问题
            retrieved_questions = self._extract_questions_from_nodes(retrieved_nodes)
            logger.info(f"从检索结果中提取到 {len(retrieved_questions)} 个问题")

            # 构建问题池
            questions_pool = QuestionsPool()
            questions_pool.add_original_questions(sub_questions)
            questions_pool.add_rewritten_questions(retrieved_questions)

            logger.info(f"Question Pool 构建完成，共 {len(questions_pool)} 个问题")

            return {
                "question_pool": questions_pool,
                "messages": [AIMessage(content=f"问题池包含 {len(questions_pool)} 个问题")]
            }

        except Exception as e:
            logger.error(f"构建问题池失败: {e}")
            return {
                "question_pool": None,
                "error": str(e)
            }

    async def _generate_answer_node(self, state: MultiAgentState) -> Dict[str, Any]:
        """节点 9: 生成最终答案

        基于检索结果和问题池生成最终答案
        """
        logger.info("[节点 9] 生成最终答案")

        original_query = state.get("original_query", "")
        sub_questions = state.get("sub_questions", [])
        retrieved_nodes = state.get("retrieved_nodes", [])
        question_pool = state.get("question_pool")
        try:
            # 转换 question_pool 为列表
            question_pool_list = list(question_pool) if question_pool else sub_questions

            # 构建检索上下文
            retrieved_contexts = []
            for node_with_score in retrieved_nodes:
                node = node_with_score.node
                metadata = node.metadata
                source = metadata.get('file_name', metadata.get('source', 'Unknown'))
                content = node.get_content()

                # 截断过长内容
                if len(content) > 500:
                    content = content[:500] + "..."

                retrieved_contexts.append(f"来源: {source}\n内容: {content}\n")

            contexts_str = "\n".join(retrieved_contexts)
            questions_str = "\n".join([f"- {q}" for q in question_pool_list])

            # 构建提示词
            prompt = f"""你是一名严谨的知识整合与分析专家。
            你的任务是：
            基于以下三个输入：
            1）用户原始问题：{original_query}
            2）基于向量检索生成的改写问题{question_pool_list}
            3）向量检索得到的参考内容：{retrieved_contexts}

            生成一个结构清晰、层次分明、严格基于证据的回答。

            ========================
            【工作原则】

            1. 优先使用“检索内容”中的信息。
            2. 不得凭空补充事实。
            3. 若信息不足，应明确指出“不足以回答”。
            4. 回答必须围绕“用户原始问题”，而不是仅围绕改写问题。
            5. 改写问题的作用是辅助理解与语义扩展，而不是替代原问题。
            6. 输出必须分层组织，并体现逻辑结构。
            7. 所有结论必须能够在“检索内容”中找到依据或合理推导路径。

            ========================
            【思考步骤】

            在生成回答时，请遵循以下步骤：

            第一步：问题对齐
            - 分析用户原始问题的核心意图
            - 分析改写问题与原问题之间的语义关系
            - 明确最终要回答的“真实问题边界”

            第二步：信息筛选
            - 从检索内容中提取与问题高度相关的事实
            - 过滤掉与问题无关或弱相关的信息
            - 若存在冲突信息，优先选择更直接相关的信息

            第三步：结构化生成
            - 先给出核心结论（如果信息足够）
            - 再分点展开关键支撑逻辑
            - 每一部分都必须与问题直接相关

            第四步：证据标注
            - 明确说明哪些内容来自检索文本
            - 哪些属于基于检索内容的合理推理
            - 如果存在信息不足，单独说明
            ========================
            【输出格式】

            请严格按照以下结构输出：

            ————————————
            【问题理解】
            - 原始问题核心意图：
            - 改写问题的补充作用：
            - 最终回答边界：

            【关键信息提取】
            - 事实1：
            - 事实2：
            - 事实3：

            【结构化回答】

            一、核心结论  
            （简洁回答原问题）

            二、关键支撑点  
            1.  
            2.  
            3.  

            三、详细解释  
            （分层展开，逻辑清晰）

            【证据说明】
            - 直接来源：
            - 合理推断：
            - 信息不足部分（如有）：
            ————————————

            请确保回答严格围绕用户原始问题展开。
"""

            # 调用 LLM 生成答案
            response = await self.llm.ainvoke(prompt)
            answer = response.content if hasattr(response, 'content') else str(response)

            logger.info(f"答案生成完成，长度: {len(answer)} 字符")

            return {
                "final_answer": answer,
                "messages": [AIMessage(content=answer)]
            }

        except Exception as e:
            logger.error(f"生成答案失败: {e}")
            return {
                "final_answer": f"抱歉，生成答案时出现错误: {str(e)}",
                "error": str(e)
            }

    # ========================================================================
    # 辅助方法
    # ========================================================================

    def _extract_questions_from_nodes(self, retrieved_nodes: list) -> List[str]:
        """从检索结果的 nodes 中提取 metadata 中的 questions

        Args:
            retrieved_nodes: 检索到的 NodeWithScore 列表

        Returns:
            提取的问题列表（去重后）
        """
        questions_set = set()

        for node_with_score in retrieved_nodes:
            try:
                metadata = node_with_score.node.metadata
                if metadata and "questions" in metadata:
                    questions = metadata["questions"]
                    # questions 可能是字符串列表或单个字符串
                    if isinstance(questions, list):
                        for q in questions:
                            if q and isinstance(q, str):
                                questions_set.add(q.strip())
                    elif isinstance(questions, str):
                        questions_set.add(questions.strip())
            except Exception as e:
                logger.warning(f"提取节点问题时出错: {e}")
                continue

        return list(questions_set)

    # ========================================================================
    # 图构建
    # ========================================================================

    def _build_graph(self) -> StateGraph:
        """构建 MultiAgent 的状态图（两阶段执行版本）

        两阶段执行流程：
            START ├──> init_vector_store (异步，独立执行)
                  └──> plan_query → execute_first (探索, url_pool=[])
                        → collect_first (第一次去重)
                        → execute_second (精炼, url_pool=<从第一阶段>)
                        → collect_second (第二次去重)
                        → process_documents → [屏障：等待向量库] → vectorize_documents
                        → rag_retrieve → build_question_pool → generate_answer → END

        关键设计：
        - 两阶段执行：探索（空url_pool） + 精炼（使用第一阶段url_pool）
        - 每阶段后立即去重，避免重复下载
        - 同步屏障位于 vectorize_documents 前（真正需要向量库的节点）
        """
        builder = StateGraph(MultiAgentState)

        # 添加节点
        builder.add_node("init_vector_store", self._init_vector_store_node)
        builder.add_node("plan_query", self._plan_query_node)
        builder.add_node("execute_first", self._execute_first_node)
        builder.add_node("collect_first", self._collect_first_node)
        builder.add_node("execute_second", self._execute_second_node)
        builder.add_node("collect_second", self._collect_second_node)
        builder.add_node("process_documents", self._process_documents_node)
        builder.add_node("vectorize_documents", self._vectorize_documents_node)
        builder.add_node("rag_retrieve", self._rag_retrieve_node)
        builder.add_node("build_question_pool", self._build_question_pool_node)
        builder.add_node("generate_answer", self._generate_answer_node)

        # 添加边（两阶段执行流程）
        # START 后并行执行 init_vector_store 和 plan_query
        builder.add_edge(START, "init_vector_store")
        builder.add_edge(START, "plan_query")

        # 两阶段执行流程
        builder.add_edge("plan_query", "execute_first")
        builder.add_edge("execute_first", "collect_first")
        builder.add_edge("collect_first", "execute_second")
        builder.add_edge("execute_second", "collect_second")
        builder.add_edge("collect_second", "process_documents")

        # 同步屏障：init_vector_store 和 process_documents 都完成后才能进入 vectorize_documents
        # LangGraph 会自动等待两个前置节点都完成
        builder.add_edge("init_vector_store", "vectorize_documents")
        builder.add_edge("process_documents", "vectorize_documents")

        # 后续流程保持不变
        builder.add_edge("vectorize_documents", "rag_retrieve")
        builder.add_edge("rag_retrieve", "build_question_pool")
        builder.add_edge("build_question_pool", "generate_answer")
        builder.add_edge("generate_answer", END)

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

        config = {"configurable": {" thread_id": thread_id}}

        # 初始状态（补充新增字段）
        initial_state: MultiAgentState = {
            "messages": [HumanMessage(content=user_query)],
            "original_query": user_query,
            "thread_id": thread_id,
            "user_id": user_id,
            "sub_questions": [],
            "executor_results": [],
            "url_pool": [],
            "all_documents": [],
            "processed_file_paths": [],
            "llama_docs": [],
            "retrieved_nodes": [],
            "question_pool": None,
            "final_answer": "",
            "vector_store_initialized": False,
            "error": None
        }

        try:
            # 运行图
            result = await self.graph.ainvoke(initial_state, config)

            # 构建返回结果
            final_result = {
                'query': user_query,
                'user_id': user_id,
                'thread_id': thread_id,
                'sub_questions': result.get('sub_questions', []),
                'rewritten_questions_count': len(result.get('question_pool', [])) if result.get('question_pool') else 0,
                'total_questions': len(result.get('question_pool', [])) if result.get('question_pool') else 0,
                'documents_processed': len(result.get('all_documents', [])),
                'url_pool_size': len(result.get('url_pool', [])),
                'answer': result.get('final_answer', ''),
                'metadata': {
                    'retrieved_count': len(result.get('retrieved_nodes', [])),
                    'unique_count': len(result.get('retrieved_nodes', [])),
                    'reranked_count': len(result.get('retrieved_nodes', []))
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
