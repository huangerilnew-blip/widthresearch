# Use the Graph API

**URL**:
https://langchain-ai.github.io/langgraph/how-tos/graph-api/

## 元数据
- 发布日期: 2025-04-14T00:00:00+00:00

## 完整内容
---
Graph API overview - Docs by LangChain
[Skip to main content] 
[Docs by LangChainhome page![light logo]![dark logo]] 
Open source
Search...
CtrlK
Search...
Navigation
Graph API
Graph API overview
[Deep Agents
] [LangChain
] [LangGraph
] [Integrations
] [Learn
] [Reference
] [Contribute
] 
Python
* [
Overview
] 
##### Get started
* [
Install
] 
* [
Quickstart
] 
* [
Local server
] 
* [
Changelog
] 
* [
Thinking in LangGraph
] 
* [
Workflows + agents
] 
##### Capabilities
* [
Persistence
] 
* [
Durable execution
] 
* [
Streaming
] 
* [
Interrupts
] 
* [
Time travel
] 
* [
Memory
] 
* [
Subgraphs
] 
##### Production
* [
Application structure
] 
* [
Test
] 
* [
LangSmith Studio
] 
* [
Agent Chat UI
] 
* [
LangSmith Deployment
] 
* [
LangSmith Observability
] 
##### LangGraph APIs
* Graph API
* [
Choosing APIs
] 
* [
Graph API
] 
* [
Use the graph API
] 
* Functional API
* [
Runtime
] 
On this page
* [Graphs] 
* [StateGraph] 
* [Compiling your graph] 
* [State] 
* [Schema] 
* [Multiple schemas] 
* [Reducers] 
* [Default reducer] 
* [Overwrite] 
* [Working with messages in graph state] 
* [Why use messages?] 
* [Using messages in your graph] 
* [Serialization] 
* [MessagesState] 
* [Nodes] 
* [START node] 
* [END node] 
* [Node caching] 
* [Edges] 
* [Normal edges] 
* [Conditional edges] 
* [Entry point] 
* [Conditional entry point] 
* [Send] 
* [Command] 
* [When should I use command instead of conditional edges?] 
* [Navigating to a node in a parent graph] 
* [Using inside tools] 
* [Human-in-the-loop] 
* [Graph migrations] 
* [Runtime context] 
* [Recursion limit] 
* [Accessing and handling the recursion counter] 
* [How it works] 
* [Accessing the current step counter] 
* [Proactive recursion handling] 
* [Proactive vs reactive approaches] 
* [Other available metadata] 
* [Visualization] 
[LangGraph APIs] 
[Graph API] 
# Graph API overview
Copy page
Copy page
## [​
] 
Graphs
At its core, LangGraph models agent workflows as graphs. You define the behavior of your agents using three key components:
1. [`State`]: A shared data structure that represents the current snapshot of your application. It can be any data type, but is typically defined using a shared state schema.
2. [`Nodes`]: Functions that encode the logic of your agents. They receive the current state as input, perform some computation or side-effect, and return an updated state.
3. [`Edges`]: Functions that determine which`Node`to execute next based on the current state. They can be conditional branches or fixed transitions.By composing`Nodes`and`Edges`, you can create complex, looping workflows that evolve the state over time. The real power, though, comes from how LangGraph manages that state.To emphasize:`Nodes`and`Edges`are nothing more than functions –they can contain an LLM or just good ol’ code.In short:*nodes do the work, edges tell what to do next*.LangGraph’s underlying graph algorithm uses[message passing] to define a general program. When a Node completes its operation, it sends messages along one or more edges to other node(s). These recipient nodes then execute their functions, pass the resulting messages to the next set of nodes, and the process continues. Inspired by Google’s[Pregel] system, the program proceeds in discrete “super-steps.”A super-step can be considered a single iteration over the graph nodes. Nodes that run in parallel are part of the same super-step, while nodes that run sequentially belong to separate super-steps. At the start of graph execution, all nodes begin in an`inactive`state. A node becomes`active`when it receives a new message (state) on any of its incoming edges (or “channels”). The active node then runs its function and responds with updates. At the end of each super-step, nodes with no incoming messages vote to`halt`by marking themselves as`inactive`. The graph execution terminates when all nodes are`inactive`and no messages are in transit.### [​
] 
StateGraph
The[`StateGraph`] class is the main graph class to use. This is parameterized by a user defined`State`object.### [​
] 
Compiling your graph
To build your graph, you first define the[state], you then add[nodes] and[edges], and then you compile it. What exactly is compiling your graph and why is it needed?Compiling is a pretty simple step. It provides a few basic checks on the structure of your graph (no orphaned nodes, etc). It is also where you can specify runtime args like[checkpointers] and breakpoints. You compile your graph by just calling the`.compile`method:
Copy
```
`graph=graph\_builder.compile(...)`
```
You**MUST**compile your graph before you can use it.
## [​
] 
State
The first thing you do when you define a graph is define the`State`of the graph. The`State`consists of the[schema of the graph] as well as[`reducer`functions] which specify how to apply updates to the state. The schema of the`State`will be the input schema to all`Nodes`and`Edges`in the graph, and can be either a`TypedDict`or a`Pydantic`model. All`Nodes`will emit updates to the`State`which are then applied using the specified`reducer`function.### [​
] 
Schema
The main documented way to specify the schema of a graph is by using a[`TypedDict`]. If you want to provide default values in your state, use a[`dataclass`]. We also support using a Pydantic[`BaseModel`] as your graph state if you want recursive data validation (though note that Pydantic is less performant than a`TypedDict`or`dataclass`).By default, the graph will have the same input and output schemas. If you want to change this, you can also specify explicit input and output schemas directly. This is useful when you have a lot of keys, and some are explicitly for input and others for output. See the[guide] for more information.#### [​
] 
Multiple schemas
Typically, all graph nodes communicate with a single schema. This means that they will read and write to the same state channels. But, there are cases where we want more control over this:
* Internal nodes can pass information that is not required in the graph’s input / output.
* We may also want to use different input / output schemas for the graph. The output might, for example, only contain a single relevant output key.It is possible to have nodes write to private state channels inside the graph for internal node communication. We can simply define a private schema,`PrivateState`.It is also possible to define explicit input and output schemas for a graph. In these cases, we define an “internal” schema that contains*all*keys relevant to graph operations. But, we also define`input`and`output`schemas that are sub-sets of the “internal” schema to constrain the input and output of the graph. See[this guide] for more detail.Let’s look at an example:
Copy
```
`classInputState(TypedDict):user\_input:strclassOutputState(TypedDict):graph\_output:strclassOverallState(TypedDict):foo:struser\_input:strgraph\_output:strclassPrivateState(TypedDict):bar:strdefnode\_1(state: InputState) -&gt; OverallState:# Write to OverallStatereturn{"foo": state["user\_input"]+" name"}defnode\_2(state: OverallState) -&gt; PrivateState:# Read from OverallState, write to PrivateStatereturn{"bar": state["foo"]+" is"}defnode\_3(state: PrivateState) -&gt; OutputState:# Read from PrivateState, write to OutputStatereturn{"graph\_output": state["bar"]+" Lance"}builder=StateGraph(OverallState,input\_schema=InputState,output\_schema=OutputState)builder.add\_node("node\_1", node\_1)builder.add\_node("node\_2", node\_2)builder.add\_node("node\_3", node\_3)builder.add\_edge(START,"node\_1")builder.add\_edge("node\_1","node\_2")builder.add\_edge("node\_2","node\_3")builder.add\_edge("node\_3",END)graph=builder.compile()graph.invoke({"user\_input":"My"})# {'graph\_output': 'My name is Lance'}`
```
There are two subtle and important points to note here:
1. We pass`state: InputState`as the input schema to`node\_1`. But, we write out to`foo`, a channel in`OverallState`. How can we write out to a state channel that is not included in the input schema? This is because a node*can write to any state channel in the graph state.*The graph state is the union of the state channels defined at initialization, which includes`OverallState`and the filters`InputState`and`OutputState`.
2. We initialize the graph with:
Copy
```
`StateGraph(OverallState,input\_schema=InputState,output\_schema=OutputState)`
```
So, how can we write to`PrivateState`in`node\_2`? How does the graph gain access to this schema if it was not passed in the`StateGraph`initialization?We can do this because`\_nodes`can also declare additional state`channels\_`as long as the state schema definition exists. In this case, the`PrivateState`schema is defined, so we can add`bar`as a new state channel in the graph and write to it.### [​
] 
Reducers
Reducers are key to understanding how updates from nodes are applied to the`State`. Each key in the`State`has its own independent reducer function. If no reducer function is explicitly specified then it is assumed that all updates to that key should override it. There are a few different types of reducers, starting with the default


---
*数据来源: Exa搜索 | 获取时间: 2026-02-19 20:08:35*