# [logo ModelEngine社区](https://modelengine.csdn.net "ModelEngine社区")

![logo](https://i-blog.csdnimg.cn/devpress/blog/e91274dd3f454fa0a048e0af88cb04ef.png)
![](https://i-blog.csdnimg.cn/devpress/blog/e91274dd3f454fa0a048e0af88cb04ef.png)

## 登录社区云

登录社区云，与社区用户共同成长

### ModelEngine社区

邀请您加入社区

![]()![]()

# LangGraph 快速入门

LangGraph简介 LangGraph是由LangChain团队开发的开源框架，专为构建具有状态管理和多智能体协作能力的应用而设计。核心功能包括： 图结构工作流：通过StateGraph组织任务流程，包含节点(Node)和边(Edge)定义执行逻辑 持久化状态管理：支持长时间运行任务的恢复和人工干预 开发工具集成：与LangSmith配合提供可视化调试功能 主要优势： 处理复杂多轮对话 支持多

![](https://profile-avatar.csdnimg.cn/6074747de68748ceb13e366e8ceeca8b_general_zy.jpg!1)

### [General\_zy](https://devpress.csdn.net/user/General_zy)

![](https://profile-avatar.csdnimg.cn/6074747de68748ceb13e366e8ceeca8b_general_zy.jpg!1)

#### 目录

## LangGraph简介

LangGraph 是由 LangChain 团队开发的开源 MIT 许可框架，专为构建具有状态管理和多智能体协作能力的应用而设计。它通过图结构（StateGraph）组织任务流程，使开发者能够精确控制执行逻辑、状态更新和任务调度。([知乎专栏](https://zhuanlan.zhihu.com/p/1903527757977191290?utm_source=chatgpt.com "深度解析LangGraph：构建可控的多智能体图模型框架 - 知乎"))

🔑 核心概念

🚀 核心优势

🛠️ 应用场景

LangGraph 的设计灵感来源于 Pregel 和 Apache Beam，其公共接口借鉴了 NetworkX。它由 LangChain Inc 创建，既可以独立使用，也能与 LangChain 等其他工具无缝集成，为开发者提供构建智能体应用的强大支持。([LangGraph](https://github.langchain.ac.cn/langgraph/?utm_source=chatgpt.com "LangGraph - LangChain 框架"))

安装 LangGraph：

`pip install -U langgraph`

然后，使用预构建组件创建一个智能体：

`# 安装模型调用依赖
# pip install -qU "langchain[anthropic]"
from langgraph.prebuilt import create_react_agent
def get_weather(city: str) -> str:
"""获取指定城市的天气。"""
return f"{city} 总是阳光明媚！"
agent = create_react_agent(
model="anthropic:claude-3-7-sonnet-latest",
tools=[get_weather],
prompt="你是一个乐于助人的助手"
)
# 运行智能体
agent.invoke(
{"messages": [{"role": "user", "content": "旧金山的天气怎么样？"}]}
)`

LangGraph 为任何长期运行、有状态的工作流或智能体提供低级支持基础设施。它不抽象提示词或架构，具有以下主要优势：

**LangGraph 可以独立使用，也能无缝集成任何 LangChain 产品**，为开发者提供构建智能体的完整工具套件。为提升 LLM 应用开发，建议配合使用：

### LangGraph&LangChain

LangChain 在构建基于大型语言模型（LLM）的应用方面提供了许多便利，但在实际开发中，尤其是面对复杂工作流时，开发者逐渐发现其存在一些明显的局限性。这些问题促使了 LangGraph 的诞生，作为对 LangChain 的补充和改进。以下是对 LangChain 不足之处的直观总结，以及 LangGraph 如何应对这些挑战的原因。

**LangChain 的主要不足**

**过度抽象，导致开发复杂性增加**

LangChain 的设计引入了多层抽象，如链（Chain）、代理（Agent）、工具（Tool）等，虽然提供了灵活性，但也增加了理解和调试的难度。开发者常常需要深入底层，才能实现特定的自定义逻辑。

**状态管理薄弱，难以处理多轮对话**

在多轮对话或需要保持上下文的应用中，LangChain 的状态管理能力有限。开发者需要手动处理状态的保存和传递，增加了开发负担。

**工具调用不稳定，缺乏可预测性**

LangChain 的代理机制在调用外部工具时，缺乏明确的执行顺序和条件控制，导致行为不可预测，尤其在复杂工作流中问题更为突出。

**性能瓶颈，难以扩展**

由于依赖于顺序处理和外部服务，LangChain 在处理大型数据集或高并发请求时，容易出现性能瓶颈，限制了其在生产环境中的应用。

**文档不完善，学习曲线陡峭**

LangChain 的文档存在不完整和不一致的问题，缺乏清晰的指导和示例，增加了新手上手的难度。

针对上述 LangChain 的不足，LangGraph 提供了以下改进：

**图结构工作流，增强可控性**

LangGraph 采用有向图（DAG）结构，明确了各个节点（任务）的执行顺序和依赖关系，使工作流更加清晰和可控。

**内置状态管理，支持复杂对话**

LangGraph 提供了内置的状态管理机制，方便开发者在多轮对话或复杂交互中维护上下文，减少了手动处理的需求。

**明确的工具调用机制**

通过图结构，LangGraph 可以精确控制工具的调用时机和条件，避免了 LangChain 中工具调用的不确定性。

**更好的性能和可扩展性**

LangGraph 的设计优化了任务的并行处理能力，减少了对外部服务的依赖，提高了整体性能，适合处理大规模数据和高并发请求。

**更清晰的文档和示例**

虽然 LangGraph 相对较新，但其文档和示例更加注重实用性，帮助开发者更快地理解和应用框架。

上文提到**LangGraph 可以独立使用，也能无缝集成任何 LangChain 产品**，那是因为LangGraph的Node是一个Callable继而被LangGraph编排，但既然有LangChain存在，那么很多功能就没必要重复造轮子，比如文档切割，我们既可以用LangChain的Spilter作为LangGraph的Node，也可以自己写一个简单的split函数（可调用）作为Node。

总体而言，如果你的应用场景具有预定义的顺序工作流程，如需要从API获取数据并进行总结的简单任务，或者你更倾向于一个直接、模块化的框架，LangChain将是不错的选择。当你的项目需要动态的、有状态的交互，例如构建一个多智能体协作的任务管理系统，或者需要在复杂的工作流程中保持持久的上下文时，LangGraph会更加适合。

## 快速开始

让我们使用 LangGraph 提供的预构建、可复用组件，这些组件旨在帮助你快速、可靠地构建智能体系统（agentic systems）！

请确保你已经具备以下条件：

如果你还没有安装，请先安装 LangGraph 和 LangChain：

`pip install -U langgraph "langchain[anthropic]"`

📌**说明：**

LangChain 被安装是为了让智能体可以调用模型。

要创建智能体，可以使用 `create_react_agent`：

`create_react_agent`
`from langgraph.prebuilt import create_react_agent
def get_weather(city: str) -> str:
"""获取指定城市的天气。"""
return f"It's always sunny in {city}!"
agent = create_react_agent(
model="anthropic:claude-3-7-sonnet-latest", # 模型名称
tools=[get_weather], # 提供的工具列表
prompt="You are a helpful assistant" # 智能体行为的提示词
)
# 运行智能体
agent.invoke(
{"messages": [{"role": "user", "content": "what is the weather in sf"}]}
)`

如果你需要为模型设置特定参数（如温度 temperature），可以使用 `init_chat_model`：

`init_chat_model`
`from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
model = init_chat_model(
"anthropic:claude-3-7-sonnet-latest",
temperature=0
)
agent = create_react_agent(
model=model,
tools=[get_weather],
)`

提示词用于指示 LLM 应如何响应。你可以添加以下两种类型的提示词：

🧩 示例：

`from langgraph.prebuilt import create_react_agent
agent = create_react_agent(
model="anthropic:claude-3-7-sonnet-latest",
tools=[get_weather],
prompt="Never answer questions about the weather." # 固定不变的提示词
)
agent.invoke(
{"messages": [{"role": "user", "content": "what is the weather in sf"}]}
)`

为了让智能体支持多轮对话（multi-turn conversations），你需要提供一个持久化组件（checkpointer），在创建智能体时启用它。同时，在运行时需提供包含 `thread_id` 的配置，它是对话的唯一标识符。

`thread_id`
`from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
checkpointer = InMemorySaver()
agent = create_react_agent(
model="anthropic:claude-3-7-sonnet-latest",
tools=[get_weather],
checkpointer=checkpointer # 启用记忆保存器
)
# 启动智能体（带对话 ID）
config = {"configurable": {"thread_id": "1"}}
sf_response = agent.invoke(
{"messages": [{"role": "user", "content": "what is the weather in sf"}]},
config
)
ny_response = agent.invoke(
{"messages": [{"role": "user", "content": "what about new york?"}]},
config
)`

📌启用 checkpointer 后，智能体的状态会在每个步骤自动保存到 checkpointer 数据库（此例为内存）。再次调用时，如 `thread_id` 相同，之前的历史会被自动包含在上下文中。

`thread_id`

**配置结构化输出（Structured Output）**

如果希望智能体返回符合结构（schema）定义的响应，可以使用 `response_format` 参数。该 schema 可以用 Pydantic 模型或 TypedDict 定义。结果会以 `structured_response` 字段返回。

`response_format`
`structured_response`
`from pydantic import BaseModel
from langgraph.prebuilt import create_react_agent
class WeatherResponse(BaseModel):
conditions: str
agent = create_react_agent(
model="anthropic:claude-3-7-sonnet-latest",
tools=[get_weather],
response_format=WeatherResponse # 输出结构定义
)
response = agent.invoke(
{"messages": [{"role": "user", "content": "what is the weather in sf"}]}
)
# 获取结构化结果
response["structured_response"]`

📌结构化输出会额外调用一次 LLM，用于格式化响应以符合 schema。

## LangGraph基础知识

开发者选择 LangGraph，是因为它具备以下优势：

✅ 可靠性与可控性

通过**内容审查机制**和**人工审批（human-in-the-loop）**来引导智能体的行为。  
LangGraph 能够**持久化上下文**，即使在长时间运行的工作流中，也能保持智能体在正确的轨道上。

✅ 低层级设计、可扩展性强

使用\*\*完全描述性的底层原语（primitives）\*\*构建自定义智能体，  
摆脱限制性的抽象层，让定制化不再受限。

你可以设计**可扩展的多智能体系统**，让每个智能体根据你的用例承担不同角色，精准服务于任务目标。

✅ 一流的流式支持

支持**逐 token 的流式输出**和**中间步骤的流式反馈**，  
让用户实时看到智能体的推理过程与操作路径，提升可观察性和透明度。

为了快速上手 LangGraph 的核心概念和功能，建议完成以下基础教程系列：

### Build a basic chatbot

#### 第1步：创建 StateGraph

`StateGraph` 是一个对象，它将我们的聊天机器人结构定义为一个“**状态机**”。

`StateGraph`

我们将添加：

`from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
class State(TypedDict):
# messages 是一个列表类型。
# 通过注解 `add_messages` 指定该键的更新方式：
# 它会将新消息追加到现有的列表中，而不是覆盖。
messages: Annotated[list, add_messages]
# 创建状态图构建器
graph_builder = StateGraph(State)`

到目前为止，我们的图（Graph）可以处理两个关键任务：

`State`
`State`
`add_messages`
`Annotated`
`messages`

在定义图（Graph）时，第一步是定义其 `State`。`State` 定义了图的**状态结构（schema）**，以及用于处理状态更新的**reducer 函数**。

`State`
`State`

在示例中，`State` 是一个包含单个键 `messages` 的 `TypedDict`。  
其中使用了 `add_messages` reducer 函数，它会将新消息**追加到消息列表中**，而不是覆盖原有内容。

`State`
`messages`
`TypedDict`
`add_messages`

如果某个键没有使用 reducer 注解，它在更新时会**直接覆盖之前的值**。

**为什么注释可以改变行为？**

Python 原生的 `Annotated[...]` 本质上只是一个类型提示工具，在运行时默认是**不会影响行为**的 —— 这是 `typing.Annotated` 的基本用途。

`Annotated[...]`
`typing.Annotated`

但在 **LangGraph** 中，`Annotated` 被赋予了“行为意义”——**LangGraph 显式读取并解释 `Annotated` 中的元信息**，从而根据你传进去的 reducer（如 `add_messages`）**控制状态的更新方式**。

`Annotated`
`Annotated`
`add_messages`

这是因为：

**LangGraph 在内部会显式地读取 `State` 类型定义，并通过反射（introspection）提取 `Annotated[...]` 中的元信息**，例如其中的 `add_messages` 函数，并在运行时使用这个函数作为 reducer。

`State`
`Annotated[...]`
`add_messages`
`messages: Annotated[list, add_messages]`

这个语句在语法层面只是类型标注，但 LangGraph 会执行如下逻辑：

`TypedDict`
`Annotated`
`add_messages`

因此：

`Annotated[list, add_messages]`
`list`

假设你没有加 `add_messages`：

`add_messages`
`class State(TypedDict):
messages: list # 默认行为：每次更新直接覆盖原有值`

然后你某个节点返回：

`return {"messages": ["hello"]}`

→ 原有 messages 被整个替换掉了。

而如果你用了：

`messages: Annotated[list, add_messages]`

然后返回同样的数据：

`return {"messages": ["hello"]}`

→ LangGraph 会帮你把 `"hello"` **追加**到原有的 messages 列表中。

`"hello"`

##### Annotated&reducer

Python 提供了反射机制（introspection），可以在运行时访问类型注解。特别是，`typing.Annotated` 在 Python 3.9+ 中的行为可以通过 `get_type_hints` + `__metadata__` 来解析。

`typing.Annotated`
`get_type_hints`
`__metadata__`
`from typing import Annotated, get_type_hints
from typing_extensions import TypedDict
# 假设这个是你的 reducer 函数
def add_messages(old, new):
return old + new
class State(TypedDict):
messages: Annotated[list, add_messages]
# 使用反射来读取注解
hints = get_type_hints(State, include_extras=True)
print(hints)`

输出：

`{
'messages': Annotated[list, <function add_messages at 0x...>]
}`

你可以进一步解析这个 `Annotated`：

`Annotated`
`from typing import get_args, get_origin, Annotated
ann = hints['messages']
if get_origin(ann) is Annotated:
base_type, *metadata = get_args(ann)
print("Base type:", base_type) # list
print("Metadata (reducers):", metadata) # [add_messages]`

LangGraph 内部就是用了类似的方法，在构建 `StateGraph` 时遍历所有字段的注解，把 reducer 信息存下来，然后在运行时合并状态时自动使用它。

`StateGraph`

什么是 **reducer**？它在 LangGraph 中的作用是什么？

**Reducer** 是一种用于聚合多个状态值的函数，它的输入是旧值和新值，输出是合并后的值。

典型形式：

`new_state = reducer(old_state, new_update)`

最常见的例子就是：

`def add_messages(old, new):
return old + new # 把两个列表连接起来`

LangGraph 中就是用 reducer 控制状态的合并行为。

在状态状态图（StateGraph）中，每个节点都会对全局状态做局部更新。LangGraph 允许多个节点**顺序更新同一个 key**，那么它需要一种机制来**决定多个更新如何组合** —— 这就是 reducer 的作用。

比如：

`messages`
`add_messages`
`count`

LangGraph 的默认行为是覆盖（overwrite），但你可以通过 Annotated 指定 reducer 改变这个行为。

#### 第2步：添加一个节点（Node）

接下来，我们添加一个名为 `"chatbot"` 的节点。

`"chatbot"`

节点是 LangGraph 中的**工作单元（unit of work）**，通常是一个普通的 Python 函数。

首先选择一个聊天模型（chat model），以 OpenAI 为例：

`pip install -U "langchain[openai]"`
`import os
from langchain.chat_models import init_chat_model
os.environ["OPENAI_API_KEY"] = "sk-..." # 替换为你的 API 密钥
llm = init_chat_model("openai:gpt-4.1")`

现在我们将该聊天模型封装进一个简单的节点函数中：

`def chatbot(state: State):
return {"messages": [llm.invoke(state["messages"])]}`

然后将该函数注册为节点：

`# 第一个参数是节点的唯一名称
# 第二个参数是函数或对象，每当该节点被调用时会执行它
graph_builder.add_node("chatbot", chatbot)`
`chatbot`
`State`
`messages`
`add_messages`

这里如果没有模型可以去外部的一些平台去获取公共的模型能力：

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/5e0eaadc313c4d39910f901e1385b5bc.png)

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/5e0eaadc313c4d39910f901e1385b5bc.png)
`import os
from openai import OpenAI
os.environ["OPENAI_API_KEY"] = "xxx"
os.environ["OPENAI_BASE_URL"] = "https://api.siliconflow.cn/v1"
client = OpenAI()
response = client.chat.completions.create(
model="Qwen/Qwen3-8B",
messages=[{
"role": "user",
"content": "你是谁",
}],
temperature=0.7,
max_tokens=4096
)
# message=ChatCompletionMessage(
# content='\n\n我是通义千问，是通义实验室开发的超大规模语言模型。
# 我能够帮助您回答问题、创作文字、编程、分析数据等，支持多语言交流。
# 我的训练数据截止到2024年，能够理解和生成各种类型的文本。无论是日常对话、学习工作，还是创意写作，我都可以为您提供帮助。
# 有什么问题或需要 assistance 的吗？',
# )
print(response)`

#### 第3步：添加入口节点（Entry Point）

添加一个入口节点，用于指明每次运行图时应从哪里开始执行：

`graph_builder.add_edge(START, "chatbot")`

#### 第4步：编译图（Compile the Graph）

在运行图之前，需要先进行编译。调用 `compile()` 方法即可完成编译。这将生成一个 `CompiledGraph`，你可以对其传入状态进行调用：

`compile()`
`CompiledGraph`
`graph = graph_builder.compile()`

#### 第5步：可视化图结构（可选）

你可以使用 `get_graph` 方法配合各种 `draw` 方法（例如 `draw_ascii` 或 `draw_png`）来可视化整个图结构。这些可视化方法依赖额外的依赖项。

`get_graph`
`draw`
`draw_ascii`
`draw_png`
`# pip install ipython
from IPython.display import Image, display
try:
display(Image(graph.get_graph().draw_mermaid_png()))
except Exception:
# 这一步是可选的，运行失败通常是缺少一些依赖
pass`

注意这段代码，我们要在Jupyter中运行，

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/4c42dc1276244639af774d00a5a0ac7f.png)

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/4c42dc1276244639af774d00a5a0ac7f.png)

#### 第6步： 运行聊天机器人

现在来运行你构建的聊天机器人吧！

`def stream_graph_updates(user_input: str):
for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
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
# 如果 input() 无法使用，使用备用输入
user_input = "What do you know about LangGraph?"
print("User: " + user_input)
stream_graph_updates(user_input)
break`

输出示例：

`Assistant: LangGraph 是一个用于构建具备状态管理的多智能体应用的库。它提供了创建工作流和状态机的工具，用于协调多个 AI 智能体或语言模型的交互。LangGraph 基于 LangChain 构建，利用其组件，同时加入了基于图的协调能力。它特别适合开发那些超越简单问答交互的复杂状态型 AI 应用。
Goodbye!`

🎉 **恭喜**! 你已经使用 LangGraph 构建了第一个聊天机器人。这个机器人能够接受用户输入并使用 LLM 生成回复。

本案例所有代码如下：

`import os
from langchain.chat_models import init_chat_model
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
os.environ["OPENAI_API_KEY"] = "your api key"
os.environ["OPENAI_BASE_URL"] = "https://api.siliconflow.cn/v1"
llm = init_chat_model("openai:Qwen/Qwen3-8B")
class State(TypedDict):
# messages 是一个列表类型。
# 通过注解 `add_messages` 指定该键的更新方式：
# 它会将新消息追加到现有的列表中，而不是覆盖。
messages: Annotated[list, add_messages]
def chatbot(state: State):
return {"messages": [llm.invoke(state["messages"])]}
# 创建状态图构建器
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph = graph_builder.compile()
for event in graph.stream({"messages": [{"role": "user", "content": input(">>>")}]}):
for value in event.values():
print("Assistant:", value["messages"][-1].content)`

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/4499eef9150a40c7a3788f2fe802cc9b.png)

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/4499eef9150a40c7a3788f2fe802cc9b.png)

### Add tools

To handle queries you chatbot can’t answer “from memory”, integrate a web search tool. The chatbot can use this tool to find relevant information and provide better responses.

在开始本教程之前，请确保你具备以下条件：

`pip install langchain-tavily`

配置环境变量：

`os.environ["TAVILY_API_KEY"] = "your key"`

定义一个web search工具：

`from langchain_tavily import TavilySearch
tool = TavilySearch(max_results=2)
tools = [tool]
tool.invoke("What's a 'node' in LangGraph?")`

这些结果是网页摘要，供我们的聊天机器人用来回答问题。

`{'query': "What's a 'node' in LangGraph?",
'follow_up_questions': None,
'answer': None,
'images': [],
'results': [{'title': "Introduction to LangGraph: A Beginner's Guide - Medium",
'url': 'https://medium.com/@cplog/introduction-to-langgraph-a-beginners-guide-14f9be027141',
'content': 'Stateful Graph: LangGraph revolves around the concept of a stateful graph, where each node in the graph represents a step in your computation, and the graph maintains a state that is passed around and updated as the computation progresses. LangGraph supports conditional edges, allowing you to dynamically determine the next node to execute based on the current state of the graph. We define nodes for classifying the input, handling greetings, and handling search queries. def classify_input_node(state): LangGraph is a versatile tool for building complex, stateful applications with LLMs. By understanding its core concepts and working through simple examples, beginners can start to leverage its power for their projects. Remember to pay attention to state management, conditional edges, and ensuring there are no dead-end nodes in your graph.',
'score': 0.7065353,
'raw_content': None},
{'title': 'LangGraph Tutorial: What Is LangGraph and How to Use It?',
'url': 'https://www.datacamp.com/tutorial/langgraph-tutorial',
'content': 'LangGraph is a library within the LangChain ecosystem that provides a framework for defining, coordinating, and executing multiple LLM agents (or chains) in a structured and efficient manner. By managing the flow of data and the sequence of operations, LangGraph allows developers to focus on the high-level logic of their applications rather than the intricacies of agent coordination. Whether you need a chatbot that can handle various types of user requests or a multi-agent system that performs complex tasks, LangGraph provides the tools to build exactly what you need. LangGraph significantly simplifies the development of complex LLM applications by providing a structured framework for managing state and coordinating agent interactions.',
'score': 0.5008063,
'raw_content': None}],
'response_time': 1.38}`

在第一个教程中创建的 `StateGraph`，在 LLM 上添加 `bind_tools`。这会让 LLM 知道，如果它要使用搜索引擎，应使用哪种正确的 JSON 格式。

`StateGraph`
`bind_tools`

我们先选择要使用的 LLM：

`from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
class State(TypedDict):
messages: Annotated[list, add_messages]
graph_builder = StateGraph(State)
# Modification: tell the LLM which tools it can call
# highlight-next-line
llm_with_tools = llm.bind_tools(tools)
def chatbot(state: State):
return {"messages": [llm_with_tools.invoke(state["messages"])]}
graph_builder.add_node("chatbot", chatbot)`

现在，创建一个函数来在工具被调用时执行它们。通过将工具添加到一个名为 `BasicToolNode` 的新节点中实现。该节点会检查状态中的最新消息，并在消息包含 `tool_calls` 时调用工具。这个过程依赖于 LLM 的工具调用（tool-calling）支持，目前在 Anthropic、OpenAI、Google Gemini 和其他一些 LLM 提供商中可用。

`BasicToolNode`
`tool_calls`
`import json
from langchain_core.messages import ToolMessage
class BasicToolNode:
"""一个在最后一条 AI 消息中运行请求的工具的节点。"""
def __init__(self, tools: list) -> None:
self.tools_by_name = {tool.name: tool for tool in tools}
def __call__(self, inputs: dict):
if messages := inputs.get("messages", []):
message = messages[-1]
else:
raise ValueError("输入中未找到消息")
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
graph_builder.add_node("tools", tool_node)`

💡 **注意**  
如果你以后不想自己实现这个功能，可以使用 LangGraph 提供的预构建工具节点 `ToolNode`。

`ToolNode`

添加完工具节点后，现在可以定义 **条件边**。

边用于将控制流从一个节点路由到下一个节点。**条件边**从一个节点出发，通常包含 `if` 判断，根据当前图的状态路由到不同的节点。这些函数接收当前状态并返回一个字符串或字符串列表，用于指示下一个要调用的节点名。

`if`

接下来定义一个名为 `route_tools` 的路由函数，该函数检查 `chatbot` 输出中是否存在 `tool_calls`。通过 `add_conditional_edges` 将这个函数添加到图中，告诉图在 `chatbot` 节点完成后调用此函数来判断下一步的跳转。

`route_tools`
`chatbot`
`tool_calls`
`add_conditional_edges`
`chatbot`

如果存在工具调用，则跳转到 `tools`；否则跳转到 `END`。因为该条件函数可能返回 `END`，所以这次不需要显式设置终点节点。

`tools`
`END`
`END`
`def route_tools(state: State):
"""
在条件边中使用：如果最后一条消息包含工具调用，则路由到 ToolNode，
否则路由到 END。
"""
if isinstance(state, list):
ai_message = state[-1]
elif messages := state.get("messages", []):
ai_message = messages[-1]
else:
raise ValueError(f"tool_edge 中输入状态无消息: {state}")
if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
return "tools"
return END
# 如果 chatbot 请求使用工具，返回 "tools"，否则返回 "END"
# 这个条件路由构成了代理的主循环逻辑
graph_builder.add_conditional_edges(
"chatbot",
route_tools,
{
"tools": "tools",
END: END,
}
)
# 每次调用工具后，返回 chatbot 节点决定下一步
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")
graph = graph_builder.compile()`

你可以使用预构建的 tools\_condition 来替代上述条件判断函数，使代码更简洁。

你可以使用 `get_graph` 方法和一种绘图方法（如 `draw_ascii` 或 `draw_png`）来可视化图结构。这些绘图方法需要额外依赖。

`get_graph`
`draw_ascii`
`draw_png`
`from IPython.display import Image, display
try:
display(Image(graph.get_graph().draw_mermaid_png()))
except Exception:
# 可选功能，缺少依赖时忽略
pass`

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/f3ca855b894249e0b63ceb649cd49823.png)

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/f3ca855b894249e0b63ceb649cd49823.png)

