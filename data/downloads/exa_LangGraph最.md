# LangGraph最佳实践：构建可靠有状态AI代理的关键策略 | Ningto's Blog

**URL**:
https://www.ningto.com/blog/2025/langGraph-best-practices-strategies-for-reliable-stateful-ai-agents-2025-09-10

## 元数据
- 发布日期: 2025-09-10T00:00:00+00:00

## 完整内容
---
LangGraph最佳实践：构建可靠有状态AI代理的关键策略 | Ningto's Blog

目录

- 参考资料
- 四、总结
- 三、实战案例：构建有状态对话代理
- 6. 优化模型与工具调用
- 5. 用LangSmith实现可视化调试
- 4. 严格控制人机协作（Human-in-the-Loop）
- 3. 利用子图（Subgraph）实现模块化
- 2. 强制使用检查点（Checkpoint）
- 1. 设计清晰的状态结构（State Design）
- 二、核心最佳实践
- 一、前言
- LangGraph最佳实践：构建可靠有状态AI代理的关键策略

# LangGraph最佳实践：构建可靠有状态AI代理的关键策略

## 一、前言

LangGraph作为专注于长期运行、有状态AI代理的低级别编排框架，其核心价值在于解决传统无状态代理的痛点（如状态丢失、调试困难、无法持久化等）。要充分发挥LangGraph的优势，需遵循一系列最佳实践，涵盖状态管理、流程设计、调试优化等多个维度。本文结合官方文档及实战经验，总结了LangGraph开发的关键策略。

## 二、核心最佳实践

### 1. 设计清晰的状态结构（State Design）

状态是LangGraph的核心，需结构化、可扩展，避免冗余或模糊。建议将状态分为以下模块：

- 控制信号（Control Signals）：用于流程控制的临时状态（如`{"need_human_approval":true}`），指示代理是否需要暂停等待人类介入。
- 长期记忆（Long-term Memory）：保存跨会话的用户偏好、任务进度等（如`{"user_preference":"喜欢简洁回答","task_progress":"完成数据收集"}`），需定期持久化（如存入数据库）。
- 工具调用记录（Tool Calls）：存储代理调用工具的输入/输出（如`[{"tool":"get_weather","input":"旧金山","output":"晴天"}]`），便于回溯工具使用情况。
- 对话上下文（Messages）：保存用户与代理的交互历史（如`[{"role":"user","content":"..."}]`），用于模型理解上下文。

示例：

```
from langgraph.schema import StateGraph
from typing import TypedDict, List
from langgraph.schema import Message

# 定义强类型状态结构
class AgentState(TypedDict):
    messages: List[Message]          # 对话历史
    tool_calls: List[dict]           # 工具调用记录
    long_term_memory: dict           # 长期记忆
    need_human_approval: bool        # 人机协作信号

```

### 2. 强制使用检查点（Checkpoint）

检查点是LangGraph持久化执行的关键，需在关键节点（如工具调用前、状态变更后）保存状态，确保任务中断后可恢复。

推荐场景：

- 高风险操作（如资金转账、内容生成）：操作前保存检查点，避免错误无法回滚；
- 长期任务（如数据爬取、多轮对话）：每完成一个子任务保存一次检查点；

示例：

```
from langgraph.checkpoint import LocalCheckpointSaver

# 初始化本地检查点保存器
checkpoint_saver = LocalCheckpointSaver(directory="./langgraph_checkpoints")

# 创建带检查点的状态图
state_graph = StateGraph(AgentState).with_checkpoint(checkpoint_saver)

```

### 3. 利用子图（Subgraph）实现模块化

子图是LangGraph代码复用的核心机制，将复杂流程拆分为独立子模块（如“用户意图识别”“工具调用”“结果整理”），降低维护成本。

推荐场景：

- 可配置流程（如不同用户角色对应不同子图）；
- 重复流程（如“获取用户信息→调用工具→生成回答”）；

示例：

```
from langgraph import Subgraph

# 定义“工具调用”子图
class ToolSubgraph(Subgraph):
    def __init__(self):
        super().__init__()
        self.add_node("call_tool", self._call_tool)
        self.add_node("parse_result", self._parse_result)
        self.add_edge("call_tool", "parse_result")

    def _call_tool(self, state: AgentState) -> AgentState:
        # 工具调用逻辑
        return state

    def _parse_result(self, state: AgentState) -> AgentState:
        # 结果解析逻辑
        return state

# 将子图嵌入主图
main_graph = StateGraph(AgentState)
main_graph.add_subgraph(ToolSubgraph(), name="tool_flow")

```

### 4. 严格控制人机协作（Human-in-the-Loop）

LangGraph支持人类在任意节点介入，需合理设计介入时机，避免过度依赖人类或忽略风险。

推荐场景：

- 模糊查询（如用户意图不明确）：请求人类补充信息；
- 高风险决策（如内容审核、资金操作）：在决策前暂停，等待人类确认；

示例：

