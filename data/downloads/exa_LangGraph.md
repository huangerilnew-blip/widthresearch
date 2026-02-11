# LangGraph 记忆系统实战：反馈循环+ 动态Prompt 让AI 持续学习

**URL**:
https://cloud.tencent.com/developer/article/2588385

## 元数据
- 发布日期: 2025-11-15T00:00:00+00:00

## 完整内容
---
LangGraph 记忆系统实战：反馈循环+ 动态Prompt 让AI 持续学习-腾讯云开发者社区-腾讯云
[] 
[deephub] 
## LangGraph 记忆系统实战：反馈循环+ 动态Prompt 让AI 持续学习**关注作者
[*腾讯云*] 
[*开发者社区*] 
[文档] [建议反馈] [控制台] 
登录/注册
[首页] 
学习活动专区圈层工具[MCP广场![]] 
文章/答案/技术大牛搜索**
搜索**关闭**
发布deephub
**
**
**
**
**
[社区首页] &gt;[专栏] &gt;LangGraph 记忆系统实战：反馈循环+ 动态Prompt 让AI 持续学习# LangGraph 记忆系统实战：反馈循环+ 动态Prompt 让AI 持续学习![作者头像] 
deephub
**关注
发布于2025-11-15 11:44:45
发布于2025-11-15 11:44:45
7030
举报**文章被收录于专栏：[DeepHub IMBA] DeepHub IMBA
**点击上方“Deephub Imba”,关注公众号,好文章不错过 !**
代理系统或者RAG 方案，基本都需要一个双层记忆架构，这样LLM 既能保持对当前上下文的专注，又能记住过往交互的内容。短期记忆负责单个会话内的即时信息管理，长期记忆则跨会话存储知识，让系统能够持续学习和进化。两者配合，代理才能表现出连贯性、上下文感知能力，看起来更加智能。这些记忆组件在现代AI 架构中的位置如下图所示：![] 
#### 线程级记忆（短期）这种记忆在单个对话线程内运作，追踪已经发生的消息、上传的文件、检索到的文档，以及代理在该会话中交互的其他内容。可以把它理解为代理的&quot;工作记忆&quot;。它帮助代理理解上下文，自然地延续讨论，不会丢失之前的步骤。LangGraph 通过检查点机制自动管理这部分记忆。对话结束后，短期记忆会被清空，下次会话则会重新开始一个新的记忆。#### 跨线程记忆（长期）第二种记忆设计用于跨越多个聊天会话。长期记忆存储代理可能需要在多个会话中记住的信息——用户偏好、早期决策、过程中学到的重要事实等。LangGraph 将这些数据以JSON 文档形式保存在记忆存储中，通过命名空间（类似文件夹）和键（类似文件名）整齐组织。因为这种记忆在对话后不会消失，所以代理能够随时间积累知识，提供更一致、更个性化的响应。> 本文会探讨生产级AI 系统如何使用LangGraph 管理长期记忆流。LangGraph 是一个构建可扩展、上下文感知AI 工作流的主流框架。### LangGraph 数据持久层处理代理记忆时，LangGraph 是最常用的组件。其中Store 功能尤为关键，它根据项目的运行位置管理记忆的保存、检索和更新方式。LangGraph 提供了几种存储实现，在简单性、持久性和可扩展性之间取得平衡。每种选项适合开发或部署的特定阶段。![] 
下面分别说明每种类型的使用场景。#### InMemory Store（用于 notebook 和快速测试）这是最简单的存储选项，适合短期实验或演示。![] 
使用`from langgraph.store.memory import InMemoryStore`导入，创建一个完全在内存中运行的存储，使用标准 Python 字典。不写入磁盘，进程结束后所有信息都会丢失。但速度快，易用，非常适合测试工作流或尝试新的图配置。如果需要，也可以添加语义搜索能力。#### 本地开发存储（langgraph dev）
这个选项的行为与上面的内存版本类似，但是可以在会话之间提供了基本持久性。![] 
用`langgraph dev`命令运行应用时，LangGraph 会自动使用Python 的pickle 格式将存储保存到本地文件系统，并在重启开发环境后恢复数据。这个方式轻量且方便，不需要外部数据库。同样支持语义搜索功能，所以它非常适合开发阶段，但不适合生产环境。#### 生产存储（LangGraph Platform 或自托管）大规模或生产部署，LangGraph 使用与pgvector 集成的PostgreSQL 数据库实现高效的向量存储和语义检索。![] 
这样可以提供完整的数据持久性、内置可靠性，并且能够处理更大的工作负载或多用户系统。语义搜索依靠pgvector ，默认使用余弦相似度作为相似性度量，也可以根据需求自定义。这种配置确保记忆数据安全存储，跨会话保持可用，即使在高流量或分布式工作负载下也能稳定运行。> 基础知识介绍完毕，接下来开始逐步编写完整的工作架构代码。### InMemory 功能实践本文要实现的是InMemory 功能，这是基于AI 系统中最常用的内存管理方式。> 它按顺序执行，在逐步构建或测试技术流程时非常实用。![] 
InMemory 功能允许在运行代码时临时存储数据，通过了解它可以有助于我们理解LangGraph 中内存处理的工作原理。从LangGraph 导入`InMemoryStore`开始。这个类让我们直接在内存中存储记忆，不需要外部数据库或文件系统。
代码语言：javascript
复制```
`# Import the InMemoryStore class for storing memories in memory (no persistence)
from langgraph.store.memory import InMemoryStore # Initialize an in-memory store instance for use in this notebook
in\_memory\_store = InMemoryStore()`
```
这里创建了InMemoryStore 的实例，用于保存临时数据。因为只在内存中运行，进程停止后所有存储的数据都会被清除。> LangGraph 中的每个记忆都保存在命名空间（namespace）中。
命名空间像标签或文件夹，帮助组织记忆。它被定义为元组，可以有一个或多个部分。下面这个例子使用包含用户ID 和&quot;memories&quot; 标签的元组。代码语言：javascript
复制```
`# Define a user ID for memory storage
user\_id = &quot;&quot;1&quot;&quot; # Set the namespace for storing and retrieving memories
namespace\_for\_memory = (user\_id, &quot;&quot;memories&quot;&quot;)`
```
命名空间可以代表任何东西，不一定基于用户ID，所以可以根据应用结构自由分组记忆。
下面我们保存一个记忆到存储中，使用`put`方法。这个方法需要三样东西：命名空间、唯一键和实际的记忆值。
这里键是用`uuid`库生成的唯一标识符，记忆值是存储信息的字典——一个简单的偏好设置。
代码语言：javascript
复制```
`import uuid # Generate a unique ID for the memory
memory\_id = str(uuid.uuid4()) # Create a memory dictionary
memory = {&quot;&quot;food\_preference&quot;&quot;: &quot;&quot;I like pizza&quot;&quot;} # Save the memory in the defined namespace
in\_memory\_store.put(namespace\_for\_memory, memory\_id, memory)`
```
这会将记忆条目添加到之前定义的命名空间下的内存存储中。存储记忆后，可以用`search`方法取回。这个方法在命名空间内查找并返回属于它的所有记忆列表。
每个记忆都是一个`Item`对象，包含命名空间、键、值和时间戳等详细信息。可以转换为字典以便更清晰地查看数据。
代码语言：javascript
复制```
`# Retrieve all stored memories for the given namespace
memories = in\_memory\_store.search(namespace\_for\_memory) # View the latest memory
memories[-1].dict()`
```
在notebook 中运行这段代码，得到以下输出：代码语言：javascript
复制```
`###### OUTPUT ######
{ &#x27;&#x27;namespace&#x27;&#x27;: [&#x27;&#x27;1&#x27;&#x27;, &#x27;&#x27;memories&#x27;&#x27;], &#x27;&#x27;key&#x27;&#x27;: &#x27;&#x27;c8619cd4-3d3f-4108-857c-5c8c12f39e87&#x27;&#x27;, &#x27;&#x27;value&#x27;&#x27;: {&#x27;&#x27;food\_preference&#x27;&#x27;: &#x27;&#x27;I like pizza&#x27;&#x27;}, &#x27;&#x27;created\_at&#x27;&#x27;: &#x27;&#x27;2025-10-08T15:46:16.531625+00:00&#x27;&#x27;, &#x27;&#x27;updated\_at&#x27;&#x27;: &#x27;&#x27;2025-10-08T15:46:16.531625+00:00&#x27;&#x27;, &#x27;&#x27;score&#x27;&#x27;: None }`
```
输出显示了存储的记忆详情。最重要的是**value**字段，包含实际保存的信息。其他字段帮助识别和管理记忆创建的时间和位置。
存储就绪后，可以将其连接到图中，让记忆和检查点协同工作。这里使用两个主要组件：* **InMemorySaver**管理线程间的检查点
* **InMemoryStore**存储跨线程的记忆
代码语言：javascript
复制```
`# To enable threads (conversations)
from langgraph.checkpoint.memory import InMemorySaver checkpointer = InMemorySaver() # To enable across-thread memory
from langgraph.store.memory import InMemoryStore in\_memory\_store = InMemoryStore() # Compile the graph with the checkpointer and store
# graph = graph.compile(checkpointer=checkpointer, store=in\_memory\_store)`
```
这使图能够记住线程内的对话上下文（短期），并使用相同的内存机制在线程间保留重要信息（长期）。> 这是转向生产级存储之前测试记忆行为的简单有效方式。### 构建代理架构在使用记忆系统工作流之前，需要构建使用它的智能代理。因为本文专注于记忆管理，所以只会构建一个中等复杂的电子邮件助手，模拟在真实场景中探索记忆的工作方式。![] 
下面我们从零开始构建这个系统，定义数据结构、&quot;大脑&quot;（提示词）和能力（工具）。最终得到一个不仅能回复邮件，还能从反馈中学习的代理。
#### 定义模式处理数据前需要定义其形状。模式是代理信息流的蓝图，确保一切结构化、可预测且类型安全。首先编写`RouterSchema`。需要它是为了让初始分类步骤可靠。不能冒险让 LLM 在期望明确决定时返回非结构化文本。这个Pydantic 模型会强制LLM 返回一个干净的JSON 对象，包含推理过程和一个严格为&#x27;ignore&#x27;、&#x27;respond&#x27; 或&#x27;notify&#x27; 之一的分类结果。代码语言：javascript
复制```
`# Import the necessary libraries from Pydantic and Python&#x27;&#x27;s typing module
from pydantic import BaseModel, Field from typing\_extensions import TypedDict, Literal # Define a Pydantic model for our router&#x27;&#x27;s structured output.
class RouterSchema(BaseModel): &quot;&quot;&quot;&quot;&quot;&quot;Analyze the unread email and route it according to its content.&quot;&quot;&quot;&quot;&quot;&quot; # Add a field for the LLM to explain its step-by-step reasoning.
reasoning: str = Field(description=&quot;&quot;分类背后的逐步推理。&quot;&quot;) # Add a field to hold the final classification.
# The `Literal` type restricts the output to one of these three specific strings.
classification: Literal[&quot;&quot;ignore&quot;&quot;, &quot;&quot;respond&quot;&quot;, &quot;&quot;notify&quot;&quot;] = Field( description=&quot;&quot;电子邮件的分类。&quot;&quot; )`
```
这是在为分类LLM 创建契约。后面与LangChain 的`.with\_structured\_output()`方法配对时，能保证输出是一个可预测的 Python 对象，让图中的逻辑更加健壮。接下来需要一个地方存储代理单次运行的所有信息，这就是`State`的作用。它像一个中央白板，图的每个部分都可以读写。
代码语言：javascript
复制```
`# Import the base state class from LangGraph
from langgraph.graph import MessagesState # Define the central state object for our graph.
class State(MessagesState): # This field will hold the initial raw email data.
email\_input: dict # This field will store the decision made by our triage router.
classification\_decision: Literal[&quot;&quot;ignore&quot;&quot;, &quot;&quot;respond&quot;&quot;, &quot;&quot;notify&quot;&quot;]`
```
继承自LangGraph 的`MessagesState`，自动获得一个`messages`列表来跟踪对话历史。然后添加自定义字段。随着流程从一个节点移动到另一个节点，这个`State`对象会被传递并累积信息。
最后定义一个小但重要的`StateInput`模式，规定图的初始输入应该是什么样子。
代码语言：javascript
复制```
`# Define a TypedDict for the initial input to our entire workflow.
class StateInput(TypedDict): # The workflow must be started with a dictionary containing an &#x27;&#x27;email\_input&#x27;&#x27; key.
email\_input: dict`
```
这个简单的模式从应用入口点就提供了清晰性和类型安全性，确保对图的任何调用都以正确的数据结构开始。#### 创建提示词使用提示词方法来指导和引导LLM 行为。对于代理，会定义几个提示词，每个都有特定的任务。代理从我们这里学到任何东西之前，需要一套基准指令。这些默认字符串会在第一次运行时加载到记忆存储中，为代理行为提供起点。首先定义`default\_background`给代理一个角色。
代码语言：javascript
复制```
`# Define a default persona for the agent.
default\_background=&quot;&quot;&quot;&quot;&quot;&quot; I&#x27;&#x27;m Lance, a software engineer at LangChain. &quot;&quot;&quot;&quot;&quot;&quot;`
```
接下来是`default\_triage\_instructions`，分类路由器遵循的初始规则。
代码语言：javascript
复制```
`# Define the initial rules for the triage LLM.
default\_triage\_instructions = &quot;&quot;&quot;&quot;&quot;&quot; Emails that are not worth responding to: - Marketing newsletters and promotional emails - Spam or suspicious emails - CC&#x27;&#x27;d on FYI threads with no direct questions Emails that require notification but no response: - Team member out sick or on vacation - Build system notifications or deployments Emails that require a response: - Direct questions from team members - Meeting requests requiring confirmation &quot;&quot;&quot;&quot;&quot;&quot;`
```
然后是`default\_response\_preferences`，定义代理的初始写作风格。
代码语言：javascript
复制```
`# Define the default preferences for how the agent should compose emails.
default\_response\_preferences = &quot;&quot;&quot;&quot;&quot;&quot; Use professional and concise language. If the e-mail mentions a deadline, make sure to explicitly acknowledge and reference the deadline in your response. When responding to meeting scheduling requests: - If times are proposed, verify calendar availability and commit to one. - If no times are proposed, check your calendar and propose multiple options. &quot;&quot;&quot;&quot;&quot;&quot;`
```
最后是`default\_cal\_preferences`，指导日程安排行为。
代码语言：javascript
复制```
`# Define the default preferences for scheduling meetings.
default\_cal\_preferences = &quot;&quot;&quot;&quot;&quot;&quot; 30 minute meetings are preferred, but 15 minute meetings are also acceptable. &quot;&quot;&quot;&quot;&quot;&quot;`
```
现在创建使用这些默认值的提示词，首先是`triage\_system\_prompt`。
代码语言：javascript
复制```
`# Define the system prompt for the initial triage step.
triage\_system\_prompt = &quot;&quot;&quot;&quot;&quot;&quot; &lt;&lt; Role &gt;&gt; Your role is to triage incoming emails based on background and instructions. &lt;&lt;/ Role &gt;&gt; &lt;&lt; Background &gt;&gt; {background} &lt;&lt;/ Background &gt;&gt; &lt;&lt; Instructions &gt;&gt; Categorize each email into IGNORE, NOTIFY, or RESPOND. &lt;&lt;/ Instructions &gt;&gt; &lt;&lt; Rules &gt;&gt; {triage\_instructions} &lt;&lt;/ Rules &gt;&gt; &quot;&quot;&quot;&quot;&quot;&quot;`
```
这个提示词模板给分类路由器提供角色和指令。`{background}`和`{triage\_instructions}


---
*数据来源: Exa搜索 | 获取时间: 2026-02-10 21:59:05*