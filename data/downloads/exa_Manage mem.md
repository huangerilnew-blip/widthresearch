# Manage memory

**URL**:
https://langchain-ai.github.io/langgraph/how-tos/memory/

## 元数据
- 发布日期: 2025-01-01T00:00:00+00:00

## 完整内容
---
Memory - Docs by LangChain
[Skip to main content] 
[Docs by LangChainhome page![light logo]![dark logo]] 
Open source
Search...
CtrlK
Search...
Navigation
Capabilities
Memory
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
* Functional API
* [
Runtime
] 
On this page
* [Add short-term memory] 
* [Use in production] 
* [Use in subgraphs] 
* [Add long-term memory] 
* [Use in production] 
* [Use semantic search] 
* [Manage short-term memory] 
* [Trim messages] 
* [Delete messages] 
* [Summarize messages] 
* [Manage checkpoints] 
* [View thread state] 
* [View the history of the thread] 
* [Delete all checkpoints for a thread] 
* [Database management] 
[Capabilities] 
# Memory
Copy page
Copy page
AI applications need[memory] to share context across multiple interactions. In LangGraph, you can add two types of memory:
* [Add short-term memory] as a part of your agent’s[state] to enable multi-turn conversations.
* [Add long-term memory] to store user-specific or application-level data across sessions.## [​
] 
Add short-term memory
**Short-term**memory (thread-level[persistence]) enables agents to track multi-turn conversations. To add short-term memory:
Copy
```
`fromlanggraph.checkpoint.memoryimportInMemorySaverfromlanggraph.graphimportStateGraphcheckpointer=InMemorySaver()builder=StateGraph(...)graph=builder.compile(checkpointer=checkpointer)graph.invoke({"messages": [{"role":"user","content":"hi! i am Bob"}]},{"configurable": {"thread\_id":"1"}},)`
```
### [​
] 
Use in production
In production, use a checkpointer backed by a database:
Copy
```
`fromlanggraph.checkpoint.postgresimportPostgresSaverDB\_URI="postgresql://postgres:postgres@localhost:5442/postgres?sslmode=disable"withPostgresSaver.from\_conn\_string(DB\_URI)ascheckpointer:builder=StateGraph(...)graph=builder.compile(checkpointer=checkpointer)`
```
Example: using Postgres checkpointer
Copy
```
`pip install -U "psycopg[binary,pool]" langgraph langgraph-checkpoint-postgres`
```
You need to call`checkpointer.setup()`the first time you’re using Postgres checkpointer
* Sync
* Async
Copy
```
`fromlangchain.chat\_modelsimportinit\_chat\_modelfromlanggraph.graphimportStateGraph, MessagesState,STARTfromlanggraph.checkpoint.postgresimportPostgresSavermodel=init\_chat\_model(model="claude-haiku-4-5-20251001")DB\_URI="postgresql://postgres:postgres@localhost:5442/postgres?sslmode=disable"withPostgresSaver.from\_conn\_string(DB\_URI)ascheckpointer:# checkpointer.setup()defcall\_model(state: MessagesState):response=model.invoke(state["messages"])return{"messages": response}builder=StateGraph(MessagesState)builder.add\_node(call\_model)builder.add\_edge(START,"call\_model")graph=builder.compile(checkpointer=checkpointer)config={"configurable": {"thread\_id":"1"}}forchunkingraph.stream({"messages": [{"role":"user","content":"hi! I'm bob"}]},config,stream\_mode="values"):chunk["messages"][-1].pretty\_print()forchunkingraph.stream({"messages": [{"role":"user","content":"what's my name?"}]},config,stream\_mode="values"):chunk["messages"][-1].pretty\_print()`
```
Copy
```
`fromlangchain.chat\_modelsimportinit\_chat\_modelfromlanggraph.graphimportStateGraph, MessagesState,STARTfromlanggraph.checkpoint.postgres.aioimportAsyncPostgresSavermodel=init\_chat\_model(model="claude-haiku-4-5-20251001")DB\_URI="postgresql://postgres:postgres@localhost:5442/postgres?sslmode=disable"asyncwithAsyncPostgresSaver.from\_conn\_string(DB\_URI)ascheckpointer:# await checkpointer.setup()asyncdefcall\_model(state: MessagesState):response=awaitmodel.ainvoke(state["messages"])return{"messages": response}builder=StateGraph(MessagesState)builder.add\_node(call\_model)builder.add\_edge(START,"call\_model")graph=builder.compile(checkpointer=checkpointer)config={"configurable": {"thread\_id":"1"}}asyncforchunkingraph.astream({"messages": [{"role":"user","content":"hi! I'm bob"}]},config,stream\_mode="values"):chunk["messages"][-1].pretty\_print()asyncforchunkingraph.astream({"messages": [{"role":"user","content":"what's my name?"}]},config,stream\_mode="values"):chunk["messages"][-1].pretty\_print()`
```
Example: using MongoDB checkpointer
Copy
```
`pip install -U pymongo langgraph langgraph-checkpoint-mongodb`
```
**Setup**To use the[MongoDB checkpointer], you will need a MongoDB cluster. Follow[this guide] to create a cluster if you don’t already have one.
* Sync
* Async
Copy
```
`fromlangchain.chat\_modelsimportinit\_chat\_modelfromlanggraph.graphimportStateGraph, MessagesState,STARTfromlanggraph.checkpoint.mongodbimportMongoDBSavermodel=init\_chat\_model(model="claude-haiku-4-5-20251001")DB\_URI="localhost:27017"withMongoDBSaver.from\_conn\_string(DB\_URI)ascheckpointer:defcall\_model(state: MessagesState):response=model.invoke(state["messages"])return{"messages": response}builder=StateGraph(MessagesState)builder.add\_node(call\_model)builder.add\_edge(START,"call\_model")graph=builder.compile(checkpointer=checkpointer)config={"configurable": {"thread\_id":"1"}}forchunkingraph.stream({"messages": [{"role":"user","content":"hi! I'm bob"}]},config,stream\_mode="values"):chunk["messages"][-1].pretty\_print()forchunkingraph.stream({"messages": [{"role":"user","content":"what's my name?"}]},config,stream\_mode="values"):chunk["messages"][-1].pretty\_print()`
```
Copy
```
`fromlangchain.chat\_modelsimportinit\_chat\_modelfromlanggraph.graphimportStateGraph, MessagesState,STARTfromlanggraph.checkpoint.mongodb.aioimportAsyncMongoDBSavermodel=init\_chat\_model(model="claude-haiku-4-5-20251001")DB\_URI="localhost:27017"asyncwithAsyncMongoDBSaver.from\_conn\_string(DB\_URI)ascheckpointer:asyncdefcall\_model(state: MessagesState):response=awaitmodel.ainvoke(state["messages"])return{"messages": response}builder=StateGraph(MessagesState)builder.add\_node(call\_model)builder.add\_edge(START,"call\_model")graph=builder.compile(checkpointer=checkpointer)config={"configurable": {"thread\_id":"1"}}asyncforchunkingraph.astream({"messages": [{"role":"user","content":"hi! I'm bob"}]},config,stream\_mode="values"):chunk["messages"][-1].pretty\_print()asyncforchunkingraph.astream({"messages": [{"role":"user","content":"what's my name?"}]},config,stream\_mode="values"):chunk["messages"][-1].pretty\_print()`
```
Example: using Redis checkpointer
Copy
```
`pip install -U langgraph langgraph-checkpoint-redis`
```
You need to call`checkpointer.setup()`the first time you’re using Redis checkpointer.
* Sync
* Async
Copy
```
`fromlangchain.chat\_modelsimportinit\_chat\_modelfromlanggraph.graphimportStateGraph, MessagesState,STARTfromlanggraph.checkpoint.redisimportRedisSavermodel=init\_chat\_model(model="claude-haiku-4-5-20251001")DB\_URI="redis://localhost:6379"withRedisSaver.from\_conn\_string(DB\_URI)ascheckpointer:# checkpointer.setup()defcall\_model(state: MessagesState):response=model.invoke(state["messages"])return{"messages": response}builder=StateGraph(MessagesState)builder.add\_node(call\_model)builder.add\_edge(START,"call\_model")graph=builder.compile(checkpointer=checkpointer)config={"configurable": {"thread\_id":"1"}}forchunkingraph.stream({"messages": [{"role":"user","content":"hi! I'm bob"}]},config,stream\_mode="values"):chunk["messages"][-1].pretty\_print()forchunkingraph.stream({"messages": [{"role":"user","content":"what's my name?"}]},config,stream\_mode="values"):chunk["messages"][-1].pretty\_print()`
```
Copy
```
`fromlangchain.chat\_modelsimportinit\_chat\_modelfromlanggraph.graphimportStateGraph, MessagesState,STARTfromlanggraph.checkpoint.redis.aioimportAsyncRedisSavermodel=init\_chat\_model(model="claude-haiku-4-5-20251001")DB\_URI="redis://localhost:6379"asyncwithAsyncRedisSaver.from\_conn\_string(DB\_URI)ascheckpointer:# await checkpointer.asetup()asyncdefcall\_model(state: MessagesState):response=awaitmodel.ainvoke(state["messages"])return{"messages": response}builder=StateGraph(MessagesState)builder.add\_node(call\_model)builder.add\_edge(START,"call\_model")graph=builder.compile(checkpointer=checkpointer)config={"configurable": {"thread\_id":"1"}}asyncforchunkingraph.astream({"messages": [{"role":"user","content":"hi! I'm bob"}]},config,stream\_mode="values"):chunk["messages"][-1].pretty\_print()asyncforchunkingraph.astream({"messages": [{"role":"user","content":"what's my name?"}]},config,stream\_mode="values"):chunk["messages"][-1].pretty\_print()`
```
### [​
] 
Use in subgraphs
If your graph contains[subgraphs], you only need to provide the checkpointer when compiling the parent graph. LangGraph will automatically propagate the checkpointer to the child subgraphs.
Copy
```
`fromlanggraph.graphimportSTART, StateGraphfromlanggraph.checkpoint.memoryimportInMemorySaverfromtypingimportTypedDictclassState(TypedDict):foo:str# Subgraphdefsubgraph\_node\_1(state: State):return{"foo": state["foo"]+"bar"}subgraph\_builder=StateGraph(State)subgraph\_builder.add\_node(subgraph\_node\_1)subgraph\_builder.add\_edge(START,"subgraph\_node\_1"


---
*数据来源: Exa搜索 | 获取时间: 2026-02-10 21:59:05*