```
from langgraph import HumanNode

# 定义人类审批节点
human_approval_node = HumanNode(
    input_schema={"approval": bool},  # 人类输入 schema（是否批准）
    output_schema={"approved": bool} # 输出 schema（审批结果）
)

# 在流程中插入人类节点
state_graph.add_edge("decide", human_approval_node)
state_graph.add_edge(human_approval_node, "execute_action")

```

### 5. 用LangSmith实现可视化调试

LangSmith是LangGraph的调试利器，需全程使用其记录执行轨迹、状态变化、工具调用等信息，快速定位问题。

关键功能：

- 错误定位：标记执行中的错误（如工具调用失败、状态异常）；
- 性能分析：统计每一步的执行时间（如模型调用耗时、工具调用耗时）；
- 轨迹回放：查看代理每一步的状态变化（如`messages`新增、`tool_calls`更新）；

示例：

```
from langsmith import Client

# 初始化LangSmith客户端（需设置环境变量LANGSMITH_API_KEY）
langsmith_client = Client()

# 创建代理时关联LangSmith
agent = create_react_agent(
    model="anthropic:claude-3-7-sonnet-latest",
    tools=[get_weather],
    prompt="你是一个helpful的助理",
    langsmith_client=langsmith_client
)

```

### 6. 优化模型与工具调用

工具调用策略：

- 缓存结果：对频繁调用的工具（如固定数据查询）缓存结果，提高效率；
- 批量调用：将多个工具调用合并为一次（如同时获取天气和新闻），减少模型调用次数；

## 三、实战案例：构建有状态对话代理

以下是一个结合上述最佳实践的对话代理示例：

```
from langgraph import StateGraph, HumanNode
from langgraph.schema import Message
from langgraph.checkpoint import LocalCheckpointSaver
from langsmith import Client
from typing import TypedDict, List

# 定义状态结构
class ConversationState(TypedDict):
    messages: List[Message]
    tool_calls: List[dict]
    user_preference: dict
    need_human_approval: bool

# 初始化依赖
checkpoint_saver = LocalCheckpointSaver(directory="./checkpoints")
langsmith_client = Client()

# 定义节点函数
def decide_next_step(state: ConversationState) -> str:
    """决定下一步操作"""
    last_msg = state["messages"][-1]
    if "天气" in last_msg.content:
        return "call_weather_tool"
    elif "敏感内容" in last_msg.content:
        state["need_human_approval"] = True
        return "human_approval"
    else:
        return "direct_answer"

def call_weather_tool(state: ConversationState) -> ConversationState:
    """调用天气工具"""
    city = last_msg.content.split("天气")[0].strip()
    weather = get_weather(city)  # 假设get_weather是工具函数
    state["tool_calls"].append({"tool": "get_weather", "input": city, "output": weather})
    state["messages"].append(Message(role="assistant", content=f"天气结果：{weather}"))
    return state

# 创建状态图
graph = StateGraph(ConversationState)

# 添加节点
graph.add_node("decide", decide_next_step)
graph.add_node("call_weather_tool", call_weather_tool)
graph.add_node("human_approval", HumanNode(input_schema={"approval": bool}))
graph.add_node("direct_answer", lambda state: state)

# 添加边
graph.add_edge("decide", "call_weather_tool")
graph.add_edge("decide", "human_approval")
graph.add_edge("decide", "direct_answer")
graph.add_edge("human_approval", "direct_answer")
graph.add_edge("call_weather_tool", "direct_answer")

# 设置入口节点
graph.set_entry_point("decide")

# 编译图（带检查点与LangSmith）
compiled_graph = graph.compile(
    checkpoint_saver=checkpoint_saver,
    langsmith_client=langsmith_client
)

# 运行代理
initial_state = {
    "messages": [Message(role="user", content="北京的天气怎么样？")],
    "tool_calls": [],
    "user_preference": {},
    "need_human_approval": False
}
result = compiled_graph.invoke(initial_state)

print(result["messages"][-1].content)

```

## 四、总结

LangGraph的最佳实践围绕“有状态、可持久化、可调试”展开，核心是设计清晰的状态结构、强制使用检查点、利用子图模块化、合理引入人机协作及用LangSmith调试。这些策略能帮助开发者构建可靠、可扩展的AI代理，适用于长期对话、数据处理、智能助手等场景。

## 参考资料

- LangGraph实战示例： [https://github.com/langchain-ai/langgraph/tree/main/examples] 
- LangSmith调试指南： [https://docs.smith.langchain.com/] 
- LangGraph官方文档： [https://langgraph.ai/docs/] 
- 错误处理：工具调用失败时（如API超时），需重试或 fallback 到默认值，并记录错误信息（如`{"tool_error":"API timeout","timestamp":"2024-05-01 10:00:00"}`）。

## 上一篇文章

[Docker & Docker Compose部署与排查常用命令总结] 

## 下一篇文章

[LangGraph入门指南：构建长期运行的有状态AI代理] 

[← 返回博客列表]


---
*数据来源: Exa搜索 | 获取时间: 2026-02-21 20:11:33*