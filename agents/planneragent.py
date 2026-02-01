import asyncio

from typing import TypedDict, Annotated, List, Any
from langchain_core.messages import AnyMessage, AIMessage, SystemMessage
from langgraph.graph import add_messages, StateGraph, START, END
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool
import logging, json
from langgraph.prebuilt import ToolNode
from langchain_core.tools import BaseTool
from concurrent_log_handler import ConcurrentRotatingFileHandler
from core.config import Config
from core.llms import get_llm
from core.mcp.tools import get_tools
from core.mcp.context7_grep import Context7GrepMCPClient
from dotenv import load_dotenv
load_dotenv()
# 设置日志基本配置，级别为DEBUG或INFO
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.handlers = []  # 清空默认处理器
# 使用ConcurrentRotatingFileHandler

handler = ConcurrentRotatingFileHandler(
    Config.LOG_FILE,
    maxBytes = Config.MAX_BYTES,
    backupCount = Config.BACKUP_COUNT
)
handler.setLevel(logging.DEBUG)
handler.setFormatter(logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
))
logger.addHandler(handler)


class PlannerState(TypedDict):
    planner_messages: Annotated[list[AnyMessage], add_messages]
    planner_result: AIMessage
    epoch: int


class PlannerAgent:
    def __init__(self, pool: AsyncConnectionPool=None, modelname: str = Config.LLM_PLANNER):
        self.chat_llm = get_llm(modelname)[0]
        if pool is None:
            self.memory = None
        else:
            self.memory = AsyncPostgresSaver(pool)
        self.planner_tools: list[BaseTool] = []
        self._context7_client = None
        self.graph = self._build_graph()

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
        prompt = """请你按照**“书记书签页”的思维方式拆解以下问题，目标是生成一组可直接用于检索的子问题**。

        拆解要求：
        - 你判断一下是否需要使用提供的工具，获取到一些客观、实时、前沿的背景信息
        - 给出一句高度凝练的整体判断，明确问题的核心方向
        - 将问题拆解为若干并列的关键子问题，这些子问题共同覆盖决策所需的信息面
        - 每一个子问题都必须满足可检索性
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
        await self._ensure_planner_tools()
        user_query = state["planner_messages"][0].content
        messages = ChatPromptTemplate.from_messages([{"role": "system", "content": prompt},
                                                     {"role":"user","content": {query}}]).format_messages(query=user_query)
        if self.llm_with_tools is None:
            self.llm_with_tools = self.chat_llm.bind_tools(self.planner_tools)
        try:
            if state["epoch"] < planner_epoch:
                result = await self.llm_with_tools.ainvoke({"planner_messages": messages})
                logger.info("完成planner_agent中chain的初始化构造")
                state["epoch"] += 1
                return {"planner_messages": [result]}
            return {}
        except Exception as e:
            logger.error(f"planner_agent llm_chat 分析用户的问题时，出现错误:{e}")
            raise e

    async def _tool_node(self, state: PlannerState) -> dict:
        tools = await self._ensure_planner_tools()
        tool_node = ToolNode(tools)
        last_message = state["planner_messages"][-1]
        tool_messages = await tool_node.ainvoke(last_message)
        if not isinstance(tool_messages, list):
            tool_messages = [tool_messages]
        return {"planner_messages": tool_messages}

    def _condition_router(self, state: PlannerState, planner_epoch=Config.PLANNER_EPOCH):
        result = state["planner_messages"][-1]
        if isinstance(result, AIMessage):
            if getattr(result, "tool_calls", None):
                return "tool_node"
            if state["epoch"] < planner_epoch:
                try:
                    if isinstance(result.content, str):
                        _ = json.loads(result.content)
                        state["planner_result"] = result
                        return "END"
                    return "llm_chat"
                except Exception:
                    return "llm_chat"
            state["planner_result"] = AIMessage(content=str({"tasks": "error"}))
            logger.warning(f"planner_agent 达到最大迭代次数{planner_epoch}，仍未能生成有效的json结构，结束planner流程")
            return "END"
        logger.error(f"planner_agent 条件路由器收到非AIMessage类型的消息，类型为:{type(result)}，内容为:{result.content}")
        raise TypeError(f"planner_agent 条件路由器收到非AIMessage类型的消息，类型为:{type(result)}")

    def _build_graph(self):
        builder = StateGraph(PlannerState)
        builder.add_node("llm_chat", self._llm_chat)
        builder.add_node("tool_node", self._tool_node)
        builder.add_edge(START, "llm_chat")
        builder.add_conditional_edges(
            "llm_chat",
            self._condition_router,
            {"END": END, "tool_node": "tool_node", "llm_chat": "llm_chat"}
        )
        builder.add_edge("tool_node", "llm_chat")
        builder.compile(checkpointer=self.memory)
        logger.info(f"完成planner_graph的初始化构造")
        return builder

    async def invoke(self, state: PlannerState, thread_id: str):
        query = state["planner_messages"][0]
        config = {"configurable": {"thread_id": thread_id}}
        try:
            response = await self.chat_llm.ainvoke(query, config)
            logger.info(f"planner_chatmodel对于用户的{query} 返回:{response}")
            return response
        except Exception as e:
            logger.error(f"planner_chatmodel对于用户的{query} 出现错误：{e}")
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
