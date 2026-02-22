import asyncio

from typing import TypedDict, Annotated, List, Any
from langchain_core.messages import AnyMessage, AIMessage, SystemMessage, HumanMessage, ToolMessage
from langgraph.graph import add_messages, StateGraph, START, END
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool
import logging, json
from langgraph.prebuilt import ToolNode
from langchain_core.tools import BaseTool
from concurrent_log_handler import ConcurrentRotatingFileHandler
from core.config import Config
from core.llms import lang_llm
from core.mcp.tools import get_tools
from core.mcp.context7_grep import Context7GrepMCPClient
from dotenv import load_dotenv
from core.log_config import setup_logger

load_dotenv()

# 设置日志
logger = setup_logger(__name__)
prompt = """请你按照**“书记书签页”的思维方式拆解以下问题，目标是生成一组可直接用于检索的子问题**。

拆解要求：
- 你判断一下是否需要使用提供的工具，获取到一些客观、实时、前沿的背景信息
- 给出一句高度凝练的整体判断，明确问题的核心方向
- 将问题拆解为若干并列的关键子问题，这些子问题共同覆盖决策所需的信息面
- 每一个子问题都必须满足可检索性
- 子问题数量不能超过4个
- 表述为明确的问题句或查询句
- 包含清晰的 主体 / 行为 / 对象 / 约束条件
- 避免抽象词（如“如何看待”“是否合理”），必要时具体化为“在什么条件下 / 针对什么对象 / 产生什么影响”
- 子问题之间应尽量正交（避免重复、交叉）
- 不限制子问题数量,你需要根据用户问题的复杂度来拆分
- 不使用章节编号或层级符号，整体呈现应类似一页书签提示清单
- 语言风格：判断导向、信息导向、检索友好。你可以在需要时调用工具获取信息。
- 当你可以获得最终的输出时，最终输出格式必须是 JSON：

Few-shot 示例：
用户问题：
“新能源补贴退坡会对地方新能源项目投资产生什么影响？”

输出：
```
{
    "tasks": [
    "在新能源补贴退坡政策实施后，地方新能源项目投资规模和节奏发生了哪些变化",
    "新能源补贴退坡对不同类型地方新能源项目（风电、光伏等）的影响差异",
    "地方政府在补贴退坡背景下对新能源项目投资决策采取了哪些应对措施",
    "新能源补贴退坡对地方新能源项目融资成本和回报预期的具体影响",
    "若补贴持续退坡，地方新能源项目投资面临的主要中长期风险有哪些"
    ]
}
```

用户问题：
“为什么 RAG 系统在复杂问题上容易出现答非所问？”

输出：
```
{
    "tasks": [
    "在复杂问题场景下，RAG 系统常见的检索失败类型有哪些",
    "RAG 系统中问题拆解和 query 生成不足会如何导致答非所问",
    "向量检索在处理长问题或多约束问题时存在哪些语义偏移问题",
    "上下文拼接策略不当对 RAG 回答相关性的影响机制",
    "提升 RAG 系统在复杂问题场景下回答准确性的典型优化方法"
    ]
}
```

用户问题：
“当前业务增长放缓的主要原因是什么？”

输出：
```
{
    "tasks": [
    "近期业务增长放缓的具体表现和关键业务指标变化情况",
    "影响当前业务增长的内部因素有哪些（产品、运营、组织等）",
    "外部市场环境和竞争格局变化对业务增长的影响",
    "用户需求变化在业务增长放缓中起到的作用",
    "若不调整现有策略，业务增长放缓可能带来的中长期影响"
    ]
}
```
"""

class PlannerState(TypedDict):
    planner_messages: Annotated[list[AnyMessage], add_messages]
    planner_result: AIMessage
    epoch: int
    