现在，你可以向 chatbot 提问它训练数据之外的问题：

`def stream_graph_updates(user_input: str):
for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
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
# 如果 input() 无法使用，使用备用输入
user_input = "What do you know about LangGraph?"
print("User: " + user_input)
stream_graph_updates(user_input)
break`

输出示例：

`Assistant: [{'text': "为了为你提供关于 LangGraph 的准确信息，我需要搜索最新内容。让我来为你查找。", 'type': 'text'}, {'id': 'toolu_01Q588CszHaSvvP2MxRq9zRD', 'input': {'query': 'LangGraph AI tool information'}, 'name': 'tavily_search_results_json', 'type': 'tool_use'}]
Assistant: [{"url": "https://www.langchain.com/langgraph", "content": "LangGraph 为我们构建和扩展 AI 工作负载奠定了基础——从对话代理、复杂任务自动化，到“开箱即用”的自定义 LLM 体验。..."}, {"url": "https://github.com/langchain-ai/langgraph", "content": "LangGraph 是一个用于构建具有状态、多参与者的 LLM 应用的库..."}]
Assistant: 基于搜索结果，我可以为你提供以下 LangGraph 的信息：
1. **用途**：
LangGraph 是一个用于构建具有状态和多参与者（multi-actor）的大语言模型（LLM）应用的库，特别适合用于创建代理和多代理工作流。
2. **开发者**：
LangGraph 由 LangChain 开发，LangChain 是一个专注于 AI 和 LLM 工具的公司。
3. **主要特性**：
- **循环支持**：允许定义包含循环的流程，这对大多数代理架构至关重要。
- **可控性**：增强对应用流程的控制。
- **持久性**：支持状态维护和持久化。
4. **应用场景**：
- 对话代理
- 复杂任务自动化
- 定制的 LLM 支持体验
5. **集成**：
LangGraph 可与 LangChain 的另一个工具 LangSmith 搭配使用，提供构建复杂、可投入生产的 LLM 应用的完整解决方案。
6. **意义**：
LangGraph 相比其他框架，在处理循环、控制性和状态维护方面具有独特优势。`

为了更方便使用，你可以将代码替换为 LangGraph 提供的预构建组件。这些组件内置了一些功能，例如并行调用 API。

`ToolNode`
`BasicToolNode`
`tools_condition`
`route_tools`
`import os
from langchain.chat_models import init_chat_model
os.environ["OPENAI_API_KEY"] = "sk-..."
llm = init_chat_model("openai:gpt-4.1")
from typing import Annotated
from langchain_tavily import TavilySearch
from langchain_core.messages import BaseMessage
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
class State(TypedDict):
messages: Annotated[list, add_messages]
graph_builder = StateGraph(State)
tool = TavilySearch(max_results=2)
tools = [tool]
llm_with_tools = llm.bind_tools(tools)
def chatbot(state: State):
return {"messages": [llm_with_tools.invoke(state["messages"])]}
graph_builder.add_node("chatbot", chatbot)
tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")
graph = graph_builder.compile()`

🎉 你已经使用 LangGraph 构建了一个可以调用搜索引擎的对话代理。它现在可以处理更多样化的用户问题。

现在，我们这样做：

`# 创建状态图构建器
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)
# 如果 chatbot 请求使用工具，返回 "tools"，否则返回 "END"
# 这个条件路由构成了代理的主循环逻辑
graph_builder.add_conditional_edges("chatbot", tools_condition)
# 每次调用工具后，返回 chatbot 节点决定下一步
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")
graph = graph_builder.compile()
for event in graph.stream({"messages": [{"role": "user", "content": input(">>>")}]}):
for value in event.values():
print("Assistant:", value["messages"][-1].content)`

点击进去`tools_condition`，发现他和我们的tool\_router做的是一样的工作：

`tools_condition`
 `if isinstance(state, list):
ai_message = state[-1]
elif isinstance(state, dict) and (messages := state.get(messages_key, [])):
ai_message = messages[-1]
elif messages := getattr(state, messages_key, []):
ai_message = messages[-1]
else:
raise ValueError(f"No messages found in input state to tool_edge: {state}")
if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
return "tools"
return "__end__"`

检查llm最后一条返回值，如果里面有tool\_calls则返回"tools"，而"tools"则是ToolNode内置的name，也就是把请求导向了ToolNode，

`def __init__(
self,
tools: Sequence[Union[BaseTool, Callable]],
*,
name: str = "tools",
tags: Optional[list[str]] = None,
handle_tool_errors: Union[
bool, str, Callable[..., str], tuple[type[Exception], ...]
] = True,
messages_key: str = "messages",
) -> None:`

然后invoke或者ainvoke触发ToolNode启动线程池或eventLoop去处理工具调用，再将工具调用信息追加到状态机返回。

### Add memory

目前，chatbot 已经可以使用工具来回答用户问题，但它**无法记住之前对话的上下文**，这限制了它进行连贯、多轮对话的能力。

**LangGraph** 通过**持久化检查点（persistent checkpointing）**机制解决了这个问题。如果你在编译图时提供了一个 `checkpointer`，并在调用图时提供了一个 `thread_id`，LangGraph 会**在每一步之后自动保存状态**。当你再次使用相同的 `thread_id` 调用图时，它会加载之前保存的状态，从而让 chatbot 能够从上次对话的上下文继续。

`checkpointer`
`thread_id`
`thread_id`

稍后你会看到，**checkpointing 的功能远比简单的聊天记忆更强大**。它不仅能保存和恢复复杂的状态，还支持诸如错误恢复、人类介入工作流（human-in-the-loop）、时间旅行式交互等高级场景。但我们首先从实现**多轮对话**的 checkpointing 开始。

先创建一个 `MemorySaver` 类型的检查点保存器（checkpointer）：

`MemorySaver`
`from langgraph.checkpoint.memory import MemorySaver
memory = MemorySaver()`

