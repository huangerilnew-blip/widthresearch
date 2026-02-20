# 4. 添加人工干预 - LangChain 框架

**URL**:
https://github.langchain.ac.cn/langgraph/tutorials/get-started/4-human-in-the-loop

## 元数据
- 发布日期: 2025-03-01T00:00:00+00:00

## 完整内容
---
[跳到内容] 

# 添加人机回圈控制 [¶] 

智能体可能不可靠，需要人类输入才能成功完成任务。同样，对于某些操作，您可能希望在运行前需要人类批准，以确保一切按预期进行。

LangGraph 的 [持久化] 层支持 **人机回圈** 工作流，允许根据用户反馈暂停和恢复执行。此功能的主要接口是 [`interrupt`] 函数。在节点内部调用 `interrupt` 将暂停执行。可以通过传入一个 [Command] 来恢复执行，同时可以附带来自人类的新输入。

`interrupt` 在人体工程学上类似于 Python 内置的 `input()`，但 [有一些注意事项] 。

注意

本教程建立在 [添加记忆] 的基础上。

## 1\. 添加 `human_assistance` 工具 [¶] 

从 [向聊天机器人添加记忆] 教程的现有代码开始，向聊天机器人添加 `human_assistance` 工具。此工具使用 `interrupt` 来接收来自人类的信息。

让我们首先选择一个聊天模型

OpenAIAnthropicAzureGoogle GeminiAWS Bedrock

```
pipinstall-U"langchain[openai]"
```

```
importosfromlangchain.chat_modelsimport init_chat_modelos.environ["OPENAI_API_KEY"] = "sk-..."llm = init_chat_model("openai:gpt-4.1")
```

👉 阅读 [OpenAI 集成文档] 

```
pipinstall-U"langchain[anthropic]"
```

```
importosfromlangchain.chat_modelsimport init_chat_modelos.environ["ANTHROPIC_API_KEY"] = "sk-..."llm = init_chat_model("anthropic:claude-3-5-sonnet-latest")
```

👉 阅读 [Anthropic 集成文档] 

```
pipinstall-U"langchain[openai]"
```

```
importosfromlangchain.chat_modelsimport init_chat_modelos.environ["AZURE_OPENAI_API_KEY"] = "..."os.environ["AZURE_OPENAI_ENDPOINT"] = "..."os.environ["OPENAI_API_VERSION"] = "2025-03-01-preview"llm = init_chat_model("azure_openai:gpt-4.1",azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],)
```

👉 阅读 [Azure 集成文档] 

```
pipinstall-U"langchain[google-genai]"
```

```
importosfromlangchain.chat_modelsimport init_chat_modelos.environ["GOOGLE_API_KEY"] = "..."llm = init_chat_model("google_genai:gemini-2.0-flash")
```

👉 阅读 [Google GenAI 集成文档] 

```
pipinstall-U"langchain[aws]"
```

```
fromlangchain.chat_modelsimport init_chat_model# Follow the steps here to configure your credentials:# https://docs.aws.amazon.com/bedrock/latest/userguide/getting-started.htmlllm = init_chat_model("anthropic.claude-3-5-sonnet-20240620-v1:0",model_provider="bedrock_converse",)
```

👉 阅读 [AWS Bedrock 集成文档] 

我们现在可以将其与一个额外的工具一起整合到我们的 `StateGraph` 中

