# LangGraph-5-Long-Term Memory - Kingnight Blog

**URL**:
https://kingnight.github.io/aigc/2025/05/30/LangGraph-5-Long-Term-Memory.html

## 元数据
- 发布日期: 2025-05-30T00:00:00+00:00

## 完整内容
---
LangGraph-5-Long-Term Memory | Kingnight Blog
[Kingnight Blog] 
# LangGraph-5-Long-Term Memory
May 30, 2025
阅读量次## Contents
* [Short vs Long-term memory] 
* [短期与长期记忆] 
* [短期记忆] 
* [长期记忆] 
* [对比] 
* [人类长期记忆] 
* [Agent长期记忆] 
* [Chatbot with Memory] 
* [LangGraph Store介绍] 
* [Chatbot with long-term memory] 
* [Chatbot with Profile Schema] 
* [Defining a user profile schema] 
* [Saving a schema to the store] 
* [Chatbot with profile schema] 
* [什么时候会失败] 
* [用于创建和更新概要模式的Trustcall] 
* [Trustcall核心原理] 
* [主要问题和解决方案] 
* [核心工作流程] 
* [关键组件] 
* [主要优势] 
* [实现机制] 
* [Chatbot with profile schema updating] 
记忆是一种认知功能，它允许人们存储、检索，并利用信息来了解他们的现在和未来。# Short vs Long-term memory
## 短期与长期记忆### 短期记忆短期记忆可以让应用程序记住单个线程或会话中的之前交互。线程在会话中组织多个交互，类似于电子邮件在单个会话中分组消息的方式。LangGraph管理短期记忆，将其作为代理状态的一部分，通过线程作用域检查点进行持久化。该状态通常包括对话历史记录以及其他有状态的数据，例如上传的文件、检索的文档或生成的工件。通过将这些存储在图的状态中，机器人可以访问给定对话的完整上下文，同时保持不同线程之间的分离。
### 长期记忆长期记忆是在会话线程之间共享的。它可以在任何时间，在任何线程中被召回。内存的作用域可以是任何自定义的命名空间，而不仅仅是一个线程ID。LangGraph提供了store来让你保存和回忆长期记忆。
### 对比||Short-term|Long-term|
Scope|Within session([thread])|Across session([thread])|
Example use-case|Persist conversational history, allow interruptions in a chat (e.g., if user is idle or to allow[human-in-the-loop])|Remember information about a specific user[across all chat sessions] |
LangGraph usage|[Checkpointer] |[Store] |
## 人类长期记忆* Episodic memory（情节记忆）：情节记忆主要涉及个人亲身经历的特定事件和情景，这些经历通常与时间、地点和相关的情感有关。例如，您记得昨天去海边度假的具体细节，包括看到的风景、感受到的微风等。
* Semantic memory（语义记忆）：语义记忆则是关于一般性的知识、概念、事实和语言信息等，不依赖于个人的具体经历或特定时间和地点。比如，您知道巴黎是法国的首都，数学中的定理，或者各种语言的词汇和语法规则等。
* procedural memory（程序性记忆）：一种长期的潜意识记忆，用于执行特定类型的动作。## Agent长期记忆
对应人类的三种一致![1.png] 
* Episodic memory（情节记忆）：agent过去的动作
* Semantic memory（语义记忆）：用户个人的具体经历或特定时间和地点
* procedural memory（程序性记忆）：Agent的提示词prompt
![2.png] 
# Chatbot with Memory
这里，我们将介绍一种保存和检索长时记忆的方法——LangGraph内存存储。
我们将构建一个同时使用短期（线程内）和长期（跨线程）内存的聊天机器人。我们将关注长期语义记忆，这将是关于用户的事实。这些**长期记忆**将被用于创建一个个性化的聊天机器人，它可以记住**有关用户的事实**。
它将在“热路径”中节省内存，因为用户正在与它聊天。热路径是指在程序运行过程中被频繁调用或执行的部分。在AI代理中，这通常是指代理在与用户交互或处理实时任务时直接涉及的逻辑。
虽然人类经常在睡眠期间形成长期记忆，但AI智能体需要一种不同的方法。智能体何时以及如何创建新记忆？智能体至少有两种主要的方法来编写记忆：“在热路径上”和“在后台”。
## LangGraph Store介绍
LangGraph内存存储提供了一种在LangGraph中跨线程存储和检索信息的方法。
这是一个用于持久键值存储的开源基类。```
`import uuid
from langgraph.store.memory import InMemoryStore
in\_memory\_store = InMemoryStore()`
```
当在Store中存储对象（例如内存）时，我们提供：
* 对象的命名空间，一个元组（类似于目录）。* 对象的键（类似于文件名）* 对象值（与文件内容类似）。* 我们使用put方法通过命名空间和键将对象保存到store中。
![截屏2025-05-15 14.15.24.png] 
```
`# Namespace for the memory to saveuser\_id="1"namespace\_for\_memory=(user\_id,"memories")# Save a memory to namespace as key and valuekey=str(uuid.uuid4())# The value needs to be a dictionaryvalue={"food\_preference":"I like pizza"}# Save the memoryin\_memory\_store.put(namespace\_for\_memory,key,value)`
```
我们使用[search] 通过`namespace`从`store`中检索对象。这将返回一个列表。
```
`# Searchmemories=in\_memory\_store.search(namespace\_for\_memory)print(type(memories))# Metatdataprint(memories[0].dict())# The key, valueprint(memories[0].key,memories[0].value)# 我们也可以使用get方法通过命名空间和键来取得对象。
# Get the memory by namespace and keymemory=in\_memory\_store.get(namespace\_for\_memory,key)print(memory.dict())`
```
输出```
`&lt;class'list'&gt;
{'namespace': ['1', 'memories'], 'key': '3fbd1852-ac50-4459-b4d2-c7ec31c6aa5b', 'value': {'food\_preference': 'Ilikepizza'}, 'created\_at': '2025-05-15T06:26:40.366310+00:00', 'updated\_at': '2025-05-15T06:26:40.366608+00:00', 'score': None}
3fbd1852-ac50-4459-b4d2-c7ec31c6aa5b {'food\_preference': 'Ilikepizza'}
{'namespace': ['1', 'memories'], 'key': '3fbd1852-ac50-4459-b4d2-c7ec31c6aa5b', 'value': {'food\_preference': 'Ilikepizza'}, 'created\_at': '2025-05-15T06:26:40.366310+00:00', 'updated\_at': '2025-05-15T06:26:40.366608+00:00'}`
```
## Chatbot with long-term memory
我们想要一个[具有两种内存类型] 的聊天机器人：
1. `短期（线程内）内存`：聊天机器人可以保留对话历史记录和/或允许聊天会话中断。
2. `长期（跨线程）内存`：聊天机器人可以**在所有聊天会话中**记住特定用户的信息。
对于`短期记忆`，我们将使用[checkpointer] 。
有关[checkpointer] 的更多信息，请参阅模块2和我们的[概念文档] ，但总结如下：
* 它们在每个步骤将图状态写入线程。* 他们将聊天记录保存在线程中。* 它们允许图形被中断和/或从线程中的任何步骤恢复。
对于`长期记忆`，我们将使用上面介绍的[LangGraph存储] 。
* 聊天历史记录将使用checkpointer保存到短期内存中。聊天机器人将反思聊天历史。
* 然后，它将创建一个内存并将其保存到LangGraph Store存储中。
* 在未来的聊天会话中可以访问此内存，以个性化聊天机器人的响应。module5/store.py
```
`fromIPython.displayimportImage,displayfromlanggraph.checkpoint.memoryimportMemorySaverfromlanggraph.graphimportStateGraph,MessagesState,START,ENDfromlanggraph.store.baseimportBaseStorefromlangchain\_core.messagesimportHumanMessage,SystemMessagefromlangchain\_core.runnables.configimportRunnableConfig# Chatbot instructionMODEL\_SYSTEM\_MESSAGE="""You are a helpful assistant with memory that provides information about the user. If you have memory for this user, use it to personalize your responses.
Here is the memory (it may be empty): {memory}"""# Create new memory from the chat history and any existing memoryCREATE\_MEMORY\_INSTRUCTION=""""You are collecting information about the user to personalize your responses.
CURRENT USER INFORMATION:
{memory}
INSTRUCTIONS:
1. Review the chat history below carefully
2. Identify new information about the user, such as:
- Personal details (name, location)
- Preferences (likes, dislikes)
- Interests and hobbies
- Past experiences
- Goals or future plans
3. Merge any new information with existing memory
4. Format the memory as a clear, bulleted list
5. If new information conflicts with existing memory, keep the most recent version
Remember: Only include factual information directly stated by the user. Do not make assumptions or inferences.
Based on the chat history below, please update the user information:"""defcall\_model(state:MessagesState,config:RunnableConfig,store:BaseStore):"""Load memory from the store and use it to personalize the chatbot's response."""# Get the user ID from the configuser\_id=config["configurable"]["user\_id"]# Retrieve memory from the storenamespace=("memory",user\_id)key="user\_memory"existing\_memory=store.get(namespace,key)# Extract the actual memory content if it exists and add a prefixifexisting\_memory:# Value is a dictionary with a memory keyexisting\_memory\_content=existing\_memory.value.get('memory')else:existing\_memory\_content="No existing memory found."# Format the memory in the system promptsystem\_msg=MODEL\_SYSTEM\_MESSAGE.format(memory=existing\_memory\_content)# Respond using memory as well as the chat historyresponse=model.invoke([SystemMessage(content=system\_msg)]+state["messages"])return{"messages":response}defwrite\_memory(state:MessagesState,config:RunnableConfig,store:BaseStore):"""Reflect on the chat history and save a memory to the store."""# Get the user ID from the configuser\_id=config["configurable"]["user\_id"]# Retrieve existing memory from the storenamespace=("memory",user\_id)existing\_memory=store.get(namespace,"user\_memory")# Extract the memoryifexisting\_memory:existing\_memory\_content=existing\_memory.value.get('memory')else:existing\_memory\_content="No existing memory found."# Format the memory in the system promptsystem\_msg=CREATE\_MEMORY\_INSTRUCTION.format(memory=existing\_memory\_content)new\_memory=model.invoke([SystemMessage(content=system\_msg)]+state['messages'])# Overwrite the existing memory in the storekey="user\_memory"# Write value as a dictionary with a memory keystore.put(namespace,key,{"memory":new\_memory.content})# Define the graphbuilder=StateGraph(MessagesState)builder.add\_node("call\_model",call\_model)builder.add\_node("write\_memory",write\_memory)builder.add\_edge(START,"call\_model")builder.add\_edge("call\_model","write\_memory")builder.add\_edge("write\_memory",END)# Store for long-term (across-thread) memoryacross\_thread\_memory=InMemoryStore()# Checkpointer for short-term (within-thread) memorywithin\_thread\_memory=MemorySaver()# Compile the graph with the checkpointer fir and storegraph=builder.compile(checkpointer=within\_thread\_memory,store=across\_thread\_memory)`
```
![截屏2025-05-15 14.43.27.png] 
当我们与聊天机器人交互时，我们提供两个东西：1. `Short-term (within-thread) memory`：用于保存聊天历史记录的`thread ID`。
2. `Long-term (cross-thread) memory`：用`user ID`命名用户的长期记忆。
让我们看看这些在实践中是如何一起工作的。```
`# We supply a thread ID for short-term (within-thread) memory
# We supply a user ID for long-term (across-thread) memoryconfig={"configurable":{"thread\_id":"1","user\_id":"1"}}# User inputinput\_messages=[HumanMessage(content="Hi, my name is Lance")]# Run the graphforchunkingraph.stream({"messages":input\_messages},config,stream\_mode="values"):chunk["messages"][-1].pretty\_print()`
```
```
`================================ Human Message =================================
Hi, my name is Lance
================================== Ai Message ==================================
Hello, Lance! It's nice to meet you. How can I assist you today?`
```
```
`# User inputinput\_messages=[HumanMessage(content="I like to bike around San Francisco")]# Run the graphforchunkingraph.stream({"messages":input\_messages},config,stream\_mode="values"):chunk["messages"][-1].pretty\_print()`
```
```
`================================ Human Message =================================
I like to bike around San Francisco
================================== Ai Message ==================================
That sounds like a great way to explore the city, Lance! San Francisco has some beautiful routes and views. Do you have a favorite trail or area you like to bike in?`
```
我们使用MemorySaver检查指针来处理线程内内存。这会将聊天历史记录保存到线程。我们可以查看保存到该线程的聊天历史记录。
```
`thread={"configurable":{"thread\_id":"1"}}state=graph.get\_state(thread).valuesforminstate["messages"]:m.pretty\_print()`
```
```
`================================ Human Message =================================
Hi, my name is Lance
================================== Ai Message


---
*数据来源: Exa搜索 | 获取时间: 2026-02-10 21:59:05*