这是一种**基于内存的 checkpointer**，非常适合教程演示使用。但在生产环境中，你更可能使用 `SqliteSaver` 或 `PostgresSaver` 并连接到一个数据库，以实现持久化存储。

`SqliteSaver`
`PostgresSaver`

使用提供的 `checkpointer` 编译图，这样图在执行每个节点时会自动保存状态（State）：

`checkpointer`
`graph = graph_builder.compile(checkpointer=memory)`

可选：可视化图结构（依赖额外库）：

`from IPython.display import Image, display
try:
display(Image(graph.get_graph().draw_mermaid_png()))
except Exception:
# 这依赖一些额外组件，非必需
pass`

现在你可以开始与 chatbot 交互了！

选择一个线程 ID 作为这次对话的标识符：

`config = {"configurable": {"thread_id": "1"}}`

调用 chatbot：

`user_input = "Hi there! My name is Will."
# 注意：config 是 stream() 或 invoke() 的**第二个位置参数**
events = graph.stream(
{"messages": [{"role": "user", "content": user_input}]},
config,
stream_mode="values",
)
for event in events:
event["messages"][-1].pretty_print()`

输出：

`================================ Human Message =================================
Hi there! My name is Will.
================================== Ai Message ==================================
Hello Will! It's nice to meet you. How can I assist you today? Is there anything specific you'd like to know or discuss?`

💡 注意：  
config 是调用图时的第二个位置参数，而不是包含在 graph 输入的 `{'messages': []}` 内部。

`{'messages': []}`

继续提问：

`user_input = "Remember my name?"
events = graph.stream(
{"messages": [{"role": "user", "content": user_input}]},
config,
stream_mode="values",
)
for event in events:
event["messages"][-1].pretty_print()`

输出：

`================================ Human Message =================================
Remember my name?
================================== Ai Message ==================================
Of course, I remember your name, Will. I always try to pay attention to important details that users share with me. Is there anything else you'd like to talk about or any questions you have? I'm here to help with a wide range of topics or tasks.`

注意我们**没有使用外部变量来保存上下文信息**：全部由 `checkpointer` 自动管理！

`checkpointer`

换一个 thread\_id 试试

我们只改变 `thread_id` 为 “2”：

`thread_id`
`events = graph.stream(
{"messages": [{"role": "user", "content": user_input}]},
{"configurable": {"thread_id": "2"}},
stream_mode="values",
)
for event in events:
event["messages"][-1].pretty_print()`

输出：

`================================ Human Message =================================
Remember my name?
================================== Ai Message ==================================
I apologize, but I don't have any previous context or memory of your name. As an AI assistant, I don't retain information from past conversations. Each interaction starts fresh. Could you please tell me your name so I can address you properly in this conversation?`

我们唯一的更改就是把 `thread_id` 从 “1” 改为了 “2”。

`thread_id`

**查看状态快照**

现在我们已经在两个不同的线程中创建了多个检查点。那么，一个检查点里到底包含了什么？

你可以通过调用 `get_state(config)` 来查看图在某个配置下的状态：

`get_state(config)`
`snapshot = graph.get_state(config)
snapshot`

示例输出包括：

`messages`
`config`
`next`

如果图已结束，`next` 会是空的：

`next`
`snapshot.next # 空表示已经执行完`

🎉 恭喜！你的 chatbot 现在已经能够**跨会话保持对话状态**，这要归功于 LangGraph 的 checkpointing 系统。它不仅支持自然、具上下文的对话交互，还能应对复杂状态恢复，比起传统聊天记忆更强大灵活。

上文所有代码：

`memory = MemorySaver()
# 创建状态图构建器
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)
# 如果 chatbot 请求使用工具，返回 "tools"，否则返回 "END"
# 这个条件路由构成了代理的主循环逻辑
graph_builder.add_conditional_edges("chatbot", tools_condition)
# 每次调用工具后，返回 chatbot 节点决定下一步
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")
graph = graph_builder.compile(checkpointer=memory)
config = {"configurable": {"thread_id": "1"}}
while True:
user: str = input(">>>")
for event in graph.stream(
{"messages": [{"role": "user", "content": user}]},
config,
stream_mode="values",
):
event["messages"][-1].pretty_print()`

这里需要注意，`stream_mode="values"` 和 **不加 `stream_mode`（即使用默认模式）** 是有区别的，它们影响了你从 `graph.stream()` 或 `graph.invoke()` 得到的输出形式和语义：

`stream_mode="values"`
`stream_mode`
`graph.stream()`
`graph.invoke()`

✅ `stream_mode="values"`

`stream_mode="values"`
`{"messages": [...]}`
`for event in graph.stream(inputs, config, stream_mode="values"):
print(event) # event 是 dict，如 {"messages": [...]}`

❌ 不加 `stream_mode`（默认行为）

`stream_mode`

默认 `stream_mode=None`，返回的是完整的 **执行事件（execution event）**，包含：

`stream_mode=None`
`"node_name"`
`"output"`

更适合用于**调试**、**日志记录**、**监控流程图执行过程**

`for event in graph.stream(inputs, config): # 默认模式
print(event)
# event 是形如 {"node_name": ..., "output": ..., "metadata": ...} 的结构体`

示例：

`# 假设 chatbot 返回 {"messages": [...]}
# values 模式
event = {"messages": [...]} # 更像是普通的状态快照
# 默认模式
event = {
"node_name": "chatbot",
"output": {"messages": [...]},
"metadata": {...}
}`

其次，在生产环境中，需要将 `thread_id` 动态地管理。

`thread_id`

**用用户ID + 会话ID 拼成 thread\_id**

LangGraph 的状态管理是以 `thread_id` 为主键进行持久化的。因此，只要每次请求传入相同的 `thread_id`，就能恢复这个用户对应的对话上下文。

`thread_id`
`thread_id`
`# 假设你有这些信息：
user_id = "user_abc123"
session_id = "sess_001"
# 构造唯一 thread_id（注意不能冲突）
thread_id = f"{user_id}:{session_id}"
# 配置传入
config = {"configurable": {"thread_id": thread_id}}
# 每次调用都传这个 config
graph.stream({"messages": [{"role": "user", "content": "Hello"}]}, config)`

**用 UUID 或 数据库自动生成的 thread\_id**

如果你要**为每个新会话动态生成一个新的对话线程**，可用随机生成或数据库分配：

`import uuid
# 新会话生成新线程ID
new_thread_id = str(uuid.uuid4())
config = {"configurable": {"thread_id": new_thread_id}}`

你需要把这个 `thread_id` 保存到数据库或者客户端 cookie/session 中，后续用户请求时带回来，才能恢复状态。

`thread_id`

**用数据库或缓存管理用户会话**

建议你在服务端有个简单的 session 数据表：

| user\_id | session\_id | thread\_id | created\_at |
| --- | --- | --- | --- |
| user\_abc | sess\_001 | user\_abc:sess\_001 | 2025-05-25 10:00 |
| user\_abc | sess\_002 | user\_abc:sess\_002 | 2025-05-25 10:10 |

这样你可以：

**搭配持久化存储（MemorySaver → Sqlite/Postgres）**

内存存储 `MemorySaver` 仅适合调试或开发。生产中应换成持久化存储：

`MemorySaver`
`from langgraph.checkpoint.sqlite import SqliteSaver
checkpointer = SqliteSaver.from_path("checkpoints.db")
graph = graph_builder.compile(checkpointer=checkpointer)`

或者 PostgreSQL：

`from langgraph.checkpoint.postgres import PostgresSaver
checkpointer = PostgresSaver.from_conn_string("postgresql://user:pass@localhost/dbname")`

这样 `thread_id` 对应的状态会持久化在数据库中，支持服务重启、分布式部署等场景。

`thread_id`

### Add human-in-the-loop controls

代理可能并不总是可靠，可能需要人为输入才能成功完成任务。类似地，对于某些操作，你可能希望在执行前要求人工审批，以确保一切按预期运行。

LangGraph 的持久化层支持“人类参与”（human-in-the-loop）工作流，允许根据用户反馈暂停和恢复执行。该功能的主要接口是 `interrupt` 函数。在一个节点内部调用 `interrupt` 会暂停执行。随后可以通过传入一个 `Command` 来恢复执行，并携带来自人类的新输入。`interrupt` 的用法在操作上类似于 Python 内置的 `input()`，但存在一些注意事项。

`interrupt`
`interrupt`
`Command`
`interrupt`
`input()`

在“为聊天机器人添加记忆”教程的现有代码基础上，向聊天机器人中添加 `human_assistance` 工具。该工具使用 `interrupt` 来接收来自人类的信息。

`human_assistance`
`interrupt`
`from typing import Annotated
from langchain_tavily import TavilySearch
from langchain_core.tools import tool
from typing_extensions import TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import Command, interrupt
class State(TypedDict):
messages: Annotated[list, add_messages]
graph_builder = StateGraph(State)
@tool
def human_assistance(query: str) -> str:
"""Request assistance from a human."""
human_response = interrupt({"query": query})
return human_response["data"]
tool = TavilySearch(max_results=2)
tools = [tool, human_assistance]
llm_with_tools = llm.bind_tools(tools)
def chatbot(state: State):
message = llm_with_tools.invoke(state["messages"])
# Because we will be interrupting during tool execution,
# we disable parallel tool calling to avoid repeating any
# tool invocations when we resume.
assert len(message.tool_calls) <= 1
return {"messages": [message]}
graph_builder.add_node("chatbot", chatbot)
tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)
graph_builder.add_conditional_edges(
"chatbot",
tools_condition,
)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")`

像之前一样，我们使用 checkpointer 编译图：

`memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)`

现在，向聊天机器人输入一个问题，使其触发 `human_assistance` 工具：

`human_assistance`
`user_input = "我需要一些关于构建 AI 代理的专家指导，你能为我请求帮助吗？"
config = {"configurable": {"thread_id": "1"}}
events = graph.stream(
{"messages": [{"role": "user", "content": user_input}]},
config,
stream_mode="values",
)
for event in events:
if "messages" in event:
event["messages"][-1].pretty_print()`

输出内容如下：

`================================ 用户消息 =================================
我需要一些关于构建 AI 代理的专家指导，你能为我请求帮助吗？
================================ AI 回复 ==================================
[
{
"text": "当然可以！我很乐意为您请求专家协助。为此，我将使用 human_assistance 工具转达您的请求，现在就为您操作。",
"type": "text"
},
{
"id": "toolu_01ABUqneqnuHNuo1vhfDFQCW",
"input": {
"query": "一位用户请求关于构建 AI 代理的专家指导。您能否就此主题提供一些专业建议或资源？"
},
"name": "human_assistance",
"type": "tool_use"
}
]`

工具调用信息：

`调用工具：human_assistance (toolu_01ABUqneqnuHNuo1vhfDFQCW)
参数：
query: 一位用户请求关于构建 AI 代理的专家指导。您能否就此主题提供一些专业建议或资源？`

此时，聊天机器人已生成工具调用，但执行被中断。查看图的状态，会发现其停在了 `tools` 节点：

`tools`
`snapshot = graph.get_state(config)
snapshot.next
# 输出: ('tools',)`

类似于 Python 的 `input()` 函数，在工具内部调用 `interrupt()` 会暂停执行。进度将通过 checkpointer 保持；因此如果使用的是 PostgreSQL 持久化存储，只要数据库存活就可以随时恢复。本例中使用的是内存持久化方式（MemorySaver），在 Python 内核运行期间可以随时恢复。

`input()`
`interrupt()`

为了恢复执行，传入一个包含工具所期望数据的 `Command` 对象。数据格式可按需自定义；本例中使用包含 `"data"` 键的字典：

`Command`
`"data"`
`human_response = (
"我们专家团队很乐意提供帮助！我们建议您查看 LangGraph，它比简单的自治代理更加可靠且可扩展。"
)
human_command = Command(resume={"data": human_response})
events = graph.stream(human_command, config, stream_mode="values")
for event in events:
if "messages" in event:
event["messages"][-1].pretty_print()`

输出内容如下：

`================================ AI 回复 ==================================
当然可以！我很乐意为您请求专家协助。为此，我将使用 human_assistance 工具转达您的请求，现在就为您操作。
调用工具：human_assistance
参数：
query: 一位用户请求关于构建 AI 代理的专家指导。您能否就此主题提供一些专业建议或资源？
================================ 工具回复 =================================
我们专家团队很乐意提供帮助！我们建议您查看 LangGraph，它比简单的自治代理更加可靠且可扩展。
================================ AI 回复 =================================
感谢您的耐心等待。我已收到专家关于构建 AI 代理的指导建议。以下是他们的推荐：
专家建议您查看 LangGraph 来构建 AI 代理。他们表示，LangGraph 比简单的自治代理更可靠、可扩展。
LangGraph 可能是一个专门用于构建 AI 代理的框架或库，具备以下优势：
1. **可靠性**：比起简单的代理方法，LangGraph 更加稳定，可能具有更强的错误处理能力或一致性表现。
2. **可扩展性**：架构灵活，易于添加新功能或根据需要调整现有逻辑。
3. **先进能力**：相较于“简单的自治代理”，LangGraph 可能提供更复杂的工具与构建能力。
建议您：
- 查找专门面向 LangGraph 的教程或指南；
- 加入社区论坛，与其他开发者交流。
如果您还想了解更详细的信息，请告诉我，我可以继续请求专家协助。`

✅ **你已成功使用 `interrupt` 将人类协作功能集成到你的聊天机器人中！**  
这使得你可以在需要时引入人工干预与审批。这也为你创建 AI 系统的 UI 打开了更多可能。  
由于已经添加了 checkpointer，只要底层持久化层运行中，图可以无限期暂停并随时恢复，就像什么都没发生过一样。

`interrupt`

本章示例代码：

`searcher = TavilySearch(max_results=2)
@tool
def human_assistance(query: str) -> str:
"""Request assistance from a human."""
human_response = interrupt({"query": query})
return human_response["data"]
tools = [searcher, human_assistance]
llm = init_chat_model("openai:Qwen/Qwen3-8B").bind_tools(tools)
class State(TypedDict):
# messages 是一个列表类型。
# 通过注解 `add_messages` 指定该键的更新方式：
# 它会将新消息追加到现有的列表中，而不是覆盖。
messages: Annotated[list, add_messages]
def route_tools(state: State):
"""
在条件边中使用：如果最后一条消息包含工具调用，则路由到 ToolNode，
否则路由到 END。
"""
if isinstance(state, list):
ai_message = state[-1]
elif messages := state.get("messages", []):
ai_message = messages[-1]
else:
raise ValueError(f"tool_edge 中输入状态无消息: {state}")
if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
return "tools"
return END
def chatbot(state: State):
return {"messages": [llm.invoke(state["messages"])]}
memory = MemorySaver()
# 创建状态图构建器
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)
# 如果 chatbot 请求使用工具，返回 "tools"，否则返回 "END"
# 这个条件路由构成了代理的主循环逻辑
graph_builder.add_conditional_edges("chatbot", tools_condition)
# 每次调用工具后，返回 chatbot 节点决定下一步
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")
graph = graph_builder.compile(checkpointer=memory)
config = {"configurable": {"thread_id": "1"}}
while True:
user_input = input(">>>")
# 判断是否是 resume 响应，比如用户输入以 "!人工:" 开头
if user_input.startswith("!人工"):
human_reply = user_input.removeprefix("!人工")
human_command = Command(
resume={"data": "我们专家团队很乐意提供帮助！我们建议您查看 LangGraph，它比简单的自治代理更加可靠且可扩展。"})
stream_input = human_command
else:
stream_input = {"messages": [{"role": "user", "content": user_input}]}
for event in graph.stream(stream_input, config, stream_mode="values"):
if "messages" in event:
event["messages"][-1].pretty_print()`

这里比较难理解的是Command和interrupt的配合：

`interrupt({"query": query})`

这里传入的 `{"query": query}` 是 **中断上下文信息** —— 用来告诉外部系统 **“我为什么要中断？”、“我需要你人工帮我处理什么？”**

`{"query": query}`

你是“人类操作员”，你看到的会是：

`{
"query": "用户正在请求构建 AI agent 的专家建议"
}`

