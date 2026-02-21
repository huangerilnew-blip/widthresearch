* [设置](#setup)
* [共享状态模式](#shared-state-schemas)
* [不同状态模式](#different-state-schemas)
* [添加持久化](#add-persistence)
* [查看子图状态](#view-subgraph-state)
* [流式传输子图输出](#stream-subgraph-outputs)

# 使用子图[¶](#use-subgraphs "Permanent link")

本指南介绍了使用[子图](../../concepts/subgraphs/)的机制。子图的一个常见应用是构建[多智能体](../../concepts/multi_agent/)系统。

添加子图时，您需要定义父图和子图如何通信

* [共享状态模式](#shared-state-schemas) — 父图和子图在其状态[模式](../../concepts/low_level/#state)中拥有**共享的状态键**
* [不同状态模式](#different-state-schemas) — 父图和子图的[模式](../../concepts/low_level/#state)中**没有共享的状态键**

## 设置[¶](#setup "永久链接")

```
pip install -U langgraph    
```

为 LangGraph 开发设置 LangSmith

注册 [LangSmith](https://smith.langchain.com) 以快速发现问题并提高您的 LangGraph 项目的性能。LangSmith 允许您使用跟踪数据来调试、测试和监控您使用 LangGraph 构建的 LLM 应用 — 在[此处](https://langsmith.langchain.ac.cn)阅读更多关于如何入门的信息。

## 共享状态模式[¶](#shared-state-schemas "Permanent link")

一种常见情况是父图和子图通过[模式](../../concepts/low_level/#state)中的共享状态键（通道）进行通信。例如，在[多智能体](../../concepts/multi_agent/)系统中，智能体通常通过共享的 [messages](https://github.langchain.ac.cn/langgraph/concepts/low_level.md#why-use-messages) 键进行通信。

如果您的子图与父图共享状态键，您可以按照以下步骤将其添加到您的图中

1. 定义子图工作流（在下面的示例中为 `subgraph_builder`）并编译它
2. 在定义父图工作流时，将编译后的子图传递给 `.add_node` 方法

*API 参考：[StateGraph](https://github.langchain.ac.cn/langgraph/reference/graphs/#langgraph.graph.state.StateGraph)*

```
 from typing_extensions import TypedDict from  typing_extensions  import TypedDictfrom langgraph.graph.state import StateGraph, START from  langgraph.graph.state  import StateGraph, START  class State(TypedDict): class  State(TypedDict): foo: str foo: str  # Subgraph # Subgraph  def subgraph_node_1(state: State): def  subgraph_node_1(state: State): return {"foo": "hi! " + state["foo"]} return{"foo":"hi! " + state["foo"]}  subgraph_builder = StateGraph(State) subgraph_builder = StateGraph(State)subgraph_builder.add_node(subgraph_node_1) subgraph_builder. add_node(subgraph_node_1)subgraph_builder.add_edge(START, "subgraph_node_1") subgraph_builder. add_edge(START, "subgraph_node_1")subgraph = subgraph_builder.compile() subgraph = subgraph_builder. compile()  # Parent graph # Parent graph  builder = StateGraph(State) builder = StateGraph(State)builder.add_node("node_1", subgraph) builder. add_node("node_1", subgraph)builder.add_edge(START, "node_1") builder. add_edge(START, "node_1")graph = builder.compile() graph = builder. compile()
```

 完整示例：共享状态模式

```
 from typing_extensions import TypedDict from  typing_extensions  import TypedDictfrom langgraph.graph.state import StateGraph, START from  langgraph.graph.state  import StateGraph, START  # Define subgraph # Define subgraphclass SubgraphState(TypedDict): class  SubgraphState(TypedDict): foo: str # (1)!  foo: str# (1)!  bar: str # (2)! bar: str# (2)!  def subgraph_node_1(state: SubgraphState): def  subgraph_node_1(state: SubgraphState): return {"bar": "bar"} return{"bar": "bar"}  def subgraph_node_2(state: SubgraphState): def  subgraph_node_2(state: SubgraphState): # note that this node is using a state key ('bar') that is only available in the subgraph # note that this node is using a state key ('bar') that is only available in the subgraph # and is sending update on the shared state key ('foo') # and is sending update on the shared state key ('foo') return {"foo": state["foo"] + state["bar"]} return{"foo": state["foo"] + state["bar"]}  subgraph_builder = StateGraph(SubgraphState) subgraph_builder = StateGraph(SubgraphState)subgraph_builder.add_node(subgraph_node_1) subgraph_builder. add_node(subgraph_node_1)subgraph_builder.add_node(subgraph_node_2) subgraph_builder. add_node(subgraph_node_2)subgraph_builder.add_edge(START, "subgraph_node_1") subgraph_builder. add_edge(START, "subgraph_node_1")subgraph_builder.add_edge("subgraph_node_1", "subgraph_node_2") subgraph_builder. add_edge("subgraph_node_1", "subgraph_node_2")subgraph = subgraph_builder.compile() subgraph = subgraph_builder. compile()  # Define parent graph # Define parent graphclass ParentState(TypedDict): class  ParentState(TypedDict): foo: str foo: str  def node_1(state: ParentState): def  node_1(state: ParentState): return {"foo": "hi! " + state["foo"]} return{"foo":"hi! " + state["foo"]}  builder = StateGraph(ParentState) builder = StateGraph(ParentState)builder.add_node("node_1", node_1) builder. add_node("node_1", node_1)builder.add_node("node_2", subgraph) builder. add_node("node_2", subgraph)builder.add_edge(START, "node_1") builder. add_edge(START, "node_1")builder.add_edge("node_1", "node_2") builder. add_edge("node_1", "node_2")graph = builder.compile() graph = builder. compile()  for chunk in graph.stream({"foo": "foo"}): for chunk in graph. stream({"foo": "foo"}): print(chunk) print(chunk)
```

1. 此键与父图状态共享
2. 此键是 `SubgraphState` 私有的，对父图不可见

```
{'node_1': {'foo': 'hi! foo'}} {'node_2': {'foo': 'hi! foobar'}} 
```

## 不同状态模式[¶](#different-state-schemas "Permanent link")

对于更复杂的系统，您可能希望定义与父图具有**完全不同模式**（没有共享键）的子图。例如，您可能希望为[多智能体](../../concepts/multi_agent/)系统中的每个智能体保留私有的消息历史记录。

如果您的应用程序属于这种情况，您需要定义一个**调用子图的节点函数**。此函数需要在调用子图之前将输入（父）状态转换为子图状态，并在从节点返回状态更新之前将结果转换回父状态。

*API 参考：[StateGraph](https://github.langchain.ac.cn/langgraph/reference/graphs/#langgraph.graph.state.StateGraph)*

```
 from typing_extensions import TypedDict from  typing_extensions  import TypedDictfrom langgraph.graph.state import StateGraph, START from  langgraph.graph.state  import StateGraph, START  class SubgraphState(TypedDict): class  SubgraphState(TypedDict): bar: str bar: str  # Subgraph # Subgraph  def subgraph_node_1(state: SubgraphState): def  subgraph_node_1(state: SubgraphState): return {"bar": "hi! " + state["bar"]} return{"bar":"hi! " + state["bar"]}  subgraph_builder = StateGraph(SubgraphState) subgraph_builder = StateGraph(SubgraphState)subgraph_builder.add_node(subgraph_node_1) subgraph_builder. add_node(subgraph_node_1)subgraph_builder.add_edge(START, "subgraph_node_1") subgraph_builder. add_edge(START, "subgraph_node_1")subgraph = subgraph_builder.compile() subgraph = subgraph_builder. compile()  # Parent graph # Parent graph  class State(TypedDict): class  State(TypedDict): foo: str foo: str  def call_subgraph(state: State): def  call_subgraph(state: State): subgraph_output = subgraph.invoke({"bar": state["foo"]}) # (1)! subgraph_output = subgraph. invoke({"bar": state["foo"]})# (1)! return {"foo": subgraph_output["bar"]} # (2)! return{"foo": subgraph_output["bar"]}# (2)!  builder = StateGraph(State) builder = StateGraph(State)builder.add_node("node_1", call_subgraph) builder. add_node("node_1", call_subgraph)builder.add_edge(START, "node_1") builder. add_edge(START, "node_1")graph = builder.compile() graph = builder. compile()
```

1. 将状态转换为子图状态
2. 将响应转换回父状态

 完整示例：不同状态模式

```
 from typing_extensions import TypedDict from  typing_extensions  import TypedDictfrom langgraph.graph.state import StateGraph, START from  langgraph.graph.state  import StateGraph, START  # Define subgraph # Define subgraphclass SubgraphState(TypedDict): class  SubgraphState(TypedDict):  # note that none of these keys are shared with the parent graph state # note that none of these keys are shared with the parent graph state bar: str bar: str baz: str baz: str  def subgraph_node_1(state: SubgraphState): def  subgraph_node_1(state: SubgraphState): return {"baz": "baz"} return{"baz": "baz"}  def subgraph_node_2(state: SubgraphState): def  subgraph_node_2(state: SubgraphState): return {"bar": state["bar"] + state["baz"]} return{"bar": state["bar"] + state["baz"]}  subgraph_builder = StateGraph(SubgraphState) subgraph_builder = StateGraph(SubgraphState)subgraph_builder.add_node(subgraph_node_1) subgraph_builder. add_node(subgraph_node_1)subgraph_builder.add_node(subgraph_node_2) subgraph_builder. add_node(subgraph_node_2)subgraph_builder.add_edge(START, "subgraph_node_1") subgraph_builder. add_edge(START, "subgraph_node_1")subgraph_builder.add_edge("subgraph_node_1", "subgraph_node_2") subgraph_builder. add_edge("subgraph_node_1", "subgraph_node_2")subgraph = subgraph_builder.compile() subgraph = subgraph_builder. compile()  # Define parent graph # Define parent graphclass ParentState(TypedDict): class  ParentState(TypedDict): foo: str foo: str  def node_1(state: ParentState): def  node_1(state: ParentState): return {"foo": "hi! " + state["foo"]} return{"foo":"hi! " + state["foo"]}  def node_2(state: ParentState): def  node_2(state: ParentState): response = subgraph.invoke({"bar": state["foo"]}) # (1)! response = subgraph. invoke({"bar": state["foo"]})# (1)! return {"foo": response["bar"]} # (2)! return{"foo": response["bar"]}# (2)!   builder = StateGraph(ParentState) builder = StateGraph(ParentState)builder.add_node("node_1", node_1) builder. add_node("node_1", node_1)builder.add_node("node_2", node_2) builder. add_node("node_2", node_2)builder.add_edge(START, "node_1") builder. add_edge(START, "node_1")builder.add_edge("node_1", "node_2") builder. add_edge("node_1", "node_2")graph = builder.compile() graph = builder. compile()  for chunk in graph.stream({"foo": "foo"}, subgraphs=True): for chunk in graph. stream({"foo": "foo"}, subgraphs = True): print(chunk) print(chunk)
```

1. 将状态转换为子图状态
2. 将响应转换回父状态

```
((), {'node_1': {'foo': 'hi! foo'}}) (('node_2:9c36dd0f-151a-cb42-cbad-fa2f851f9ab7',), {'grandchild_1': {'my_grandchild_key': 'hi Bob, how are you'}}) (('node_2:9c36dd0f-151a-cb42-cbad-fa2f851f9ab7',), {'grandchild_2': {'bar': 'hi! foobaz'}}) ((), {'node_2': {'foo': 'hi! foobaz'}}) 
```

  完整示例：不同状态模式（两级子图）

这是一个具有两级子图的示例：父级 -> 子级 -> 孙级。

```
 # Grandchild graph # Grandchild graph from typing_extensions import TypedDict from  typing_extensions  import TypedDictfrom langgraph.graph.state import StateGraph, START, END from  langgraph.graph.state  import StateGraph, START, END  class GrandChildState(TypedDict): class  GrandChildState(TypedDict): my_grandchild_key: str my_grandchild_key: str  def grandchild_1(state: GrandChildState) -> GrandChildState: def  grandchild_1(state: GrandChildState) -> GrandChildState: # NOTE: child or parent keys will not be accessible here # NOTE: child or parent keys will not be accessible here return {"my_grandchild_key": state["my_grandchild_key"] + ", how are you"} return{"my_grandchild_key": state["my_grandchild_key"] +", how are you"}   grandchild = StateGraph(GrandChildState) grandchild = StateGraph(GrandChildState)grandchild.add_node("grandchild_1", grandchild_1) grandchild. add_node("grandchild_1", grandchild_1)  grandchild.add_edge(START, "grandchild_1") grandchild. add_edge(START, "grandchild_1")grandchild.add_edge("grandchild_1", END) grandchild. add_edge("grandchild_1", END)  grandchild_graph = grandchild.compile() grandchild_graph = grandchild. compile()  # Child graph # Child graphclass ChildState(TypedDict): class  ChildState(TypedDict): my_child_key: str my_child_key: str  def call_grandchild_graph(state: ChildState) -> ChildState: def  call_grandchild_graph(state: ChildState) -> ChildState: # NOTE: parent or grandchild keys won't be accessible here # NOTE: parent or grandchild keys won't be accessible here grandchild_graph_input = {"my_grandchild_key": state["my_child_key"]} # (1)! grandchild_graph_input ={"my_grandchild_key": state["my_child_key"]}# (1)! grandchild_graph_output = grandchild_graph.invoke(grandchild_graph_input) grandchild_graph_output = grandchild_graph. invoke(grandchild_graph_input) return {"my_child_key": grandchild_graph_output["my_grandchild_key"] + " today?"} # (2)! return{"my_child_key": grandchild_graph_output["my_grandchild_key"] + " today?"}# (2)!  child = StateGraph(ChildState) child = StateGraph(ChildState)child.add_node("child_1", call_grandchild_graph) # (3)! child. add_node("child_1", call_grandchild_graph)# (3)!child.add_edge(START, "child_1") child. add_edge(START, "child_1")child.add_edge("child_1", END) child. add_edge("child_1", END)child_graph = child.compile() child_graph = child. compile()  # Parent graph # Parent graphclass ParentState(TypedDict): class  ParentState(TypedDict): my_key: str my_key: str  def parent_1(state: ParentState) -> ParentState: def  parent_1(state: ParentState) -> ParentState: # NOTE: child or grandchild keys won't be accessible here # NOTE: child or grandchild keys won't be accessible here return {"my_key": "hi " + state["my_key"]} return{"my_key": "hi " + state["my_key"]}  def parent_2(state: ParentState) -> ParentState: def  parent_2(state: ParentState) -> ParentState: return {"my_key": state["my_key"] + " bye!"} return{"my_key": state["my_key"] +" bye!"}  def call_child_graph(state: ParentState) -> ParentState: def  call_child_graph(state: ParentState) -> ParentState: child_graph_input = {"my_child_key": state["my_key"]} # (4)! child_graph_input ={"my_child_key": state["my_key"]}# (4)! child_graph_output = child_graph.invoke(child_graph_input) child_graph_output = child_graph. invoke(child_graph_input) return {"my_key": child_graph_output["my_child_key"]} # (5)! return{"my_key": child_graph_output["my_child_key"]}# (5)!  parent = StateGraph(ParentState) parent = StateGraph(ParentState)parent.add_node("parent_1", parent_1) parent. add_node("parent_1", parent_1)parent.add_node("child", call_child_graph) # (6)! parent. add_node("child", call_child_graph)# (6)!parent.add_node("parent_2", parent_2) parent. add_node("parent_2", parent_2)  parent.add_edge(START, "parent_1") parent. add_edge(START, "parent_1")parent.add_edge("parent_1", "child") parent. add_edge("parent_1", "child")parent.add_edge("child", "parent_2") parent. add_edge("child", "parent_2")parent.add_edge("parent_2", END) parent. add_edge("parent_2", END)  parent_graph = parent.compile() parent_graph = parent. compile()  for chunk in parent_graph.stream({"my_key": "Bob"}, subgraphs=True): for chunk in parent_graph. stream({"my_key": "Bob"}, subgraphs = True): print(chunk) print(chunk)
```

1. 我们正在将状态从子状态通道（`my_child_key`）转换为孙状态通道（`my_grandchild_key`）
2. 我们正在将状态从孙状态通道（`my_grandchild_key`）转换回子状态通道（`my_child_key`）
3. 我们在这里传递一个函数，而不仅仅是编译后的图（`grandchild_graph`）
4. 我们正在将状态从父状态通道（`my_key`）转换为子状态通道（`my_child_key`）
5. 我们正在将状态从子状态通道（`my_child_key`）转换回父状态通道（`my_key`）
6. 我们在这里传递一个函数，而不仅仅是编译后的图（`child_graph`）

```
((), {'parent_1': {'my_key': 'hi Bob'}}) (('child:2e26e9ce-602f-862c-aa66-1ea5a4655e3b', 'child_1:781bb3b1-3971-84ce-810b-acf819a03f9c'), {'grandchild_1': {'my_grandchild_key': 'hi Bob, how are you'}}) (('child:2e26e9ce-602f-862c-aa66-1ea5a4655e3b',), {'child_1': {'my_child_key': 'hi Bob, how are you today?'}}) ((), {'child': {'my_key': 'hi Bob, how are you today?'}}) ((), {'parent_2': {'my_key': 'hi Bob, how are you today? bye!'}}) 
```

## 添加持久化[¶](#add-persistence "Permanent link")

您只需要**在编译父图时提供检查点（checkpointer）**。LangGraph 将自动将检查点传播到子图。

*API 参考： [START](https://github.langchain.ac.cn/langgraph/reference/constants/#langgraph.constants.START) | [StateGraph](https://github.langchain.ac.cn/langgraph/reference/graphs/#langgraph.graph.state.StateGraph) | [InMemorySaver](https://github.langchain.ac.cn/langgraph/reference/checkpoints/#langgraph.checkpoint.memory.InMemorySaver)*

```
from langgraph.graph import START, StateGraph from  langgraph.graph  import START, StateGraphfrom langgraph.checkpoint.memory import InMemorySaver from  langgraph.checkpoint.memory  import InMemorySaver from typing_extensions import TypedDict from  typing_extensions  import TypedDict  class State(TypedDict): class  State(TypedDict): foo: str foo: str  # Subgraph # Subgraph  def subgraph_node_1(state: State): def  subgraph_node_1(state: State): return {"foo": state["foo"] + "bar"} return{"foo": state["foo"] + "bar"}  subgraph_builder = StateGraph(State) subgraph_builder = StateGraph(State)subgraph_builder.add_node(subgraph_node_1) subgraph_builder. add_node(subgraph_node_1)subgraph_builder.add_edge(START, "subgraph_node_1") subgraph_builder. add_edge(START, "subgraph_node_1")subgraph = subgraph_builder.compile() subgraph = subgraph_builder. compile()  # Parent graph # Parent graph  builder = StateGraph(State) builder = StateGraph(State)builder.add_node("node_1", subgraph) builder. add_node("node_1", subgraph)builder.add_edge(START, "node_1") builder. add_edge(START, "node_1")  checkpointer = InMemorySaver() checkpointer = InMemorySaver()graph = builder.compile(checkpointer=checkpointer) graph = builder. compile(checkpointer = checkpointer)
```

如果您希望子图**拥有自己的内存**，您可以在编译时设置 `with checkpointer=True`。这在[多智能体](../../concepts/multi_agent/)系统中很有用，如果您希望智能体能够跟踪其内部消息历史记录。

```
subgraph_builder = StateGraph(...) subgraph_builder = StateGraph(...)subgraph = subgraph_builder.compile(checkpointer=True) subgraph = subgraph_builder. compile(checkpointer = True)
```

## 查看子图状态[¶](#view-subgraph-state "Permanent link")

当您启用[持久化](../../concepts/persistence/)后，您可以通过 `graph.get_state(config)` [检查图的状态](../../concepts/persistence/#checkpoints)（检查点）。要查看子图的状态，您可以使用 `graph.get_state(config, subgraphs=True)`。

**仅**在中断时可用

子图状态只能在**子图被中断时**查看。一旦您恢复图的运行，您将无法访问子图状态。

 查看中断的子图状态

```
from langgraph.graph import START, StateGraph from  langgraph.graph  import START, StateGraphfrom langgraph.checkpoint.memory import InMemorySaver from  langgraph.checkpoint.memory  import InMemorySaverfrom langgraph.types import interrupt, Command from  langgraph.types  import interrupt, Command from typing_extensions import TypedDict from  typing_extensions  import TypedDict  class State(TypedDict): class  State(TypedDict): foo: str foo: str  # Subgraph # Subgraph  def subgraph_node_1(state: State): def  subgraph_node_1(state: State): value = interrupt("Provide value:") value = interrupt("Provide value:") return {"foo": state["foo"] + value} return{"foo": state["foo"] + value}  subgraph_builder = StateGraph(State) subgraph_builder = StateGraph(State)subgraph_builder.add_node(subgraph_node_1) subgraph_builder. add_node(subgraph_node_1)subgraph_builder.add_edge(START, "subgraph_node_1") subgraph_builder. add_edge(START, "subgraph_node_1")  subgraph = subgraph_builder.compile() subgraph = subgraph_builder. compile()  # Parent graph # Parent graph  builder = StateGraph(State) builder = StateGraph(State)builder.add_node("node_1", subgraph) builder. add_node("node_1", subgraph)builder.add_edge(START, "node_1") builder. add_edge(START, "node_1")  checkpointer = InMemorySaver() checkpointer = InMemorySaver()graph = builder.compile(checkpointer=checkpointer) graph = builder. compile(checkpointer = checkpointer)  config = {"configurable": {"thread_id": "1"}} config ={"configurable":{"thread_id": "1"}}  graph.invoke({"foo": ""}, config) graph. invoke({"foo": ""}, config)parent_state = graph.get_state(config) parent_state = graph. get_state(config)subgraph_state = graph.get_state(config, subgraphs=True).tasks[0].state # (1)! subgraph_state = graph. get_state(config, subgraphs = True). tasks[0]. state# (1)!  # resume the subgraph # resume the subgraphgraph.invoke(Command(resume="bar"), config) graph. invoke(Command(resume = "bar"), config)
```

1. 这仅在子图被中断时可用。一旦您恢复图的运行，您将无法访问子图状态。

## 流式传输子图输出[¶](#stream-subgraph-outputs "Permanent link")

要将子图的输出包含在流式输出中，您可以在父图的 `.stream()` 方法中设置 `subgraphs=True`。这将从父图和任何子图中流式传输输出。

```
for chunk in graph.stream( for chunk in graph. stream( {"foo": "foo"}, {"foo": "foo"}, subgraphs=True, # (1)! subgraphs = True,# (1)! stream_mode="updates", stream_mode = "updates",): ): print(chunk) print(chunk)
```

1. 设置 `subgraphs=True` 以从子图中流式传输输出。

 从子图流式传输

```
 from typing_extensions import TypedDict from  typing_extensions  import TypedDictfrom langgraph.graph.state import StateGraph, START from  langgraph.graph.state  import StateGraph, START  # Define subgraph # Define subgraphclass SubgraphState(TypedDict): class  SubgraphState(TypedDict): foo: str foo: str bar: str bar: str  def subgraph_node_1(state: SubgraphState): def  subgraph_node_1(state: SubgraphState): return {"bar": "bar"} return{"bar": "bar"}  def subgraph_node_2(state: SubgraphState): def  subgraph_node_2(state: SubgraphState): # note that this node is using a state key ('bar') that is only available in the subgraph # note that this node is using a state key ('bar') that is only available in the subgraph # and is sending update on the shared state key ('foo') # and is sending update on the shared state key ('foo') return {"foo": state["foo"] + state["bar"]} return{"foo": state["foo"] + state["bar"]}  subgraph_builder = StateGraph(SubgraphState) subgraph_builder = StateGraph(SubgraphState)subgraph_builder.add_node(subgraph_node_1) subgraph_builder. add_node(subgraph_node_1)subgraph_builder.add_node(subgraph_node_2) subgraph_builder. add_node(subgraph_node_2)subgraph_builder.add_edge(START, "subgraph_node_1") subgraph_builder. add_edge(START, "subgraph_node_1")subgraph_builder.add_edge("subgraph_node_1", "subgraph_node_2") subgraph_builder. add_edge("subgraph_node_1", "subgraph_node_2")subgraph = subgraph_builder.compile() subgraph = subgraph_builder. compile()  # Define parent graph # Define parent graphclass ParentState(TypedDict): class  ParentState(TypedDict): foo: str foo: str  def node_1(state: ParentState): def  node_1(state: ParentState): return {"foo": "hi! " + state["foo"]} return{"foo":"hi! " + state["foo"]}  builder = StateGraph(ParentState) builder = StateGraph(ParentState)builder.add_node("node_1", node_1) builder. add_node("node_1", node_1)builder.add_node("node_2", subgraph) builder. add_node("node_2", subgraph)builder.add_edge(START, "node_1") builder. add_edge(START, "node_1")builder.add_edge("node_1", "node_2") builder. add_edge("node_1", "node_2")graph = builder.compile() graph = builder. compile()  for chunk in graph.stream( for chunk in graph. stream( {"foo": "foo"}, {"foo": "foo"}, stream_mode="updates", stream_mode = "updates", subgraphs=True, # (1)! subgraphs = True,# (1)!): ): print(chunk) print(chunk)
```

1. 设置 `subgraphs=True` 以从子图中流式传输输出。

``` ((), {'node\_1': {'foo': 'hi! foo'}}) (('node\_2:e58e5673-a661-ebb0-70d4-e298a7fc28b7',), {'subgraph\_node\_1': {'bar': 'bar'}}) (('node\_2:e58e5673-a661-ebb0-70d4-e298a7fc28b7',), {'subgraph\_node\_2': {'foo': 'hi! foobar'}}) ((), {'node\_2': {'foo': 'hi! foobar'}})