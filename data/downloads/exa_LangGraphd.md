# LangGraphd的细节大全——如何定义或者更新状态原创 - CSDN博客

**URL**:
https://blog.csdn.net/weixin_40143861/article/details/145483735

## 元数据
- 发布日期: 2025-02-06T00:00:00+00:00

## 完整内容
---

 
 我们这节来探讨一下如何从节点更新图状态一些基本的方式和需要注意的细节，同学们跟随我一起进入 Graph 的世界。 
在 LangGraph 中，State 可以是 TypedDict、Pydantic 模型或 dataclass。这些结构主要用于描述状态的类型，并使得状态的管理更加清晰和有序。我们可以通过不同的方式来定义状态。 
下面我分别举一个 TypedDict、Pydantic 模型和 dataclass 的例子来说明： 
TypedDict 是 Python 中的一种类型，用于表示字典结构，并能指定字典中每个键的类型 
 from typing import TypedDict
 class State ( TypedDict): 
 name: str 
 age: int 
 active: bool 
 # 创建状态实例 
state: State = { 
 "name": "Alice", 
 "age": 30, 
 "active": True 
} 
 print ( state) 
 
 Pydantic 是一个非常强大的数据验证和解析库，可以将数据转换成 Pydantic 模型实例，并进行类型检查和验证 
 from pydantic import BaseModel
 class State ( BaseModel): 
 name: str 
 age: int 
 active: bool 
 # 创建状态实例 
state = State ( name = "Bob", age = 25, active = False) 
 print ( state) 
 
 在这个例子中，State 是一个继承自 BaseModel 的 Pydantic 模型。Pydantic 自动为模型字段提供了类型验证。我们可以通过 State(name=“Bob”, age=25, active=False) 来创建一个实例，Pydantic 会确保类型正确。 
dataclass 是 Python 3.7 引入的标准库，提供了一种简单的方式来定义类，并自动生成常用的方法（如 init 、 repr 等） 
 from dataclasses import dataclass
 @dataclass 
 class State: 
 name: str 
 age: int 
 active: bool 
 # 创建状态实例 
state = State ( name = "Charlie", age = 40, active = True) 
 print ( state) 
 
 在这个例子中，State 是一个简单的 dataclass，它具有三个字段：name、age 和 active。dataclass 会自动生成 init 方法，所以你可以直接通过 State(name=“Charlie”, age=40, active=True) 来创建实例。 
在我们langraph中，默认情况下，图的输入和输出结构将是相同的，且状态决定了该结构。 
我们定义一个简单的 State 例子： 
 from langchain_core. messages import AnyMessage
 from typing_extensions import TypedDict
 class State ( TypedDict): 
 messages: list [ AnyMessage] 
 extra_field: int 
 
 这个状态保存跟踪了一系列消息对象，并且还有一个额外的整数字段。 
 定义图形结构 
 让我们构建一个包含单个节点的图。我们的节点只是一个 Python 函数，它读取图的状态并对其进行更新。这个函数的第一个参数将始终是状态： 
 from langchain_core. messages import AIMessage
 def node ( state: State): 
 messages = state [ "messages"] 
 new_message = AIMessage ( "Hello!") 
 return { "messages": messages + [ new_message], "extra_field": 10} 
 
 定义节点只是将消息附加到我们的消息列表中，然后填充一个额外的字段。 
接下来，接下来我们将定义一个简单的图，其中包含我们之前创建的节点。我们将使用 StateGraph 来定义一个操作该状态的图，并使用 add_node 将我们的节点添加到图中。 
 from langgraph. graph import StateGraph
graph_builder = StateGraph ( State) 
graph_builder. add_node ( node) 
graph_builder. set_entry_point ( "node") 
graph = graph_builder. compile () 
 
 执行下面可视化： 
 from IPython. display import Image, display
display ( Image ( graph. get_graph (). draw_mermaid_png ())) 
 
 
在这种情况下，我们的图只是执行一个节点。 
 使用图 
 我们来调用它，同学们还记得不： 
 from langchain_core. messages import HumanMessage
result = graph. invoke ( { "messages": [ HumanMessage ( "Hi")]}) 
 // 打印 result
 
 得到： 
 { 'messages': [ HumanMessage ( content = 'Hi', additional_kwargs = {}, response_metadata = {}), 
 AIMessage ( content = 'Hello!', additional_kwargs = {}, response_metadata = {})], 
 'extra_field': 10} 
 
 这里需要注意的是，我们执行上面定义的 graph ，我们是通过更新状态的单个字段启动了调用。在调用结果中，我们接收到整个状态。 
为了方便我们查看，我们换一种打印方式： 
 for message in result [ "messages"]: 
 message. pretty_print () 
 
 得到下面结果 
 ================================[1m Human Message [0m=================================
Hi
==================================[1m Ai Message [0m==================================
Hello!
 
 通过 reducer 处理状态更新。 
 在状态中的每个键可以有自己的独立 reducer 函数，用于控制节点的更新如何应用。如果没有显式指定 reducer 函数，则默认假设所有对该键的更新都会覆盖其当前值。对于 TypedDict 状态架构，我们可以通过在状态的相应字段上使用 reducer 函数注解来定义 reducers。 
在上面的代码中，我们的节点通过向 messages 键附加一条消息来更新状态。在下面的示例中，我们为这个键添加了一个 reducer，使得更新会自动地附加消息： 
 from typing_extensions import Annotated
 def add ( left, right): 
 """Can also import `add` from the `operator` built-in.""" 
 return left + right
 class State ( TypedDict): 
 messages: Annotated [ list [ AnyMessage], add] 
 extra_field: int 
 
 我们的节点可以简化成： 
 def node ( state: State): 
 new_message = AIMessage ( "Hello!") 
 return { "messages": [ new_message], "extra_field": 10} 
 
 然后定义并执行我们的graph： 
 from langgraph. graph import START
graph = StateGraph ( State). add_node ( node). add_edge ( START, "node"). compile () 
result = graph. invoke ( { "messages": [ HumanMessage ( "Hi")]}) 
 for message in result [ "messages"]: 
 message. pretty_print () 
 
 得到结果 
 ================================[1m Human Message [0m=================================
Hi
==================================[1m Ai Message [0m==================================
Hello!
 
 更新的消息就自动的附加到后面了。 
 MessagesState 
 如果我们希望更新状态中已有的消息。并且还想接受消息格式的简写，例如 OpenAI 格式。该怎么做呢？ 
LangGraph 包含一个内置的 reducer add_messages，它处理了这些考虑事项： 
 from langgraph. graph. message import add_messages
 class State ( TypedDict): 
 messages: Annotated [ list [ AnyMessage], add_messages] 
 extra_field: int 
 def node ( state: State): 
 new_message = AIMessage ( "Hello!") 
 return { "messages": [ new_message], "extra_field": 10} 
graph = StateGraph ( State). add_node ( node). set_entry_point ( "node"). compile () 
 
 我们来执行它： 
 input_message = { "role": "user", "content": "Hi"} 
result = graph. invoke ( { <


---
*数据来源: Exa搜索 | 获取时间: 2026-02-21 19:57:14*