你可以把它想象成：`interrupt({"query": query})` 就像前端弹窗里的一段提示话术：

`interrupt({"query": query})`

❓ *用户请求构建 AI Agent 的专家指导，请输入建议内容。*

然后人类填了一句建议点“提交” → resume → LangGraph 恢复执行。

至于， `human_assistance(query: str)` 的入参是怎么来的？

`human_assistance(query: str)`

它的入参 `query` 是由 **LLM 的工具调用生成的**。也就是说，当大语言模型判断“需要调用 `human_assistance` 工具”时，它会自动构造这个函数的入参。

`query`
`human_assistance`

假设你让机器人处理这个用户输入：

`user_input = "我需要一些专家建议来构建 AI agent"`

大语言模型（如 GPT-4）会自动构造如下 **工具调用（tool call）**：

`{
"name": "human_assistance",
"arguments": {
"query": "我需要一些专家建议来构建 AI agent"
}
}`

此时，LangGraph 调用你注册的工具：

`@tool
def human_assistance(query: str) -> str:
...`

框架自动把 `"arguments"` 中的 `"query"` 这个字段取出来，传进了你的函数 `query: str`。

`"arguments"`
`"query"`
`query: str`

至于：

`human_response = interrupt({"query": query})
return human_response["data"]
和
Command(resume={"data": "我们专家团队很乐意提供帮助！我们建议您查看 LangGraph，它比简单的自治代理更加可靠且可扩展。"})`

相当于`human_response =input("显示的内容")`，human\_response 的内容是Command传输的resume字典！

`human_response =input("显示的内容")`

我们的调试程序是这样的：

`while True:
user_input = input(">>>")
# 判断是否是 resume 响应，比如用户输入以 "!人工:" 开头
if user_input.startswith("!人工"):
human_reply = user_input.removeprefix("!人工")
human_command = Command(
resume={"data": "我们专家团队很乐意提供帮助！我们建议您查看 LangGraph，它比简单的自治代理更加可靠且可扩展。"})
stream_input = human_command
else:
stream_input = {"messages": [{"role": "user", "content": user_input}]}
for event in graph.stream(stream_input, config, stream_mode="values"):
if "messages" in event:
event["messages"][-1].pretty_print()`

当程序遇到interrupt时，for event循环打印出提示信息后进入下一次输入，这时候因为程序要求你输入一个Command，那就应该将input改为Command，当然你也可以继续输入普通内容：

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/ee6a1f3a98c7449d8767dfc288fce513.png)  
而你触发Command时，对话会变成这样：

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/ee6a1f3a98c7449d8767dfc288fce513.png)

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/4a3a20bb5c2a47ac9c1713d5a5b61167.png)

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/4a3a20bb5c2a47ac9c1713d5a5b61167.png)

#### human-in-the-loop controls的意义

**Human-in-the-loop (HITL)** 是指：

在自动化系统（如 Agent）运行过程中，保留人类参与决策的能力。

在 LangGraph 中，它体现在你可以使用 `interrupt(...)` 主动中断代理流程，并等待 **人工输入/决策后再恢复执行**。

`interrupt(...)`

**为什么需要 HITL？**

现实中，完全自治的 Agent 容易出错。HITL 提供了一个机制，让系统“学会反问”或“等待人工干预”，从而：

举例：实际应用场景

✅ 1. 自动回复客服系统

`human_assistance(query=...)`

✅ 2. 内部问答机器人（如公司知识库）

`interrupt(...)`

✅ 3. Agent 工作流执行系统

比如自动化执行某些流程（更新配置、生成代码、操作数据库）：

✅ 4. 训练与评估阶段辅助标注

有些人可能理解为“AI反问用户、等待用户答复”，而“AI反问用户、等待用户答复”其实是 **正常对话流程**（模型自动生成消息、用户回复） ，**`interrupt()` 是一种**更强的、**流程级别的“打断执行”机制**，适用于：

`interrupt()`

✅ **引入第三方人工输入**  
✅ **需要人为决策或审查**  
✅ **流程不能继续，必须等待外部指令**

| 类型 | 描述 |
| --- | --- |
| ✅ 普通对话反问 | 模型主动说：“你想了解哪方面？”；用户回复；模型继续处理。 |
| ✅ `interrupt()` 中断控制 | 模型不再自己回复，而是“停住”、发出请求等待外部（人类）输入决策。 |

`interrupt()`

就像这样：

👤 用户问：“给我部署下线上服务”  
🤖 模型判断这个请求比较敏感，**不能随便答应**  
⛔ 它不直接答复你、也不继续处理，而是执行：

`interrupt({"query": "用户请求部署服务，是否允许？"})`

这时你可以：

`resume={"data": ...}`

AI 反问的实现不需要 `interrupt()`，只要让模型生成“反问”的 prompt 即可：

`interrupt()`
`messages = [
{"role": "user", "content": "langGraph怎么样？"},
{"role": "assistant", "content": "你想了解它的哪一方面？性能、扩展性、还是上手体验？"},
{"role": "user", "content": "我想知道框架性能和评分"},
...
]`

这套流程是 **用户 ↔ 模型自洽对话**；而 `interrupt()` 是插入了 **第三方“人类审批”** 的逻辑。

`interrupt()`

下面给出一些实际场景：

用户在网页联系客服，AI 自动初步回答问题，但遇到模糊或高风险问题时中断，请人类客服接入。

**实际案例：京东/淘宝/Apple 支持网页客服系统**

**用户对话：**

`用户：我升级后手机频繁死机，怎么回事？
AI：这个问题可能属于系统兼容问题，是否需要我们请专家进一步确认？
[👉 请人工客服接入]（按钮）`

**LangGraph 实现思路：**

`@tool
def human_assistance(query: str) -> str:
"""Request human support."""
return interrupt({"query": query})["data"]
# 触发中断时：
human_response = interrupt({"query": "用户反馈 iOS 升级后设备死机"})
# 人类客服在界面上输入答复后返回：
# { "data": "您好，我们确认这是 iOS 17.2 的已知问题，建议恢复出厂设置..." }`

**前端页面**（客服后台）：

企业内部员工向 AI 问公司战略、业务数据、HR 政策等，但某些内容模型不能随便回答，需人工审核。

**实际产品参考：** Slack + LangChain 实现的内部问答机器人

**交互示意：**

`员工：今年Q1我们公司的利润同比下降了吗？
AI：这个问题涉及财务数据，我将请求一位负责人提供权威答复。
[👉 通知财务团队]`

**LangGraph 代码概念：**

`@tool
def human_review(query: str) -> str:
return interrupt({"query": query})["data"]`

**前端页面：**

综上所述，`interrupt(...)` **本质上就是一个特殊的“工具调用（Tool Call）”，但这个工具不是自动执行的，而是专门设计给“人类介入”的！**

`interrupt(...)`

### Customize state

本章节，我们将为状态（state）添加额外的字段，以定义更复杂的行为，而不是仅依赖消息列表。聊天机器人将使用其搜索工具查找特定信息，并将其提交给人工审核。

通过在状态中添加 `name` 和 `birthday` 字段来更新聊天机器人，实现查找实体生日的功能：

`name`
`birthday`
`from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
class State(TypedDict):
messages: Annotated[list, add_messages]
name: str
birthday: str`

将这些信息添加到状态中，可以让图中其他节点（比如后续存储或处理信息的节点）轻松访问这些字段，同时也便于图的持久化层访问。

接下来，在 `human_assistance` 工具中填充状态字段。在将信息存入状态之前，请人工审核。使用 `Command` 对象在工具中发起状态更新：

`human_assistance`
`Command`
`from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.types import Command, interrupt
@tool
def human_assistance(
name: str, birthday: str, tool_call_id: Annotated[str, InjectedToolCallId]
) -> str:
"""Request assistance from a human."""
human_response = interrupt(
{
"question": "这些信息正确吗？",
"name": name,
"birthday": birthday,
},
)
if human_response.get("correct", "").lower().startswith("y"):
verified_name = name
verified_birthday = birthday
response = "Correct"
else:
verified_name = human_response.get("name", name)
verified_birthday = human_response.get("birthday", birthday)
response = f"Made a correction: {human_response}"
state_update = {
"name": verified_name,
"birthday": verified_birthday,
"messages": [ToolMessage(response, tool_call_id=tool_call_id)],
}
return Command(update=state_update)`

图的其他部分保持不变。

向聊天机器人提问，让机器人查找 LangGraph 库的“发布日期”，并在查找完成后调用 `human_assistance` 工具进行人工审核。通过设置工具的参数 `name` 和 `birthday`，引导模型生成这些字段的候选值：

`human_assistance`
`name`
`birthday`
`user_input = (
"Can you look up when LangGraph was released? "
"When you have the answer, use the human_assistance tool for review."
)
config = {"configurable": {"thread_id": "1"}}
events = graph.stream(
{"messages": [{"role": "user", "content": user_input}]},
config,
stream_mode="values",
)
for event in events:
if "messages" in event:
event["messages"][-1].pretty_print()`

输出显示模型先使用 `tavily_search_results_json` 搜索，然后调用 `human_assistance` 工具请求审核。

`tavily_search_results_json`
`human_assistance`

如果聊天机器人未能查到正确日期，你可以手动提供：

`human_command = Command(
resume={
"name": "LangGraph",
"birthday": "Jan 17, 2024",
},
)
events = graph.stream(human_command, config, stream_mode="values")
for event in events:
if "messages" in event:
event["messages"][-1].pretty_print()`

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/2d6ab8e3b9b848579572313dc80b3fb4.png)

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/2d6ab8e3b9b848579572313dc80b3fb4.png)

机器人将更新状态并输出最终信息：

`LangGraph was initially released on January 17, 2024...`

你可以验证状态已更新：

`snapshot = graph.get_state(config)
{k: v for k, v in snapshot.values.items() if k in ("name", "birthday")}
# 输出：{'name': 'LangGraph', 'birthday': 'Jan 17, 2024'}`

此外，LangGraph 允许你在任何时刻手动更新状态，包括中断期间：

`graph.update_state(config, {"name": "LangGraph (library)"})`

你可以再次查看状态变化：

`snapshot = graph.get_state(config)
{k: v for k, v in snapshot.values.items() if k in ("name", "birthday")}
# 输出：{'name': 'LangGraph (library)', 'birthday': 'Jan 17, 2024'}`

手动状态更新会在 LangSmith 中留下 trace，如果愿意，也可以用于控制人工审核流程。不过，通常推荐使用 `interrupt` 函数，它能更清晰地区分数据交互与状态更新逻辑。

`interrupt`

示例代码：

`searcher = TavilySearch(max_results=2)
@tool
def human_assistance(
name: str, birthday: str, tool_call_id: Annotated[str, InjectedToolCallId]
) -> str:
"""Request assistance from a human."""
human_response = interrupt(
{
"question": "这些信息正确吗？",
"name": name,
"birthday": birthday,
},
)
if human_response.get("correct", "").lower().startswith("y"):
verified_name = name
verified_birthday = birthday
response = "Correct"
else:
verified_name = human_response.get("name", name)
verified_birthday = human_response.get("birthday", birthday)
response = f"Made a correction: {human_response}"
state_update = {
"name": verified_name,
"birthday": verified_birthday,
"messages": [ToolMessage(response, tool_call_id=tool_call_id)],
}
return Command(update=state_update)
tools = [human_assistance]
llm = init_chat_model("openai:Qwen/Qwen3-8B").bind_tools(tools)
class State(TypedDict):
# messages 是一个列表类型。
# 通过注解 `add_messages` 指定该键的更新方式：
# 它会将新消息追加到现有的列表中，而不是覆盖。
messages: Annotated[list, add_messages]
# 用户信息
name: str
birthday: str
def route_tools(state: State):
"""
在条件边中使用：如果最后一条消息包含工具调用，则路由到 ToolNode，
否则路由到 END。
"""
if isinstance(state, list):
ai_message = state[-1]
elif messages := state.get("messages", []):
ai_message = messages[-1]
else:
raise ValueError(f"tool_edge 中输入状态无消息: {state}")
if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
return "tools"
return END
def chatbot(state: State):
return {"messages": [llm.invoke(state["messages"])]}
memory = MemorySaver()
# 创建状态图构建器
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)
# 如果 chatbot 请求使用工具，返回 "tools"，否则返回 "END"
# 这个条件路由构成了代理的主循环逻辑
graph_builder.add_conditional_edges("chatbot", tools_condition)
# 每次调用工具后，返回 chatbot 节点决定下一步
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")
graph = graph_builder.compile(checkpointer=memory)
config = {"configurable": {"thread_id": "1"}}
while True:
user_input = input(">>>")
if user_input.lower() in ["quit", "exit", "q"]:
print("Goodbye!")
break
# 判断是否是 resume 响应，比如用户输入以 "!人工:" 开头
if user_input.startswith("!人工"):
human_reply = user_input.removeprefix("!人工")
human_command = Command(
resume={
"name": "LangGraph",
"birthday": "Jan 17, 2024",
},
)
stream_input = human_command
else:
stream_input = {"messages": [{"role": "user", "content": user_input}]}
for event in graph.stream(stream_input, config, stream_mode="values"):
if "messages" in event:
event["messages"][-1].pretty_print()
snapshot = graph.get_state(config)
print({k: v for k, v in snapshot.values.items() if k in ("name", "birthday")})
# 输出：{'name': 'LangGraph', 'birthday': 'Jan 17, 2024'}`

**自定义状态的意义远不只是“改内容”那么简单，它带来的核心价值包括：**

**让状态结构显式化（结构化 memory）**

默认的 LangGraph 状态（`messages`）是对话消息列表。如果你不自定义状态，那整个系统只能靠消息上下文推理。例如：

`messages`
`{"messages": [{"role": "user", "content": "LangGraph 是什么时候发布的？"}]}`

系统并不知道你想追踪 `name` 和 `birthday` —— 它只是一堆文本。

`name`
`birthday`

**而通过添加结构化字段（比如 `name` / `birthday`），LangGraph 里的节点就可以“以编程方式”访问这些字段，避免反复解析 messages 内容。**

`name`
`birthday`

**支持复杂流程编排（Workflow Composition）**

结构化状态的最大价值是支持**工作流中的自动决策与跳转**。比如：

`birthday`
`search`
`birthday`
`verified`
`human_assistance`
`store_to_db`

这些流程的条件判断，**无法通过仅仅依赖对话历史完成**，而必须通过显式的字段值控制。

**状态字段可用于持久化、恢复、中断点追踪**

LangGraph 本质是个「状态机」+「事件流」，每个中间状态都可以 checkpoint：

`snapshot = graph.get_state(config)
graph.update_state(config, {"verified": True})`

这意味着：

**便于“模型无感知”的后台逻辑更新**

比如你想更新 `name` 字段，不用让 LLM 重新生成对话、也不用发提示词。直接：

`name`
`graph.update_state(config, {"name": "LangGraph (library)"})`

这个更新动作对模型是**透明的**，但对整体系统却是确定性的。

**支持人类中断/修正控制（Interrupt + Command）**

你看到例子中 `interrupt(...)` 是靠状态字段把数据传给人类的：

`interrupt(...)`
`Command(update=state_update)`

这种人类回环（human-in-the-loop）能力，**非常依赖结构化状态**，否则很难以结构化方式交互。

在 LangGraph 中，**每个 Node 就是一个函数：接收 State，返回新的 State**。

`def my_node(state: YourStateType) -> YourStateType:
# ...处理逻辑...
return new_state`

也可以写成 async 函数（如果你要查数据库、调 API）

`async def my_node(state: YourStateType) -> YourStateType:
...
return new_state`

**Node 一般要做什么？**

`state`
`state`

因此，state里面的信息就是我们要在workflow中修改的内容！

最常见的几种 Node 类型：

1️⃣ 提取信息的 Node（抽取设备名、用户名等）

`from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableLambda
def collect_info_node(state: SupportState) -> SupportState:
# 用 LLM 提取用户输入中的信息
latest_user_msg = state["messages"][-1].content
prompt = f"请从这句话中提取用户名和设备名称：'{latest_user_msg}'"
resp = call_llm(prompt)
# 假设 resp = {"username": "张三", "device": "空调"}
return {
**state,
"username": resp["username"],
"device": resp["device"],
"messages": state["messages"] + [AIMessage(content=prompt), AIMessage(content=str(resp))]
}`

