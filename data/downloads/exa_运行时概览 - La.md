# 运行时概览 - LangChain 框架

**URL**:
https://langgraph.com.cn/concepts/pregel/index.html

## 元数据
- 发布日期: 2025-01-01T00:00:00+00:00

## 完整内容
---
[跳到内容] 

# LangGraph 运行时 [¶] 

[Pregel] 实现了 LangGraph 的运行时，管理 LangGraph 应用程序的执行。

编译一个 [StateGraph] 或创建一个 [entrypoint] 会生成一个 [Pregel] 实例，该实例可以通过输入进行调用。

本指南从高层解释了运行时，并提供了直接使用 Pregel 实现应用程序的说明。

> **注意：** [Pregel] 运行时以 [Google 的 Pregel 算法] 命名，该算法描述了一种使用图进行大规模并行计算的有效方法。

## 概览 [¶] 

在 LangGraph 中，Pregel 将 [**执行器（actors）**] 和 **通道（channels）** 组合成一个单一的应用程序。 **执行器** 从通道读取数据并向通道写入数据。Pregel 按照 **Pregel 算法**/ **批量同步并行（Bulk Synchronous Parallel）** 模型，将应用程序的执行组织成多个步骤。

每个步骤包括三个阶段

- **规划**：确定在此步骤中要执行哪些 **执行器**。例如，在第一步中，选择订阅特殊 **输入** 通道的 **执行器**；在后续步骤中，选择订阅前一步骤中更新的通道的 **执行器**。
- **执行**：并行执行所有选定的 **执行器**，直到全部完成，或一个失败，或达到超时。在此阶段，通道更新对执行器不可见，直到下一个步骤。
- **更新**：用此步骤中 **执行器** 写入的值更新通道。

重复此过程，直到没有 **执行器** 被选中执行，或达到最大步骤数。

## 执行器 [¶] 

一个 **执行器** 是一个 `PregelNode`。它订阅通道，从它们读取数据，并向它们写入数据。它可以被认为是 Pregel 算法中的一个 **执行器**。 `PregelNodes` 实现了 LangChain 的 Runnable 接口。

## 通道 [¶] 

通道用于在执行器（PregelNodes）之间进行通信。每个通道都有一个值类型、一个更新类型和一个更新函数——该函数接受一系列更新并修改存储的值。通道可以用于将数据从一个链发送到另一个链，或在未来的步骤中将数据从一个链发送到自身。LangGraph 提供了许多内置通道：

- [LastValue]: 默认通道，存储发送到通道的最后一个值，适用于输入和输出值，或将数据从一个步骤发送到下一个步骤。
- [Topic]: 可配置的 PubSub 主题，适用于在 **执行器** 之间发送多个值，或用于累积输出。可以配置为重复数据删除或在多个步骤中累积值。
- [BinaryOperatorAggregate]: 存储一个持久值，通过对当前值和发送到通道的每个更新应用二元运算符进行更新，适用于在多个步骤中计算聚合；例如， `total = BinaryOperatorAggregate(int, operator.add)`

## 示例 [¶] 

虽然大多数用户会通过 [StateGraph] API 或 [entrypoint] 装饰器与 Pregel 交互，但也可以直接与 Pregel 交互。

下面是一些不同的示例，让您了解 Pregel API 的用法。

单节点多节点主题BinaryOperatorAggregate循环

```
fromlanggraph.channelsimport EphemeralValuefromlanggraph.pregelimport Pregel, Channelnode1 = (Channel.subscribe_to("a")| (lambda x: x + x)| Channel.write_to("b"))app = Pregel(nodes={"node1": node1},channels={"a": EphemeralValue(str),"b": EphemeralValue(str),},input_channels=["a"],output_channels=["b"],)app.invoke({"a": "foo"})
```

```
{'b': 'foofoo'}

```

```
fromlanggraph.channelsimport LastValue, EphemeralValuefromlanggraph.pregelimport Pregel, Channelnode1 = (Channel.subscribe_to("a")| (lambda x: x + x)| Channel.write_to("b"))node2 = (Channel.subscribe_to("b")| (lambda x: x + x)| Channel.write_to("c"))app = Pregel(nodes={"node1": node1, "node2": node2},channels={"a": EphemeralValue(str),"b": LastValue(str),"c": EphemeralValue(str),},input_channels=["a"],output_channels=["b", "c"],)app.invoke({"a": "foo"})
```

```
{'b': 'foofoo', 'c': 'foofoofoofoo'}

```

```
fromlanggraph.channelsimport EphemeralValue, Topicfromlanggraph.pregelimport Pregel, Channelnode1 = (Channel.subscribe_to("a")| (lambda x: x + x)| {"b": Channel.write_to("b"),"c": Channel.write_to("c")})node2 = (Channel.subscribe_to("b")| (lambda x: x + x)| {"c": Channel.write_to("c"),})app = Pregel(nodes={"node1": node1, "node2": node2},channels={"a": EphemeralValue(str),"b": EphemeralValue(str),"c": Topic(str, accumulate=True),},input_channels=["a"],output_channels=["c"],)app.invoke({"a": "foo"})
```

```
{'c': ['foofoo', 'foofoofoofoo']}
```

此示例演示了如何使用 BinaryOperatorAggregate 通道来实现一个 reducer。