```
fromtypingimport Annotatedfromlangchain_tavilyimport TavilySearchfromlangchain_core.toolsimport toolfromtyping_extensionsimport TypedDictfromlanggraph.checkpoint.memoryimport InMemorySaverfromlanggraph.graphimport StateGraph, START, ENDfromlanggraph.graph.messageimport add_messagesfromlanggraph.prebuiltimport ToolNode, tools_conditionfromlanggraph.typesimport Command, interruptclassState(TypedDict):messages: Annotated[list, add_messages]graph_builder = StateGraph(State)@tooldefhuman_assistance(query: str) -> str:"""Request assistance from a human."""human_response = interrupt({"query": query})return human_response["data"]tool = TavilySearch(max_results=2)tools = [tool, human_assistance]llm_with_tools = llm.bind_tools(tools)defchatbot(state: State):message = llm_with_tools.invoke(state["messages"])# Because we will be interrupting during tool execution,# we disable parallel tool calling to avoid repeating any# tool invocations when we resume.assert len(message.tool_calls) <= 1return {"messages": [message]}graph_builder.add_node("chatbot", chatbot)tool_node = ToolNode(tools=tools)graph_builder.add_node("tools", tool_node)graph_builder.add_conditional_edges("chatbot",tools_condition,)graph_builder.add_edge("tools", "chatbot")graph_builder.add_edge(START, "chatbot")
```

提示

有关人机回圈工作流的更多信息和示例，请参见 [人机回圈] 。

## 2\. 编译图 [¶] 

我们和之前一样，使用检查点编译图

```
memory = InMemorySaver()graph = graph_builder.compile(checkpointer=memory)
```

## 3\. 可视化图（可选） [¶] 

可视化图，你会得到和之前一样的布局——只是多了一个工具！

```
fromIPython.displayimport Image, displaytry:display(Image(graph.get_graph().draw_mermaid_png()))except Exception:# This requires some extra dependencies and is optionalpass
```

## 4\. 提示聊天机器人 [¶] 

现在，用一个会调用新的 `human_assistance` 工具的问题来提示聊天机器人

```
user_input = "I need some expert guidance for building an AI agent. Could you request assistance for me?"config = {"configurable": {"thread_id": "1"}}events = graph.stream({"messages": [{"role": "user", "content": user_input}]},config,stream_mode="values",)for event in events:if "messages" in event:event["messages"][-1].pretty_print()
```

```
================================ Human Message =================================
I need some expert guidance for building an AI agent. Could you request assistance for me?
================================== Ai Message ==================================
[{'text': "Certainly! I'd be happy to request expert assistance for you regarding building an AI agent. To do this, I'll use the human_assistance function to relay your request. Let me do that for you now.", 'type': 'text'}, {'id': 'toolu_01ABUqneqnuHNuo1vhfDFQCW', 'input': {'query': 'A user is requesting expert guidance for building an AI agent. Could you please provide some expert advice or resources on this topic?'}, 'name': 'human_assistance', 'type': 'tool_use'}]
Tool Calls:
  human_assistance (toolu_01ABUqneqnuHNuo1vhfDFQCW)
 Call ID: toolu_01ABUqneqnuHNuo1vhfDFQCW
  Args:
    query: A user is requesting expert guidance for building an AI agent. Could you please provide some expert advice or resources on this topic?

```

聊天机器人生成了一个工具调用，但随后执行被中断。如果检查图状态，你会看到它停在了工具节点

```
snapshot = graph.get_state(config)snapshot.next
```

```
('tools',)

```

信息

仔细看看 `human_assistance` 工具

```
@tooldefhuman_assistance(query: str) -> str:"""Request assistance from a human."""human_response = interrupt({"query": query})return human_response["data"]
```

与 Python 的内置 `input()` 函数类似，在工具内部调用 `interrupt` 将暂停执行。进度会根据 [检查点] 进行持久化；因此，如果它使用 Postgres 进行持久化，只要数据库处于活动状态，它就可以在任何时候恢复。在此示例中，它使用内存检查点进行持久化，只要 Python 内核正在运行，就可以随时恢复。

## 5\. 恢复执行 [¶] 

要恢复执行，请传递一个包含工具预期数据的 [`Command`] 对象。此数据的格式可以根据需要进行自定义。

在此示例中，使用一个带有名为 `"data"` 的键的字典

```
human_response = ("We, the experts are here to help! We'd recommend you check out LangGraph to build your agent."" It's much more reliable and extensible than simple autonomous agents.")human_command = Command(resume={"data": human_response})events = graph.stream(human_command, config, stream_mode="values")for event in events:if "messages" in event:event["messages"][-1].pretty_print()
```