2️⃣ 判断逻辑的 Node（是否需要人工处理）

`def decide_node(state: SupportState) -> SupportState:
human_needed = not state["warranty_valid"]
return {
**state,
"human_needed": human_needed
}`

3️⃣ 接 LLM 的 Node（调用 ChatModel）

你可以直接用 langchain 的 Runnable：

`from langchain_core.runnables import RunnableLambda, RunnableMap
from langchain_core.messages import HumanMessage
from langchain.chat_models import ChatOpenAI
llm = ChatOpenAI(model="gpt-4")
llm_node = RunnableLambda(
lambda state: {
**state,
"messages": state["messages"] + [
llm.invoke(state["messages"])
]
}
)`

也可以封装一下：

`def ask_llm_node(state: SupportState) -> SupportState:
response = llm.invoke(state["messages"])
return {
**state,
"messages": state["messages"] + [response]
}`

4️⃣ 人工中断的 Node（中止等待人工）

LangGraph 内置了 `ToolNode`, `HumanInput`, `breakpoint` 等机制：

`ToolNode`
`HumanInput`
`breakpoint`
`from langgraph.prebuilt import ToolNode
human_node = ToolNode(name="human", input_schema=SupportState)`

或者你自定义：

`def wait_human_node(state: SupportState) -> NoReturn:
raise BreakpointException() # 停在这里，等人类继续`

**记住：Node 是纯函数 + 状态变更器** 每个节点你就当它是个“处理器”：

`输入：老状态 state
处理：干点事
输出：新状态 state'`

只要你把所有 Node 函数写清楚，整个状态机就像装配流水线一样工作。

### Time travel

在典型的聊天机器人工作流中，用户会与机器人进行一次或多次交互以完成某项任务。内存（Memory）和人工干预（Human-in-the-loop）机制允许我们在图状态中设置检查点，并控制未来的响应。

**如果你希望用户能从之前的某个响应出发去探索不同的结果呢？**

又或者你希望用户能够“回退”聊天机器人的执行过程，以修复错误或尝试不同策略呢？你可以使用 **LangGraph 内置的“时间旅行”功能** 来创建这些类型的交互体验。

你可以通过图的 `get_state_history` 方法获取状态历史中的检查点，然后从该时间点恢复执行。

`get_state_history`
`from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_tavily import TavilySearch
from langchain_core.messages import BaseMessage
from typing import Annotated
from typing_extensions import TypedDict
class State(TypedDict):
messages: Annotated[list, add_messages]
graph_builder = StateGraph(State)
# 初始化 LLM + 工具
tool = TavilySearch(max_results=2)
tools = [tool]
llm_with_tools = llm.bind_tools(tools)
def chatbot(state: State):
return {"messages": [llm_with_tools.invoke(state["messages"])]}
graph_builder.add_node("chatbot", chatbot)
tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)
# 添加边与分支条件
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")
# 使用内存型检查点机制
memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)`

每次图执行的步骤都会被记录在状态历史中。

`config = {"configurable": {"thread_id": "1"}}
events = graph.stream(
{
"messages": [
{
"role": "user",
"content": (
"我正在学习 LangGraph，"
"你能帮我搜索一些相关信息吗？"
),
},
],
},
config,
stream_mode="values",
)
for event in events:
if "messages" in event:
event["messages"][-1].pretty_print()`

输出类似如下（简略）：

`Human: 我正在学习 LangGraph，能帮我研究下吗？
AI: 我将使用 Tavily 搜索引擎帮你查找最新信息……
Tool 调用: tavily_search_results_json
Tool 返回内容: [...]
AI 总结: LangGraph 是 LangChain 生态中的一部分，最近更新包括……`

继续添加更多对话：

`events = graph.stream(
{
"messages": [
{
"role": "user",
"content": (
"这很有帮助，也许我可以用它构建一个自动代理（autonomous agent）！"
),
},
],
},
config,
stream_mode="values",
)`

现在你已经为聊天机器人添加了步骤，你可以回放完整的状态历史，以查看整个执行过程中的所有事件。

`to_replay = None
for state in graph.get_state_history(config):
print("消息数量: ", len(state.values["messages"]), "下一步: ", state.next)
print("-" * 80)
if len(state.values["messages"]) == 6:
to_replay = state`

输出（部分）：

`Num Messages: 8 Next: ()
--------------------------------------------------------------------------------
Num Messages: 7 Next: ('chatbot',)
--------------------------------------------------------------------------------
Num Messages: 6 Next: ('tools',)
--------------------------------------------------------------------------------
Num Messages: 5 Next: ('chatbot',)
--------------------------------------------------------------------------------
Num Messages: 4 Next: ('__start__',)
--------------------------------------------------------------------------------
Num Messages: 4 Next: ()
--------------------------------------------------------------------------------
Num Messages: 3 Next: ('chatbot',)
--------------------------------------------------------------------------------
Num Messages: 2 Next: ('tools',)
--------------------------------------------------------------------------------
Num Messages: 1 Next: ('chatbot',)
--------------------------------------------------------------------------------
Num Messages: 0 Next: ('__start__',)
--------------------------------------------------------------------------------
...`

这些检查点会在每一步都自动保存，可以跨整个对话线程回滚。

**从某个时间点恢复（Resume from a checkpoint）**

从 `to_replay` 状态恢复，该状态位于第二次图调用中 chatbot 节点之后。从此处恢复将会接着调用 action 节点。

`to_replay`
`print(to_replay.next)
print(to_replay.config)`

输出示例：

`('tools',)
{'configurable': {'thread_id': '1', 'checkpoint_ns': '', 'checkpoint_id': '1efd43e3-0c1f-6c4e-8006-891877d65740'}}`

你可以使用这个 `checkpoint_id` 来恢复状态并继续执行：to\_replay.config 中包含一个 checkpoint\_id 时间戳。提供该 checkpoint\_id 值后，LangGraph 的检查点管理器（checkpointer）会从该时间点加载对应的状态。

`checkpoint_id`
`for event in graph.stream(None, to_replay.config, stream_mode="values"):
if "messages" in event:
event["messages"][-1].pretty_print()`

输出：

`AI: 构建一个自动代理确实是个好主意。让我来帮你查找一些相关的教程与示例……
Tool 调用：搜索 “用 LangGraph 构建 autonomous agent”
Tool 返回：两个链接
AI 总结：LangGraph 适合构建多步骤、多工具的自动智能体……`

#### 理解"时间旅行"

LangGraph 的“时间旅行”（time-travel checkpointing）确实是一个比较抽象、偏底层的概念。它的核心目的是：**允许开发者在多步骤流程中“回到某一时刻的状态”，并从那里重新执行或探索不同的路径**。

在使用 LangGraph 构建多步骤 AI 工作流（比如一个多轮问答机器人、一个自动化代理系统）时：

实际应用场景有哪些？这个机制对以下需求特别有用：

以下是一个关键代码片段（来自官方教程），从某个 checkpoint ID 开始 replay：

`# 从历史某个状态重新执行
for event in graph.stream(None, to_replay.config, stream_mode="values"):
if "messages" in event:
print(event["messages"][-1]["text"])`

其中 `to_replay.config` 包含了时间点信息，比如：

`to_replay.config`
`{
"checkpoint_id": "1716732978"
}`

**我们常说checkpoint，那么checkpoint到底是什么呢？**

**Checkpoint 是 LangGraph 用来记录「某个节点执行之后的完整状态」的一份快照（snapshot）**。

每次你的 graph 执行到一个 node，它会把：

**全部记录下来**，保存成一个 checkpoint。

就像游戏存档：

一个 checkpoint 长什么样？

它是一个结构体（dict），大概像这样：

`{
"checkpoint_id": "1716732978",
"messages": [
{"role": "user", "content": "推荐一个旅游路线"},
{"role": "ai", "content": "你想去哪里？"}
],
"node": "chatbot",
"config": {...}
}`
`checkpoint_id`
`messages`
`node`
`config`
`stream`
`interrupt`
`stop_at_node`
`to_replay`

综上，时间旅行（time-travel）本质上就是基于 checkpoint 实现的一种调试/开发工具。

## 预构建Agent

LangGraph 提供了构建 Agent 应用所需的底层原语和高级预构建组件。这些**可复用的高级组件**，它们能帮助你**快速稳定地构建 Agent 系统**，而无需从零实现调度、内存或人类反馈机制。

**什么是 Agent？**

一个 Agent 由三部分组成：

LLM 在一个循环中运行。在每轮中，模型：

这个循环持续进行，直到满足停止条件，通常是 Agent 已获得足够信息来回应用户请求。

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/e2d7f1cffc3c48a19c28fa450be2440d.png)

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/e2d7f1cffc3c48a19c28fa450be2440d.png)

**核心特性**

LangGraph 提供多项功能，帮助你构建**强健、可部署的 Agent 系统**：

高级构建模块：

LangGraph 提供一组预构建组件，用于实现常见的 Agent 行为与工作流。这些封装基于 LangGraph 框架构建，**可加快上线速度，同时保留灵活定制的能力**。使用 LangGraph 构建 Agent，意味着你可以专注于应用逻辑和行为，而不是从零管理状态、内存与人类反馈等基础设施。

生态组件：这些高层组件被组织为多个功能明确的包，每个包专注于特定领域。

| 包名 | 描述 | 安装命令 |
| --- | --- | --- |
| `langgraph-prebuilt` | 构建 Agent 的预构建组件（LangGraph 自带） | `pip install -U langgraph langchain` |
| `langgraph-supervisor` | 用于构建 Supervisor Agent（多 Agent 协调） | `pip install -U langgraph-supervisor` |
| `langgraph-swarm` | 构建多智能体群体系统（Swarm） | `pip install -U langgraph-swarm` |
| `langchain-mcp-adapters` | 连接 MCP 服务器的工具/资源适配器 | `pip install -U langchain-mcp-adapters` |
| `langmem` | Agent 的短期/长期内存管理工具 | `pip install -U langmem` |
| `agentevals` | Agent 性能评估工具集 | `pip install -U agentevals` |

`langgraph-prebuilt`
`pip install -U langgraph langchain`
`langgraph-supervisor`
`pip install -U langgraph-supervisor`
`langgraph-swarm`
`pip install -U langgraph-swarm`
`langchain-mcp-adapters`
`pip install -U langchain-mcp-adapters`
`langmem`
`pip install -U langmem`
`agentevals`
`pip install -U agentevals`

**可视化 Agent 图结构**

你可以使用工具将由 `create_react_agent()` 创建的 Agent 工作流图形化展示，同时查看核心结构包括：

`create_react_agent()`

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/895f1b040a594d76b8b937b807e8057b.png)

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/895f1b040a594d76b8b937b807e8057b.png)

示例代码：创建一个 React Agent 并可视化

`from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
model = ChatOpenAI("o4-mini")
def tool() -> None:
"""Testing tool."""
...
def pre_model_hook() -> None:
"""Pre-model hook."""
...
def post_model_hook() -> None:
"""Post-model hook."""
...
class ResponseFormat(BaseModel):
"""Response format for the agent."""
result: str
agent = create_react_agent(
model,
tools=[tool],
pre_model_hook=pre_model_hook,
post_model_hook=post_model_hook,
response_format=ResponseFormat,
)
agent.get_graph().draw_mermaid_png()`

`create_react_agent` 是 LangGraph 提供的一个 **高阶封装函数**，它可以基于一套默认的 Agent 行为和结构，快速生成一张 LangGraph 图（Graph）用于执行。你可以把它理解为一个 **“官方内建模板”**，对用户手动构建的图（Graph）做了简化与封装。

`create_react_agent`

特点：

`agent.get_graph().draw_mermaid_png()`

使用示例：

`from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
agent = create_react_agent(
model=ChatOpenAI("gpt-4o"),
tools=[search_tool, calculator_tool],
)
graph = agent.get_graph()`

手动构建图（自定义 Graph）

特点：

使用示例（简略）：

`from langgraph.graph import StateGraph, END
graph = StateGraph(StateType)
graph.add_node("llm", llm_node)
graph.add_node("tool", tool_node)
graph.add_edge("llm", "tool")
graph.set_entry_point("llm")
graph.set_finish_point("tool")`

⚖️ 总结对比

| 特性 | `create_react_agent` | 手动构建图 |
| --- | --- | --- |
| 是否快速上手 | ✅ 是 | ❌ 否 |
| 是否支持高度自定义 | ❌ 限制较多 | ✅ 非常灵活 |
| 适合 ReAct 结构 | ✅ 最佳场景 | ✅ 也可以做 |
| 状态管理 / 工具调用 | 自动封装 | 需自行管理 |
| 适合构建简单或中等复杂度 Agent | ✅ | ✅ |
| 适合构建复杂工作流 / 多阶段决策系统 | ❌ 不够灵活 | ✅ 最佳选择 |

`create_react_agent`

如果你是第一次构建 Agent 或想快速验证一个工具集成场景，建议用 `create_react_agent` 起步。

`create_react_agent`

如果你要构建：

那就建议你手动定义图结构，使用底层 API 构建 Graph。

需要的话，我可以演示一个 `create_react_agent` 和一个自定义 Graph 的对比代码。

`create_react_agent`

### 运行 Agent

代理（Agents）支持同步和异步两种执行方式，可分别使用 `.invoke()` / `await .ainvoke()` 获取完整响应，或使用 `.stream()` / `.astream()` 实现增量流式输出。

`.invoke()`
`await .ainvoke()`
`.stream()`
`.astream()`

代理可以通过两种主要模式执行：

`.invoke()`
`.stream()`
`await .ainvoke()`
`async for`
`.astream()`

同步调用

`from langgraph.prebuilt import create_react_agent
agent = create_react_agent(...)
response = agent.invoke({"messages": [{"role": "user", "content": "what is the weather in sf"}]})`

异步调用

`from langgraph.prebuilt import create_react_agent
agent = create_react_agent(...)
response = await agent.ainvoke({
"messages": [{"role": "user", "content": "what is the weather in sf"}]
})`

代理使用语言模型，其期望的输入是一个**消息列表**，因此代理的输入输出都以 `messages` 这个键存储于代理状态中。

`messages`

代理输入必须是一个包含 `messages` 键的字典。支持的格式包括：

`messages`

| 格式 | 示例 |
| --- | --- |
| 字符串 | `{"messages": "Hello"}` —— 被解释为一个 HumanMessage |
| 消息字典 | `{"messages": {"role": "user", "content": "Hello"}}` |
| 消息列表 | `{"messages": [{"role": "user", "content": "Hello"}]}` |
| 带自定义状态 | `{"messages": [{"role": "user", "content": "Hello"}], "user_name": "Alice"}` —— 如果使用了自定义的 `state_schema` |

`{"messages": "Hello"}`
`{"messages": {"role": "user", "content": "Hello"}}`
`{"messages": [{"role": "user", "content": "Hello"}]}`
`{"messages": [{"role": "user", "content": "Hello"}], "user_name": "Alice"}`
`state_schema`

消息会被自动转换为 LangChain 内部的消息格式。

你可以在输入字典中直接提供由代理的 `state_schema` 定义的附加字段。这样可以根据运行时数据或之前工具的输出动态控制行为。

`state_schema`

这句话的意思是：

如果你定义了一个包含额外字段的 `state_schema`（也就是代理的状态结构），那么你在调用代理时，就可以**在输入的字典里添加这些字段**，而不仅仅是 `messages`。这样做的好处是：

`state_schema`
`messages`

假设你定义的代理有以下状态结构（`state_schema`）：

`state_schema`
`{
"messages": List[Message],
"user_name": str,
"location": str
}`

那么你可以这样调用代理：

`agent.invoke({
"messages": [{"role": "user", "content": "What's the weather like?"}],
"user_name": "Alice",
"location": "San Francisco"
})`

然后代理就可以在内部使用这些状态字段，比如在提示中自动加入：

“Hi Alice, you’re asking about the weather in San Francisco…”

**注意**  
字符串类型的 `messages` 输入会被转换为 `HumanMessage`。这个行为和 `create_react_agent` 中的 `prompt` 参数不同，后者若传入字符串会被解释为 `SystemMessage`。

