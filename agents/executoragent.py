import asyncio

from langchain_core.tools import BaseTool
from langgraph.prebuilt import ToolNode
from core.config import Config
from core.llms import lang_llm
from core.mcp.context7_grep import Context7GrepMCPClient
from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph import add_messages, StateGraph, START, END, state
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import AnyMessage, AIMessage, HumanMessage, ToolMessage
from mcp.types import TextContent
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool
import logging, json, asyncio, os
from concurrent_log_handler import ConcurrentRotatingFileHandler
from core.mcp.tools import get_tools
from dotenv import load_dotenv
from core.log_config import setup_logger
import traceback
load_dotenv()

# 设置日志
logger = setup_logger(__name__)

class ExecutorState(TypedDict):
    sub_url_pool: list[str]  # url 池，防止重复下载
    executor_messages: Annotated[list[AnyMessage], add_messages]
    user_query: str  # 用户的原始查询
    sub_query: str  # 当前处理的子问题
    optional_search_results: Annotated[list[ToolMessage], add_messages]  # 可选工具的搜索结果
    search_results: List[Dict]  # 所有搜索结果（必需工具 + 可选工具）
    deduplicated_results: List[Dict]  # 去重后的结果
    downloaded_papers: List[Dict]  # 已下载的论文

class ExecutorAgent:
    """
    ExecutorAgent: 负责执行单个子问题的完整处理流程
    
    处理流程：
    START → search_node → llm_chat_node → [条件边] → optional_tool_node → llm_chat_node (循环) → clean → download → END
    
    LLM 可以多次决策是否调用可选工具，形成循环，直到 LLM 认为已经收集了足够的信息。
    """
    
    def __init__(self, pool: AsyncConnectionPool | None, modelname: str = Config.LLM_EXECUTOR):
        self.chat_llm = lang_llm(
            chat_name=modelname,
            embedding_name=Config.LLM_EMBEDDING
        )[0]
        # 搜索工具延迟加载
        self.search_tools: list[BaseTool] = None
        # 下载工具单独获取
        self.download_tools: list[BaseTool] = None  # 延迟加载
        self._context7_grep_client = None
        if pool:
            self.memory = AsyncPostgresSaver(pool) # 异步持久化存储
        else:
            self.memory = None
        self.graph = None  # 延迟构建
    async def _ensure_initialized(self):
        """确保异步资源已初始化"""
        if self.search_tools is None:
            self.search_tools = await self._get_search_tools()
        if self.graph is None:
            self.graph = self._build_graph()
    
    async def _get_search_tools(self) -> list[BaseTool]:
        """获取搜索工具（只包含 search 类工具）"""
        search_tools = await get_tools(tool_type="search")

        if self._context7_grep_client is None:
            self._context7_grep_client = Context7GrepMCPClient(
                context7_need=True,
                grep_need=True
            )

        context7_grep_tools = await self._context7_grep_client.get_tools()

        merged_tools = {tool.name: tool for tool in search_tools}
        for tool in context7_grep_tools:
            merged_tools.setdefault(tool.name, tool)

        return list(merged_tools.values())
    
    async def _get_download_tools(self) -> list[BaseTool]:
        """获取下载工具（只包含 download 类工具）"""
        if self.download_tools is None:

            self.download_tools = await get_tools(tool_type="download")
        return self.download_tools
    
    def _get_required_tools(self) -> List[str]:
        """获取必需调用的工具列表"""
        return ["wikipedia_search", "exa_context_search", "tavily_search"]
    
    def _get_optional_tools(self) -> List[BaseTool]:
        """获取可选工具列表（由 LLM 决定是否调用）"""
        optional_tool_names = [
            "sec_edgar_search",
            "akshare_search",
            "resolve-library-id",
            "query-docs",
            "grep_query"
        ]
        return [t for t in self.search_tools if any(opt in t.name.lower() for opt in optional_tool_names)]
    
    async def _invoke_single_tool(self, tool: BaseTool, query: str)->list[dict]:
        """单个工具调用的异步函数
        
        Args:
            tool: 已验证存在的工具对象
            query: 搜索查询
        """
        logger.info(f"调用工具 {tool.name} 搜索: {query}")
        
        try:
            result = await tool.ainvoke({"query": query})
        except Exception as e:
            logger.error(f"工具 {tool.name} 调用失败: {e}")
            raise RuntimeError(f"工具 {tool.name} 调用失败: {e}")
        
        if result is None:
            logger.error(f"工具 {tool.name} 返回结果为空")
            raise TypeError(f"工具 {tool.name} 返回结果类型错误")

        papers = None
        source_tool = None
        count = None
        parsed_content = result

        if isinstance(result, str):
            if result.startswith("Unknown tool:"):
                logger.error(f"MCP 工具名不存在: {result}")
                raise NameError(f"MCP 工具名不存在: {tool.name}")

            if result.startswith("Error executing"):
                logger.error(f"MCP 工具执行错误: {result[:200]}")
                raise RuntimeError(f"MCP 工具执行错误: {tool.name}")

            try:
                parsed_content = json.loads(result)
            except json.JSONDecodeError as e:
                logger.error(f"JSON 解析失败: {e}, 原始结果: {result[:200]}")
                raise ValueError(f"工具 {tool.name} 返回的 JSON 格式错误")
        elif isinstance(result, (list, dict)):
            parsed_content = self._parse_tool_content(result)
        else:
            logger.error(f"工具 {tool.name} 返回结果异常: type={type(result)}")
            raise TypeError(f"工具 {tool.name} 返回结果类型错误")

        papers, source_tool, count = self._extract_papers_payload(parsed_content)

        if not isinstance(papers, list):
            logger.error(f"工具 {tool.name} 返回的数据不是列表: {type(papers)}")
            raise TypeError(f"工具 {tool.name} 返回数据格式错误")

        if not all(isinstance(item, dict) for item in papers):
            logger.error(f"工具 {tool.name} 返回的数据不是 dict 列表")
            raise TypeError(f"工具 {tool.name} 返回数据格式错误")

        required_keys = {"title", "source", "url"}
        filtered_papers = []
        for paper in papers:
            missing_keys = required_keys.difference(paper.keys())
            if missing_keys:
                logger.warning(f"工具 {tool.name} 返回结果缺少字段: {missing_keys}")
                continue
            filtered_papers.append(paper)

        log_source = source_tool or tool.name
        result_count = count if count is not None else len(filtered_papers)
        if result_count:
            logger.info(f"{log_source} 返回了 {result_count} 条数据")
        else:
            logger.warning(f"{log_source} 返回了 0 条数据")
        return filtered_papers

    def _parse_tool_args(self, tool_args: Any) -> Dict[str, Any]:
        if isinstance(tool_args, dict):
            return tool_args
        if isinstance(tool_args, str):
            try:
                return json.loads(tool_args)
            except json.JSONDecodeError:
                return {}
        return {}

    def _build_tool_call_info(self, tool_calls: Any) -> Dict[str, Dict[str, Any]]:
        tool_call_info = {}
        for call in tool_calls or []:
            if isinstance(call, dict):
                call_id = call.get("id")
                name = call.get("name", "")
                args = self._parse_tool_args(call.get("args", {}))
            else:
                call_id = getattr(call, "id", None) or getattr(call, "tool_call_id", None)
                name = getattr(call, "name", "")
                args = self._parse_tool_args(getattr(call, "args", {}))
            if call_id:
                tool_call_info[call_id] = {"name": name, "args": args}
        return tool_call_info

    def _parse_tool_content(self, content: Any) -> Any:
        if isinstance(content, TextContent):
            return self._parse_tool_content(content.text)
        if isinstance(content, str):
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return content
        if isinstance(content, dict) and "text" in content:
            return self._parse_tool_content(content.get("text"))
        if isinstance(content, list):
            if content and all(isinstance(item, TextContent) for item in content):
                if len(content) == 1:
                    return self._parse_tool_content(content[0].text)
                parsed_items = [self._parse_tool_content(item.text) for item in content]
                return parsed_items
            if content and all(isinstance(item, dict) and "text" in item for item in content):
                if len(content) == 1:
                    return self._parse_tool_content(content[0].get("text"))
                parsed_items = [self._parse_tool_content(item.get("text")) for item in content]
                return parsed_items
        return content

    def _extract_papers_payload(self, parsed_content: Any) -> tuple[list[dict], str | None, int | None]:
        source_tool = None
        count = None
        if isinstance(parsed_content, dict):
            source_tool = parsed_content.get("source_tool")
            count_value = parsed_content.get("count")
            count = count_value if isinstance(count_value, int) else None
            papers = parsed_content.get("papers")
            if isinstance(papers, list):
                return papers, source_tool, count
            results = parsed_content.get("results")
            if isinstance(results, list):
                return results, source_tool, count
            return [parsed_content], source_tool, count

        if isinstance(parsed_content, list):
            if len(parsed_content) == 1 and isinstance(parsed_content[0], dict):
                return self._extract_papers_payload(parsed_content[0])
            return parsed_content, None, None

        return [], None, None

    def _ensure_tool_message_name(self, tool_msg: ToolMessage, tool_name: str) -> ToolMessage:
        if tool_name and not getattr(tool_msg, "name", None):
            if hasattr(tool_msg, "model_copy"):
                return tool_msg.model_copy(update={"name": tool_name})
            try:
                setattr(tool_msg, "name", tool_name)
                return tool_msg
            except Exception:
                return ToolMessage(
                    content=tool_msg.content,
                    tool_call_id=tool_msg.tool_call_id,
                    name=tool_name
                )
        return tool_msg

    def _build_query_docs_records(self, content: Any, tool_args: Dict[str, Any]) -> List[Dict[str, Any]]:
        items = content if isinstance(content, list) else [content]
        records = []
        for item in items:
            if isinstance(item, dict):
                text = item.get("text")
                if text is None:
                    text = json.dumps(item, ensure_ascii=True)
                metadata = {}
                if isinstance(item.get("metadata"), dict):
                    metadata.update(item.get("metadata", {}))
            else:
                text = str(item)
                metadata = {}

            metadata.update({
                "tool": "query-docs",
                "source": "context7_query_docs"
            })
            if tool_args.get("library_id"):
                metadata["library_id"] = tool_args["library_id"]
            if tool_args.get("libraryId"):
                metadata["library_id"] = tool_args["libraryId"]
            if tool_args.get("query"):
                metadata["query"] = tool_args["query"]

            records.append({"text": text, "metadata": metadata})
        return records

    def _build_grep_query_records(self, content: Any, tool_args: Dict[str, Any]) -> List[Dict[str, Any]]:
        records = []
        query_value = None
        if isinstance(content, dict) and "results_by_repository" in content:
            query_value = content.get("query") or tool_args.get("query")
            for repo in content.get("results_by_repository", []):
                repo_name = repo.get("repository")
                for file_info in repo.get("files", []):
                    text = file_info.get("code_snippet") or ""
                    metadata = {
                        "tool": "grep_query",
                        "source": "grep",
                        "repository": repo_name,
                        "file_path": file_info.get("file_path"),
                        "branch": file_info.get("branch"),
                        "line_numbers": file_info.get("line_numbers"),
                        "language": file_info.get("language"),
                        "total_matches": file_info.get("total_matches")
                    }
                    if query_value:
                        metadata["query"] = query_value
                    records.append({"text": text, "metadata": metadata})
        else:
            text = json.dumps(content, ensure_ascii=True) if not isinstance(content, str) else content
            metadata = {
                "tool": "grep_query",
                "source": "grep"
            }
            if tool_args.get("query"):
                metadata["query"] = tool_args["query"]
            records.append({"text": text, "metadata": metadata})
        return records

    def _build_context7_grep_records(
        self,
        tool_name: str,
        content: Any,
        tool_args: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        if tool_name == "query-docs":
            return self._build_query_docs_records(content, tool_args)
        if tool_name == "grep_query":
            return self._build_grep_query_records(content, tool_args)
        return []

    def _persist_context7_grep_results(
        self,
        tool_name: str,
        content: Any,
        tool_args: Dict[str, Any] | None = None
    ) -> None:
        parsed_content = self._parse_tool_content(content)
        records = self._build_context7_grep_records(tool_name, parsed_content, tool_args or {})
        if not records:
            return

        os.makedirs(Config.DOC_SAVE_PATH, exist_ok=True)
        file_path = os.path.join(Config.DOC_SAVE_PATH, "context7_grep.json")
        with open(file_path, "a", encoding="utf-8") as file:
            for record in records:
                file.write(json.dumps(record, ensure_ascii=True) + "\n")

    def _truncate_tool_content(self, content: Any, limit: int = 100) -> str:
        if isinstance(content, str):
            text = content
        elif isinstance(content, (dict, list)):
            text = json.dumps(content, ensure_ascii=True)
        else:
            text = str(content)
        return text[:limit]

    def _compress_executor_messages(self, messages: list[AnyMessage]) -> list[AnyMessage]:
        compressed_messages = []
        for message in messages or []:
            if isinstance(message, ToolMessage):
                compressed_messages.append(
                    ToolMessage(
                        content=self._truncate_tool_content(message.content),
                        tool_call_id=message.tool_call_id,
                        name=getattr(message, "name", None)
                    )
                )
            else:
                compressed_messages.append(message)
        return compressed_messages

    def _count_required_tool_results(self, results: Any, required_tools: List[str]) -> List[Dict[str, int]]:
        counts = {tool: 0 for tool in required_tools}
        if isinstance(results, list):
            for item in results:
                if not isinstance(item, dict):
                    continue
                source = str(item.get("source", "")).lower()
                if "wikipedia" in source:
                    counts["wikipedia_search"] += 1
                elif "tavily" in source:
                    counts["tavily_search"] += 1
                elif "exa" in source:
                    counts["exa_context_search"] += 1
        return [{tool: counts[tool]} for tool in required_tools]
    
    # def _crop_observation(self, tool_messages: List[ToolMessage]) -> List[ToolMessage]:
    #     """
    #     裁剪工具执行结果为观察信息（Observation）
    #     裁剪 ToolMessage 内容，只保留关键信息用于 LLM 决策
    #     目的：减少 Token 消耗，加快 LLM 判断速度
        
    #     Args:
    #         tool_messages: 原始的 ToolMessage 列表

    #     Returns:
    #         格式化后的 ToolMessage 列表，内容精简但包含关键信息
    #     """
    #     if not tool_messages:
    #         logger.error(f"ExecutorAgent的optional_search_results状态为空，无法进行格式化处理")
    #         return []
        
    #     formatted_messages = []
        
    #     for tool_msg in tool_messages:
    #         content = tool_msg.content
            
    #         try:
    #             # 解析 JSON 内容
    #             if isinstance(content, str):
    #                 papers = json.loads(content)
    #             elif isinstance(content, list):
    #                 papers = content
    #             else:
    #                 formatted_messages.append(tool_msg)
    #                 continue
                
    #             # 提取关键信息摘要
    #             observations = []
    #             for paper in papers:
    #                 source = paper.get("source", "unknown")
    #                 title = paper.get("title", "无标题")
                    
    #                 if source == "sec_edgar":
    #                     # SEC EDGAR: 显示公司名和简短预览
    #                     company_name = paper.get("extra", {}).get("company_name", title)
    #                     abstract = paper.get("abstract", "")
    #                     preview = abstract[:150] + "..." if len(abstract) > 150 else abstract
    #                     observations.append(
    #                         f"✓ {company_name}\n"
    #                         f"  来源: SEC EDGAR\n"
    #                         f"  预览: {preview}"
    #                     )
    #                 elif source == "akshare":
    #                     # AkShare: 显示公司名和简短预览
    #                     abstract = paper.get("abstract", "")
    #                     preview = abstract[:150] + "..." if len(abstract) > 150 else abstract
    #                     observations.append(
    #                         f"✓ {title}\n"
    #                         f"  来源: AkShare\n"
    #                         f"  预览: {preview}"
    #                     )
    #                 else:
    #                     # 其他来源：只显示标题和来源
    #                     observations.append(f"✓ {title} (来源: {source})")
                
    #             # 创建精简的 ToolMessage
    #             if observations:
    #                 formatted_content = "\n\n".join(observations)
    #                 formatted_msg = ToolMessage(
    #                     content=formatted_content,
    #                     tool_call_id=tool_msg.tool_call_id,
    #                     name=tool_msg.name
    #                 )
    #                 formatted_messages.append(formatted_msg)
    #             else:
    #                 formatted_messages.append(tool_msg)
            
    #         except (json.JSONDecodeError, TypeError) as e:
    #             logger.warning(f"解析 ToolMessage 内容失败: {e}")
    #             formatted_messages.append(tool_msg)
    #             continue
        
    #     return formatted_messages
    async def _llm_chat_node(self, state: ExecutorState) -> Dict:
        """
        LLM 决策节点：按照 ReAct 模式让 LLM 进行推理和决策
        利用 LangGraph 的消息流机制，让 LLM 看到完整的对话历史自主决策
        """
        messages = state.get("executor_messages", [])
        query = state.get("sub_query") or state.get("user_query", "")
        if not query and messages:
            first_message = messages[0]
            query = getattr(first_message, "content", "")
        if not query:
            logger.error("ExecutorAgent-llm_chat_node 状态错误，无法正确提取用户查询")
            raise ValueError("ExecutorAgent missing user query")
        if not messages:
            messages = [HumanMessage(content=query)]
            state["executor_messages"] = messages
        # 缓存到 sub_query 中，方便后续节点使用
        if not state.get("sub_query"):
            state["sub_query"] = query

        optional_tools = self._get_optional_tools()
        optional_search_results = state.get("optional_search_results", [])

        if not optional_tools:
            logger.info("没有可选工具，跳过 LLM 决策")
            return {"executor_messages": [AIMessage(content="Thought: 不需要额外的专业工具，可以直接进行清洗。")]}

        logger.info(f"让 LLM 决定是否调用可选工具: {[t.name for t in optional_tools]}")

        try:
            llm_with_tools = self.chat_llm.bind_tools(optional_tools)

            # LLM 会看到完整的对话历史，自主决策
            response = await llm_with_tools.ainvoke(state["executor_messages"])

            # 记录决策结果
            has_tool_calls = hasattr(response, 'tool_calls') and bool(response.tool_calls)
            logger.info(f"LLM 决策结果: 是否调用工具={has_tool_calls}")
            if hasattr(response, 'content') and response.content:
                logger.info(f"LLM 思考: {response.content[:150]}...")

            return {"executor_messages": [response]}

        except Exception as e:
            logger.error(f"ExecutorAgent-llm_chat_node 状态错误{e}")
            return {"executor_messages": [AIMessage(content="Thought: 决策过程出错，跳过可选工具，直接进行清洗。")]}
    
    def _should_call_optional_tools(self, state: ExecutorState) -> str:
        """条件路由：判断是否需要调用可选工具"""
        last_message = state["executor_messages"][-1]

        if isinstance(last_message, AIMessage):
            # 检查是否有工具调用
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                logger.info(f"LLM 决定调用 {len(last_message.tool_calls)} 个可选工具")
                return "optional_tool_node"
            else:
                # LLM 决定不再调用可选工具，进入清洗阶段
                logger.info("LLM 决定不调用可选工具，进入清洗阶段")
                return "clean"
        else:
            logger.warning(f"意外的消息类型: {type(last_message)}")
            return "clean"
    
    async def _optional_tool_node(self, state: ExecutorState) -> dict:
        """
        可选工具节点：使用 LangGraph 的 ToolNode 执行工具调用
        按照 ReAct 模式，执行 Action 并返回 Observation (ToolMessage)
        """
        # 检查最后一条消息是否有 tool_calls
        last_message = state["executor_messages"][-1] if state["executor_messages"] else None
        
        if not last_message or not isinstance(last_message, AIMessage):
            logger.warning("最后一条消息不是 AIMessage")
            return {"optional_search_results": []}
        
        if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
            logger.warning("AIMessage 中没有 tool_calls")
            return {"optional_search_results": []}
        
        optional_tools = self._get_optional_tools()
        tool_node = ToolNode(optional_tools)
        tool_call_info = self._build_tool_call_info(last_message.tool_calls)
        
        try:
            logger.info(f"准备执行 {len(last_message.tool_calls)} 个可选工具调用")
            
            # ToolNode.ainvoke() 接收 AIMessage，返回 ToolMessage 列表
            tool_messages = await tool_node.ainvoke([last_message])
            
            # 确保返回的是列表
            if not isinstance(tool_messages, list):
                tool_messages = [tool_messages]
            
            normalized_tool_messages = []
            logger.info(f"可选工具执行完成，返回 {len(tool_messages)} 条 ToolMessage")
            for tool_msg in tool_messages:
                tool_call_id = getattr(tool_msg, "tool_call_id", None)
                call_info = tool_call_info.get(tool_call_id, {})
                tool_name = call_info.get("name", "") or getattr(tool_msg, "name", "")
                tool_args = call_info.get("args", {})

                tool_msg = self._ensure_tool_message_name(tool_msg, tool_name)
                normalized_tool_messages.append(tool_msg)

                try:
                    content = json.loads(tool_msg.content) if isinstance(tool_msg.content, str) else tool_msg.content
                    if isinstance(content, list):
                        logger.info(f"  - 工具 {tool_name} 返回 {len(content)} 条结果")
                    else:
                        logger.info(f"  - 工具 {tool_name} 执行完成")
                except Exception:
                    logger.info(f"  - 工具 {tool_name} 执行完成")
            
            return {"optional_search_results": normalized_tool_messages, "executor_messages": normalized_tool_messages}
        
        except Exception as e:
            logger.error(f"执行可选工具时出错: {e}")
            raise e
    
    async def _search_node(self, state: ExecutorState) -> dict:
        """搜索节点：并行调用必需的搜索工具"""
        query = state["sub_query"]
        required_tool_names = self._get_required_tools()
        
        search_results = []
        
        # 并行调用必需工具
        logger.info(f"开始并行调用必需工具: {required_tool_names}")
        
        # 提前验证并获取工具对象
        tools_to_invoke = []
        for tool_name in required_tool_names:
            tool = next((t for t in self.search_tools if tool_name in t.name.lower()), None)
            if not tool:
                logger.error(f"未找到必需工具: {tool_name}")
                raise ValueError(f"未找到必需工具: {tool_name}")
            tools_to_invoke.append(tool)
        
        # 使用 asyncio.gather 并发调用所有工具
        tasks = [self._invoke_single_tool(tool, query) for tool in tools_to_invoke]
        #[Exception，[paper]] 将正常结果进行判断
        results = await asyncio.gather(*tasks, return_exceptions=True) #有异常也不终端
        
        # 处理结果，遇到异常记录，继续执行 
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"工具 {tools_to_invoke[i].name} 执行失败: {result}")
                # 不中断流程，继续处理其他工具的结果
            elif isinstance(result, list):# list[paper]
                search_results.extend(result)
        
        logger.info(f"搜索完成，共获得 {len(search_results)} 条结果")
        return {"search_results": search_results} #先不将工具检索的list[paper] 保存到"executor_messages"中
    
    def _deduplicate_with_priority(self,
                                   search_results: List[Dict],
                                   optional_results: List[Dict]) -> List[Dict]:
        """
        根据 URL 去重，优先级：wiki > tavily > exa > optional
        注意：context7 和 grep 的结果不进行去重，全部保留
        因为这些工具返回的是代码片段和文档内容，不应该基于 URL 去重

        Args:
            search_results: 必需工具的结果（wiki, tavily, exa）
            optional_results: 可选工具的结果（可能包含 context7 和 grep）

        Returns:
            去重后的结果列表（context7 和 grep 结果全部保留）
        """
        # 按优先级分组（扩展支持 context7 和 grep）
        priority_groups = {
            "wiki": [],
            "tavily": [],
            "exa": [],
            "context7": [],  # 新增：Context7 结果单独分组
            "grep": [],      # 新增：Grep 结果单独分组
            "optional": []   # 其他可选工具（sec_edgar, akshare）
        }

        # 分类 search_results
        for paper in search_results:
            source = paper.get("source", "").lower()
            if "wikipedia" in source:
                priority_groups["wiki"].append(paper)
            elif "tavily" in source:
                priority_groups["tavily"].append(paper)
            elif "exa" in source or "context" in source:
                priority_groups["exa"].append(paper)

        # 分类 optional_results（根据 source 字段）
        for paper in optional_results:
            source = paper.get("source", "").lower()

            if "context7" in source:
                priority_groups["context7"].append(paper)
                logger.debug(f"将结果归类到 context7 组: {paper.get('title', 'N/A')[:50]}")
            elif "grep" in source:
                priority_groups["grep"].append(paper)
                logger.debug(f"将结果归类到 grep 组: {paper.get('file_path', 'N/A')[:50]}")
            else:
                # 其他可选工具（sec_edgar, akshare）
                priority_groups["optional"].append(paper)
                logger.debug(f"将结果归类到 optional 组: source={source}")

        # 步骤 1: 对 wiki/tavily/exa/optional 按 URL 去重
        url_to_paper = {}

        for priority in ["wiki", "tavily", "exa", "optional"]:
            for paper in priority_groups[priority]:
                url = paper.get("url")
                if url and url not in url_to_paper:
                    url_to_paper[url] = paper
                    logger.debug(f"保留结果（URL去重）: {url[:80]}")
                elif not url:
                    # 没有 URL 的也保留（使用递增 key）
                    unique_key = f"no_url_{len(url_to_paper)}"
                    url_to_paper[unique_key] = paper
                    logger.debug(f"保留结果（无URL）: {unique_key}")

        # 步骤 2: 提取去重后的结果
        deduplicated = list(url_to_paper.values())

        # 步骤 3: 追加 context7 结果（不进行去重，全部保留）
        context7_count = len(priority_groups["context7"])
        if context7_count > 0:
            deduplicated.extend(priority_groups["context7"])
            logger.info(f"追加 {context7_count} 条 Context7 结果（不进行去重）")

        # 步骤 4: 追加 grep 结果（不进行去重，全部保留）
        grep_count = len(priority_groups["grep"])
        if grep_count > 0:
            deduplicated.extend(priority_groups["grep"])
            logger.info(f"追加 {grep_count} 条 Grep 结果（不进行去重）")

        # 步骤 5: 记录去重统计
        total_before = len(search_results) + len(optional_results)
        total_after = len(deduplicated)
        dedup_ratio = ((total_before - total_after) / total_before * 100) if total_before > 0 else 0

        logger.info(f"去重统计: 去重前={total_before}, 去重后={total_after}, 去重率={dedup_ratio:.1f}%")

        return deduplicated

    async def _clean_node(self, state: ExecutorState) -> dict:
        """
        清洗和去重节点

        1. 合并 search_results 和 optional_search_results
        2. 根据 URL 去重（优先级：wiki > tavily > exa > optional）
        3. 更新 sub——url_pool
        """
        try:
            search_results = state.get("search_results", [])
            optional_search_results = state.get("optional_search_results", [])
            sub_url_pool = state.get("sub_url_pool", [])
            if not sub_url_pool:
                logger.warning(
                    f"处理{state.get('user_query')}----{state.get('sub_query')}时sub_url_pool 为空"
                )
        except Exception as e:
            logger.error(f"ExecutorAgent clean_node 获取状态失败: {e}")
            raise e

        if not search_results and not optional_search_results:
            logger.warning("没有搜索结果需要去重")
            return {"deduplicated_results": [], "url_pool": []}

        # 从 optional_search_results 中提取 paper 并添加 source 字段
        optional_papers = []
        for tool_msg in optional_search_results:
            try:
                content = tool_msg.content

                # 根据 tool_msg.name 识别工具类型并添加 source
                tool_name = getattr(tool_msg, "name", "") or ""
                if tool_name in {"query-docs", "grep_query", "resolve-library-id"}:
                    logger.info(f"跳过工具 {tool_name} 的结果（非 paper 结构）")
                    continue
                source = None

                if "grep" in tool_name.lower():
                    source = "grep"
                    logger.debug(f"识别到 grep 工具，添加 source='grep'")
                elif "query" in tool_name.lower() and "doc" in tool_name.lower():
                    source = "context7"
                    logger.debug(f"识别到 query-docs 工具，添加 source='context7'")
                elif "resolve" in tool_name.lower() and "library" in tool_name.lower():
                    source = "context7"  # resolve-library-id 也属于 Context7
                    logger.debug(f"识别到 resolve-library-id 工具，添加 source='context7'")

                parsed_content = self._parse_tool_content(content)
                papers, _, _ = self._extract_papers_payload(parsed_content)
                if not isinstance(papers, list):
                    logger.warning(f"ToolMessage content 类型异常: {type(papers)}")
                    continue

                # 为每个 paper 添加 source 字段（如果工具级别有 source）
                for paper in papers:
                    if not isinstance(paper, dict):
                        continue
                    if source and not paper.get("source"):
                        paper["source"] = source
                    optional_papers.append(paper)
                logger.info(f"从工具 {tool_name} 提取 {len(papers)} 条结果，source={source}")

            except (json.JSONDecodeError, AttributeError) as e:
                logger.warning(f"解析 optional_search_results 失败: {e}")

        # 先基于 sub_url_pool 过滤 wiki/tavily/exa/optional
        pool_set = set(sub_url_pool or [])
        filtered_search_results = []
        filtered_optional_papers = []
        for paper in search_results:
            source = paper.get("source", "").lower()
            if source in {"wikipedia", "tavily"} or "exa" in source:
                url = paper.get("url")
                if url and url in pool_set:
                    continue
                if url:
                    pool_set.add(url)
            filtered_search_results.append(paper)

        for paper in optional_papers:
            source = paper.get("source", "").lower()
            if source in {"sec_edgar", "akshare", "optional"}:
                url = paper.get("url")
                if url and url in pool_set:
                    continue
                if url:
                    pool_set.add(url)
            filtered_optional_papers.append(paper)

        # 应用去重逻辑（优先级：wiki > tavily > exa > optional）
        deduplicated_results = self._deduplicate_with_priority(
            filtered_search_results, filtered_optional_papers
        )

        logger.info(f"去重前: {len(search_results) + len(optional_papers)} 篇")
        logger.info(f"去重后: {len(deduplicated_results)} 篇")

        return {
            "deduplicated_results": deduplicated_results,
            "sub_url_pool": list(pool_set)
        }
    
    async def _download_node(self, state: ExecutorState) -> dict:
        """下载节点：下载 deduplicated_results 和 optional_search_results 中的文档"""
        deduplicated_results = state.get("deduplicated_results", [])
        optional_search_results = state.get("optional_search_results", [])

        allowed_sources = {
            "wikipedia",
            "tavily",
            "exa_context",
            "exa_summary",
            "sec_edgar",
            "akshare"
        }

        # 合并所有需要下载的文档
        all_papers = []

        # 添加 deduplicated_results
        if deduplicated_results:
            all_papers.extend(deduplicated_results)
            logger.info(f"从 deduplicated_results 获取 {len(deduplicated_results)} 篇文档")
        
        # 从 optional_search_results (List[ToolMessage]) 中提取文档
        if optional_search_results:
            for tool_msg in optional_search_results:
                try:
                    # tool_msg 是 ToolMessage 对象
                    tool_name = getattr(tool_msg, "name", "") or ""
                    if tool_name in {"query-docs", "grep_query"}:
                        self._persist_context7_grep_results(tool_name, tool_msg.content)
                        logger.info(f"已将工具 {tool_name} 结果追加写入 context7_grep.json")
                        continue
                    if tool_name == "resolve-library-id":
                        logger.info(f"跳过工具 {tool_name} 的下载结果合并")
                        continue

                    parsed_content = self._parse_tool_content(tool_msg.content)
                    papers, _, _ = self._extract_papers_payload(parsed_content)
                    if not isinstance(papers, list):
                        continue

                    filtered_papers = [
                        paper for paper in papers
                        if isinstance(paper, dict) and paper.get("source") in allowed_sources
                    ]
                    if filtered_papers:
                        all_papers.extend(filtered_papers)
                        logger.info(
                            f"从 optional_search_results 的工具 {tool_msg.name} 获取 {len(filtered_papers)} 篇文档"
                        )
                except (json.JSONDecodeError, AttributeError) as e:
                    logger.warning(f"解析 optional_search_results 失败: {e}")
                    continue
        
        if not all_papers:
            logger.warning("没有需要下载的文档")
            return {"downloaded_papers": []}
        
        logger.info(f"总共需要下载 {len(all_papers)} 篇文档")
        
        download_tools = await self._get_download_tools()
        downloaded_papers = []
        
        # 按 source 分组
        papers_by_source = {}
        for paper in all_papers:
            if not isinstance(paper, dict):
                continue
            source = paper.get("source", "unknown")
            if source not in allowed_sources:
                continue
            if source not in papers_by_source:
                papers_by_source[source] = []
            papers_by_source[source].append(paper)
        
        # 并发调用所有数据源的下载工具
        async def download_source(source: str, papers: list, download_tools: list) -> list:
            """并发下载单个数据源的文档"""
            try:
                logger.info(f"开始下载 {source} 的 {len(papers)} 篇文档到 {Config.DOC_SAVE_PATH}")

                download_tool_name = f"{source}_download"
                download_tool = next((t for t in download_tools if download_tool_name in t.name.lower()), None)

                if download_tool:
                    logger.info(f"使用下载工具 {download_tool.name} 处理 {source} 数据")
                    result = await download_tool.ainvoke({
                        "papers": papers,
                        "save_path": Config.DOC_SAVE_PATH
                    })

                    if result:
                        logger.info(f"下载工具 {download_tool.name} 返回类型: {type(result)}")
                        if isinstance(result, list) and result:
                            logger.info(
                                f"下载工具 {download_tool.name} 首项类型: {type(result[0])}"
                            )
                        parsed_content = self._parse_tool_content(result)
                        if isinstance(parsed_content, dict):
                            logger.info(
                                f"下载解析 payload: keys={list(parsed_content.keys())}, "
                                f"count={parsed_content.get('count')}"
                            )
                        else:
                            logger.warning(
                                f"下载解析 payload 失败，返回类型: {type(parsed_content)}"
                            )
                        downloaded, _, _ = self._extract_papers_payload(parsed_content)
                        if isinstance(downloaded, list):
                            logger.info(f"成功下载 {len(downloaded)} 篇 {source} 文档")
                            return downloaded
                        logger.warning(f"未知的下载结果类型: {type(parsed_content)}")
                        return []
                else:
                    logger.warning(f"未找到 {source} 的下载工具")

            except Exception as e:
                logger.error(f"下载 {source} 文档时出错: {e}")
                import traceback
                traceback.print_exc()

            return []

        # 并发执行所有下载任务
        tasks = [
            download_source(source, papers, download_tools)
            for source, papers in papers_by_source.items()
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 合并结果
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"下载任务异常: {result}")
            elif isinstance(result, list):
                downloaded_papers.extend(result)
        
        logger.info(f"下载完成，共下载 {len(downloaded_papers)} 篇文档")
        return {"downloaded_papers": downloaded_papers}
      
    def _build_graph(self):
        """构建 ExecutorAgent 的处理流程图"""
        builder = StateGraph(ExecutorState)
        
        # 添加节点
        builder.add_node("search", self._search_node)
        builder.add_node("llm_chat", self._llm_chat_node)
        builder.add_node("optional_tool_node", self._optional_tool_node)
        builder.add_node("clean", self._clean_node)
        builder.add_node("download", self._download_node)

        # 添加边
        builder.add_edge(START, "search")
        builder.add_conditional_edges(
            "llm_chat",
            self._should_call_optional_tools,
            {
                "optional_tool_node": "optional_tool_node",
                "clean": "clean"
            }
        )
        builder.add_edge("optional_tool_node", "llm_chat")
        builder.add_edge("search", "llm_chat")
        builder.add_edge("clean", "download")
        builder.add_edge("download", END)
        
        if self.memory:
            graph = builder.compile(checkpointer=self.memory)
        else:
            graph = builder.compile()
        logger.info("完成 executor_graph 的初始化构造")
        return graph
    
    async def ainvoke(self, query: str, thread_id: str,user_id:str, sub_url_pool:list[str],user_query: str ) -> Dict:
        """执行单个子问题的完整处理流程"""
        # 确保异步资源已初始化
        await self._ensure_initialized()

        config = {"configurable": {"thread_id": thread_id, "user_id": user_id}}
        initial_state = {
            "executor_messages": [HumanMessage(content=query)],
            "user_query": user_query,
            "sub_query": query,
            "optional_search_results": [],
            "search_results": [],
            "deduplicated_results": [],
            "downloaded_papers": [],
            "sub_url_pool": sub_url_pool
        }
        
        try:
            result = await self.graph.ainvoke(initial_state, config)
            logger.info(f"executor 完成子问题 '{query}' 的处理")
            required_tools = self._get_required_tools()
            compressed_state = dict(result)
            compressed_state["executor_messages"] = self._compress_executor_messages(
                result.get("executor_messages", [])
            )
            compressed_state["user_query"] = user_query
            compressed_state["sub_query"] = query
            compressed_state["optional_search_results"] = []
            compressed_state["search_summary"] = self._count_required_tool_results(
                result.get("search_results", []),
                required_tools
            )
            compressed_state["deduplicated_summary"] = self._count_required_tool_results(
                result.get("deduplicated_results", []),
                required_tools
            )
            compressed_state["downloaded_summary"] = self._count_required_tool_results(
                result.get("downloaded_papers", []),
                required_tools
            )
            compressed_state["sub_url_pool"] = result.get("sub_url_pool", [])
            
            compressed_state["downloaded_papers"]=result.get("downloaded_papers", [])
            if not compressed_state["downloaded_papers"]:
                logger.warning(f"executor 完成后 downloaded_papers 为空")
            if not compressed_state["sub_url_pool"]:
                logger.warning(f"executor 完成后 sub_url_pool 为空")
            return compressed_state
        except Exception as e:
            logger.error(f"executor 处理子问题 '{query}' 时出错: {e}")
            traceback.print_exc()
            raise e
    
    async def _clean(self):
        """清理资源"""
        if self._context7_grep_client:
            try:
                await self._context7_grep_client.close()
            except Exception as e:
                logger.info(f"尝试关闭 Context7GrepMCPClient 失败：{e}")
        if self.memory:
            try:
                await self.memory.aclose()
                logger.info("对实例化的 ExecutorAgent,完成对短期记忆连接池的断开处理")
            except Exception as e:
                logger.info(f"尝试对实例化的 ExecutorAgent 与短期记忆连接池断开，出现错误：{e}")
