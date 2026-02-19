# 思维导图备注

**URL**:
https://www.bookstack.cn/read/langgraph-0.2.73-en/deceb9d0769000c9.md

## 元数据
- 发布日期: 2026-02-19T20:52:34.089578

## 完整内容
---
Guides - How-to Guides - 《LangGraph v0.2.73 Documentation》 - 书栈网 · BookStack

# How-to Guides

How-to Guides

LangGraph

- Prebuilt ReAct Agent
- Other
- State Management
- Multi-agent
- Subgraphs
- Tool calling
- Streaming
- Time Travel
- Human-in-the-loop
- Memory
- Persistence
- Fine-grained Control
- Graph API Basics

LangGraph Platform

- LangGraph Studio
- Cron Jobs
- Webhooks
- Double-texting
- Human-in-the-loop
- Streaming
- Runs
- Threads
- Assistants
- Authentication & Access Control
- Deployment
- Application Structure

Troubleshooting

LangGraph Platform Troubleshooting

# How-to Guides

Here you’ll find answers to “How do I…?” types of questions. These guides are goal-oriented and concrete; they’re meant to help you complete a specific task. For conceptual explanations see the [Conceptual guide]. For end-to-end walk-throughs see [Tutorials]. For comprehensive descriptions of every class and function see the [API Reference].

## LangGraph

### Graph API Basics

- [How to visualize your graph] 
- [How to create and control loops with recursion limits] 
- [How to create branches for parallel execution] 
- [How to create a sequence of steps] 
- [How to update graph state from nodes] 

### Fine-grained Control

These guides demonstrate LangGraph features that grant fine-grained control over the execution of your graph.

- [How to return state before hitting recursion limit] 
- [How to add node retries] 
- [How to add runtime configuration to your graph] 
- [How to update state and jump to nodes in graphs and subgraphs] 
- [How to create map-reduce branches for parallel execution] 

### Persistence

[LangGraph Persistence] makes it easy to persist state across graph runs (per-thread persistence) and across threads (cross-thread persistence). These how-to guides show how to add persistence to your graph.

- [How to create a custom checkpointer using Redis] 
- [How to use MongoDB checkpointer for persistence] 
- [How to use Postgres checkpointer for persistence] 
- [How to add cross-thread persistence to your graph] 
- [How to add thread-level persistence to a subgraph] 
- [How to add thread-level persistence to your graph] 

See the below guides for how-to add persistence to your workflow using the (beta) [Functional API]:

- [How to add cross-thread persistence (functional API)] 
- [How to add thread-level persistence (functional API)] 

### Memory

LangGraph makes it easy to manage conversation [memory] in your graph. These how-to guides show how to implement different strategies for that.

- [How to use semantic search for long-term memory] 
- [How to add long-term memory (cross-thread)] 
- [How to add summary conversation memory] 
- [How to delete messages] 
- [How to manage conversation history] 

### Human-in-the-loop

[Human-in-the-loop] functionality allows you to involve humans in the decision-making process of your graph. These how-to guides show how to implement human-in-the-loop workflows in your graph.

Key workflows:

- [How to review tool calls]: Incorporate human-in-the-loop for reviewing/editing/accepting tool call requests before they executed using the`interrupt` function.
- [How to wait for user input]: A basic example that shows how to implement a human-in-the-loop workflow in your graph using the`interrupt` function.

Other methods:

- [How to add dynamic breakpoints with NodeInterrupt]: Not recommended: Use the [interrupt function] instead.
- [How to edit graph state]: Edit graph state using`graph.update_state` method. Use this if implementing a human-in-the-loop workflow via static breakpoints.
- [How to add static breakpoints]: Use for debugging purposes. For [human-in-the-loop] workflows, we recommend the [interrupt function] instead.

See the below guides for how-to implement human-in-the-loop workflows with the (beta) [Functional API]:

- [How to review tool calls (Functional API)] 
- [How to wait for user input (Functional API)] 

### Time Travel

[Time travel] allows you to replay past actions in your LangGraph application to explore alternative paths and debug issues. These how-to guides show how to use time travel in your graph.

- [How to view and update past graph state] 

### Streaming

[Streaming] is crucial for enhancing the responsiveness of applications built on LLMs. By displaying output progressively, even before a complete response is ready, streaming significantly improves user experience (UX), particularly when dealing with the latency of LLMs.