class PlannerAgent:
    def __init__(self, pool: AsyncConnectionPool=None, modelname: str = Config.LLM_PLANNER):
        self.chat_llm = lang_llm(
            chat_name=modelname,
            embedding_name=Config.LLM_EMBEDDING
        )[0]
        if pool is None:
            self.memory = None
        else:
            self.memory = AsyncPostgresSaver(pool)
        self.planner_tools: list[BaseTool] = []
        self._context7_client = None
        self.graph = self._build_graph()
        self.llm_with_tools = None
    async def _ensure_planner_tools(self) -> list[BaseTool]:
        if self.planner_tools:
            return self.planner_tools

        search_tools = await get_tools(tool_type="search")
        exa_tools = [tool for tool in search_tools if tool.name == "exa_summary_search"]

        self._context7_client = Context7GrepMCPClient(context7_need=True, grep_need=False)
        context7_tools = await self._context7_client.get_context7_tools()

        self.planner_tools = exa_tools + context7_tools
        return self.planner_tools

    async def _llm_chat(self, state: PlannerState, planner_epoch=Config.PLANNER_EPOCH) -> dict:

        await self._ensure_planner_tools()
        if self.llm_with_tools is None:
            self.llm_with_tools = self.chat_llm.bind_tools(self.planner_tools)
        try:
            if state["epoch"] < planner_epoch:
                result = await self.llm_with_tools.ainvoke(state["planner_messages"])
                if isinstance(result, AIMessage):
                    logger.info(f"planner_agent llm_chat 节点在第{state['epoch']}轮迭代中，成功生成AIMessage类型的消息，内容为:{result.content}")
                    tool_calls = result.tool_calls or []
                    logger.info(
                        "planner_agent llm_chat: tool_calls_count=%s, tool_names=%s",
                        len(tool_calls),
                        [call.get("name") for call in tool_calls],
                    )
                    logger.info(
                        "planner_agent llm_chat: planner_messages_len=%s",
                        len(state["planner_messages"]),
                    )
                    if result.tool_calls:
                        logger.info(f"planner_agent llm_chat 节点在第{state['epoch']}轮迭代中，生成的AIMessage类型的消息包含工具调用，工具调用内容为:{result.tool_calls}")
                        epoch=state["epoch"]
                    else:
                        epoch=state["epoch"]+1
                else:
                    logger.error(f"planner_agent llm_chat 节点在第{state['epoch']}轮迭代中，生成的消息非AIMessage类型，类型为:{type(result)}，内容为:{result}")
                    raise TypeError(f"planner_agent llm_chat 节点在第{state['epoch']}轮迭代中，生成的消息非AIMessage类型，类型为:{type(result)}")
                return {"planner_messages": [result], "epoch":epoch}
        except Exception as e:
            logger.error(f"planner_agent llm_chat 分析用户的问题时，出现错误:{e}")
            raise e

    async def _tool_node(self, state: PlannerState) -> dict:
        tools = await self._ensure_planner_tools()
        tool_node = ToolNode(tools, messages_key="planner_messages")
        tool_messages_raw: Any = []
        tool_calls = []
        last_message = state["planner_messages"][-1]
        if isinstance(last_message, AIMessage):
            tool_calls = last_message.tool_calls or []
            tool_names = [call.get("name") for call in tool_calls]
            registered = [tool.name for tool in tools]
            missing = [name for name in tool_names if name and name not in registered]
            logger.info("planner_agent tool_node: tool_calls=%s", tool_names)
            logger.info("planner_agent tool_node: registered_tools=%s", registered)
            if missing:
                logger.warning("planner_agent tool_node: missing_tools=%s", missing)
        try:
            tool_result = await tool_node.ainvoke(state)
            if isinstance(tool_result, dict) and "planner_messages" in tool_result:
                tool_messages_raw = tool_result["planner_messages"]
            else:
                tool_messages_raw = tool_result
        except Exception as e:
            logger.error(f"planner_agent tool_node 执行失败: {e}")
            tool_messages_raw = []

        if not isinstance(tool_messages_raw, list):
            tool_messages = [tool_messages_raw]
        else:
            tool_messages = tool_messages_raw

        existing_tool_ids = {
            message.tool_call_id
            for message in tool_messages
            if isinstance(message, ToolMessage)
        }
        logger.info(
            "planner_agent tool_node: tool_messages_count=%s, tool_message_ids=%s",
            len(existing_tool_ids),
            sorted(existing_tool_ids),
        )
        for call in tool_calls:
            call_id = call.get("id")
            if not call_id or call_id in existing_tool_ids:
                continue
            tool_messages.append(
                ToolMessage(
                    content="tool execution failed or empty result",
                    tool_call_id=call_id,
                )
            )
        return {"planner_messages": tool_messages}

    def _condition_router(self, state: PlannerState, planner_epoch=Config.PLANNER_EPOCH):
        result = state["planner_messages"][-1]
        if isinstance(result, AIMessage):
            def is_valid_tasks(obj: Any) -> bool:
                if isinstance(obj, dict):
                    return "tasks" in obj and isinstance(obj["tasks"], list)
                if isinstance(obj, list):
                    return any(
                        isinstance(item, dict)
                        and "tasks" in item
                        and isinstance(item["tasks"], list)
                        for item in obj
                    )
                return False

            def strip_code_fence(content: str) -> str:
                cleaned = content.strip()
                if cleaned.startswith("```") and cleaned.endswith("```"):
                    cleaned_lines = [
                        line for line in cleaned.splitlines() if not line.strip().startswith("```")
                    ]
                    cleaned = "\n".join(cleaned_lines).strip()
                return cleaned

            def extract_json_from_text(content: str) -> Any:
                cleaned = content.strip()
                lower = cleaned.lower()
                fence_start = lower.find("```json")
                if fence_start != -1:
                    fence_open = cleaned.find("```", fence_start)
                    if fence_open != -1:
                        fence_open += 3
                        newline = cleaned.find("\n", fence_open)
                        if newline != -1:
                            fence_open = newline + 1
                    fence_end = cleaned.find("```", fence_open)
                    if fence_end != -1:
                        fenced_content = cleaned[fence_open:fence_end].strip()
                        if fenced_content:
                            try:
                                return json.loads(fenced_content)
                            except Exception:
                                pass

                opens = [index for index, ch in enumerate(cleaned) if ch == "{"]
                closes = [index for index, ch in enumerate(cleaned) if ch == "}"]
                for start in opens:
                    for end in closes:
                        if end <= start:
                            continue
                        snippet = cleaned[start : end + 1].strip()
                        if not snippet:
                            continue
                        try:
                            return json.loads(snippet)
                        except Exception:
                            continue
                return None

            if state["epoch"] >= planner_epoch:
                state["planner_result"] = AIMessage(content=json.dumps({"tasks": []}))
                logger.warning(f"planner_agent 达到最大迭代次数{planner_epoch}，结束planner流程")
                return "END"
            if result.tool_calls:
                logger.info("planner_agent 条件路由器检测到上一步存在工具调用，进入tool_node节点")
                return "tool_node"
            if state["epoch"] < planner_epoch:
                try:
                    if isinstance(result.content, str):
                        parsed = json.loads(strip_code_fence(result.content))
                        if is_valid_tasks(parsed):
                            logger.info(
                                f"planner_agent 在第{state['epoch']}轮迭代中，成功生成有效的json结构，进入persist_result节点"
                            )
                            return "persist_result"
                        return "llm_chat"
                    if is_valid_tasks(result.content):
                        logger.info(
                            f"planner_agent 在第{state['epoch']}轮迭代中，成功生成有效的json结构，进入persist_result节点"
                        )
                        return "persist_result"
                    return "llm_chat"
                except Exception:
                    if isinstance(result.content, str):
                        extracted = extract_json_from_text(result.content)
                        if extracted is not None and is_valid_tasks(extracted):
                            logger.info(
                                f"planner_agent 在第{state['epoch']}轮迭代中，解析混合文本后获得有效json结构，进入persist_result节点"
                            )
                            return "persist_result"
                    logger.info(f"planner_agent 在第{state['epoch']}轮迭代中，未能生成有效的json结构，继续进入llm_chat节点")
                    return "llm_chat"
        logger.error(f"planner_agent 条件路由器收到非AIMessage类型的消息，类型为:{type(result)}，内容为:{result.content}")
        raise TypeError(f"planner_agent 条件路由器收到非AIMessage类型的消息，类型为:{type(result)}")

    async def _persist_result(self, state: PlannerState) -> dict:
        result = state["planner_messages"][-1]
        content = result.content
        def is_valid_tasks(obj: Any) -> bool:
            if isinstance(obj, dict):
                return "tasks" in obj and isinstance(obj["tasks"], list)
            if isinstance(obj, list):
                return any(
                    isinstance(item, dict)
                    and "tasks" in item
                    and isinstance(item["tasks"], list)
                    for item in obj
                )
            return False

        def extract_json_from_text(text: str) -> Any:
            cleaned = text.strip()
            lower = cleaned.lower()
            fence_start = lower.find("```json")
            if fence_start != -1:
                fence_open = cleaned.find("```", fence_start)
                if fence_open != -1:
                    fence_open += 3
                    newline = cleaned.find("\n", fence_open)
                    if newline != -1:
                        fence_open = newline + 1
                fence_end = cleaned.find("```", fence_open)
                if fence_end != -1:
                    fenced_content = cleaned[fence_open:fence_end].strip()
                    if fenced_content:
                        try:
                            return json.loads(fenced_content)
                        except Exception:
                            pass

            opens = [index for index, ch in enumerate(cleaned) if ch == "{"]
            closes = [index for index, ch in enumerate(cleaned) if ch == "}"]
            for start in opens:
                for end in closes:
                    if end <= start:
                        continue
                    snippet = cleaned[start : end + 1].strip()
                    if not snippet:
                        continue
                    try:
                        return json.loads(snippet)
                    except Exception:
                        continue
            return None

        parsed: Any = None
        if isinstance(content, (dict, list)):
            parsed = content
        elif isinstance(content, str):
            parsed = extract_json_from_text(content)

        if parsed is None or not is_valid_tasks(parsed):
            parsed = {"tasks": []}

        persisted = json.dumps(parsed, ensure_ascii=True)
        logger.info(f"planner_agent persist_result 节点写入结果:{persisted}")
        return {"planner_result": AIMessage(content=persisted)}

    def _build_graph(self):
        builder = StateGraph(PlannerState)
        builder.add_node("llm_chat", self._llm_chat)
        builder.add_node("tool_node", self._tool_node)
        builder.add_node("persist_result", self._persist_result)
        builder.add_edge(START, "llm_chat")
        builder.add_conditional_edges(
            "llm_chat",
            self._condition_router,
            {
                "END": END,
                "tool_node": "tool_node",
                "llm_chat": "llm_chat",
                "persist_result": "persist_result",
            }
        )
        builder.add_edge("tool_node", "llm_chat")
        builder.add_edge("persist_result", END)
        graph=builder.compile(checkpointer=self.memory)
        logger.info(f"完成planner_graph的初始化构造")
        return graph

    async def invoke(self, user_query: str, thread_id: str, user_id: str) -> Any:
        config = {"configurable": {"thread_id": thread_id, "user_id": user_id}}
        try:
            messages = [SystemMessage(content=prompt), HumanMessage(content=user_query)]
            schema = {"planner_messages": messages, "planner_result": AIMessage(content=""), "epoch": 0}
            response = await self.graph.ainvoke(schema, config)
            if response["planner_result"].content:
                logger.info(f"planner_chatmodel对于用户的{user_query} 返回结果为:{response['planner_result'].content}") 
                if isinstance(response["planner_result"].content, str):
                    try:
                        response["planner_result"].content = json.loads(response["planner_result"].content)
                        logger.info(f"planner_chatmodel对于用户的{user_query} 返回结果json解析成功，内容为:{response['planner_result'].content}")
                    except Exception as e:
                        logger.error(f"planner_chatmodel对于用户的{user_query} 返回结果json解析失败，错误为:{e}")
                elif not isinstance(response["planner_result"].content, dict):
                    logger.error(f"planner_chatmodel对于用户的{user_query} 返回结果不是dict类型，也不是string类型，内容为:{response['planner_result'].content}")
                elif isinstance(response["planner_result"].content, dict):
                    logger.info(f"planner_chatmodel对于用户的{user_query} 返回结果为dict类型，内容为:{response['planner_result'].content}")
            return response["planner_result"].content
        except Exception as e:
            logger.error(f"planner_chatmodel对于用户的{user_query} 出现错误：{e}")
            raise e

    async def _clean(self):
        if self.memory:
            try:
                close_method = getattr(self.memory, "aclose", None)
                if close_method:
                    await close_method()
                logger.info("对实例化的PlannerAgent,完成对短期记忆连接池的断开处理")
            except Exception as e:
                logger.info(f"尝试对实例化的PlannerAgent与短期记忆连接池断开，出现错误：{e}")
        if self._context7_client:
            try:
                await self._context7_client.close()
            except Exception as e:
                logger.info(f"尝试对 PlannerAgent 的 Context7 客户端断开，出现错误：{e}")