`messages`
`HumanMessage`
`create_react_agent`
`prompt`
`SystemMessage`

代理输出是一个包含以下内容的字典：

`messages`
`structured_response`
`state_schema`

代理支持流式响应，用于更具响应性的应用场景，包括：

流式输出可用于同步和异步模式：

同步流式

`for chunk in agent.stream(
{"messages": [{"role": "user", "content": "what is the weather in sf"}]},
stream_mode="updates"
):
print(chunk)`

异步流式

`async for chunk in agent.astream(
{"messages": [{"role": "user", "content": "what is the weather in sf"}]},
stream_mode="updates"
):
print(chunk)`

为控制代理执行，避免无限循环，可以设置**递归限制**（recursion limit）。该值定义了代理最多能执行的步骤数，超出将抛出 `GraphRecursionError`。

`GraphRecursionError`

你可以在运行时或通过 `.with_config()` 在定义代理时设置该限制：

`.with_config()`

运行时：

`from langgraph.errors import GraphRecursionError
from langgraph.prebuilt import create_react_agent
max_iterations = 3
recursion_limit = 2 * max_iterations + 1
agent = create_react_agent(
model="anthropic:claude-3-5-haiku-latest",
tools=[get_weather]
)
try:
response = agent.invoke(
{"messages": [{"role": "user", "content": "what's the weather in sf"}]},
{"recursion_limit": recursion_limit},
)
except GraphRecursionError:
print("Agent stopped due to max iterations.")`

with\_config：

`from langgraph.errors import GraphRecursionError
from langgraph.prebuilt import create_react_agent
max_iterations = 3
recursion_limit = 2 * max_iterations + 1
agent = create_react_agent(
model="anthropic:claude-3-5-haiku-latest",
tools=[get_weather]
)
agent_with_recursion_limit = agent.with_config(recursion_limit=recursion_limit)
try:
response = agent_with_recursion_limit.invoke(
{"messages": [{"role": "user", "content": "what's the weather in sf"}]},
)
except GraphRecursionError:
print("Agent stopped due to max iterations.")`

### Streaming

流式输出是构建高响应应用的关键。你可能希望流式传输以下几种类型的数据：

你可以**同时流式传输多种类型的数据**。

要流式获取代理执行的进度信息，可使用 `stream()` 或 `astream()` 方法，并设置 `stream_mode="updates"`。这将在每一步代理操作后发出事件。

`stream()`
`astream()`
`stream_mode="updates"`

例如，如果代理只调用一个工具，你会依次看到以下更新：

同步示例

`agent = create_react_agent(
model="anthropic:claude-3-7-sonnet-latest",
tools=[get_weather],
)
for chunk in agent.stream(
{"messages": [{"role": "user", "content": "what is the weather in sf"}]},
stream_mode="updates"
):
print(chunk)
print("\n")`

异步示例

`agent = create_react_agent(
model="anthropic:claude-3-7-sonnet-latest",
tools=[get_weather],
)
async for chunk in agent.astream(
{"messages": [{"role": "user", "content": "what is the weather in sf"}]},
stream_mode="updates"
):
print(chunk)
print("\n")`

要在 token 被语言模型生成时逐个流式获取，可以使用 `stream_mode="messages"`。

`stream_mode="messages"`

同步示例

`agent = create_react_agent(
model="anthropic:claude-3-7-sonnet-latest",
tools=[get_weather],
)
for token, metadata in agent.stream(
{"messages": [{"role": "user", "content": "what is the weather in sf"}]},
stream_mode="messages"
):
print("Token", token)
print("Metadata", metadata)
print("\n")`

异步示例

`agent = create_react_agent(
model="anthropic:claude-3-7-sonnet-latest",
tools=[get_weather],
)
async for token, metadata in agent.astream(
{"messages": [{"role": "user", "content": "what is the weather in sf"}]},
stream_mode="messages"
):
print("Token", token)
print("Metadata", metadata)
print("\n")`

**工具更新**

要在工具执行过程中获取其发送的流式更新，可以使用 `get_stream_writer`。

`get_stream_writer`

如果你想让工具在运行中**实时输出一些进度信息**（比如“正在拉取数据”、“已处理 50 条”等），可以在工具里调用 `get_stream_writer()` 获得一个“写入器”，这个写入器支持将消息发射出去，LangGraph 会监听并展示它。

`get_stream_writer()`

`get_stream_writer()` 是 LangGraph 提供的“上下文绑定”能力，**它只能在 LangGraph 的 stream 执行中调用**。  
如果你单独调用这个工具函数（例如在普通 Python 程序中直接 `get_weather("sf")`），由于没有 LangGraph 的上下文支持，它会报错或者无法正常运行。

`get_stream_writer()`
`get_weather("sf")`

举个例子：

`def get_weather(city: str) -> str:
writer = get_stream_writer() # <- 只能在 LangGraph 中用
writer(f"查找城市: {city}") # 实时发射进度信息
return f"{city} 天气晴朗"`

这个函数可以在 LangGraph 中以 stream 方式运行，并输出中间信息；但如果你这样单独运行：

`print(get_weather("Beijing"))`

它会因为找不到上下文而失败或异常。

| 内容 | 解释 |
| --- | --- |
| `get_stream_writer()` | LangGraph 提供的工具，用于工具函数内发射自定义流数据 |
| 作用 | 可以实现像：“正在处理第 x 条记录”的进度推送 |
| 限制 | 只能在 LangGraph 的 `stream()` 或 `astream()` 之中使用，否则无法运行 |

`get_stream_writer()`
`stream()`
`astream()`

你可以把 `get_stream_writer()` 理解为一种“只在 LangGraph 环境中才能用的管道”，普通运行时它是“失效”的。

`get_stream_writer()`

同步示例：

`from langgraph.config import get_stream_writer
def get_weather(city: str) -> str:
"""Get weather for a given city."""
writer = get_stream_writer()
# stream any arbitrary data
writer(f"Looking up data for city: {city}")
return f"It's always sunny in {city}!"
agent = create_react_agent(
model="anthropic:claude-3-7-sonnet-latest",
tools=[get_weather],
)
for chunk in agent.stream(
{"messages": [{"role": "user", "content": "what is the weather in sf"}]},
stream_mode="custom"
):
print(chunk)
print("\n")`

异步示例

`from langgraph.config import get_stream_writer
def get_weather(city: str) -> str:
"""获取指定城市的天气信息。"""
writer = get_stream_writer()
# 发送任意自定义流数据
writer(f"Looking up data for city: {city}")
return f"It's always sunny in {city}!"
agent = create_react_agent(
model="anthropic:claude-3-7-sonnet-latest",
tools=[get_weather],
)
for chunk in agent.stream(
{"messages": [{"role": "user", "content": "what is the weather in sf"}]},
stream_mode="custom"
):
print(chunk)
print("\n")`

**注意**  
如果你在工具函数中使用了 `get_stream_writer`，则**无法在 LangGraph 执行上下文外部调用该工具**。

`get_stream_writer`

同时启用多种流式模式：

你可以通过将 `stream_mode` 设为列表来同时启用多种模式，例如 `stream_mode=["updates", "messages", "custom"]`：

`stream_mode`
`stream_mode=["updates", "messages", "custom"]`

同步示例

`agent = create_react_agent(
model="anthropic:claude-3-7-sonnet-latest",
tools=[get_weather],
)
for stream_mode, chunk in agent.stream(
{"messages": [{"role": "user", "content": "what is the weather in sf"}]},
stream_mode=["updates", "messages", "custom"]
):
print(chunk)
print("\n")`

异步示例

`agent = create_react_agent(
model="anthropic:claude-3-7-sonnet-latest",
tools=[get_weather],
)
async for stream_mode, chunk in agent.astream(
{"messages": [{"role": "user", "content": "what is the weather in sf"}]},
stream_mode=["updates", "messages", "custom"]
):
print(chunk)
print("\n")`

在某些应用中，你可能需要关闭某个模型的 token 流式输出功能。这在多代理系统中尤其有用，可以控制哪些代理启用流式，哪些禁用。

