# 如何使用图 API ¶

**URL**:
https://github.langchain.ac.cn/langgraph/how-tos/graph-api/

## 元数据
- 发布日期: 2026-02-24T22:27:15.491216

## 完整内容
---
使用 Graph API - LangChain 教程[跳到内容] 
**LangGraph 平台文档已迁移！**请在新的[LangChain 文档] 网站上查找 LangGraph 平台文档。[] # 如何使用图API[¶] 
本指南演示了LangGraph 的Graph API 的基础知识。它详细介绍了[状态] ，以及如何组合常见的图结构，如[序列] 、[分支] 和[循环] 。它还涵盖了 LangGraph 的控制功能，包括用于map-reduce 工作流的[Send API] 和用于结合状态更新与节点间“跳转”的[Command API] 。
## 设置[¶] 
安装`langgraph`
```
`[]<web_link>pipinstall-Ulanggraph`
```
设置LangSmith 以便更好地调试注册[LangSmith] ，以便快速发现问题并提高您的 LangGraph 项目的性能。LangSmith 允许您使用跟踪数据来调试、测试和监控您使用LangGraph 构建的LLM 应用程序——请在[文档] 中阅读更多关于如何入门的信息。
## 定义和更新状态[¶] 
这里我们展示了如何在LangGraph 中定义和更新[状态] 。我们将演示：
1. 如何使用状态来定义图的[模式] 
2. 如何使用[reducer] 来控制状态更新的处理方式。### 定义状态[¶] 
LangGraph 中的[状态] 可以是`TypedDict`、`Pydantic`模型或 dataclass。下面我们将使用`TypedDict`。有关使用 Pydantic 的详细信息，请参阅[此部分] 。
默认情况下，图将具有相同的输入和输出模式，并且状态决定了该模式。有关如何定义不同的输入和输出模式，请参阅[此部分] 。
让我们考虑一个使用[消息] 的简单示例。这代表了许多 LLM 应用程序的一种通用状态形式。更多详细信息，请参阅我们的[概念页面] 。
*API 参考：[AnyMessage] *
```
`[]<web_link>fromlangchain\_core.messagesimportAnyMessage[]<web_link>fromtyping\_extensionsimportTypedDict[]<web_link>[]<web_link>classState(TypedDict):[]<web_link>messages:list[AnyMessage][]<web_link>extra\_field:int`
```
这个状态跟踪一个[消息] 对象列表，以及一个额外的整数字段。
### 更新状态[¶] 
让我们构建一个带单个节点的示例图。我们的[节点] 只是一个 Python 函数，它读取图的状态并对其进行更新。此函数的第一个参数将始终是状态。*API 参考：[AIMessage] *
```
`[]<web_link>fromlangchain\_core.messagesimportAIMessage[]<web_link>[]<web_link>defnode(state:State):[]<web_link>messages=state["messages"][]<web_link>new\_message=AIMessage("Hello!")[]<web_link>return{"messages":messages+[new\_message],"extra\_field":10}`
```
这个节点只是向我们的消息列表追加一条消息，并填充一个额外的字段。重要节点应该直接返回对状态的更新，而不是修改状态。接下来，让我们定义一个包含此节点的简单图。我们使用[StateGraph] 来定义一个操作此状态的图。然后我们使用[add\_node] 来填充我们的图。
*API 参考：[StateGraph] *
```
`[]<web_link>fromlanggraph.graphimportStateGraph[]<web_link>[]<web_link>builder=StateGraph(State)[]<web_link>builder.add\_node(node)[]<web_link>builder.set\_entry\_point("node")[]<web_link>graph=builder.compile()`
```
LangGraph 提供了内置的工具来可视化您的图。让我们检查一下我们的图。有关可视化的详细信息，请参阅[此部分] 。
```
`[]<web_link>fromIPython.displayimportImage,display[]<web_link>[]<web_link>display(Image(graph.get\_graph().draw\_mermaid\_png()))`
```
![Simple graph with single node] 
在这种情况下，我们的图只执行一个节点。让我们进行一个简单的调用。*API 参考：[HumanMessage] *
```
`[]<web_link>fromlangchain\_core.messagesimportHumanMessage[]<web_link>[]<web_link>result=graph.invoke({"messages":[HumanMessage("Hi")]})[]<web_link>result`
```
```
`[]<web_link>{'messages': [HumanMessage(content='Hi'), AIMessage(content='Hello!')], 'extra\_field': 10}`
```
请注意* 我们通过更新状态的单个键来启动调用。* 我们在调用结果中收到了整个状态。为了方便，我们经常通过pretty-print 检查[消息对象] 的内容。
```
`[]<web_link>formessageinresult["messages"]:[]<web_link>message.pretty\_print()`
```
```
`[]<web_link>================================ Human Message ================================[]<web_link>[]<web_link>Hi[]<web_link>================================== Ai Message ==================================[]<web_link>[]<web_link>Hello!`
```
### 使用reducer 处理状态更新[¶] 
状态中的每个键都可以有自己独立的[reducer] 函数，该函数控制如何应用来自节点的更新。如果未明确指定 reducer 函数，则假定对该键的所有更新都应覆盖它。对于`TypedDict`状态模式，我们可以通过使用 reducer 函数注解状态的相应字段来定义reducer。
在前面的示例中，我们的节点通过向消息列表追加一条消息来更新状态中的`"messages"`键。下面，我们向此键添加一个 reducer，以便更新会自动追加。
```
`[]<web_link>fromtyping\_extensionsimportAnnotated[]<web_link>[]<web_link>defadd(left,right):[]<web_link>"""Can also import `add` from the `operator` built-in."""[]<web_link>returnleft+right[]<web_link>[]<web_link>classState(TypedDict):[]<web_link>messages:Annotated[list[AnyMessage],add][]<web_link>extra\_field:int`
```
现在我们的节点可以被简化```
`[] defnode(state:State):[] new\_message=AIMessage("Hello!")[] return{"messages":[new\_message],"extra\_field":10}`
```
*API 参考：[START]<web_link>*
```
`[] fromlanggraph.graphimportSTART[] [] graph=StateGraph(State).add\_node(node).add\_edge(START,"node").compile()[] [] result=graph.invoke({"messages":[HumanMessage("Hi")]})[] [] formessageinresult["messages"]:[] message.pretty\_print()`
```
```
`[] ================================ Human Message ================================[] [] Hi[] ================================== Ai Message ==================================[] [] Hello!`
```
#### MessagesState[¶]<web_link>
实际上，在更新消息列表时还有其他考虑因素：* 我们可能希望更新状态中已有的消息。* 我们可能希望接受[消息格式]<web_link>的简写，例如[OpenAI 格式]<web_link>。
LangGraph 包含一个内置的reducer`add\_messages`，它处理了这些考虑因素。
*API 参考：[add\_messages]<web_link>*
```
`[] fromlanggraph.graph.messageimportadd\_messages[] [] classState(TypedDict):[] messages:Annotated[list[AnyMessage],add\_messages][] extra\_field:int[] [] defnode(state:State):[] new\_message=AIMessage("Hello!")[] return{"messages":[new\_message],"extra\_field":10}[] [] graph=StateGraph(State).add\_node(node).set\_entry\_point("node").compile()`
```
```
`[] input\_message={"role":"user","content":"Hi"}[] [] result=graph.invoke({"messages":[input\_message]})[] [] formessageinresult["messages"]:[] message.pretty\_print()`
```
```
`[] ================================ Human Message ================================[] [] Hi[] ================================== Ai Message ==================================[] [] Hello!`
```
对于涉及[聊天模型]<web_link>的应用程序，这是一种通用的状态表示。为了方便，LangGraph 包含一个预构建的`MessagesState`，因此我们可以拥有：
```
`[] fromlanggraph.graphimportMessagesState[] [] classState(MessagesState):[] extra\_field:int`
```
### 定义输入和输出模式[¶]<web_link>
默认情况下，`StateGraph`使用单一模式运行，所有节点都应使用该模式进行通信。但是，也可以为图定义不同的输入和输出模式。
当指定了不同的模式时，节点之间的通信仍将使用内部模式。输入模式确保提供的输入与预期结构匹配，而输出模式则根据定义的输出模式筛选内部数据，仅返回相关信息。下面，我们将看到如何定义不同的输入和输出模式。*API 参考：[StateGraph]<web_link>|[START]<web_link>|[END]<web_link>*
```
`[] fromlanggraph.graphimportStateGraph,START,END[] fromtyping\_extensionsimportTypedDict[] [] # Define the schema for the input[] classInputState(TypedDict):[] question:str[] [] # Define the schema for the output[] classOutputState(TypedDict):[] answer:str[] [] # Define the overall schema, combining both input and output[] classOverallState(InputState,OutputState):[] pass[] [] # Define the node that processes the input and generates an answer[] defanswer\_node(state:InputState):[] # Example answer and an extra key[] return{"answer":"bye","question":state["question"]}[] [] # Build the graph with input and output schemas specified[] builder=StateGraph(OverallState,input\_schema=InputState,output\_schema=OutputState)[] builder.add\_node(answer\_node)# Add the answer node[] builder.add\_edge(START,"answer\_node")# Define the starting edge[] builder.add\_edge("answer\_node",END)# Define the ending edge[] graph=builder.compile()# Compile the graph[] [] # Invoke the graph with an input and print the result[] print(graph.invoke({"question":"hi"}))`
```
```
`[] {'answer': 'bye'}`
```
注意，invoke 的输出只包含输出模式。### 在节点之间传递私有状态[¶]<web_link>
在某些情况下，您可能希望节点之间交换一些对中间逻辑至关重要但不需要成为图主模式一部分的信息。这些私有数据与图的整体输入/输出无关，只应在某些节点之间共享。
下面，我们将创建一个由三个节点（node\_1、node\_2 和node\_3）组成的顺序图示例，其中私有数据在前两个步骤（node\_1 和node\_2）之间传递，而第三个步骤（node\_3）只能访问公共的整体状态。
*API 参考：[StateGraph]<web_link>|[START]<web_link>|[END]<web_link>*
```
`[] fromlanggraph.graphimportStateGraph,START,END[] fromtyping\_extensionsimportTypedDict[] [] # The overall state of the graph (this is the public state shared across nodes)[] classOverallState(TypedDict):[] a:str[] [] # Output from node\_1 contains private data that is not part of the overall state[] classNode1Output(TypedDict):[] private\_data:str[] [] # The private data is only shared between node\_1 and node\_2[] defnode\_1(state:OverallState)-&gt;Node1Output:[] output={"private\_data":"set by node\_1"}[] print(f"Entered node `node\_1`:\\n\\tInput:{state}.\\n\\tReturned:{output}")[] returnoutput[] [] # Node 2 input only requests the private data available after node\_1[] classNode2Input(TypedDict):[] private\_data:str[] [] defnode\_2(state:Node2Input)-&gt;OverallState:[] output={"a":"set by node\_2"}[] print(f"Entered node `node\_2`:\\n\\tInput:{state}.\\n\\tReturned:{output}")[] returnoutput[] [] # Node 3 only has access to the overall state (no access to private data from node\_1)[] defnode\_3(state:OverallState)-&gt;OverallState:[] output={"a":"set by node\_3"}[] print(f"Entered node `node\_3`:\\n\\tInput:{state}.\\n\\tReturned:{output}")[] returnoutput[] [] # Connect nodes in a sequence[] # node\_2 accepts private data from node\_1, whereas[] # node\_3 does not see the private data.[] builder=StateGraph(OverallState).add\_sequence([node\_1,node\_2,node\_3])[] builder.add\_edge(START,"node\_1")[] graph=builder.compile()[] [] # Invoke the graph with the initial state[] response=graph.invoke([] {[] "a":"set at start",[]}[])[] [] print()[] print(f"Output of graph invocation:{response}")`
```
```
`[] Entered node `node\_1`:[] Input: {'a': 'set at start'}.[] Returned: {'private\_data'


---
*数据来源: Exa搜索 | 获取时间: 2026-02-24 22:27:43*