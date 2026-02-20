# LangGraph 快速入门 - AiDocZh

**URL**:
https://www.aidoczh.com/langgraph/tutorials/introduction/

## 元数据
- 发布日期: 2026-02-20T20:40:07.476603

## 完整内容
---
🚀 LangGraph 快速入门

Skip to content

# 🚀 LangGraph 快速入门¶

在本教程中，我们将构建一个支持的聊天机器人，在LangGraph中可以：

✅ 通过搜索网络 来 回答常见问题 ✅ 在调用之间保持对话状态 ✅ 将复杂查询 转发给人工进行审核 ✅ 使用自定义状态 来控制其行为 ✅ 回溯并探索 替代对话路径

我们将从一个 基本的聊天机器人 开始，并逐步添加更复杂的功能，在此过程中介绍关键的LangGraph概念。让我们开始吧！🌟

## 设置¶

首先，安装所需的包并配置您的环境：

```
%%capture --no-stderr
%pip install -U langgraph langsmith langchain_anthropic

```

```
import getpass
import os


def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")


_set_env("ANTHROPIC_API_KEY")

```

```
ANTHROPIC_API_KEY:  ········

```

为LangGraph开发设置 [LangSmith] 

注册使用LangSmith，快速发现问题并提高您的LangGraph项目的性能。LangSmith允许您使用跟踪数据来调试、测试和监控基于LangGraph构建的LLM应用程序 — 阅读更多关于如何启动的信息，请 [点击这里] 。

## 第1部分：构建一个基本的聊天机器人¶

我们将首先使用LangGraph创建一个简单的聊天机器人。这个聊天机器人将直接对用户消息做出回应。虽然简单，但它将说明使用LangGraph构建的核心概念。在本节结束时，您将构建一个基本的聊天机器人。

首先创建一个`StateGraph`。`StateGraph`对象定义了我们聊天机器人的结构，作为一个“状态机”。我们将添加`nodes`来表示聊天机器人可以调用的llm和函数，并添加`edges`来指定机器人如何在这些函数之间转换。

```
from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # 在注释中定义了该状态键应如何更新。
    # （在这种情况下，它将消息附加到列表中，而不是覆盖它们）
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)

```

API Reference: [StateGraph] | [START] | [END] | [add_messages] 

我们的图现在可以处理两个关键任务：

1. 对`messages`的更新将附加到现有列表中，而不是覆盖它，这得益于与`Annotated`语法一起使用的预构建 [add_messages] 函数。
2. 每个`node`可以接收当前`State`作为输入，并输出对状态的更新。

---

概念

定义图的第一步是定义它的`State`。`State`包括图的架构和处理状态更新的 [reducer 函数] 。在我们的示例中，`State`是一个`TypedDict`，其中有一个键：`messages`。 [add_messages] reducer 函数用于将新消息附加到列表中，而不是覆盖它。没有 reducer 注释的键将覆盖先前的值。请在 [此指南] 中了解更多有关状态、reducer 及相关概念的信息。

---

接下来，添加一个 "`chatbot`" 节点。节点表示工作单元。它们通常是常规的 python 函数。

```
from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")


def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}


# 第一个参数是唯一的节点名称。
# 第二个参数是将在每次调用时使用的函数或对象。
# 节点正在被使用。
graph_builder.add_node("chatbot", chatbot)

```

API Reference: [ChatAnthropic] 

注意`chatbot`节点函数如何将当前的`State`作为输入，并返回一个包含更新后的`messages`列表的字典，键为 "messages"。这是所有 LangGraph 节点函数的基本模式。

我们`State`中的`add_messages`函数将 LLM 的响应消息追加到状态中已有的消息中。

接下来，添加一个`entry`点。这告诉我们的图 每次运行时应该从哪里开始工作。

```
graph_builder.add_edge(START, "chatbot")

```

同样，设置一个`finish`点。这指示图 “每当运行这个节点时，你可以退出。”

```
graph_builder.add_edge("chatbot", END)

```

最后，我们希望能够运行我们的图。为此，调用图构建器上的 "`compile()`"。这会创建一个 "`CompiledGraph`"，我们可以在我们的状态上调用它。

```
graph = graph_builder.compile()

```

您可以使用`get_graph`方法和`draw`方法之一（如`draw_ascii`或`draw_png`）来可视化图形。每个`draw`方法都需要额外的依赖项。

```
from IPython.display import Image, display

try:
    display(Image(graph.get_graph().draw_mermaid_png()))
except Exception:
    # 这需要一些额外的依赖，并且是可选的。
    pass

```

现在让我们运行聊天机器人！

提示： 您可以随时通过输入 "quit"、"exit" 或 "q" 来退出聊天循环。

```
def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [("user", user_input)]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)


while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        stream_graph_updates(user_input)
    except:
        # 如果 input() 不可用，则备选方案。
        user_input = "What do you know about LangGraph?"
        print("User: " + user_input)
        stream_graph_updates(user_input)
        break

```

```
Assistant: LangGraph is a library designed to help build stateful multi-agent applications using language models. It provides tools for creating workflows and state machines to coordinate multiple AI agents or language model interactions. LangGraph is built on top of LangChain, leveraging its components while adding graph-based coordination capabilities. It's particularly useful for developing more complex, stateful AI applications that go beyond simple query-response interactions.
Goodbye!

```

恭喜你！ 你已经使用LangGraph构建了你的第一个聊天机器人。这个机器人可以通过接受用户输入并使用LLM生成响应来进行基本的对话。你可以通过提供的链接查看上述调用的 [LangSmith Trace] 。

然而，你可能注意到机器人的知识仅限于其训练数据。在接下来的部分，我们将添加一个网络搜索工具，以扩展机器人的知识，使其更加强大。

