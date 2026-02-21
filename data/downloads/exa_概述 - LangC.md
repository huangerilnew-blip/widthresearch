# 概述 - LangChain 框架

**URL**:
https://github.langchain.ac.cn/langgraph/concepts/subgraphs

## 元数据
- 发布日期: 2025-01-01T00:00:00+00:00

## 完整内容
---
概述 - LangChain 教程[跳到内容] 
**LangGraph 平台文档已迁移！**请在新的[LangChain 文档] 网站上查找 LangGraph 平台文档。[] # 子图[¶] 
子图（subgraph）是一个在另一个图中作为[节点] 使用的[图] ——这是封装概念在 LangGraph 中的应用。子图允许您构建包含多个组件的复杂系统，而这些组件本身就是图。![Subgraph] 
使用子图的一些原因包括：* 构建[多智能体系统] 
* 当您想在多个图中重用一组节点时* 当您希望不同的团队独立开发图的不同部分时，您可以将每个部分定义为一个子图。只要遵守子图的接口（输入和输出模式），父图就可以在不了解子图任何细节的情况下进行构建。添加子图时，主要的问题是父图和子图如何通信，即它们在图执行期间如何相互传递[状态] 。有两种情况：
* 父图和子图的状态[模式] 中有**共享的状态键**。在这种情况下，您可以[将子图作为父图中的一个节点包含进来] 。
```
`[]<web_link>fromlanggraph.graphimportStateGraph,MessagesState,START[]<web_link>[]<web_link># Subgraph[]<web_link>[]<web_link>defcall\_model(state:MessagesState):[]<web_link>response=model.invoke(state["messages"])[]<web_link>return{"messages":response}[]<web_link>[]<web_link>subgraph\_builder=StateGraph(State)[]<web_link>subgraph\_builder.add\_node(call\_model)[]<web_link>...[]<web_link>subgraph=subgraph\_builder.compile()[]<web_link>[]<web_link># Parent graph[]<web_link>[]<web_link>builder=StateGraph(State)[]<web_link>builder.add\_node("subgraph\_node",subgraph)[]<web_link>builder.add\_edge(START,"subgraph\_node")[]<web_link>graph=builder.compile()[]<web_link>...[]<web_link>graph.invoke({"messages":[{"role":"user","content":"hi!"}]})`
```
* 父图和子图有**不同的模式**（它们的状态[模式] 中没有共享的状态键）。在这种情况下，您必须[从父图的一个节点内部调用子图] ：当父图和子图具有不同的状态模式，并且您需要在调用子图之前或之后转换状态时，这种方法很有用。
```
`[]<web_link>fromtyping\_extensionsimportTypedDict,Annotated[]<web_link>fromlangchain\_core.messagesimportAnyMessage[]<web_link>fromlanggraph.graphimportStateGraph,MessagesState,START[]<web_link>fromlanggraph.graph.messageimportadd\_messages[]<web_link>[]<web_link>classSubgraphMessagesState(TypedDict):[]<web_link>subgraph\_messages:Annotated[list[AnyMessage],add\_messages][]<web_link>[]<web_link># Subgraph[]<web_link>[]<web_link>defcall\_model(state:SubgraphMessagesState):[]<web_link>response=model.invoke(state["subgraph\_messages"])[]<web_link>return{"subgraph\_messages":response}[]<web_link>[]<web_link>subgraph\_builder=StateGraph(SubgraphMessagesState)[]<web_link>subgraph\_builder.add\_node("call\_model\_from\_subgraph",call\_model)[]<web_link>subgraph\_builder.add\_edge(START,"call\_model\_from\_subgraph")[]<web_link>...[]<web_link>subgraph=subgraph\_builder.compile()[]<web_link>[]<web_link># Parent graph[]<web_link>[]<web_link>defcall\_subgraph(state:MessagesState):[]<web_link>response=subgraph.invoke({"subgraph\_messages":state["messages"]})[]<web_link>return{"messages":response["subgraph\_messages"]}[]<web_link>[]<web_link>builder=StateGraph(State)[]<web_link>builder.add\_node("subgraph\_node",call\_subgraph)[]<web_link>builder.add\_edge(START,"subgraph\_node")[]<web_link>graph=builder.compile()[]<web_link>...[]<web_link>graph.invoke({"messages":[{"role":"user","content":"hi!"}]})`
```
回到顶


---
*数据来源: Exa搜索 | 获取时间: 2026-02-21 19:56:59*