- [How to disable streaming for models that don’t support it] 
- [How to stream from subgraphs] 
- [How to stream data from within a tool] 
- [How to stream LLM tokens from specific nodes] 
- [How to stream LLM tokens] 
- [How to stream] 

### Tool calling

[Tool calling] is a type of [chat model] API that accepts tool schemas, along with messages, as input and returns invocations of those tools as part of the output message.

These how-to guides show common patterns for tool calling with LangGraph:

- [How to handle large numbers of tools] 
- [How to update graph state from tools] 
- [How to pass config to tools] 
- [How to pass runtime values to tools] 
- [How to handle tool calling errors] 
- [How to call tools using ToolNode] 

### Subgraphs

[Subgraphs] allow you to reuse an existing graph from another graph. These how-to guides show how to use subgraphs:

- [How to transform inputs and outputs of a subgraph] 
- [How to view and update state in subgraphs] 
- [How to use subgraphs] 

### Multi-agent

[Multi-agent systems] are useful to break down complex LLM applications into multiple agents, each responsible for a different part of the application. These how-to guides show how to implement multi-agent systems in LangGraph:

- [How to add multi-turn conversation in a multi-agent application] 
- [How to build a multi-agent network] 
- [How to implement handoffs between agents] 

See the [multi-agent tutorials] for implementations of other multi-agent architectures.

See the below guides for how to implement multi-agent workflows with the (beta) [Functional API]:

- [How to add multi-turn conversation in a multi-agent application (functional API)] 
- [How to build a multi-agent network (functional API)] 

### State Management

- [How to pass private state between nodes inside the graph] 
- [How to define input/output schema for your graph] 
- [How to use Pydantic model as graph state] 

### Other

- [How to integrate LangGraph with AutoGen, CrewAI, and other frameworks] 
- [How to pass custom LangSmith run ID for graph runs] 
- [How to force tool-calling agent to structure output] 
- [How to run graph asynchronously] 

See the below guide for how to integrate with other frameworks using the (beta) [Functional API]:

- [How to integrate LangGraph (functional API) with AutoGen, CrewAI, and other frameworks] 

### Prebuilt ReAct Agent

The LangGraph [prebuilt ReAct agent] is pre-built implementation of a [tool calling agent].

One of the big benefits of LangGraph is that you can easily create your own agent architectures. So while it’s fine to start here to build an agent quickly, we would strongly recommend learning how to build your own agent so that you can take full advantage of LangGraph.

These guides show how to use the prebuilt ReAct agent:

- [How to add semantic search for long-term memory to a ReAct agent] 
- [How to return structured output from a ReAct agent] 
- [How to add human-in-the-loop processes to a ReAct agent] 
- [How to add a custom system prompt to a ReAct agent] 
- [How to add thread-level memory to a ReAct Agent] 
- [How to use the pre-built ReAct agent] 

Interested in further customizing the ReAct agent? This guide provides an overview of its underlying implementation to help you customize for your own needs:

- [How to create prebuilt ReAct agent from scratch] 

See the below guide for how-to build ReAct agents with the (beta) [Functional API]:

- [How to create a ReAct agent from scratch (Functional API)] 

## LangGraph Platform

This section includes how-to guides for LangGraph Platform.

LangGraph Platform is a commercial solution for deploying agentic applications in production, built on the open-source LangGraph framework.

The LangGraph Platform offers a few different deployment options described in the [deployment options guide].

Tip

- You can always deploy LangGraph applications on your own infrastructure using the open-source LangGraph project without using LangGraph Platform.
- LangGraph is an MIT-licensed open-source library, which we are committed to maintaining and growing for the community.

### Application Structure

Learn how to set up your app for deployment to LangGraph Platform:

- [How to integrate LangGraph into your React application] 
- [How to use LangGraph Platform to deploy CrewAI, AutoGen, and other frameworks] 
- [How to rebuild graph at runtime] 
- [How to test locally] 
- [How to customize Dockerfile] 
- [How to add semantic search] 
- [How to set up app for deployment (JavaScript)] 
- [How to set up app for deployment (pyproject.toml)] 
- [How to set up app for deployment (requirements.txt)]


---
*数据来源: Exa搜索 | 获取时间: 2026-02-19 20:54:46*