```
================================== Ai Message ==================================
[{'text': "Certainly! I'd be happy to request expert assistance for you regarding building an AI agent. To do this, I'll use the human_assistance function to relay your request. Let me do that for you now.", 'type': 'text'}, {'id': 'toolu_01ABUqneqnuHNuo1vhfDFQCW', 'input': {'query': 'A user is requesting expert guidance for building an AI agent. Could you please provide some expert advice or resources on this topic?'}, 'name': 'human_assistance', 'type': 'tool_use'}]
Tool Calls:
  human_assistance (toolu_01ABUqneqnuHNuo1vhfDFQCW)
 Call ID: toolu_01ABUqneqnuHNuo1vhfDFQCW
  Args:
    query: A user is requesting expert guidance for building an AI agent. Could you please provide some expert advice or resources on this topic?
================================= Tool Message =================================
Name: human_assistance
We, the experts are here to help! We'd recommend you check out LangGraph to build your agent. It's much more reliable and extensible than simple autonomous agents.
================================== Ai Message ==================================
Thank you for your patience. I've received some expert advice regarding your request for guidance on building an AI agent. Here's what the experts have suggested:
The experts recommend that you look into LangGraph for building your AI agent. They mention that LangGraph is a more reliable and extensible option compared to simple autonomous agents.
LangGraph is likely a framework or library designed specifically for creating AI agents with advanced capabilities. Here are a few points to consider based on this recommendation:
1. Reliability: The experts emphasize that LangGraph is more reliable than simpler autonomous agent approaches. This could mean it has better stability, error handling, or consistent performance.
2. Extensibility: LangGraph is described as more extensible, which suggests that it probably offers a flexible architecture that allows you to easily add new features or modify existing ones as your agent's requirements evolve.
3. Advanced capabilities: Given that it's recommended over "simple autonomous agents," LangGraph likely provides more sophisticated tools and techniques for building complex AI agents.
...
2. Look for tutorials or guides specifically focused on building AI agents with LangGraph.
3. Check if there are any community forums or discussion groups where you can ask questions and get support from other developers using LangGraph.
If you'd like more specific information about LangGraph or have any questions about this recommendation, please feel free to ask, and I can request further assistance from the experts.
Output is truncated. View as a scrollable element or open in a text editor. Adjust cell output settings...

```

输入已被接收并作为工具消息处理。查看此调用的 [LangSmith 跟踪] ，以查看上述调用中完成的确切工作。请注意，状态在第一步被加载，以便我们的聊天机器人可以从它离开的地方继续。

**恭喜！** 您已经使用 `interrupt` 为您的聊天机器人添加了人机回圈执行，从而在需要时允许人类监督和干预。这为您使用 AI 系统创建的潜在 UI 开辟了可能性。由于您已经添加了 **检查点**，只要底层的持久化层正在运行，图就可以 **无限期地** 暂停，并随时恢复，就像什么都没发生过一样。

查看下面的代码片段，回顾本教程中的图

OpenAIAnthropicAzureGoogle GeminiAWS Bedrock

```
pipinstall-U"langchain[openai]"
```

```
importosfromlangchain.chat_modelsimport init_chat_modelos.environ["OPENAI_API_KEY"] = "sk-..."llm = init_chat_model("openai:gpt-4.1")
```

👉 阅读 [OpenAI 集成文档] 

```
pipinstall-U"langchain[anthropic]"
```

```
importosfromlangchain.chat_modelsimport init_chat_modelos.environ["ANTHROPIC_API_KEY"] = "sk-..."llm = init_chat_model("anthropic:claude-3-5-sonnet-latest")
```

👉 阅读 [Anthropic 集成文档] 

```
pipinstall-U"langchain[openai]"
```

```
importosfromlangchain.chat_modelsimport init_chat_modelos.environ["AZURE_OPENAI_API_KEY"] = "..."os.environ["AZURE_OPENAI_ENDPOINT"


---
*数据来源: Exa搜索 | 获取时间: 2026-02-20 20:40:34*