详细内容见 [模型指南（Models guide）](https://docs.langchain.com/langgraph/guides/models)。

### Models

#### 工具调用支持（Tool calling support）

要启用支持工具调用的代理，底层的大语言模型（LLM）必须具备工具调用能力。

兼容的模型可以在 LangChain 的集成目录中找到。

#### 通过名称指定模型（Specifying a model by name）

你可以使用模型名称字符串为代理配置模型：

`import os
from langgraph.prebuilt import create_react_agent
os.environ["OPENAI_API_KEY"] = "sk-..."
agent = create_react_agent(
model="openai:gpt-4.1",
# 其他参数
)`

#### 使用 `init_chat_model`（Using init\_chat\_model）

`init_chat_model`

`init_chat_model` 工具可以通过可配置参数简化模型初始化流程：

`init_chat_model`

支持以下提供商：

`pip install -U "langchain[openai]"`
`import os
from langchain.chat_models import init_chat_model
os.environ["OPENAI_API_KEY"] = "sk-..."
model = init_chat_model(
"openai:gpt-4.1",
temperature=0,
# 其他参数
)`

高级参数请参考 API 文档。

#### 使用特定厂商模型（Using provider-specific LLMs）

如果某个模型提供商未通过 `init_chat_model` 提供，你可以直接实例化该厂商的模型类。  
模型必须实现 `BaseChatModel` 接口，并支持工具调用：

`init_chat_model`
`BaseChatModel`

API 文档：`ChatAnthropic` | `create_react_agent`

`ChatAnthropic`
`create_react_agent`
`from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
model = ChatAnthropic(
model="claude-3-7-sonnet-latest",
temperature=0,
max_tokens=2048
)
agent = create_react_agent(
model=model,
# 其他参数
)`

📌 **说明示例**

上述示例使用了 `ChatAnthropic`，虽然该模型也已被 `init_chat_model` 支持，但此处示范的目的是说明如何手动实例化那些尚未被 `init_chat_model` 支持的模型。

`ChatAnthropic`
`init_chat_model`
`init_chat_model`

#### 禁用流式输出（Disable streaming）

若你希望禁用模型生成时的逐 token 流式输出，  
可在模型初始化时设置 `disable_streaming=True`：

`disable_streaming=True`
`from langchain.chat_models import init_chat_model
model = init_chat_model(
"anthropic:claude-3-7-sonnet-latest",
disable_streaming=True
)
或
from langchain_anthropic import ChatAnthropic
model = ChatAnthropic(
model="claude-3-7-sonnet-latest",
disable_streaming=True
)`

#### 添加模型回退机制（Adding model fallbacks）

你可以使用 `model.with_fallbacks([...])` 为模型添加回退项，以便在当前模型不可用时自动切换到备用模型或不同提供商的模型：

`model.with_fallbacks([...])`
`from langchain.chat_models import init_chat_model
model_with_fallbacks = (
init_chat_model("anthropic:claude-3-5-haiku-latest")
.with_fallbacks([
init_chat_model("openai:gpt-4.1-mini"),
])
)`

### 工具（Tools）

**工具**是一种将函数及其输入模式封装的方式，能够传递给支持工具调用的聊天模型。

这允许模型使用指定输入请求执行该函数。

你可以自定义工具，也可以使用 LangChain 提供的预构建集成工具。

#### 定义简单工具（Define simple tools）

你可以将一个普通函数传递给 `create_react_agent` 来作为工具使用：

`create_react_agent`
`from langgraph.prebuilt import create_react_agent
def multiply(a: int, b: int) -> int:
"""两个数相乘。"""
return a * b
create_react_agent(
model="anthropic:claude-3-7-sonnet",
tools=[multiply]
)`

`create_react_agent` 会自动将普通函数转换为 LangChain 工具。

`create_react_agent`

#### 自定义工具行为（Customize tools）

若想更细致地控制工具行为，可以使用 `@tool` 装饰器：

`@tool`
`from langchain_core.tools import tool
@tool("multiply_tool", parse_docstring=True)
def multiply(a: int, b: int) -> int:
"""两个数相乘。
参数:
a: 第一个操作数
b: 第二个操作数
"""
return a * b`

你也可以通过 Pydantic 定义自定义输入模式：

`from pydantic import BaseModel, Field
class MultiplyInputSchema(BaseModel):
"""两个数相乘"""
a: int = Field(description="第一个操作数")
b: int = Field(description="第二个操作数")
@tool("multiply_tool", args_schema=MultiplyInputSchema)
def multiply(a: int, b: int) -> int:
return a * b`

#### 隐藏模型不可见参数（Hide arguments from the model）

有些工具需要运行时参数（如用户 ID 或会话上下文），这些参数不应由模型控制。

你可以将这些参数放入代理的 `state` 或 `config` 中，并在工具内访问：

`state`
`config`
`from langgraph.prebuilt import InjectedState
from langgraph.prebuilt.chat_agent_executor import AgentState
from langchain_core.runnables import RunnableConfig
def my_tool(
tool_arg: str, # 由 LLM 填充
state: Annotated[AgentState, InjectedState], # 动态上下文
config: RunnableConfig, # 静态配置信息
) -> str:
"""我的工具"""
do_something_with_state(state["messages"])
do_something_with_config(config)
...`

#### 禁用并行工具调用（Disable parallel tool calling）

部分模型提供商支持并行调用多个工具，你可以通过如下方式禁用：

`from langchain.chat_models import init_chat_model
def add(a: int, b: int) -> int:
return a + b
def multiply(a: int, b: int) -> int:
return a * b
model = init_chat_model("anthropic:claude-3-5-sonnet-latest", temperature=0)
tools = [add, multiply]
agent = create_react_agent(
model=model.bind_tools(tools, parallel_tool_calls=False),
tools=tools
)
agent.invoke({"messages": [{"role": "user", "content": "what's 3 + 5 and 4 * 7?"}]})`

#### 直接返回工具结果（Return tool results directly）

使用 `return_direct=True`，可在工具执行完立即返回结果并终止代理循环：

`return_direct=True`
`from langchain_core.tools import tool
@tool(return_direct=True)
def add(a: int, b: int) -> int:
return a + b
agent = create_react_agent(
model="anthropic:claude-3-7-sonnet-latest",
tools=[add]
)
agent.invoke({"messages": [{"role": "user", "content": "what's 3 + 5?"}]})`

#### 强制使用某个工具（Force tool use）

你可以使用 `tool_choice` 强制代理使用某个指定工具：

`tool_choice`
`from langchain_core.tools import tool
@tool(return_direct=True)
def greet(user_name: str) -> str:
return f"Hello {user_name}!"
tools = [greet]
agent = create_react_agent(
model=model.bind_tools(tools, tool_choice={"type": "tool", "name": "greet"}),
tools=tools
)
agent.invoke({"messages": [{"role": "user", "content": "Hi, I am Bob"}]})`

⚠️ 警告：强制使用工具但未设置终止条件，可能导致**无限循环**。请使用以下方式防护：

`return_direct=True`
`recursion_limit`

#### 处理工具错误（Handle tool errors）

默认情况下，代理会捕捉工具调用中抛出的所有异常，并作为工具消息返回给 LLM。

要自定义错误处理，可通过 `create_react_agent` 内部的 `ToolNode` 配置 `handle_tool_errors` 参数。

`create_react_agent`
`ToolNode`
`handle_tool_errors`

默认：

`from langgraph.prebuilt import create_react_agent
def multiply(a: int, b: int) -> int:
if a == 42:
raise ValueError("The ultimate error")
return a * b
agent = create_react_agent(
model="anthropic:claude-3-7-sonnet-latest",
tools=[multiply]
)
agent.invoke({"messages": [{"role": "user", "content": "what's 42 x 7?"}]})`

禁止处理异常：

`from langgraph.prebuilt import create_react_agent, ToolNode
def multiply(a: int, b: int) -> int:
"""Multiply two numbers."""
if a == 42:
raise ValueError("The ultimate error")
return a * b
tool_node = ToolNode(
[multiply],
handle_tool_errors=False
)
agent_no_error_handling = create_react_agent(
model="anthropic:claude-3-7-sonnet-latest",
tools=tool_node
)
agent_no_error_handling.invoke(
{"messages": [{"role": "user", "content": "what's 42 x 7?"}]}
)`

自定义异常：

`from langgraph.prebuilt import create_react_agent, ToolNode
def multiply(a: int, b: int) -> int:
"""Multiply two numbers."""
if a == 42:
raise ValueError("The ultimate error")
return a * b
tool_node = ToolNode(
[multiply],
handle_tool_errors=(
"Can't use 42 as a first operand, you must switch operands!"
)
)
agent_custom_error_handling = create_react_agent(
model="anthropic:claude-3-7-sonnet-latest",
tools=tool_node
)
agent_custom_error_handling.invoke(
{"messages": [{"role": "user", "content": "what's 42 x 7?"}]}
)`

#### 使用记忆（Working with memory）

LangGraph 工具可以访问代理的**短期记忆**与**长期记忆**。

#### 使用预构建工具（Prebuilt tools）

你可以通过 `tools` 参数传入工具规范（字典格式），使用模型厂商提供的内置工具。

`tools`

例如，使用 OpenAI 的 `web_search_preview` 工具：

`web_search_preview`
`from langgraph.prebuilt import create_react_agent
agent = create_react_agent(
model="openai:gpt-4o-mini",
tools=[{"type": "web_search_preview"}]
)
response = agent.invoke(
{"messages": ["What was a positive news story from today?"]}
)`

LangChain 还支持多种预构建工具集成，涵盖 API、数据库、文件系统、网页数据等。

常见工具分类包括：

这些工具均可通过上述 `tools` 参数方式添加到代理中。

`tools`

以下是 **MCP 集成** 相关内容的翻译：

### MCP 集成

**Model Context Protocol (MCP)** 是一个开放协议，用于标准化应用程序向语言模型提供工具与上下文的方式。LangGraph 的 agent 可以通过 `langchain-mcp-adapters` 库使用 MCP 服务器上定义的工具。

`langchain-mcp-adapters`

若要在 LangGraph 中使用 MCP 工具，请先安装相关库：

`pip install langchain-mcp-adapters`

`langchain-mcp-adapters` 包允许 agent 使用一个或多个 MCP 服务器上定义的工具。

`langchain-mcp-adapters`

**示例：使用 MCP 服务器上的工具**

`from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
client = MultiServerMCPClient(
{
"math": {
"command": "python",
# 替换为你本地 math_server.py 文件的绝对路径
"args": ["/path/to/math_server.py"],
"transport": "stdio",
},
"weather": {
# 确保你已在 8000 端口启动了天气服务
"url": "http://localhost:8000/mcp",
"transport": "streamable_http",
}
}
)
tools = await client.get_tools()
agent = create_react_agent(
"anthropic:claude-3-7-sonnet-latest",
tools
)
# 调用数学工具
math_response = await agent.ainvoke(
{"messages": [{"role": "user", "content": "what's (3 + 5) x 12?"}]}
)
# 调用天气工具
weather_response = await agent.ainvoke(
{"messages": [{"role": "user", "content": "what is the weather in nyc?"}]}
)`

你也可以使用 `mcp` 库来创建自己的 MCP 工具服务器。该库提供了一种简单方式来定义工具并以服务器形式运行。

`mcp`
`pip install mcp`

以下是参考实现，可用于测试你的 agent 与 MCP 工具服务器的集成：

示例：数学工具服务器（使用 stdio 传输）

`from mcp.server.fastmcp import FastMCP
mcp = FastMCP("Math")
@mcp.tool()
def add(a: int, b: int) -> int:
"""加法运算"""
return a + b
@mcp.tool()
def multiply(a: int, b: int) -> int:
"""乘法运算"""
return a * b
if __name__ == "__main__":
mcp.run(transport="stdio")`

示例：天气工具服务器（使用可流式 HTTP 传输）

`from mcp.server.fastmcp import FastMCP
mcp = FastMCP("Weather")
@mcp.tool()
async def get_weather(location: str) -> str:
"""获取指定位置天气"""
return "纽约永远是晴天"
if __name__ == "__main__":
mcp.run(transport="streamable-http")`

### 上下文（Context）

代理（Agents）往往不仅仅需要一组消息列表来有效运行，还需要上下文信息。

**上下文**是指消息列表之外的任何可以影响代理行为或工具执行的数据，例如：

`user_id`

LangGraph 提供三种主要方式来提供上下文：

| 类型 | 描述 | 可变？ | 生命周期 |
| --- | --- | --- | --- |
| Config | 运行开始时传入的数据 | ❌ | 每次运行 |
| State | 在执行过程中可能变化的动态数据 | ✅ | 每次运行或对话期间 |
| 长期记忆（Store） | 可在对话之间共享的数据 | ✅ | 跨对话 |

你可以使用上下文来：

#### 提供运行时上下文

在你需要在运行时向代理注入数据时使用此方式。

Config（静态上下文）

`Config` 用于不可变的数据，例如用户元数据或 API 密钥。适用于在运行过程中不会变化的值。

`Config`

使用一个名为 `configurable` 的保留键来指定配置：

`configurable`
`agent.invoke(
{"messages": [{"role": "user", "content": "hi!"}]},
config={"configurable": {"user_id": "user_123"}}
)`

State（可变上下文）

`State` 是运行期间的短期记忆。它包含可能在执行中演化的数据，例如工具返回值或 LLM 输出。

`State`
`class CustomState(AgentState):
user_name: str
agent = create_react_agent(
# 其他参数...
state_schema=CustomState,
)
agent.invoke({
"messages": "hi!",
"user_name": "Jane"
})`

启用记忆功能

详见 Memory 指南，以了解如何启用记忆。这是一个强大的功能，允许你在多个调用之间持久化代理状态。否则，`state` 的作用范围仅限于一次运行。

`state`

长期记忆（跨对话上下文）

对于跨会话或会话持续存在的上下文，LangGraph 提供了访问长期记忆（store）的能力。这可以用于读取或更新持久性事实（如用户资料、偏好、过往交互记录）。详见 Memory 指南。

#### 使用上下文自定义提示词

提示词决定代理的行为。你可以根据代理的状态或配置动态生成提示词来引入运行时上下文。

常见用途：

使用 Config

`from langchain_core.messages import AnyMessage
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import create_react_agent
from langgraph.prebuilt.chat_agent_executor import AgentState
def prompt(
state: AgentState,
config: RunnableConfig,
) -> list[AnyMessage]:
user_name = config["configurable"].get("user_name")
system_msg = f"You are a helpful assistant. User's name is {user_name}"
return [{"role": "system", "content": system_msg}] + state["messages"]
agent = create_react_agent(
model="anthropic:claude-3-7-sonnet-latest",
tools=[get_weather],
prompt=prompt
)
agent.invoke(
...,
config={"configurable": {"user_name": "John Smith"}}
)`

适用State

`from langchain_core.messages import AnyMessage
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import create_react_agent
from langgraph.prebuilt.chat_agent_executor import AgentState
class CustomState(AgentState):
user_name: str
def prompt(
state: CustomState
) -> list[AnyMessage]:
user_name = state["user_name"]
system_msg = f"You are a helpful assistant. User's name is {user_name}"
return [{"role": "system", "content": system_msg}] + state["messages"]
agent = create_react_agent(
model="anthropic:claude-3-7-sonnet-latest",
tools=[...],
state_schema=CustomState,
prompt=prompt
)
agent.invoke({
"messages": "hi!",
"user_name": "John Smith"
})`

#### 在工具中访问上下文

工具可以通过特殊参数注解访问上下文。

`RunnableConfig`
`config`
`Annotated[StateSchema, InjectedState]`
`state`

💡 **提示：** 这些注解会防止 LLM 试图填充这些值。这些参数对 LLM 是不可见的。

使用 Config

`def get_user_info(
config: RunnableConfig,
) -> str:
"""Look up user info."""
user_id = config["configurable"].get("user_id")
return "User is John Smith" if user_id == "user_123" else "Unknown user"
agent = create_react_agent(
model="anthropic:claude-3-7-sonnet-latest",
tools=[get_user_info],
)
agent.invoke(
{"messages": [{"role": "user", "content": "look up user information"}]},
config={"configurable": {"user_id": "user_123"}}
)`

使用 State

`from typing import Annotated
from langgraph.prebuilt import InjectedState
class CustomState(AgentState):
user_id: str
def get_user_info(
state: Annotated[CustomState, InjectedState]
) -> str:
"""Look up user info."""
user_id = state["user_id"]
return "User is John Smith" if user_id == "user_123" else "Unknown user"
agent = create_react_agent(
model="anthropic:claude-3-7-sonnet-latest",
tools=[get_user_info],
state_schema=CustomState,
)
agent.invoke({
"messages": "look up user information",
"user_id": "user_123"
})`

工具可以在执行过程中更新代理上下文（包括 `state` 和长期记忆）。这对于保存中间结果或将信息传递给后续工具或提示非常有用。详见 Memory 指南。

`state`

### 记忆（Memory）

LangGraph 支持两种构建对话代理所必需的记忆类型：

**注意**：短期和长期记忆都需要持久化存储，以在多个 LLM 调用之间保持连续性。在生产环境中，这些数据通常存储在数据库中。

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/c717aab6f5fe4effaa69010991870ba0.png)

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/c717aab6f5fe4effaa69010991870ba0.png)

在 LangGraph 中：

`thread_id`

#### 短期记忆

短期记忆让代理能够跟踪多轮对话。要使用它，你需要：

`checkpointer`
`thread_id`

示例：

`from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
checkpointer = InMemorySaver()
def get_weather(city: str) -> str:
return f"It's always sunny in {city}!"
agent = create_react_agent(
model="anthropic:claude-3-7-sonnet-latest",
tools=[get_weather],
checkpointer=checkpointer
)
config = {"configurable": {"thread_id": "1"}}
sf_response = agent.invoke(
{"messages": [{"role": "user", "content": "what is the weather in sf"}]},
config
)
ny_response = agent.invoke(
{"messages": [{"role": "user", "content": "what about new york?"}]},
config
)`

第二次调用时使用相同 `thread_id`，代理将自动包含历史消息，从而理解用户的上下文。

`thread_id`

##### 管理消息历史

长时间的对话可能会超出大语言模型（LLM）的上下文窗口限制。常见的解决方案包括：

这些方法可以帮助代理在不超过 LLM 上下文窗口限制的情况下，持续跟踪对话进程。

若要管理消息历史，可使用 `pre_model_hook` 参数 —— 这是一个在调用语言模型之前始终执行的函数（节点）。

`pre_model_hook`

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/d50923b263784fb8a221fd1f51fd082f.png)  
若要对消息历史进行摘要，可以使用 pre\_model\_hook 配合预构建的 SummarizationNode 来实现。

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/d50923b263784fb8a221fd1f51fd082f.png)

使用摘要功能：

`from langchain_anthropic import ChatAnthropic
from langmem.short_term import SummarizationNode
from langchain_core.messages.utils import count_tokens_approximately
from langgraph.prebuilt import create_react_agent
from langgraph.prebuilt.chat_agent_executor import AgentState
from langgraph.checkpoint.memory import InMemorySaver
from typing import Any
model = ChatAnthropic(model="claude-3-7-sonnet-latest")
summarization_node = SummarizationNode(
token_counter=count_tokens_approximately,
model=model,
max_tokens=384,
max_summary_tokens=128,
output_messages_key="llm_input_messages",
)
class State(AgentState):
# NOTE: we're adding this key to keep track of previous summary information
# to make sure we're not summarizing on every LLM call
context: dict[str, Any]
checkpointer = InMemorySaver()
agent = create_react_agent(
model=model,
tools=tools,
pre_model_hook=summarization_node,
state_schema=State,
checkpointer=checkpointer,
)`

使用修剪功能：

要裁剪消息历史，可以使用 `pre_model_hook` 搭配 `trim_messages` 函数来实现。

`pre_model_hook`
`trim_messages`
`from langchain_core.messages.utils import (
trim_messages,
count_tokens_approximately
)
from langgraph.prebuilt import create_react_agent
# This function will be called every time before the node that calls LLM
def pre_model_hook(state):
trimmed_messages = trim_messages(
state["messages"],
strategy="last",
token_counter=count_tokens_approximately,
max_tokens=384,
start_on="human",
end_on=("human", "tool"),
)
return {"llm_input_messages": trimmed_messages}
checkpointer = InMemorySaver()
agent = create_react_agent(
model,
tools,
pre_model_hook=pre_model_hook,
checkpointer=checkpointer,
)`

##### 在工具中读取状态

LangGraph 允许代理在工具中访问其短期记忆（state）。

`from typing import Annotated
from langgraph.prebuilt import InjectedState, create_react_agent
class CustomState(AgentState):
user_id: str
def get_user_info(
state: Annotated[CustomState, InjectedState]
) -> str:
"""Look up user info."""
user_id = state["user_id"]
return "User is John Smith" if user_id == "user_123" else "Unknown user"
agent = create_react_agent(
model="anthropic:claude-3-7-sonnet-latest",
tools=[get_user_info],
state_schema=CustomState,
)
agent.invoke({
"messages": "look up user information",
"user_id": "user_123"
})`

##### 在工具中写入状态

要在执行过程中修改代理的短期记忆（state），可以直接从工具中返回状态更新。这对于持久化中间结果或让后续工具或提示能够访问相关信息非常有用。

`from typing import Annotated
from langchain_core.tools import InjectedToolCallId
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import ToolMessage
from langgraph.prebuilt import InjectedState, create_react_agent
from langgraph.prebuilt.chat_agent_executor import AgentState
from langgraph.types import Command
class CustomState(AgentState):
user_name: str
def update_user_info(
tool_call_id: Annotated[str, InjectedToolCallId],
config: RunnableConfig
) -> Command:
"""Look up and update user info."""
user_id = config["configurable"].get("user_id")
name = "John Smith" if user_id == "user_123" else "Unknown user"
return Command(update={
"user_name": name,
# update the message history
"messages": [
ToolMessage(
"Successfully looked up user information",
tool_call_id=tool_call_id
)
]
})
def greet(
state: Annotated[CustomState, InjectedState]
) -> str:
"""Use this to greet the user once you found their info."""
user_name = state["user_name"]
return f"Hello {user_name}!"
agent = create_react_agent(
model="anthropic:claude-3-7-sonnet-latest",
tools=[update_user_info, greet],
state_schema=CustomState
)
agent.invoke(
{"messages": [{"role": "user", "content": "greet the user"}]},
config={"configurable": {"user_id": "user_123"}}
)`

#### 长期记忆

使用长期记忆可以在多轮对话中存储用户特定或应用特定的数据。这对于希望记住用户偏好或其他信息的应用（如聊天机器人）非常有用。

要使用长期记忆，你需要：

`get_store`

##### 读取数据（Read）

定义一个工具供代理查找用户信息：

`from langchain_core.runnables import RunnableConfig
from langgraph.config import get_store
from langgraph.prebuilt import create_react_agent
from langgraph.store.memory import InMemoryStore
store = InMemoryStore()
store.put(
("users",),
"user_123",
{
"name": "John Smith",
"language": "English",
}
)
def get_user_info(config: RunnableConfig) -> str:
"""查找用户信息"""
store = get_store() # 与 create_react_agent 中配置一致
user_id = config["configurable"].get("user_id")
user_info = store.get(("users",), user_id)
return str(user_info.value) if user_info else "Unknown user"
agent = create_react_agent(
model="anthropic:claude-3-7-sonnet-latest",
tools=[get_user_info],
store=store
)
# 执行代理调用
agent.invoke(
{"messages": [{"role": "user", "content": "look up user information"}]},
config={"configurable": {"user_id": "user_123"}}
)`

#### 写入数据（Write）

定义一个工具，用于更新用户信息：

`from typing_extensions import TypedDict
from langgraph.config import get_store
from langgraph.prebuilt import create_react_agent
from langgraph.store.memory import InMemoryStore
store = InMemoryStore()
class UserInfo(TypedDict):
name: str
def save_user_info(user_info: UserInfo, config: RunnableConfig) -> str:
"""保存用户信息"""
store = get_store()
user_id = config["configurable"].get("user_id")
store.put(("users",), user_id, user_info)
return "Successfully saved user info."
agent = create_react_agent(
model="anthropic:claude-3-7-sonnet-latest",
tools=[save_user_info],
store=store
)
# 执行代理调用
agent.invoke(
{"messages": [{"role": "user", "content": "My name is John Smith"}]},
config={"configurable": {"user_id": "user_123"}}
)
# 你可以直接访问 store 获取该值
store.get(("users",), "user_123").value`