```
fromlanggraph.channelsimport EphemeralValue, BinaryOperatorAggregatefromlanggraph.pregelimport Pregel, Channelnode1 = (Channel.subscribe_to("a")| (lambda x: x + x)| {"b": Channel.write_to("b"),"c": Channel.write_to("c")})node2 = (Channel.subscribe_to("b")| (lambda x: x + x)| {"c": Channel.write_to("c"),})defreducer(current, update):if current:return current + " | " + updateelse:return updateapp = Pregel(nodes={"node1": node1, "node2": node2},channels={"a": EphemeralValue(str),"b": EphemeralValue(str),"c": BinaryOperatorAggregate(str, operator=reducer),},input_channels=["a"],output_channels=["c"],)app.invoke({"a": "foo"})
```

此示例演示了如何在图中引入一个循环，通过让一个链写入它订阅的通道。执行将继续，直到一个 None 值被写入通道。

```
fromlanggraph.channelsimport EphemeralValuefromlanggraph.pregelimport Pregel, Channel, ChannelWrite, ChannelWriteEntryexample_node = (Channel.subscribe_to("value")| (lambda x: x + x if len(x) < 10 else None)| ChannelWrite(writes=[ChannelWriteEntry(channel="value", skip_none=True)]))app = Pregel(nodes={"example_node": example_node},channels={"value": EphemeralValue(str),},input_channels=["value"],output_channels=["value"],)app.invoke({"value": "a"})
```

```
{'value': 'aaaaaaaaaaaaaaaa'}
```

## 高级 API [¶] 

LangGraph 提供了两种创建 Pregel 应用程序的高级 API： [StateGraph (Graph API)] 和 [函数式 API] 。

StateGraph (Graph API)函数式 API

[StateGraph (Graph API)] 是一种更高级别的抽象，它简化了 Pregel 应用程序的创建。它允许您定义节点和边的图。当您编译图时，StateGraph API 会自动为您创建 Pregel 应用程序。

```
fromtypingimport TypedDict, Optionalfromlanggraph.constantsimport STARTfromlanggraph.graphimport StateGraphclassEssay(TypedDict):topic: strcontent: Optional[str]score: Optional[float]defwrite_essay(essay: Essay):return {"content": f"Essay about {essay['topic']}",}defscore_essay(essay: Essay):return {"score": 10}builder = StateGraph(Essay)builder.add_node(write_essay)builder.add_node(score_essay)builder.add_edge(START, "write_essay")# Compile the graph. # This will return a Pregel instance.graph = builder.compile()
```

编译后的 Pregel 实例将与节点和通道列表相关联。您可以通过打印它们来检查节点和通道。

```
print(graph.nodes)
```

您将看到类似以下内容

```
{'__start__': <langgraph.pregel.read.PregelNode at 0x7d05e3ba1810>, 'write_essay': <langgraph.pregel.read.PregelNode at 0x7d05e3ba14d0>, 'score_essay': <langgraph.pregel.read.PregelNode at 0x7d05e3ba1710>}
```

```
print(graph.channels)
```

您应该会看到类似以下内容

```
{'topic': <langgraph.channels.last_value.LastValue at 0x7d05e3294d80>, 'content': <langgraph.channels.last_value.LastValue at 0x7d05e3295040>, 'score': <langgraph.channels.last_value.LastValue at 0x7d05e3295980>, '__start__': <langgraph.channels.ephemeral_value.EphemeralValue at 0x7d05e3297e00>, 'write_essay': <langgraph.channels.ephemeral_value.EphemeralValue at 0x7d05e32960c0>, 'score_essay': <langgraph.channels.ephemeral_value.EphemeralValue at 0x7d05e2d8ab80>, 'branch:__start__:__self__:write_essay': <langgraph.channels.ephemeral_value.EphemeralValue at 0x7d05e32941c0>, 'branch:__start__:__self__:score_essay': <langgraph.channels.ephemeral_value.EphemeralValue at 0x7d05e2d88800>, 'branch:write_essay:__self__:write_essay': <langgraph.channels.ephemeral_value.EphemeralValue at 0x7d05e3295ec0>, 'branch:write_essay:__self__:score_essay': <langgraph.channels.ephemeral_value.EphemeralValue at 0x7d05e2d8ac00>, 'branch:score_essay:__self__:write_essay': <langgraph.channels.ephemeral_value.EphemeralValue at 0x7d05e2d89700>, 'branch:score_essay:__self__:score_essay': <langgraph.channels.ephemeral_value.EphemeralValue at 0x7d05e2d8b400>, 'start:write_essay': <langgraph.channels.ephemeral_value.EphemeralValue at 0x7d05e2d8b280>}
```

在 [函数式 API] 中，您可以使用 [`entrypoint`] 来创建 Pregel 应用程序。 `entrypoint` 装饰器允许您定义一个接受输入并返回输出的函数。

```
fromtypingimport TypedDict, Optionalfromlanggraph.checkpoint.memoryimport InMemorySaverfromlanggraph.funcimport entrypointclassEssay(TypedDict):topic: strcontent: Optional[str]score: Optional[float]checkpointer = InMemorySaver()@entrypoint(checkpointer=checkpointer)defwrite_essay(essay: Essay):return {"content": f"Essay about {essay['topic']}",}print("Nodes: ")print(write_essay.nodes)print("Channels: ")print(write_essay.channels)
```

```
Nodes: {'write_essay': <langgraph.pregel.read.PregelNode object at 0x7d05e2f9aad0>}Channels: {'__start__': <langgraph.channels.ephemeral_value.EphemeralValue object at 0x7d05e2c906c0>, '__end__': <langgraph.channels.last_value.LastValue object at 0x7d05e2c90c40>, '__previous__': <langgraph.channels.last_value.LastValue object at 0x7d05e1007280>}
```

返回顶部


---
*数据来源: Exa搜索 | 获取时间: 2026-02-24 22:27:43*