以下是本节的完整代码供你参考：

完整代码

```
from typing import Annotated

from langchain_anthropic import ChatAnthropic
from typing_extensions import TypedDict

from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages


class State(TypedDict):
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)


llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")


def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}


# 第一个参数是唯一的节点名称
# 第二个参数是每当使用该节点时将被调用的函数或对象。
graph_builder.add_node("chatbot", chatbot)
graph_builder.set_entry_point("chatbot")
graph_builder.set_finish_point("chatbot")
graph = graph_builder.compile()

```

## 第二部分：🛠️ 用工具增强聊天机器人¶

为了处理我们的聊天机器人无法“凭记忆”回答的查询，我们将集成一个网络搜索工具。我们的机器人可以使用这个工具找到相关信息并提供更好的响应。

#### 要求¶

在我们开始之前，请确保您已安装必要的软件包并设置了 API 密钥：

首先，安装使用 [Tavily 搜索引擎] 所需的依赖，并设置您的 [TAVILY_API_KEY] 。

```
%%capture --no-stderr
%pip install -U tavily-python langchain_community

```

```
_set_env("TAVILY_API_KEY")

```

```
TAVILY_API_KEY:  ········

```

请提供ipynb文件中的markdown内容，我将为您翻译成中文。

```
from langchain_community.tools.tavily_search import TavilySearchResults

tool = TavilySearchResults(max_results=2)
tools = [tool]
tool.invoke("What's a 'node' in LangGraph?")

```

```
[{'url': 'https://medium.com/@cplog/introduction-to-langgraph-a-beginners-guide-14f9be027141',
  'content': 'Nodes: Nodes are the building blocks of your LangGraph. Each node represents a function or a computation step. You define nodes to perform specific tasks, such as processing input, making ...'},
 {'url': 'https://saksheepatil05.medium.com/demystifying-langgraph-a-beginner-friendly-dive-into-langgraph-concepts-5ffe890ddac0',
  'content': 'Nodes (Tasks): Nodes are like the workstations on the assembly line. Each node performs a specific task on the product. In LangGraph, nodes are Python functions that take the current state, do some work, and return an updated state. Next, we define the nodes, each representing a task in our sandwich-making process.'}]

```

API Reference: [TavilySearchResults] 

结果是我们的聊天机器人可以用来回答问题的页面摘要。

接下来，我们将开始定义我们的图形。以下内容与第一部分**完全相同**，除了我们在我们的LLM上添加了`bind_tools`。这让LLM知道如果它想使用我们的搜索引擎，应该使用正确的JSON格式。

```
from typing import Annotated

from langchain_anthropic import ChatAnthropic
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages


class State(TypedDict):
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)


llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")
# 修改：告诉语言模型可以调用哪些工具。
llm_with_tools = llm.bind_tools(tools)


def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


graph_builder.add_node("chatbot", chatbot)

```

API Reference: [ChatAnthropic] | [StateGraph] | [START] | [END] | [add_messages] 

接下来，我们需要创建一个函数，以便在调用工具时实际运行这些工具。我们通过将工具添加到一个新的节点来实现这一点。

下面，我们实现了一个`BasicToolNode`，它检查状态中最近的消息，并在消息包含`tool_calls`时调用工具。它依赖于LLM的`tool_calling`支持，该支持在Anthropic、OpenAI、Google Gemini以及其他多个LLM提供商中可用。

稍后我们将用LangGraph的预构建 [ToolNode] 来替代它，以加快进程，但首先自己构建它是很有启发性的。

```
import json

from langchain_core.messages import ToolMessage


class BasicToolNode:
    """一个运行上一个AI消息中请求的工具的节点。"""

    def __init__(self, tools: list) -> None:
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, inputs: dict):
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No message found in input")
        outputs = []
        for tool_call in message.tool_calls:
            tool_result = self.tools_by_name[tool_call["name"]].invoke(
                tool_call["args"]
            )
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        return {"messages": outputs}


tool_node = BasicToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)

```

API Reference: [ToolMessage] 

添加了工具节点后，我们可以定义`conditional_edges`。

回想一下，**边**负责将控制流从一个节点路由到下一个节点。**条件边**通常包含“if”语句，以根据当前图的状态路由到不同的节点。这些函数接收当前图的`state`，并返回一个字符串或字符串列表，指示下一个要调用的节点。

下面定义一个名为`route_tools`的路由函数，该函数检查聊天机器人的输出中的工具调用。通过调用`add_conditional_edges`将此函数提供给图，以告知图在`chatbot`节点完成后检查此函数以查看下一步该去哪里。

如果存在工具调用，则条件将路由到`tools`，否则路由到`END`。

稍后，我们将用预构建的 [tools_condition] 来替代这个函数，以使其更加简洁，但我们首先自己实现它可以使事情更加清晰。

```
from typing import Literal


def route_tools(
    state: State,
):
    """
    在conditional_edge中使用以便在最后一条消息有工具调用时路由到ToolNode。否则，路由到结束。
    """
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return END


# The `tools_condition` function returns "tools" if the chatbot asks to use a tool, and "END" if
# 直接响应是可以的。这个条件路由定义了主要的代理循环。
graph_builder.add_conditional_edges(
    "chatbot",
    route_tools,
    # 以下字典允许你告诉图形将条件的输出解释为特定节点。
    # 它默认为恒等函数，但如果你
    # want to use a node named something else apart from "tools",
    # 你可以将字典的值更新为其他内容。
    # e.g., "tools": "my_tools"
    {"tools": "tools", END: END},
)
# 每当调用一个工具时，我们会返回到聊天机器人以决定下一步。
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START,


---
*数据来源: Exa搜索 | 获取时间: 2026-02-20 20:40:34*