#### 语义搜索（Semantic search）

LangGraph 还支持通过语义相似度，在长期记忆中进行搜索。

**LangMem** 是一个由 LangChain 维护的库，提供用于管理代理长期记忆的工具。可参考 LangMem 文档了解使用示例。

### 人类介入（Human-in-the-loop）

为了让代理在执行工具调用时支持人工审查、编辑和批准，LangGraph 提供了内建的 Human-In-the-Loop（HIL）特性，核心是 `interrupt()` 原语。

`interrupt()`

LangGraph 支持无限期地暂停代理执行 —— 可以是几分钟、几小时，甚至几天 —— 直到接收到人类输入。

这得益于代理状态被 **checkpoint** 到数据库中，从而支持上下文持久化，并在稍后恢复流程时从中断处继续执行。

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/3d56b948c2f544b9851ed351d0f649b5.png)

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/3d56b948c2f544b9851ed351d0f649b5.png)

#### 工具调用审查（Review tool calls）

要给某个工具添加人工审批步骤：

`interrupt()`
`Command(resume=...)`
`from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt
from langgraph.prebuilt import create_react_agent
# An example of a sensitive tool that requires human review / approval
def book_hotel(hotel_name: str):
"""Book a hotel"""
response = interrupt(
f"Trying to call `book_hotel` with args {{'hotel_name': {hotel_name}}}. "
"Please approve or suggest edits."
)
if response["type"] == "accept":
pass
elif response["type"] == "edit":
hotel_name = response["args"]["hotel_name"]
else:
raise ValueError(f"Unknown response type: {response['type']}")
return f"Successfully booked a stay at {hotel_name}."
checkpointer = InMemorySaver()
agent = create_react_agent(
model="anthropic:claude-3-5-sonnet-latest",
tools=[book_hotel],
checkpointer=checkpointer,
)`

使用 `stream()` 方法运行代理，传入 `config` 对象以指定线程 ID。这使得代理能够在后续调用时恢复同一个对话。

`stream()`
`config`
`config = {
"configurable": {
"thread_id": "1"
}
}
for chunk in agent.stream(
{"messages": [{"role": "user", "content": "book a stay at McKittrick hotel"}]},
config
):
print(chunk)
print("\n")`

你会看到代理运行直到遇到 `interrupt()` 调用，此时它会暂停并等待人工输入。

`interrupt()`

通过 `Command(resume=...)` 恢复代理，以根据人工输入继续执行。

`Command(resume=...)`
`from langgraph.types import Command
for chunk in agent.stream(
Command(resume={"type": "accept"}),
# Command(resume={"type": "edit", "args": {"hotel_name": "McKittrick Hotel"}}),
config
):
print(chunk)
print("\n")`

#### 与 Agent Inbox 一起使用

你可以创建一个包装器，为任何工具添加中断功能。

下面的示例提供了一个参考实现，兼容Agent Inbox UI 和 Agent 聊天界面。

`from typing import Callable
from langchain_core.tools import BaseTool, tool as create_tool
from langchain_core.runnables import RunnableConfig
from langgraph.types import interrupt
from langgraph.prebuilt.interrupt import HumanInterruptConfig, HumanInterrupt
def add_human_in_the_loop(
tool: Callable | BaseTool,
*,
interrupt_config: HumanInterruptConfig = None,
) -> BaseTool:
"""Wrap a tool to support human-in-the-loop review."""
if not isinstance(tool, BaseTool):
tool = create_tool(tool)
if interrupt_config is None:
interrupt_config = {
"allow_accept": True,
"allow_edit": True,
"allow_respond": True,
}
@create_tool(
tool.name,
description=tool.description,
args_schema=tool.args_schema
)
def call_tool_with_interrupt(config: RunnableConfig, **tool_input):
request: HumanInterrupt = {
"action_request": {
"action": tool.name,
"args": tool_input
},
"config": interrupt_config,
"description": "Please review the tool call"
}
response = interrupt([request])[0]
# approve the tool call
if response["type"] == "accept":
tool_response = tool.invoke(tool_input, config)
# update tool call args
elif response["type"] == "edit":
tool_input = response["args"]["args"]
tool_response = tool.invoke(tool_input, config)
# respond to the LLM with user feedback
elif response["type"] == "response":
user_feedback = response["args"]
tool_response = user_feedback
else:
raise ValueError(f"Unsupported interrupt response type: {response['type']}")
return tool_response
return call_tool_with_interrupt`

你可以使用 add\_human\_in\_the\_loop 包装器，将 interrupt() 添加到任何工具中，而无需在工具内部添加它：

`from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
checkpointer = InMemorySaver()
def book_hotel(hotel_name: str):
"""Book a hotel"""
return f"Successfully booked a stay at {hotel_name}."
agent = create_react_agent(
model="anthropic:claude-3-5-sonnet-latest",
tools=[
add_human_in_the_loop(book_hotel),
],
checkpointer=checkpointer,
)
config = {"configurable": {"thread_id": "1"}}
# Run the agent
for chunk in agent.stream(
{"messages": [{"role": "user", "content": "book a stay at McKittrick hotel"}]},
config
):
print(chunk)
print("\n")`

你会看到代理运行到调用 interrupt() 的位置时暂停，等待人工输入。

然后使用 Command(resume=…) 恢复代理，根据人工输入继续执行。

`from langgraph.types import Command
for chunk in agent.stream(
Command(resume=[{"type": "accept"}]),
# Command(resume=[{"type": "edit", "args": {"args": {"hotel_name": "McKittrick Hotel"}}}]),
config
):
print(chunk)
print("\n")`

**“Using with Agent Inbox” 这部分讲什么？**

这部分内容是在说，**你可以用一个“包装器”（wrapper）来给任意工具（tool）添加“人工干预”功能**，也就是加上中断（interrupt），让执行过程中可以暂停等待人工确认或修改。

为什么要这么做？

**它具体做了什么？**

定义了一个叫 `add_human_in_the_loop` 的函数，这个函数：

`add_human_in_the_loop`
`interrupt()`

这个包装器可以和 Agent Inbox UI 和 Agent Chat UI 配合使用，方便人工在界面上审查和操作工具调用。

**用法举例**

`book_hotel`
`add_human_in_the_loop(book_hotel)`

总结一下：

### 多智能体

如果单个智能体需要在多个领域专业化或管理许多工具，可能会遇到困难。为了解决这个问题，你可以将智能体拆分成更小的、独立的智能体，并将它们组合成一个多智能体系统。

在多智能体系统中，智能体之间需要相互通信。它们通过“移交”（handoffs）来实现——这是一种原语，用来描述将控制权交给哪个智能体以及发送给该智能体的负载内容。

两种最流行的多智能体架构是：

#### Supervisor

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/8c6991254e924011b53e736a70e31958.png)  
Use langgraph-supervisor library to create a supervisor multi-agent system:

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/8c6991254e924011b53e736a70e31958.png)
`pip install langgraph-supervisor`
`from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor
def book_hotel(hotel_name: str):
"""Book a hotel"""
return f"Successfully booked a stay at {hotel_name}."
def book_flight(from_airport: str, to_airport: str):
"""Book a flight"""
return f"Successfully booked a flight from {from_airport} to {to_airport}."
flight_assistant = create_react_agent(
model="openai:gpt-4o",
tools=[book_flight],
prompt="You are a flight booking assistant",
name="flight_assistant"
)
hotel_assistant = create_react_agent(
model="openai:gpt-4o",
tools=[book_hotel],
prompt="You are a hotel booking assistant",
name="hotel_assistant"
)
supervisor = create_supervisor(
agents=[flight_assistant, hotel_assistant],
model=ChatOpenAI(model="gpt-4o"),
prompt=(
"You manage a hotel booking assistant and a"
"flight booking assistant. Assign work to them."
)
).compile()
for chunk in supervisor.stream(
{
"messages": [
{
"role": "user",
"content": "book a flight from BOS to JFK and a stay at McKittrick Hotel"
}
]
}
):
print(chunk)
print("\n")`

#### Swarm

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/f21bc407e271424b82fac26731306a45.png)  
Use langgraph-swarm library to create a swarm multi-agent system:

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/f21bc407e271424b82fac26731306a45.png)
`pip install langgraph-swarm`
`from langgraph.prebuilt import create_react_agent
from langgraph_swarm import create_swarm, create_handoff_tool
transfer_to_hotel_assistant = create_handoff_tool(
agent_name="hotel_assistant",
description="Transfer user to the hotel-booking assistant.",
)
transfer_to_flight_assistant = create_handoff_tool(
agent_name="flight_assistant",
description="Transfer user to the flight-booking assistant.",
)
flight_assistant = create_react_agent(
model="anthropic:claude-3-5-sonnet-latest",
tools=[book_flight, transfer_to_hotel_assistant],
prompt="You are a flight booking assistant",
name="flight_assistant"
)
hotel_assistant = create_react_agent(
model="anthropic:claude-3-5-sonnet-latest",
tools=[book_hotel, transfer_to_flight_assistant],
prompt="You are a hotel booking assistant",
name="hotel_assistant"
)
swarm = create_swarm(
agents=[flight_assistant, hotel_assistant],
default_active_agent="flight_assistant"
).compile()
for chunk in swarm.stream(
{
"messages": [
{
"role": "user",
"content": "book a flight from BOS to JFK and a stay at McKittrick Hotel"
}
]
}
):
print(chunk)
print("\n")`

#### 交接（Handoffs）

多智能体交互中常见的模式是交接（handoffs），即一个智能体将控制权交给另一个智能体。交接允许你指定：

这既适用于 langgraph-supervisor（主管将控制权交给各个独立智能体），也适用于 langgraph-swarm（单个智能体可以将控制权交给其他智能体）。

要在 `create_react_agent` 中实现交接，你需要：

`create_react_agent`

创建一个特殊工具，用于将控制权转移给另一个智能体

`def transfer_to_bob():
"""转移控制权给 bob。"""
return Command(
# 目标智能体（节点）名称
goto="bob",
# 发送给目标智能体的数据
update={"messages": [...]},
# 告诉 LangGraph 需要导航到父图中的智能体节点
graph=Command.PARENT,
)`

创建可使用交接工具的各个智能体：

`flight_assistant = create_react_agent(
..., tools=[book_flight, transfer_to_hotel_assistant]
)
hotel_assistant = create_react_agent(
..., tools=[book_hotel, transfer_to_flight_assistant]
)`

定义一个包含各个智能体节点的父图：

`from langgraph.graph import StateGraph, MessagesState
multi_agent_graph = (
StateGraph(MessagesState)
.add_node(flight_assistant)
.add_node(hotel_assistant)
...
)`

组合起来，你可以实现一个简单的多智能体系统，包含航班预订助手和酒店预订助手：

`from typing import Annotated
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import create_react_agent, InjectedState
from langgraph.graph import StateGraph, START, MessagesState
from langgraph.types import Command
def create_handoff_tool(*, agent_name: str, description: str | None = None):
name = f"transfer_to_{agent_name}"
description = description or f"Transfer to {agent_name}"
@tool(name, description=description)
def handoff_tool(
state: Annotated[MessagesState, InjectedState],
tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
tool_message = {
"role": "tool",
"content": f"Successfully transferred to {agent_name}",
"name": name,
"tool_call_id": tool_call_id,
}
return Command(
goto=agent_name,
update={"messages": state["messages"] + [tool_message]},
graph=Command.PARENT,
)
return handoff_tool
# 创建交接工具
transfer_to_hotel_assistant = create_handoff_tool(
agent_name="hotel_assistant",
description="Transfer user to the hotel-booking assistant.",
)
transfer_to_flight_assistant = create_handoff_tool(
agent_name="flight_assistant",
description="Transfer user to the flight-booking assistant.",
)
# 简单工具函数
def book_hotel(hotel_name: str):
"""预订酒店"""
return f"Successfully booked a stay at {hotel_name}."
def book_flight(from_airport: str, to_airport: str):
"""预订航班"""
return f"Successfully booked a flight from {from_airport} to {to_airport}."
# 定义智能体
flight_assistant = create_react_agent(
model="anthropic:claude-3-5-sonnet-latest",
tools=[book_flight, transfer_to_hotel_assistant],
prompt="You are a flight booking assistant",
name="flight_assistant"
)
hotel_assistant = create_react_agent(
model="anthropic:claude-3-5-sonnet-latest",
tools=[book_hotel, transfer_to_flight_assistant],
prompt="You are a hotel booking assistant",
name="hotel_assistant"
)
# 定义多智能体图
multi_agent_graph = (
StateGraph(MessagesState)
.add_node(flight_assistant)
.add_node(hotel_assistant)
.add_edge(START, "flight_assistant")
.compile()
)
# 运行多智能体图
for chunk in multi_agent_graph.stream(
{
"messages": [
{
"role": "user",
"content": "book a flight from BOS to JFK and a stay at McKittrick Hotel"
}
]
}
):
print(chunk)
print("\n")`

**注意**

该交接实现假设：

### Evals（评估）&部署（Deployment） & UI

这三个功能是需要langSmith的，而langSmith属于平台服务，提供收费功能。

因此部署我们采用 langfuse + FastAPI + langGraph + SSE…，也就是如下划分：

![Logo](https://i-blog.csdnimg.cn/devpress/blog/e91274dd3f454fa0a048e0af88cb04ef.png)

更多推荐

![cover](https://i-blog.csdnimg.cn/direct/2504cd5a87f346c69ca440dedd604da7.png)

08.大模型Function Call的应用

![avatar](https://i-blog.csdnimg.cn/devpress/blog/e91274dd3f454fa0a048e0af88cb04ef.png)

零代码构建企业级智能工作流：AutoAgent多模型协作与动态任务编排实战指南

你是否还在为复杂业务逻辑的自动化实现而烦恼？面对多步骤任务拆解、跨模型协作和动态流程调整时束手无策？本文将通过AutoAgent框架的数学解题工作流实例，带你掌握零代码构建智能业务流程的核心技术，无需编程基础也能打造企业级自动化解决方案。读完本文你将获得：多智能体协作设计方法、动态任务路由实现、结果聚合策略以及可视化工作流编排技巧。## 智能工作流核心架构解析AutoAgent工作流框架采

![avatar](https://i-blog.csdnimg.cn/devpress/blog/e91274dd3f454fa0a048e0af88cb04ef.png)

从零到一：AutoAgent多语言支持实现全球化AI应用的完整指南

你是否正在为AI应用的全球化部署而烦恼？当你的智能体（Agent）只能理解单一语言时，如何突破地域限制触达全球用户？本文将通过三个关键步骤，带你掌握AutoAgent的多语言支持能力，让你的AI应用无缝适配不同语言环境，轻松实现全球化布局。读完本文，你将获得：多语言架构设计思路、自动化翻译工作流搭建方法，以及本地化测试的完整流程。## 多语言支持的商业价值在全球化背景下，语言支持能力直接影

![avatar](https://i-blog.csdnimg.cn/devpress/blog/e91274dd3f454fa0a048e0af88cb04ef.png)
![浏览量](https://csdnimg.cn/release/devpress/public/img/watch.a5bd9e9b.svg)
![点赞](https://csdnimg.cn/release/devpress/public/img/thumb.a0b81433.svg)
![收藏](https://csdnimg.cn/release/devpress/public/img/mark.f1a889ab.svg)
![](https://csdnimg.cn/release/devpress/public/img/share.f1fdda75.svg)

扫一扫分享内容

![]()
![](https://csdnimg.cn/release/devpress/public/img/share.f1fdda75.svg)

### 所有评论(0)

![]()![](https://profile-avatar.csdnimg.cn/6074747de68748ceb13e366e8ceeca8b_general_zy.jpg!1)

### [General\_zy](https://devpress.csdn.net/user/General_zy)

![](https://csdnimg.cn/release/devpress/public/img/devote.fe704c8a.svg)
![](https://csdnimg.cn/release/devpress/public/img/top.c3a2945a.svg)
![]()![logo](https://csdnimg.cn/release/devpress/public/img/csdn-logo.07312d72.png)
![logo](https://csdnimg.cn/release/devpress/public/img/csdn-logo.07312d72.png)