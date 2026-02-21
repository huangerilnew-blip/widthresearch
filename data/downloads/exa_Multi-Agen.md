# Multi-Agent系统构建初探：基于LangGraph的长短期记忆管理实践指南

**URL**:
https://zhuanlan.zhihu.com/p/1981392181592871894

## 元数据
- 发布日期: 2025-12-08T00:00:00+00:00

## 完整内容
---
Multi-Agent系统构建初探：基于LangGraph的长短期记忆管理实践指南 - 知乎[] 
​[直答] 
切换模式登录/注册
# Multi-Agent系统构建初探：基于LangGraph的长短期记忆管理实践指南
[![腾讯技术工程]] 
[腾讯技术工程] [​![]] 
编程话题下的优秀答主作者：adacyang
> 如何让AI智能体（Agent）像人类一样拥有持久的记忆，从而在复杂的连续任务中保持上下文感知和深度理解？这已成为构建高级智能体的核心挑战。本文将深入探讨Agent Memory的核心概念，并聚焦于
> LangGraph
> 框架下的长短期记忆实现，详解短期会话与长期知识的存储、管理、语义检索等技巧。更进一步地，我们将通过一个引入> MCP协议
> 的实战案例，手把手带你构建一个真实的融合长记忆机制的Multi-Agent系统，直观展示中断、记忆与协作的融合。
基于大语言模型（LLM）的智能体（Agent）系统中，记忆机制是实现持续、连贯和个性化交互的核心基石，通过记忆，可以让Agent记住过往的交互，保持上下文的一致性，并能从反馈中学习，适应用户的偏好。
**本文核心要点概述：**
1.介绍Agent Memory的基本情况
2.LangGraph长短期记忆详解及案例说明：包含短期记忆实现、管理方法，长期记忆的实现方法，以及搭建了融合postgres数据库、集成Embedding服务进行语义搜索等可用于生产环境的真实案例。
3.引入MCP协议构建真实的Agent长记忆应用：搭建一个基于supervisor架构，集成中断机制、长短期记忆机制的multi-agent系统。
### **记忆机制介绍**
### **Agent Memory是什么？**
![] 
上图中（来源于Mem0[1]），左边是没有Memory的agent，右边是有Memory的agent，后者可以根据用户的过往信息（素食主义者、不喜欢乳制品）给出更合理的响应（不含乳制品的素食菜单），而前者的回答显然是不合适的。
简单来说，Memory是赋予Agent记忆能力的技术和架构，能够让Agent像人一样记住过去的交互、学到的知识、执行过的任务及未来的计划，是将一个LLM转变为能够执行复杂、长期任务的真正”智能体“的核心所在。
### **关于Agent Memory我们需要考虑什么？**
如何获取记忆：通过和用户交互、环境交互...
怎么组织记忆：模型参数、模型上下文、数据库怎么利用记忆：RAG、Few-shot...
### **有哪些Memory类型？**
关于Memory的分类，有许多种分类体系，这里我们只讨论最常见及最易于理解的。
正如人类利用长短期记忆进行有效的交互和学习一样，Agent的记忆机制通常划分为短期记忆（short-term memory）和长期记忆(long-term memory)，短期记忆决定了Agent在微观任务上的即时表现，而长期记忆则作为持久知识库，决定了Agent在宏观时间尺度上的智能深度和个性化水平，通过两者配合，Agent才能表现出连贯性、上下文感知能力，才会显得更智能。
### **Agent Memory如何工作？**
Agent通常通过以下几步来有效地管理记忆，使得每次于用户的交互都更加精准智能：
1. 记忆存储：通过设计一系列策略来存储重要的交互信息，这些信息可能来源于对话内容、历史数据或任务要求等等。2. 记忆更新：记忆会随着交互的发生，不断地进行更新，例如用户的偏好、最新的近况等等。记忆更新使得Agent能够不断优化其响应。
3. 记忆检索：Agent根据当下的需求，去记忆中检索需要的记忆内容，从而提供更加智能的回复。### **Agent Memory怎么实现？**
1. 物理外挂：即外置数据库和RAG，需要检索当前query相关的内容，例如：Mem0、ACE。好处是即插即用，坏处是不够end-to-end
2. Memory as Reasoning / Tool：通过训练Reasoning或Tool的方式动态更新context，例如：MemAgent、memory-R1。好处是更接近end-to-end，但不是很灵活。
3.参数更新：LLM本身就是一个Memory体，所有参数都是它的Memory，通过更新参数来更新记忆，这种方式是最本质的，但也是最难实现的。
### **LangGraph中的记忆管理**
LangGraph[2]作为一款面向多智能体协作与状态管理的框架，其设计了巧妙的记忆管理系统，旨在为Agent提供在不同交互中存储、检索和利用信息的能力。它区分了两种主要的记忆类型：短期记忆和长期记忆。在实际使用中，通过这两种记忆协同，既能保障实时任务的高效执行，又支持了跨任务、跨周期的经验复用。
●short-term memory（通过Checkpointer实现）：针对单个对话线程，核心价值在于保障对话的临时性，使得Agent能够跟踪会话中的多轮对话，可以在该线程内的任何时刻被回忆。
●long-term memory（通过Store实现）：可以跨对话线程共享，可以在任何时间，任何线程中被回忆，而不像短期记忆局限于单个对话。
![] 
通过下表，可以更清晰的看到两者的区别：||short-term memory|long-term memory|
目的|维持对话上下文|存储跨会话的持久化事实、偏好和知识|
持久性|会话级别（可以临时，可以持久）|应用级别（始终持久）|
作用域|单一会话|跨会话、跨用户|
持久化方式|检查点（checkpoint）|存储（Store）|
更新机制|自动（在每个图步骤后保存状态）|手动/显式|
典型用途|对话历史、中间状态|用户偏好、知识库、语义记忆|
![] ### **LangGraph记忆的架构基础**
要想更好的理解LangGraph中的记忆机制，首先需要理解其支持双轨记忆系统的核心概念。
### **Checkpointer**
LangGraph有一个内置的持久化（Persistence）层，通过checkpointer实现，能够持久化存储图状态，这使得开发记忆功能和人类干预功能成为可能。
当使用检查点编译一个图时，检查点会在每个super-step保存图状态的checkpoint，这些checkpoint被保存到一个thread中，可以在图执行后访问。因为threads允许在执行后访问图的状态，所以可以实现记忆、人机协作、时间旅行、容错等多种强大的功能。
![] 
工作流程：```
`用户输入 →[节点 1] →💾保存状态→[节点 2] →💾保存状态→输出↓↓Checkpoint 1 Checkpoint 2`
```
### **Thread**
为了管理多个独立的对话，LangGraph使用了thread的概念。thread\_id是由checkpointer保存的每个checkpoint的唯一id，是激活和区分不同对话线程的唯一key。在调用图的invoke或stream方法时，通过configurable字典传入一个thread\_id，就代表这次操作属于thread\_id这个特定的对话。
### **Store**
如上所述，图状态可以由checkpointer在每个super-step写入线程，从而实现状态的持久化。但是，如果想在多个线程之间保留一些信息的话，那么就需要用到Store。Store本质上是一个暴露给图节点和工具的键值数据库，与checkpointer的自动化快照不同，Store需要显式和主动的进行操作。
![]<image_link>### **Namespace**
Store中的数据通常通过更持久的标识来组织。user\_id是最常见的，用于关联用户的所有信息，此外，namespace提供了一种数据隔离机制，例如，使用使用 (“memories”, user\_id) 这样的元组作为命名空间，可以将用户的记忆与其他类型的数据（如用户偏好(“preferences”, user\_id)）清晰地分离开来，避免数据冲突，保持知识库的整洁有序。
### **短期记忆详解**
### **InMemorySaver内存会话临时存储**
对于开发、原型设计和测试阶段，最简单快捷的方式是使用InMemorySaver。它将所有的对话状态存储在内存中的一个Python字典里。
1.**设置记忆管理检查点**
```
`from langchain\_openai import ChatOpenAI
from langchain.chat\_models import init\_chat\_model
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create\_react\_agent
# 初始化检查点保存器checkpointer = InMemorySaver()`
```
2.**定义大模型并创建agent**
```
`BASE\_URL=&#34;&#34;&#34;&#34; TOKEN=&#34;&#34;&#34;&#34;
MODEL\_NAME=&#34;&#34;&#34;&#34;
model = init\_chat\_model(
model=MODEL\_NAME,
model\_provider=&#34;&#34;openai&#34;&#34;, base\_url=BASE\_URL,
api\_key=TOKEN,
temperature=0,
)
agent = create\_react\_agent(
model=model,
tools=[],
# 传入检查点，是将持久化能力“注入”图的关键步骤。编译后的graph对象现在具备了状态管理的能力。
checkpointer=checkpointer
)`
```
如果是底层自定义api在图构建阶段传入检查点的代码是graph = builder.compile(checkpointer=checkpointer)。
3.**短期记忆-内存后端**
```
`config = {&#34;&#34;configurable&#34;&#34;: {&#34;&#34;thread\_id&#34;&#34;: &#34;&#34;1&#34;&#34;}} # 激活记忆机制的核心。如果没有提供thread\_id，每次invoke调用都将是无状态的，只要使用相同的thread\_id，LangGraph就会在多次调用之间维持对话状态
response = agent.invoke(
{&#34;&#34;messages&#34;&#34;: [{&#34;&#34;role&#34;&#34;: &#34;&#34;user&#34;&#34;, &#34;&#34;content&#34;&#34;: &#34;&#34;你好，我叫ada！&#34;&#34;}]},
config
)
print(f&#34;&#34;thread1\_bot\_answer：{response[&#39;&#39;messages&#39;&#39;][-1].content}&#34;&#34;)
response = agent.invoke(
{&#34;&#34;messages&#34;&#34;: [{&#34;&#34;role&#34;&#34;: &#34;&#34;user&#34;&#34;, &#34;&#34;content&#34;&#34;: &#34;&#34;你好，请问你还记得我叫什么名字么？&#34;&#34;}]},
config
)
print(&#39;&#39;------------线程1------------------&#39;&#39;)
print(f&#34;&#34;thread1\_bot\_answer：{response[&#39;&#39;messages&#39;&#39;][-1].content}&#34;&#34;)
new\_config = {&#34;&#34;configurable&#34;&#34;: {&#34;&#34;thread\_id&#34;&#34;: &#34;&#34;2&#34;&#34;}}
response = agent.invoke(
{&#34;&#34;messages&#34;&#34;: [{&#34;&#34;role&#34;&#34;: &#34;&#34;user&#34;&#34;, &#34;&#34;content&#34;&#34;: &#34;&#34;你好，请问你还记得我叫什么名字么？&#34;&#34;}]},
new\_config
)
print(&#39;&#39;------------线程2------------------&#39;&#39;)
print(f&#34;&#34;thread2\_bot\_answer：{response[&#39;&#39;messages&#39;&#39;][-1].content}&#34;&#34;)`
```
执行上面代码，可以看到输出如下：```
`thread1\_bot\_answer：你好，Ada！很高兴认识你！😊
这是一个很美的名字呢！有什么我可以帮助你的吗？无论是想聊聊天，还是有任何问题需要解答，我都很乐意为你提供帮助。------------线程1------------------
thread1\_bot\_answer：当然记得！你刚才告诉我你叫 Ada～很高兴再次和你打招呼！😊
------------线程2------------------
thread2\_bot\_answer：你好！很抱歉，我无法记住之前对话中的个人信息，比如你的名字。这是为了保护你的隐私，所以我不会保留这类数据。你可以告诉我你的名字，或者任何你想让我称呼你的方式，我会很乐意在这次的对话中使用它！😊`
```
**短期记忆与线程相关，在对话时，需要在配置中传入thread\_id**。通过上面的结果我们可以看到，当我们传入相同的thread\_id时，agent就可以记住用户的名字，然而当我们更换thread\_id时，agent就不记得用户的名字了。
需要注意的是，**InMemorySaver将所有状态都保存在内存中**，一旦程序终止，那么所有对话历史都会消失。
### **数据库持久化存储**
可以发现，上面一小节的代码在应用程序结束后再启动，记忆就又消失了。这是因为InMemorySaver仅仅是把记忆保存在内存中，应用程序结束后释放内存记忆就消失了。在生产环境中常常使用数据库支持的检查点记录器持久化保存记忆，以保证数据的可靠性和服务的连续性。
这里我们以postgres数据库为例来说明，怎么持久化地保存记忆数据。
1.首先安装以下依赖：
```
`pip install -U &#34;psycopg[binary,pool]&#34; langgraph-checkpoint-postgres`
```
2.安装postgres数据库，具体的安装方法可以参考：[Linux下安装PostgreSQL\_linux安装postgresql-CSDN博客] 。这里选择以源码的方式进行安装，安装包从官网（[PostgreSQL: Downloads] ）下载，选择最新的postgresql-18.0.tar.gz。
3.安装数据库成功后，编码如下代码。
DB\_URI是数据库连接的URL。想要自动保存在数据库中的State需要在PostgresSaver.from\_conn\_string(DB\_URI)上下文中操作。
```
`from langchain.chat\_models import init\_chat\_model
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.checkpoint.postgres import PostgresSaver
BASE\_URL=&#34;&#34;&#34;&#34; TOKEN=&#34;&#34;&#34;&#34;
MODEL\_NAME=&#34;&#34;&#34;&#34;
model = init\_chat\_model(
model=MODEL\_NAME,
model\_provider=&#34;&#34;openai&#34;&#34;, base\_url=BASE\_URL,
api\_key=TOKEN,
temperature=0,
)
DB\_URI = &#34;&#34;postgresql://postgres:postgres@localhost:5432/postgres?sslmode=disable&#34;&#34;
with PostgresSaver.from\_conn\_string(DB\_URI) as checkpointer:
checkpointer.setup() # 第一次调用时必须要setup()
def call\_model(state: MessagesState):
response = model.invoke(state[&#34;&#34;messages&#34;&#34;])
return {&#34;&#34;messages&#34;&#34;: response}
builder = StateGraph(MessagesState)
builder.add\_node(call\_model)
builder.add\_edge(START, &#34;&#34;call\_model&#34;&#34;)
graph = builder.compile(checkpointer=checkpointer)
config = {
&#34;&#34;configurable&#34;&#34;: {
&#34;&#34;thread\_id&#34;&#34;: &#34;&#34;1&#34;&#34;
}
}
response = graph.invoke(
{&#34;&#34;messages&#34;&#34;: [{&#34;&#34;role&#34;&#34;: &#34;&#34;user&#34;&#34;, &#34;&#34;content&#34;&#34;: &#34;&#34;你好，我叫ada！&#34;&#34;}]},
config
)
print(response[&#39;&#39;messages&#39;&#39;][-1].content)
response = graph.invoke(
{&#34;&#34;messages&#34;&#34;: [{&#34;&#34;role&#34;&#34;: &#34;&#34;user&#34;&#34;, &#34;&#34;content&#34;&#34;: &#34;&#34;你好，请问你还记得我叫什么名字么？&#34;&#34;}]},
config
)
print(response[&#39;&#39;messages&#39;&#39;][-1].content)`
```
运行一次上述代码后，关闭应用程序后重启，再次运行上述代码，print结果如下：
```
`bot\_answer\_1：你好，Ada！很高兴再次见到你！😊
你的名字真动听！今天有什么我可以帮你解答或者想聊的话题吗？bot\_answer\_2：当然记得！你告诉我你叫 \*\*Ada\*\*。很高兴再次和你打招呼！😊`
```
可以看到，记忆已经被保存了。我们检查数据库可以发现，postgres数据库中出现了四个表：
![] 
上述表中，checkpoints表是”状态快照“表，每当程序执行一个step时，它就会在这张表中创建一条新记录，这条记录就是一个检查点的快照。查询该表，可以得到如下结果：
![] 
接下来，我们来分析每一列的含义：![] |列名|含义|举例说明|
thread\_id|线程ID|上表中，所有thread\_id都为1，表示这些记录都属于同一个会话流|
checkpoint\_ns|检查点命名空间（Namespace），用于对检查点进行分组或分类|上表中都是空的，表示未使用或使用了默认的命名空间|
checkpoint\_id|检查点的唯一标识符，该记录的主键||
parent\_checkpoint\_id|父检查点的ID，它将检查点链接起来|第一条记录的parent\_checkpoint\_id是空的，代表是整个流程的起点。|
checkpoint|核心状态数据，是一个json对象。|ts代表时间戳；channel\_values代表通道值，可以理解为工作流中的变量值；updated\_channels代表在当前这步中被修改过的通道|
metadata|该检查点本身的元数据|step表示这是工作流的第几步；source表来源，&#34;input&#34;指外外部输入，&#34;loop&#34;指工作流内部循环或某个节点执行的结果|
理解了上面checkpoints表后，那么不禁会问，真正的消息内容被存到了哪里呢？真正的消息内容存储在checkpoint\_writes表中，如下：
![] 
除了PostgreSQL之外，LangGraph还支持MongoDB、Redis等数据库。
### **子图中的记忆**
当构建复杂的、由多个子图嵌套而成的应用时，需要更灵活的记忆管理策略。●记忆继承（默认）：默认情况下，子图会继承其父图的checkpointer。这意味着整个嵌套图共享同一个对话状态，数据可以在父子图之间无缝流动。这对于将一个大型任务分解为多个模块化子任务非常有用。
●记忆隔离：在某些场景下，例如构建多智能体系统，希望每个智能体（由一个子图表示）拥有自己独立的内存空间，互不干扰。此时，可以在编译子图时设置checkpointer=True。
如下代码，可以在子图中直接使用父图的短期记忆：```
`from langgraph.graph import START, StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from typing import TypedDict
class State(TypedDict):
foo: str
# 子图def subgraph\_node\_1(state: State):
return {&#34;&#34;foo&#34;&#34;: state[&#34;&#34;foo&#34;&#34;] + &#34;&#34;bar&#34;&#34;}
subgraph\_builder = StateGraph(State)
subgraph\_builder.add\_node(subgraph\_node\_1)
subgraph\_builder.add\_edge(START, &#34;&#34;subgraph\_node\_1&#34;&#34;


---
*数据来源: Exa搜索 | 获取时间: 2026-02-21 20:11:32*