## LangGraph 记忆系统实战：反馈循环 + 动态 Prompt 让 AI 持续学习

[*腾讯云*](/?from=20060&from_column=20060)
[*开发者社区*](/developer)

[文档](/document/product?from=20702&from_column=20702)[建议反馈](/voc/?from=20703&from_column=20703)[控制台](https://console.cloud.tencent.com?from=20063&from_column=20063)

[首页](/developer)

文章/答案/技术大牛

deephub

[社区首页](/developer) >[专栏](/developer/column) >LangGraph 记忆系统实战：反馈循环 + 动态 Prompt 让 AI 持续学习

# LangGraph 记忆系统实战：反馈循环 + 动态 Prompt 让 AI 持续学习

deephub

发布于 2025-11-15 11:44:45

发布于 2025-11-15 11:44:45

8610

文章被收录于专栏：[DeepHub IMBA](/developer/column/86944)DeepHub IMBA

**点击上方“Deephub Imba”,关注公众号,好文章不错过 !**

代理系统或者 RAG 方案，基本都需要一个双层记忆架构，这样 LLM 既能保持对当前上下文的专注，又能记住过往交互的内容。

短期记忆负责单个会话内的即时信息管理，长期记忆则跨会话存储知识，让系统能够持续学习和进化。两者配合，代理才能表现出连贯性、上下文感知能力，看起来更加智能。这些记忆组件在现代 AI 架构中的位置如下图所示：

#### 线程级记忆（短期）

可以把它理解为代理的"工作记忆"。它帮助代理理解上下文，自然地延续讨论，不会丢失之前的步骤。LangGraph 通过检查点机制自动管理这部分记忆。对话结束后，短期记忆会被清空，下次会话则会重新开始一个新的记忆。

#### 跨线程记忆（长期）

LangGraph 将这些数据以 JSON 文档形式保存在记忆存储中，通过命名空间（类似文件夹）和键（类似文件名）整齐组织。因为这种记忆在对话后不会消失，所以代理能够随时间积累知识，提供更一致、更个性化的响应。

> 本文会探讨生产级 AI 系统如何使用 LangGraph 管理长期记忆流。LangGraph 是一个构建可扩展、上下文感知 AI 工作流的主流框架。

### LangGraph 数据持久层

处理代理记忆时，LangGraph 是最常用的组件。其中 Store 功能尤为关键，它根据项目的运行位置管理记忆的保存、检索和更新方式。

LangGraph 提供了几种存储实现，在简单性、持久性和可扩展性之间取得平衡。每种选项适合开发或部署的特定阶段。

#### InMemory Store（用于 notebook 和快速测试）

使用 `from langgraph.store.memory import InMemoryStore` 导入，创建一个完全在内存中运行的存储，使用标准 Python 字典。

不写入磁盘，进程结束后所有信息都会丢失。但速度快，易用，非常适合测试工作流或尝试新的图配置。如果需要，也可以添加语义搜索能力。

#### 本地开发存储（langgraph dev）

这个选项的行为与上面的内存版本类似，但是可以在会话之间提供了基本持久性。

用 `langgraph dev` 命令运行应用时，LangGraph 会自动使用 Python 的 pickle 格式将存储保存到本地文件系统，并在重启开发环境后恢复数据。

这个方式轻量且方便，不需要外部数据库。同样支持语义搜索功能，所以它非常适合开发阶段，但不适合生产环境。

#### 生产存储（LangGraph Platform 或自托管）

大规模或生产部署，LangGraph 使用与 pgvector 集成的 PostgreSQL 数据库实现高效的向量存储和语义检索。

这样可以提供完整的数据持久性、内置可靠性，并且能够处理更大的工作负载或多用户系统。语义搜索依靠pgvector ，默认使用余弦相似度作为相似性度量，也可以根据需求自定义。

这种配置确保记忆数据安全存储，跨会话保持可用，即使在高流量或分布式工作负载下也能稳定运行。

> 基础知识介绍完毕，接下来开始逐步编写完整的工作架构代码。

### InMemory 功能实践

本文要实现的是 InMemory 功能，这是基于 AI 系统中最常用的内存管理方式。

> 它按顺序执行，在逐步构建或测试技术流程时非常实用。

InMemory 功能允许在运行代码时临时存储数据，通过了解它可以有助于我们理解 LangGraph 中内存处理的工作原理。

从 LangGraph 导入 `InMemoryStore` 开始。这个类让我们直接在内存中存储记忆，不需要外部数据库或文件系统。

代码语言：javascript

复制

```
 # Import the InMemoryStore class for storing memories in memory (no persistence) from langgraph.store.memory import InMemoryStore # Initialize an in-memory store instance for use in this notebook in_memory_store = InMemoryStore()
```

这里创建了 InMemoryStore 的实例，用于保存临时数据。因为只在内存中运行，进程停止后所有存储的数据都会被清除。

> LangGraph 中的每个记忆都保存在命名空间（namespace）中。

命名空间像标签或文件夹，帮助组织记忆。它被定义为元组，可以有一个或多个部分。下面这个例子使用包含用户 ID 和 "memories" 标签的元组。

代码语言：javascript

复制

```
 # Define a user ID for memory storage user_id = "1" # Set the namespace for storing and retrieving memories namespace_for_memory = (user_id, "memories")
```

命名空间可以代表任何东西，不一定基于用户 ID，所以可以根据应用结构自由分组记忆。

下面我们保存一个记忆到存储中，使用 `put` 方法。这个方法需要三样东西：命名空间、唯一键和实际的记忆值。

这里键是用 `uuid` 库生成的唯一标识符，记忆值是存储信息的字典——一个简单的偏好设置。

代码语言：javascript

复制

```
 import uuid # Generate a unique ID for the memory memory_id = str(uuid.uuid4()) # Create a memory dictionary memory = {"food_preference": "I like pizza"} # Save the memory in the defined namespace in_memory_store.put(namespace_for_memory, memory_id, memory)
```

这会将记忆条目添加到之前定义的命名空间下的内存存储中。

存储记忆后，可以用 `search` 方法取回。这个方法在命名空间内查找并返回属于它的所有记忆列表。

每个记忆都是一个 `Item` 对象，包含命名空间、键、值和时间戳等详细信息。可以转换为字典以便更清晰地查看数据。

代码语言：javascript

复制

```
 # Retrieve all stored memories for the given namespace memories = in_memory_store.search(namespace_for_memory) # View the latest memory memories[-1].dict()
```

在 notebook 中运行这段代码，得到以下输出：

代码语言：javascript

复制

```
 ###### OUTPUT ###### { 'namespace': ['1', 'memories'], 'key': 'c8619cd4-3d3f-4108-857c-5c8c12f39e87', 'value': {'food_preference': 'I like pizza'}, 'created_at': '2025-10-08T15:46:16.531625+00:00', 'updated_at': '2025-10-08T15:46:16.531625+00:00', 'score': None }
```

输出显示了存储的记忆详情。最重要的是 **value** 字段，包含实际保存的信息。其他字段帮助识别和管理记忆创建的时间和位置。

存储就绪后，可以将其连接到图中，让记忆和检查点协同工作。这里使用两个主要组件：

* **InMemorySaver** 管理线程间的检查点
* **InMemoryStore** 存储跨线程的记忆

代码语言：javascript

复制

```
 # To enable threads (conversations) from langgraph.checkpoint.memory import InMemorySaver checkpointer = InMemorySaver() # To enable across-thread memory from langgraph.store.memory import InMemoryStore in_memory_store = InMemoryStore() # Compile the graph with the checkpointer and store # graph = graph.compile(checkpointer=checkpointer, store=in_memory_store)
```

这使图能够记住线程内的对话上下文（短期），并使用相同的内存机制在线程间保留重要信息（长期）。

> 这是转向生产级存储之前测试记忆行为的简单有效方式。

### 构建代理架构

在使用记忆系统工作流之前，需要构建使用它的智能代理。因为本文专注于记忆管理，所以只会构建一个中等复杂的电子邮件助手，模拟在真实场景中探索记忆的工作方式。

下面我们从零开始构建这个系统，定义数据结构、"大脑"（提示词）和能力（工具）。最终得到一个不仅能回复邮件，还能从反馈中学习的代理。

#### 定义模式

处理数据前需要定义其形状。模式是代理信息流的蓝图，确保一切结构化、可预测且类型安全。

首先编写 `RouterSchema`。需要它是为了让初始分类步骤可靠。不能冒险让 LLM 在期望明确决定时返回非结构化文本。

这个 Pydantic 模型会强制 LLM 返回一个干净的 JSON 对象，包含推理过程和一个严格为 'ignore'、'respond' 或 'notify' 之一的分类结果。

代码语言：javascript

复制

```
 # Import the necessary libraries from Pydantic and Python's typing module from pydantic import BaseModel, Field from typing_extensions import TypedDict, Literal # Define a Pydantic model for our router's structured output. class RouterSchema(BaseModel): """Analyze the unread email and route it according to its content.""" # Add a field for the LLM to explain its step-by-step reasoning. reasoning: str = Field(description="分类背后的逐步推理。") # Add a field to hold the final classification. # The `Literal` type restricts the output to one of these three specific strings. classification: Literal["ignore", "respond", "notify"] = Field( description="电子邮件的分类。" )
```

这是在为分类 LLM 创建契约。后面与 LangChain 的 `.with_structured_output()` 方法配对时，能保证输出是一个可预测的 Python 对象，让图中的逻辑更加健壮。

接下来需要一个地方存储代理单次运行的所有信息，这就是 `State` 的作用。它像一个中央白板，图的每个部分都可以读写。

代码语言：javascript

复制

```
 # Import the base state class from LangGraph from langgraph.graph import MessagesState # Define the central state object for our graph. class State(MessagesState): # This field will hold the initial raw email data. email_input: dict # This field will store the decision made by our triage router. classification_decision: Literal["ignore", "respond", "notify"]
```

继承自 LangGraph 的 `MessagesState`，自动获得一个 `messages` 列表来跟踪对话历史。然后添加自定义字段。随着流程从一个节点移动到另一个节点，这个 `State` 对象会被传递并累积信息。

最后定义一个小但重要的 `StateInput` 模式，规定图的初始输入应该是什么样子。

代码语言：javascript

复制

```
 # Define a TypedDict for the initial input to our entire workflow. class StateInput(TypedDict): # The workflow must be started with a dictionary containing an 'email_input' key. email_input: dict
```

这个简单的模式从应用入口点就提供了清晰性和类型安全性，确保对图的任何调用都以正确的数据结构开始。

#### 创建提示词

使用提示词方法来指导和引导 LLM 行为。对于代理，会定义几个提示词，每个都有特定的任务。

代理从我们这里学到任何东西之前，需要一套基准指令。这些默认字符串会在第一次运行时加载到记忆存储中，为代理行为提供起点。

首先定义 `default_background` 给代理一个角色。

代码语言：javascript

复制

```
 # Define a default persona for the agent. default_background=""" I'm Lance, a software engineer at LangChain. """
```

接下来是 `default_triage_instructions`，分类路由器遵循的初始规则。

代码语言：javascript

复制

```
 # Define the initial rules for the triage LLM. default_triage_instructions = """ Emails that are not worth responding to: - Marketing newsletters and promotional emails - Spam or suspicious emails - CC'd on FYI threads with no direct questions Emails that require notification but no response: - Team member out sick or on vacation - Build system notifications or deployments Emails that require a response: - Direct questions from team members - Meeting requests requiring confirmation """
```

然后是 `default_response_preferences`，定义代理的初始写作风格。

代码语言：javascript

复制

```
 # Define the default preferences for how the agent should compose emails. default_response_preferences = """ Use professional and concise language. If the e-mail mentions a deadline, make sure to explicitly acknowledge and reference the deadline in your response. When responding to meeting scheduling requests: - If times are proposed, verify calendar availability and commit to one. - If no times are proposed, check your calendar and propose multiple options. """
```

最后是 `default_cal_preferences`，指导日程安排行为。

代码语言：javascript

复制

```
 # Define the default preferences for scheduling meetings. default_cal_preferences = """ 30 minute meetings are preferred, but 15 minute meetings are also acceptable. """
```

现在创建使用这些默认值的提示词，首先是 `triage_system_prompt`。

代码语言：javascript

复制

```
 # Define the system prompt for the initial triage step. triage_system_prompt = """ < Role > Your role is to triage incoming emails based on background and instructions.  Role > < Background > {background}  Background > < Instructions > Categorize each email into IGNORE, NOTIFY, or RESPOND.  Instructions > < Rules > {triage_instructions}  Rules > """
```

这个提示词模板给分类路由器提供角色和指令。`{background}` 和 `{triage_instructions}` 占位符会被刚才定义的默认字符串填充。

接着是 `triage_user_prompt`，一个简单的模板，用于将原始邮件内容构造成 LLM 易于解析的清晰格式。

代码语言：javascript

复制

```
 # Define the user prompt for triage, which will format the raw email. triage_user_prompt = """ Please determine how to handle the following email: From: {author} To: {to} Subject: {subject} {email_thread}"""
```

现在是主要组件，必须创建 `agent_system_prompt_hitl_memory`，它包含到目前为止编码的角色和其他指令。

代码语言：javascript

复制

```
 # Import the datetime library to include the current date in the prompt. from datetime import datetime # Define the main system prompt for the response agent. agent_system_prompt_hitl_memory = """ < Role > You are a top-notch executive assistant.  Role > < Tools > You have access to the following tools: {tools_prompt}  Tools > < Instructions > 1. Analyze the email content carefully. 2. Always call one tool at a time until the task is complete. 3. Use Question to ask the user for clarification. 4. Draft emails using write_email. 5. For meetings, check availability and schedule accordingly. - Today's date is """ + datetime.now().strftime("%Y-%m-%d") + """ 6. After sending emails, use the Done tool.  Instructions > < Background > {background}  Background > < Response Preferences > {response_preferences}  Response Preferences > < Calendar Preferences > {cal_preferences}  Calendar Preferences > """
```

这是主响应代理的主指令集。像 `{response_preferences}` 和 `{cal_preferences}` 这样的占位符是记忆系统的关键。

> 它们允许动态地从记忆存储中注入代理学到的知识，使其能够随时间调整行为。

为了让代理改进，为专门的"记忆管理器"LLM 定义特殊提示词。它唯一的工作就是安全、智能地更新记忆存储。

代码语言：javascript

复制

```
 # Define the system prompt for our specialized memory update manager LLM. MEMORY_UPDATE_INSTRUCTIONS = """ # Role You are a memory profile manager for an email assistant. # Rules - NEVER overwrite the entire profile - ONLY add new information - ONLY update facts contradicted by feedback - PRESERVE all other information # Reasoning Steps 1. Analyze the current memory profile. 2. Review feedback messages. 3. Extract relevant preferences. 4. Compare to existing profile. 5. Identify facts to update. 6. Preserve everything else. 7. Output updated profile. # Process current profile for {namespace}  {current_profile}  """
```

`MEMORY_UPDATE_INSTRUCTIONS` 提示词高度结构化，规则严格：永不覆盖、只做针对性添加、保留现有信息。这种方法对防止代理记忆被破坏至关重要。

代码语言：javascript

复制

```
 # Define a reinforcement prompt to remind the LLM of the most critical rules. MEMORY_UPDATE_INSTRUCTIONS_REINFORCEMENT = """ Remember: - NEVER overwrite the entire profile - ONLY make targeted additions - ONLY update specific facts contradicted by feedback - PRESERVE all other information """
```

`MEMORY_UPDATE_INSTRUCTIONS_REINFORCEMENT` 是现代提示词工程技术。它是要求 LLM 更新记忆时会附加到消息中的最关键规则的简明摘要。重复关键指令有助于确保 LLM 遵守它们。

#### 定义工具和实用函数

代理有了指令，现在需要赋予它采取行动的能力。会定义作为工具的 Python 函数，以及一些辅助实用函数，保持主代码整洁有序。

编写实际工具函数之前，需要一个关于它们的简单文本描述。这是代理在主提示词中会"看到"的内容，让它理解有哪些工具可用以及如何使用。

代码语言：javascript

复制

```
 # A simple string describing the available tools for the LLM. HITL_MEMORY_TOOLS_PROMPT = """ 1. write_email(to, subject, content) - Send emails to specified recipients 2. schedule_meeting(attendees, subject, duration_minutes, preferred_day, start_time) - Schedule calendar meetings 3. check_calendar_availability(day) - Check available time slots 4. Question(content) - Ask follow-up questions 5. Done - Mark the email as sent """
```

这个字符串本身不是可执行代码，而是作为 LLM 的文档。它会被插入到主 `agent_system_prompt_hitl_memory` 中的 `{tools_prompt}` 占位符。这样代理就知道 `write_email` 函数存在，需要 `to`、`subject` 和 `content` 参数。

好的项目都有一个 `utils.py` 文件来存放执行常见、重复性任务的辅助函数，保持主图逻辑整洁，专注于工作流本身。

首先需要一个函数来解析初始邮件输入。

代码语言：javascript

复制

```
 # This utility unpacks the email input dictionary for easier access. def parse_email(email_input: dict) -> tuple[str, str, str, str]: """Parse an email input dictionary into its constituent parts.""" # Return a tuple containing the author, recipient, subject, and body of the email. return ( email_input["author"], email_input["to"], email_input["subject"], email_input["email_thread"], )
```

`parse_email` 函数是输入字典的简单解包器。虽然可以在图节点中直接访问 `email_input["author"]`，但这个辅助函数让代码更可读，并集中了解析逻辑。

接下来，一个将邮件内容格式化为 Markdown 供 LLM 使用的函数。

代码语言：javascript

复制

```
 # This function formats the raw email data into clean markdown for the LLM. def format_email_markdown(subject, author, to, email_thread): """Format email details into a nicely formatted markdown string.""" # Use f-string formatting to create a structured string with clear labels. return f""" **Subject**: {subject} **From**: {author} **To**: {to} {email_thread} --- """
```

`format_email_markdown` 函数接收解析后的邮件部分，将它们排列成干净的 Markdown 格式块。这种结构化格式比原始的非结构化字符串更容易被 LLM 解析，帮助它更好地理解邮件的不同组成部分（发件人、主题、正文）。

最后需要一个函数为人工审阅者格式化代理建议的操作。

代码语言：javascript

复制

```
 # This function creates a human-friendly view of a tool call for the HITL interface. def format_for_display(tool_call: dict) -> str: """Format a tool call into a readable string for the user.""" # Initialize an empty string to build our display. display = "" # Use conditional logic to create custom, readable formats for our main tools. if tool_call["name"] == "write_email": display += f'# Email Draft\n\n**To**: {tool_call["args"].get("to")}\n**Subject**: {tool_call["args"].get("subject")}\n\n{tool_call["args"].get("content")}' elif tool_call["name"] == "schedule_meeting": display += f'# Calendar Invite\n\n**Meeting**: {tool_call["args"].get("subject")}\n**Attendees**: {", ".join(tool_call["args"].get("attendees"))}' elif tool_call["name"] == "Question": display += f'# Question for User\n\n{tool_call["args"].get("content")}' # Provide a generic fallback for any other tools. else: display += f'# Tool Call: {tool_call["name"]}\n\nArguments:\n{tool_call["args"]}' # Return the final formatted string. return display
```

这个 `format_for_display` 函数对人机协作（HITL）步骤很重要。当代理提出工具调用如 `write_email` 时，不想向人工审阅者展示原始 JSON 对象。

这个函数将技术表示转换为看起来像实际邮件草稿或日历邀请的内容，让用户更容易审阅、编辑或批准。

模式、提示词和实用函数都定义好了，现在可以将它们组装成完整的图，让学习代理运转起来。

### 记忆功能与图节点

从这里开始我们就要实现记忆逻辑了，先看看整个系统如何运作。

代理从静态指令集转变为能够学习的动态系统，关键就在这里。

构建使用记忆的图节点之前，需要实际与 `InMemoryStore` 交互的函数。我们需要创建两个关键函数：一个获取现有偏好，另一个根据反馈更新它们。

首先需要可靠的方式从存储中获取偏好。编写一个叫 `get_memory` 的函数，它会在存储中查找特定偏好（如 `"triage_preferences"`）。找到就返回存储的值。

如果找不到——这会在用户第一次运行时发生——它会使用之前定义的默认内容创建条目。这确保代理始终有一套规则可以遵循。

代码语言：javascript

复制

```
 # A function to retrieve memory from the store or initialize with defaults. def get_memory(store, namespace, default_content=None): """Get memory from the store or initialize with default if it doesn't exist.""" # Use the store's .get() method to search for an item with a specific key. user_preferences = store.get(namespace, "user_preferences") # If the item exists, return its value (the stored string). if user_preferences: return user_preferences.value # If the item does not exist, this is the first time we're accessing this memory. else: # Use the store's .put() method to create the memory item with default content. store.put(namespace, "user_preferences", default_content) # Return the default content to be used in this run. return default_content
```

这个简单的函数功能强大。它抽象了检查和初始化记忆的逻辑。图中的任何节点现在都可以调用 `get_memory` 获取最新的用户偏好，无需知道这是第一次运行还是第一百次。

这里是代理学习被触发的地方。`update_memory` 函数设计用来接收用户反馈——比如编辑过的邮件或自然语言指令——并用它来精炼代理存储的知识。它使用之前精心制作的 `MEMORY_UPDATE_INSTRUCTIONS` 提示词来协调一个特殊用途的 LLM 调用。

为确保 LLM 输出可预测，先定义一个 `UserPreferences` Pydantic 模式。这会强制记忆管理器 LLM 返回一个 JSON 对象，包含推理过程和最终更新的偏好字符串。

代码语言：javascript

复制

```
 # A Pydantic model to structure the output of our memory update LLM call. class UserPreferences(BaseModel): """Updated user preferences based on user's feedback.""" # A field for the LLM to explain its reasoning, useful for debugging. chain_of_thought: str = Field(description="Reasoning about which user preferences need to add / update if required") # The final, updated string of user preferences. user_preferences: str = Field(description="Updated user preferences")
```

现在可以编写 `update_memory` 函数本身。它会检索当前偏好，将它们与用户反馈和特殊提示词结合，然后将 LLM 的精炼输出保存回存储。

代码语言：javascript

复制

```
 # Import AIMessage to help filter messages before sending them to the memory updater. from langchain_core.messages import AIMessage # This function intelligently updates the memory store based on user feedback. def update_memory(store, namespace, messages): """Update memory profile in the store.""" # First, get the current memory from the store so we can provide it as context. user_preferences = store.get(namespace, "user_preferences") # Initialize a new LLM instance specifically for this task, configured for structured output. memory_updater_llm = llm.with_structured_output(UserPreferences) # This is a small but important fix: filter out any previous AI messages with tool calls. # Passing these complex objects can sometimes cause errors in the downstream LLM call. messages_to_send = [ msg for msg in messages if not (isinstance(msg, AIMessage) and hasattr(msg, 'tool_calls') and msg.tool_calls) ] # Invoke the LLM with the memory prompt, current preferences, and the user's feedback. result = memory_updater_llm.invoke( [ # The system prompt that instructs the LLM on how to update memory. {"role": "system", "content": MEMORY_UPDATE_INSTRUCTIONS.format(current_profile=user_preferences.value, namespace=namespace)}, ] # Append the filtered conversation messages containing the feedback. + messages_to_send ) # Save the newly generated preference string back into the store, overwriting the old one. store.put(namespace, "user_preferences", result.user_preferences)
```

这个函数是代理学习能力的主要组成部分。通过使用带有严格指令的专用 LLM 调用，确保记忆以受控和增量方式更新，让代理随时间逐渐与用户偏好对齐。

现在可以定义代理的核心逻辑。在 LangGraph 中，这个逻辑封装在节点中。每个节点都是一个 Python 函数，接收图的当前 `State`，执行操作，返回对该状态的更新。

> 电子邮件助手会有几个关键节点，处理从初始分类到生成最终响应的所有事情。

工作流中的第一个节点是 `triage_router`。这个函数的任务是对收到的邮件做初步决定……

> 应该回复、只通知用户，还是完全忽略？长期记忆首次发挥作用就在这里。

路由器会使用 `get_memory` 函数获取用户最新的 `triage_preferences` 并注入到提示词中，确保决策能力随时间提高。

代码语言：javascript

复制

```
 # Import the Command class for routing and BaseStore for type hinting from langgraph.types import Command from langgraph.store.base import BaseStore # Define the first node in our graph, the triage router. def triage_router(state: State, store: BaseStore) -> Command: """Analyze email content to decide the next step.""" # Unpack the raw email data using our utility function. author, to, subject, email_thread = parse_email(state["email_input"]) # Format the email content into a clean string for the LLM. email_markdown = format_email_markdown(subject, author, to, email_thread) # Here is the memory integration: fetch the latest triage instructions. # If they don't exist, it will use the `default_triage_instructions`. triage_instructions = get_memory(store, ("email_assistant", "triage_preferences"), default_triage_instructions) # Format the system prompt, injecting the retrieved triage instructions. system_prompt = triage_system_prompt.format( background=default_background, triage_instructions=triage_instructions, ) # Format the user prompt with the specific details of the current email. user_prompt = triage_user_prompt.format( author=author, to=to, subject=subject, email_thread=email_thread ) # Invoke the LLM router, which is configured to return our `RouterSchema`. result = llm_router.invoke( [ {"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}, ] ) # Based on the LLM's classification, decide which node to go to next. if result.classification == "respond": print("📧 Classification: RESPOND - This email requires a response") # Set the next node to be the 'response_agent'. goto = "response_agent" # Update the state with the decision and the formatted email for the agent. update = { "classification_decision": result.classification, "messages": [{"role": "user", "content": f"Respond to the email: {email_markdown}"}], } elif result.classification == "ignore": print("🚫 Classification: IGNORE - This email can be safely ignored") # End the workflow immediately. goto = END # Update the state with the classification decision. update = {"classification_decision": result.classification} elif result.classification == "notify": print("🔔 Classification: NOTIFY - This email contains important information") # Go to the human-in-the-loop handler for notification. goto = "triage_interrupt_handler" # Update the state with the classification decision. update = {"classification_decision": result.classification} else: # Raise an error if the classification is invalid. raise ValueError(f"Invalid classification: {result.classification}") # Return a Command object to tell LangGraph where to go next and what to update. return Command(goto=goto, update=update)
```

这个节点是整个系统的入口。通过添加一行 `triage_instructions = get_memory(...)`，就把它从静态路由器变成了能学习的路由器。当用户对分类决策提供反馈时，存储中的 `triage_preferences` 会被更新，这个节点就会自动开始在未来的邮件上做出更好、更个性化的分类。

邮件被分类为 "respond" 时，会被传递给主响应代理。该代理的核心是 `llm_call` 节点。这个函数的目的是获取当前对话历史并采取下一步行动，通常是决定调用哪个工具。

跟分类路由器一样，这个节点集成了记忆来指导决策。它获取 `response_preferences` 和 `cal_preferences`，确保行为与用户学到的风格保持一致。

代码语言：javascript

复制

```
 # This is the primary reasoning node for the response agent. def llm_call(state: State, store: BaseStore): """LLM decides whether to call a tool or not, using stored preferences.""" # Fetch the user's latest calendar preferences from the memory store. cal_preferences = get_memory(store, ("email_assistant", "cal_preferences"), default_cal_preferences) # Fetch the user's latest response (writing style) preferences. response_preferences = get_memory(store, ("email_assistant", "response_preferences"), default_response_preferences) # Filter out previous AI messages with tool calls to prevent API errors. messages_to_send = [ msg for msg in state["messages"] if not (isinstance(msg, AIMessage) and hasattr(msg, 'tool_calls') and msg.tool_calls) ] # Invoke the main LLM, which is bound to our set of tools. # The prompt is formatted with the preferences retrieved from memory. response = llm_with_tools.invoke( [ {"role": "system", "content": agent_system_prompt_hitl_memory.format( tools_prompt=HITL_MEMORY_TOOLS_PROMPT, background=default_background, response_preferences=response_preferences, cal_preferences=cal_preferences )} ] + messages_to_send ) # Return the LLM's response to be added to the state. return {"messages": [response]}
```

这个节点展示了长期记忆的重要性。每次执行时都会提取用户最新的写作风格和日历偏好。

当用户提供反馈说更喜欢较短的邮件或 30 分钟的会议时，`update_memory` 函数会修改存储。下次这个 `llm_call` 节点运行时，会自动获取那些新偏好并注入到提示词中，立即改变代理行为，无需任何代码更改。

这就创建了一个反馈循环，代理在其中不断适应用户。

### 通过人机协作捕获反馈

代理不仅仅是在行动，还得知道何时请求帮助或确认。接下来要构建的节点集是中断处理器。

这些特殊节点会暂停图的执行并等待人类输入。神奇的地方就发生在这里：在这些步骤中提供的反馈会被捕获并用于更新代理的长期记忆。

会有两个中断点：

一个在初始分类之后（用于 `notify` 分类），另一个更复杂，用于审查代理建议的工具调用。

首先构建 `triage_interrupt_handler`。当 `triage_router` 将邮件分类为 `notify` 时，这个节点被触发。代理不会对邮件采取行动，而是呈现给用户并请求决策：

> 应该忽略，还是实际回复？用户在这里的选择是关于分类偏好的宝贵反馈。

代码语言：javascript

复制

```
 # Import the `interrupt` function from LangGraph. from langgraph.types import interrupt # Define the interrupt handler for the triage step. def triage_interrupt_handler(state: State, store: BaseStore) -> Command: """Handles interrupts from the triage step, pausing for user input.""" # Parse the email input to format it for display. author, to, subject, email_thread = parse_email(state["email_input"]) email_markdown = format_email_markdown(subject, author, to, email_thread) # This is the data structure that defines the interrupt. # It specifies the action, the allowed user responses, and the content to display. request = { "action_request": { "action": f"Email Assistant: {state['classification_decision']}", "args": {} }, "config": { "allow_ignore": True, "allow_respond": True }, "description": email_markdown, } # The `interrupt()` function pauses the graph and sends the request to the user. # It waits here until it receives a response. response = interrupt([request])[0] # Now, we process the user's response. if response["type"] == "response": # The user decided to respond, overriding the 'notify' classification. user_input = response["args"] # We create a message to pass to the memory updater. messages = [{"role": "user", "content": f"The user decided to respond to the email, so update the triage preferences to capture this."}] # This is a key step: we call `update_memory` to teach the agent. update_memory(store, ("email_assistant", "triage_preferences"), messages) # Prepare to route to the main response agent. goto = "response_agent" # Update the state with the user's feedback. update = {"messages": [{"role": "user", "content": f"User wants to reply. Use this feedback: {user_input}"}]} elif response["type"] == "ignore": # The user confirmed the email should be ignored. messages = [{"role": "user", "content": f"The user decided to ignore the email even though it was classified as notify. Update triage preferences to capture this."}] # We still update memory to reinforce this preference. update_memory(store, ("email_assistant", "triage_preferences"), messages) # End the workflow. goto = END update = {} # No message update needed. else: raise ValueError(f"Invalid response: {response}") # Return a Command to direct the graph's next step. return Command(goto=goto, update=update)
```

如果代理认为一封邮件只是通知，但用户决定回复，`update_memory` 就会被调用。记忆管理器 LLM 会看到消息"用户决定回复..."并分析邮件内容。

然后它会精确地更新 `triage_preferences` 字符串，也许通过将"构建系统通知"从 `NOTIFY` 类别移动到 `RESPOND` 类别。下次类似邮件到达时，`triage_router` 会做出更好、更个性化的决定。

但还需要一个主中断处理器，这是图中最复杂的节点。`llm_call` 节点提出要使用的工具（如 `write_email` 或 `schedule_meeting`）后，这个 `interrupt_handler` 就会介入。它将代理建议的操作呈现给用户审查。

然后用户可以接受、忽略、提供自然语言反馈或直接编辑。每种选择都为记忆系统提供了不同且有价值的信号。

代码语言：javascript

复制

```
 # The main interrupt handler for reviewing tool calls. def interrupt_handler(state: State, store: BaseStore) -> Command: """Creates an interrupt for human review of tool calls and updates memory.""" # We'll build up a list of new messages to add to the state. result = [] # By default, we'll loop back to the LLM after this. goto = "llm_call" # The agent can propose multiple tool calls, so we loop through them. for tool_call in state["messages"][-1].tool_calls: # We only want to interrupt for certain "high-stakes" tools. hitl_tools = ["write_email", "schedule_meeting", "Question"] if tool_call["name"] not in hitl_tools: # For other tools (like check_calendar), execute them without interruption. tool = tools_by_name[tool_call["name"]] observation = tool.invoke(tool_call["args"]) result.append({"role": "tool", "content": observation, "tool_call_id": tool_call["id"]}) continue # Format the proposed action for display to the human reviewer. tool_display = format_for_display(tool_call) # Define the interrupt request payload. request = { "action_request": {"action": tool_call["name"], "args": tool_call["args"]}, "config": { "allow_ignore": True, "allow_respond": True, "allow_edit": True, "allow_accept": True }, "description": tool_display, } # Pause the graph and wait for the user's response. response = interrupt([request])[0] # --- MEMORY UPDATE LOGIC BASED ON USER RESPONSE --- if response["type"] == "edit": # The user directly edited the agent's proposed action. initial_tool_call = tool_call["args"] edited_args = response["args"]["args"] # This is the most direct form of feedback. We call `update_memory`. if tool_call["name"] == "write_email": update_memory(store, ("email_assistant", "response_preferences"), [{"role": "user", "content": f"User edited the email. Initial draft: {initial_tool_call}. Edited draft: {edited_args}."}]) elif tool_call["name"] == "schedule_meeting": update_memory(store, ("email_assistant", "cal_preferences"), [{"role": "user", "content": f"User edited the meeting. Initial invite: {initial_tool_call}. Edited invite: {edited_args}."}]) # Execute the tool with the user's edited arguments. tool = tools_by_name[tool_call["name"]] observation = tool.invoke(edited_args) result.append({"role": "tool", "content": observation, "tool_call_id": tool_call["id"]}) elif response["type"] == "response": # The user gave natural language feedback. user_feedback = response["args"] # We capture this feedback and use it to update memory. if tool_call["name"] == "write_email": update_memory(store, ("email_assistant", "response_preferences"), [{"role": "user", "content": f"User gave feedback on the email draft: {user_feedback}"}]) elif tool_call["name"] == "schedule_meeting": update_memory(store, ("email_assistant", "cal_preferences"), [{"role": "user", "content": f"User gave feedback on the meeting invite: {user_feedback}"}]) # We don't execute the tool. Instead, we pass the feedback back to the agent. result.append({"role": "tool", "content": f"User gave feedback: {user_feedback}", "tool_call_id": tool_call["id"]}) elif response["type"] == "ignore": # The user decided this action should not be taken. This is triage feedback. update_memory(store, ("email_assistant", "triage_preferences"), [{"role": "user", "content": f"User ignored the proposal to {tool_call['name']}. This email should not have been classified as 'respond'."}]) result.append({"role": "tool", "content": "User ignored this. End the workflow.", "tool_call_id": tool_call["id"]}) goto = END elif response["type"] == "accept": # The user approved the action. No memory update is needed. tool = tools_by_name[tool_call["name"]] observation = tool.invoke(tool_call["args"]) result.append({"role": "tool", "content": observation, "tool_call_id": tool_call["id"]}) # Return a command with the next node and the messages to add to the state. return Command(goto=goto, update={"messages": result})
```

这个节点是学习系统的核心。注意到没有，每种类型的用户反馈——编辑、响应和忽略——都会触发对 `update_memory` 的调用，并带有特定的、上下文相关的消息。

当用户将会议时长从 45 分钟编辑为 30 分钟时，记忆管理器 LLM 会看到这个明确信号，并更新 `cal_preferences` 以在未来偏好 30 分钟的会议。当用户说"让它不那么正式"时，LLM 会对此进行概括，并在 `response_preferences` 中添加新规则。这种持续、细粒度的反馈循环让代理能够随时间成为高度个性化的助手。

### 组装成工作流

代理的所有单独组件都构建好了：模式、提示词、工具、实用函数和图节点。现在用 LangGraph 将它们组装成功能性的状态机。这涉及定义图结构、添加节点以及指定连接它们的边。

主 `llm_call` 节点运行后，代理会提出一个或多个工具调用。需要一种方法来决定接下来会发生什么。代理应该停止，还是应该进入人工审查步骤？这由条件边来处理。它是一个简单的函数，检查状态中的最后一条消息并指导图的流程。

代码语言：javascript

复制

```
 # This function determines the next step after the LLM has made its decision. def should_continue(state: State) -> Literal["interrupt_handler", END]: """Route to the interrupt handler or end the workflow if the 'Done' tool is called.""" # Get the list of messages from the current state. messages = state["messages"] # Get the most recent message, which contains the agent's proposed action. last_message = messages[-1] # Check if the last message contains any tool calls. if last_message.tool_calls: # Loop through each proposed tool call. for tool_call in last_message.tool_calls: # If the agent has decided it's finished, we end the workflow. if tool_call["name"] == "Done": return END # For any other tool, we proceed to the human review step. else: return "interrupt_handler"
```

这个函数是响应代理的主路由器。它检查代理的决定并充当交通警察。如果调用了 `Done` 工具，通过返回 `END` 表示过程已完成。

对于任何其他工具调用，它将图路由到 `interrupt_handler` 节点进行人工审查，确保在未经批准的情况下不采取任何行动。

现在可以组装图，直观地看到它的样子。用 `StateGraph` 定义结构。该过程涉及两个主要阶段：

构建 `response_agent` 子图——包含 `llm_call` -> `interrupt_handler` 的核心循环。构建 `overall_workflow`——这个主图从 `triage_router` 开始，并将 `response_agent` 子图作为其节点之一。

这种方式保持架构清晰易懂。

代码语言：javascript

复制

```
 # Import the main graph-building class from LangGraph. from langgraph.graph import StateGraph, START, END # --- Part 1: Build the Response Agent Subgraph --- # Initialize a new state graph with our defined `State` schema. agent_builder = StateGraph(State) # Add the 'llm_call' node to the graph. agent_builder.add_node("llm_call", llm_call) # Add the 'interrupt_handler' node to the graph. agent_builder.add_node("interrupt_handler", interrupt_handler) # Set the entry point of this subgraph to be the 'llm_call' node. agent_builder.add_edge(START, "llm_call") # Add the conditional edge that routes from 'llm_call' to either 'interrupt_handler' or END. agent_builder.add_conditional_edges( "llm_call", should_continue, { "interrupt_handler": "interrupt_handler", END: END, }, ) # After the interrupt handler, the graph always loops back to the LLM to continue the task. agent_builder.add_edge("interrupt_handler", "llm_call") # Compile the subgraph into a runnable object. response_agent = agent_builder.compile() # --- Part 2: Build the Overall Workflow --- # Initialize the main graph, defining its input schema as `StateInput`. overall_workflow = ( StateGraph(State, input=StateInput) # Add the triage router as the first node. .add_node("triage_router", triage_router) # Add the triage interrupt handler node. .add_node("triage_interrupt_handler", triage_interrupt_handler) # Add our entire compiled `response_agent` subgraph as a single node. .add_node("response_agent", response_agent) # Set the entry point for the entire workflow. .add_edge(START, "triage_router") # Define the edges from the triage router to the appropriate next steps. .add_edge("triage_router", "response_agent") .add_edge("triage_router", "triage_interrupt_handler") .add_edge("triage_interrupt_handler", "response_agent") ) # Compile the final, complete graph. email_assistant = overall_workflow.compile()
```

`triage_router` 做初步决定，然后分支到结束流程、通过 `triage_interrupt_handler` 询问用户输入，或者将控制权交给 `response_agent`。

`response_agent` 进入自己的思考（`llm_call`）和请求审查（`interrupt_handler`）循环，在此过程中更新记忆，直到任务完成。

这种有状态架构使得 LangGraph 非常适合构建复杂的、能够学习的代理。现在可以拿着这个编译好的 `email_assistant` 开始测试它从反馈中学习的能力。

### 使用记忆测试代理

记忆功能已经实现到电子邮件助手中，接下来测试系统如何从用户反馈中学习并随时间适应。这部分测试会探讨不同类型的用户交互如何创建不同的记忆更新，从而提高助手未来的性能。

主要解决一下的问题：

* 系统如何捕获和持久化用户偏好？
* 存储的偏好以何种方式影响后续决策过程？
* 哪些用户交互模式会触发特定类型的记忆更新？

首先构建一个辅助函数来显示记忆内容，以便在整个测试过程中跟踪其演变。

代码语言：javascript

复制

```
 # Import necessary libraries for testing. import uuid from langgraph.checkpoint.memory import MemorySaver from langgraph.types import Command from langgraph.store.memory import InMemoryStore # Define a helper function to display the content of our memory store. def display_memory_content(store, namespace=None): """A utility to print the current state of the memory store.""" # Print a header for clarity. print("\n======= CURRENT MEMORY CONTENT =======") # If a specific namespace is requested, show only that one. if namespace: # Retrieve the memory item for the specified namespace. memory = store.get(namespace, "user_preferences") print(f"\n--- {namespace[1]} ---") if memory: print(memory.value) else: print("No memory found") # If no specific namespace is given, show all of them. else: # Define the list of all possible namespaces we are using. for ns in [ ("email_assistant", "triage_preferences"), ("email_assistant", "response_preferences"), ("email_assistant", "cal_preferences"), ("email_assistant", "background") ]: # Retrieve and print the memory content for each namespace. memory = store.get(ns, "user_preferences") print(f"\n--- {ns[1]} ---") if memory: print(memory.value) else: print("No memory found") print("=======================================\n")
```

这个实用程序提供了一个实时窗口，可以观察代理不断演变的知识库，能轻松看到每次交互后到底学到了什么。

开始执行不同的测试用例。

#### 测试用例 1：基线——接受提议

第一个测试检查当用户未经修改地接受代理操作时会发生什么。这个基线案例帮助理解在没有提供反馈时系统的行为。期望代理使用记忆来做决定，但不会更新它。

先设置一个新的测试运行。

代码语言：javascript

复制

```
 # Define the input email for our test case. email_input_respond = { "to": "Lance Martin ", "author": "Project Manager ", "subject": "Tax season let's schedule call", "email_thread": "Lance,\n\nIt's tax season again... Are you available sometime next week? ... for about 45 minutes." } # --- Setup for a new test run --- # Initialize a new checkpointer and a fresh, empty memory store. checkpointer = MemorySaver() store = InMemoryStore() # Compile our graph, connecting it to our new checkpointer and store. graph = overall_workflow.compile(checkpointer=checkpointer, store=store) # Create a unique ID and configuration for this conversation. thread_id_1 = uuid.uuid4() thread_config_1 = {"configurable": {"thread_id": thread_id_1}} # Run the graph until its first interrupt. print("Running the graph until the first interrupt...") for chunk in graph.stream({"email_input": email_input_respond}, config=thread_config_1): if '__interrupt__' in chunk: Interrupt_Object = chunk['__interrupt__'][0] print("\nINTERRUPT OBJECT:") print(f"Action Request: {Interrupt_Object.value[0]['action_request']}") # Check the memory state after the first interrupt. display_memory_content(store)
```

图会一直运行直到代理提出第一个动作并暂停供审查。

代码语言：javascript

复制

```
 ####### OUTPUT ######### Running the graph until the first interrupt... 📧 Classification: RESPOND - This email requires a response INTERRUPT OBJECT: Action Request: {'action': 'schedule_meeting', 'args': {'attendees': ['lance@company.com', 'pm@client.com'], 'subject': 'Tax Planning Strategies', 'duration_minutes': 45, ...}} ======= CURRENT MEMORY CONTENT ======= --- triage_preferences --- Emails that are not worth responding to: ... --- response_preferences --- Use professional and concise language. ... --- cal_preferences --- 30 minute meetings are preferred, but 15 minute meetings are also acceptable. --- background --- No memory found =======================================
```

输出显示了两件关键的事。首先，代理正确提出了一个 45 分钟的 `schedule_meeting` 工具调用，尊重了发件人的请求，即使默认偏好是 30 分钟。

其次，`display_memory_content` 函数确认所有记忆命名空间都已使用默认值初始化。尚未发生学习。

现在接受代理的提议。

代码语言：javascript

复制

```
 # Resume the graph by sending an 'accept' command. print(f"\nSimulating user accepting the {Interrupt_Object.value[0]['action_request']['action']} tool call...") for chunk in graph.stream(Command(resume=[{"type": "accept"}]), config=thread_config_1): # Let the graph run until its next natural pause point. if '__interrupt__' in chunk: Interrupt_Object = chunk['__interrupt__'][0] print("\nINTERRUPT OBJECT:") print(f"Action Request: {Interrupt_Object.value[0]['action_request']}")
```

代理执行会议工具并进入下一个逻辑步骤：起草一封确认邮件。然后再次中断供审查。

代码语言：javascript

复制

```
 Simulating user accepting the schedule_meeting tool call... INTERRUPT OBJECT: Action Request: {'action': 'write_email', 'args': {'to': 'pm@client.com', 'subject': "Re: Tax season let's schedule call", 'content': 'Dear Project Manager, I have scheduled a meeting...for 45 minutes...'}}
```

代理已经起草了适当的确认邮件，等待最终批准。现在接受这第二个提议并检查记忆的最终状态。

代码语言：javascript

复制

```
 # Resume the graph one last time with another 'accept' command. print(f"\nSimulating user accepting the {Interrupt_Object.value[0]['action_request']['action']} tool call...") for chunk in graph.stream(Command(resume=[{"type": "accept"}]), config=thread_config_1): pass # Let the graph finish. # Check the final state of all memory namespaces. display_memory_content(store)
```

工作流完成。用户批准了代理的所有操作。

代码语言：javascript

复制

```
 ###### OUTPUT ####### Simulating user accepting the write_email tool call... ======= CURRENT MEMORY CONTENT ======= --- triage_preferences --- Emails that are not worth responding to: ... --- response_preferences --- Use professional and concise language. ... --- cal_preferences --- 30 minute meetings are preferred, but 15 minute meetings are also acceptable. --- background --- No memory found =======================================
```

最终的记忆检查证实了假设。即使在一次完整、成功的运行之后，记忆内容也与其初始默认状态相同。这是正确的行为。简单的接受不能提供强烈的学习信号，所以代理明智地没有改变其长期知识。它使用记忆，但没有明确反馈就不会改变它。

#### 测试用例 2：从直接编辑中学习

下面我们测试一个有趣的例子，看看当通过直接编辑代理提议来提供明确反馈时会发生什么。这创建了一个清晰的"之前"和"之后"场景，记忆管理器 LLM 可以从中学习。

用相同的邮件开始一次新的运行。

代码语言：javascript

复制

```
 # --- Setup for a new edit test run --- checkpointer = MemorySaver() store = InMemoryStore() graph = overall_workflow.compile(checkpointer=checkpointer, store=store) thread_id_2 = uuid.uuid4() thread_config_2 = {"configurable": {"thread_id": thread_id_2}} # Run the graph until the first interrupt. print("Running the graph until the first interrupt...") for chunk in graph.stream({"email_input": email_input_respond}, config=thread_config_2): if '__interrupt__' in chunk: Interrupt_Object = chunk['__interrupt__'][0] print("\nINTERRUPT OBJECT:") print(f"Action Request: {Interrupt_Object.value[0]['action_request']}") # Check the initial memory state. display_memory_content(store,("email_assistant", "cal_preferences"))
```

代理暂停，再次提议一个 45 分钟的会议。现在不接受，而是将提议编辑成真正的偏好：一个 30 分钟的会议，主题更简洁。

代码语言：javascript

复制

```
 # Define the user's edits to the proposed `schedule_meeting` tool call. edited_schedule_args = { "attendees": ["pm@client.com", "lance@company.com"], "subject": "Tax Planning Discussion", # Changed from "Tax Planning Strategies" "duration_minutes": 30, # Changed from 45 to 30 "preferred_day": "2025-04-22", "start_time": 14 } # Resume the graph by sending an 'edit' command with our new arguments. print("\nSimulating user editing the schedule_meeting tool call...") for chunk in graph.stream(Command(resume=[{"type": "edit", "args": {"args": edited_schedule_args}}]), config=thread_config_2): if '__interrupt__' in chunk: # Capture the next interrupt Interrupt_Object = chunk['__interrupt__'][0] print("\nINTERRUPT OBJECT (Second Interrupt):") print(f"Action Request: {Interrupt_Object.value[0]['action_request']}") # Check the memory AGAIN, after the edit has been processed. print("\nChecking memory after editing schedule_meeting:") display_memory_content(store,("email_assistant", "cal_preferences"))
```

运行这个看看效果。

代码语言：javascript

复制

```
 ###### OUTPUT ####### Simulating user editing the schedule_meeting tool call... INTERRUPT OBJECT (Second Interrupt): Action Request: {'action': 'write_email', 'args': {'to': 'pm@client.com', ...}} Checking memory after editing schedule_meeting: ======= CURRENT MEMORY CONTENT ======= --- cal_preferences --- 30 minute meetings are preferred, but 15 minute meetings are also acceptable. The subject of the meeting should be 'Tax Planning Discussion' instead of 'Tax Planning Strategies'. The meeting duration should be 30 minutes instead of 45 minutes. ...
```

这个输出证明了系统有效。`cal_preferences` 记忆不再是简单的默认值。记忆管理器 LLM 分析了代理提议和编辑之间的差异，将更改概括为更广泛的规则。

它已经学会了对较短会议和更简洁主题的偏好，这个新知识现在成为了代理记忆的永久组成部分。

现在通过编辑邮件草稿来完成工作流。

代码语言：javascript

复制

```
 # The graph is paused. Let's define our edits for the email draft. edited_email_args = { "to": "pm@client.com", "subject": "Re: Tax Planning Discussion", "content": "Thanks for reaching out. Sounds good. I've scheduled a 30-minute call for us next Tuesday. Looking forward to it!\n\nBest,\nLance" } # Resume the graph with the 'edit' command for the write_email tool. print("\nSimulating user editing the write_email tool call...") for chunk in graph.stream(Command(resume=[{"type": "edit", "args": {"args": edited_email_args}}]), config=thread_config_2): pass # Check the 'response_preferences' memory to see what was learned. print("\nChecking memory after editing write_email:") display_memory_content(store, ("email_assistant", "response_preferences")) print("\n--- Workflow Complete ---")
```

看看终端中显示了什么。

代码语言：javascript

复制

```
 ######## OUTPUT ######### Simulating user editing the write_email tool call... Checking memory after editing write_email: ======= CURRENT MEMORY CONTENT ======= --- response_preferences --- When responding to meeting scheduling requests, the assistant should schedule a meeting for 30 minutes instead of 45 minutes. The assistant should also use the subject line "Re: Tax Planning Discussion" instead of "Re: Tax season let's schedule call". The rest of the user preferences remain the same. --- Workflow Complete ---
```

再一次学习显而易见。`response_preferences` 已被更新。记忆管理器 LLM 正确识别了语气和结构上的关键差异，提取了关于主题行和会议时长的可概括规则。

通过在单次运行中提供两次编辑，已经在两个不同领域个性化了代理行为，展示了这种反馈循环的力量。

### 长期记忆系统的工作原理

我们通过本文已经看到代理从反馈中学习，但是背后发生了什么呢？这是一个简单而强大的四步循环，将更正转化为代理的新规则。

整个过程的分解：

**反馈是触发器**。学习过程只在提供反馈时才会开始。简单接受一个提议不会改变记忆。只有当编辑一个动作或给出对话式响应时，学习才会被触发。

**调用专用的记忆管理器**。不只是保存原始反馈。而是进行一次特殊用途的 LLM 调用。这个"记忆管理器"使用严格的 `MEMORY_UPDATE_INSTRUCTIONS` 提示词来分析反馈。

**对记忆进行精确更新**。记忆管理器的任务是进行有针对性的更新。它将反馈与现有偏好进行比较，在不覆盖或删除旧规则的情况下集成新规则。这确保代理永远不会忘记过去的教训。

**新知识在下次运行时注入**。更新后的偏好字符串被保存到 `Store` 中。下次代理开始新任务时会获取这个新字符串，将学到的行为注入其提示词中，改变其未来的行为方式。

这个"触发 -> 管理 -> 更新 -> 注入"循环使代理能够从一个通用工具演变为个性化的助手。

作者：Fareed Khan

本文参与 [腾讯云自媒体同步曝光计划](/developer/support-plan)，分享自微信公众号。

原始发表：2025-10-20，如有侵权请联系 [cloudcommunity@tencent.com](mailto:cloudcommunity@tencent.com) 删除

[存储](/developer/tag/10665)

[prompt](/developer/tag/15406)

[代理](/developer/tag/17225)

[工具](/developer/tag/17276)

[函数](/developer/tag/17290)

本文分享自 DeepHub IMBA 微信公众号，前往查看

如有侵权，请联系 [cloudcommunity@tencent.com](mailto:cloudcommunity@tencent.com) 删除。

本文参与 [腾讯云自媒体同步曝光计划](/developer/support-plan)  ，欢迎热爱写作的你一起参与！

[存储](/developer/tag/10665)

[prompt](/developer/tag/15406)

[代理](/developer/tag/17225)

[工具](/developer/tag/17276)

[函数](/developer/tag/17290)

登录后参与评论

登录 后参与评论

* 线程级记忆（短期）

* 跨线程记忆（长期）

* LangGraph 数据持久层
  + InMemory Store（用于 notebook 和快速测试）
  + 本地开发存储（langgraph dev）
  + 生产存储（LangGraph Platform 或自托管）

* InMemory 功能实践

* 构建代理架构
  + 定义模式
  + 创建提示词
  + 定义工具和实用函数

* 记忆功能与图节点

* 通过人机协作捕获反馈

* 组装成工作流

* 使用记忆测试代理
  + 测试用例 1：基线——接受提议
  + 测试用例 2：从直接编辑中学习

* 长期记忆系统的工作原理

对象存储（Cloud Object Storage，COS）是由腾讯云推出的无目录层次结构、无数据格式限制，可容纳海量数据且支持 HTTP/HTTPS 协议访问的分布式存储服务。腾讯云 COS 的存储桶空间无容量上限，无需分区管理，适用于 CDN 数据分发、数据万象处理或大数据计算与分析的数据湖等多种场景。

[产品介绍](https://cloud.tencent.com/product/cos?from=21341&from_column=21341)[产品文档](https://cloud.tencent.com/document/product/436?from=21342&from_column=21342)

* ### 社区

  + [技术文章](/developer/column)
  + [技术问答](/developer/ask)
  + [技术沙龙](/developer/salon)
  + [技术视频](/developer/video)
  + [学习中心](/developer/learning)
  + [技术百科](/developer/techpedia)
  + [技术专区](/developer/zone/list)
* ### 活动

  + [自媒体同步曝光计划](/developer/support-plan)
  + [邀请作者入驻](/developer/support-plan-invitation)
  + [自荐上首页](/developer/article/1535830)
  + [技术竞赛](/developer/competition)
* ### 圈层

  + [腾讯云最具价值专家](/tvp)
  + [腾讯云架构师技术同盟](/developer/program/tm)
  + [腾讯云创作之星](/developer/program/tci)
  + [腾讯云TDP](/developer/program/tdp)
* ### 关于

  + [社区规范](/developer/article/1006434)
  + [免责声明](/developer/article/1006435)
  + [联系我们](mailto:cloudcommunity@tencent.com)
  + [友情链接](/developer/friendlink)
  + [MCP广场开源版权声明](/developer/article/2537547)

### 腾讯云开发者

### 热门产品

* [域名注册](/product/domain?from=20064&from_column=20064)
* [云服务器](/product/cvm?from=20064&from_column=20064)
* [区块链服务](/product/tbaas?from=20064&from_column=20064)
* [消息队列](/product/message-queue-catalog?from=20064&from_column=20064)
* [网络加速](/product/ecdn?from=20064&from_column=20064)
* [云数据库](/product/tencentdb-catalog?from=20064&from_column=20064)
* [域名解析](/product/dns?from=20064&from_column=20064)
* [云存储](/product/cos?from=20064&from_column=20064)
* [视频直播](/product/css?from=20064&from_column=20064)

### 热门推荐

* [人脸识别](/product/facerecognition?from=20064&from_column=20064)
* [腾讯会议](/product/tm?from=20064&from_column=20064)
* [企业云](/act/pro/enterprise2022?from=20064&from_column=20064)
* [CDN加速](/product/cdn?from=20064&from_column=20064)
* [视频通话](/product/trtc?from=20064&from_column=20064)
* [图像分析](/product/imagerecognition?from=20064&from_column=20064)
* [MySQL 数据库](/product/cdb?from=20064&from_column=20064)
* [SSL 证书](/product/ssl?from=20064&from_column=20064)
* [语音识别](/product/asr?from=20064&from_column=20064)

### 更多推荐

* [数据安全](/solution/data_protection?from=20064&from_column=20064)
* [负载均衡](/product/clb?from=20064&from_column=20064)
* [短信](/product/sms?from=20064&from_column=20064)
* [文字识别](/product/ocr?from=20064&from_column=20064)
* [云点播](/product/vod?from=20064&from_column=20064)
* [大数据](/product/bigdata-class?from=20064&from_column=20064)
* [小程序开发](/solution/la?from=20064&from_column=20064)
* [网站监控](/product/tcop?from=20064&from_column=20064)
* [数据迁移](/product/cdm?from=20064&from_column=20064)

Copyright © 2013 - 2026Tencent Cloud. All Rights Reserved. 腾讯云 版权所有

[深圳市腾讯计算机系统有限公司](https://qcloudimg.tencent-cloud.cn/raw/986376a919726e0c35e96b311f54184d.jpg) ICP备案/许可证号：[粤B2-20090059](https://beian.miit.gov.cn/#/Integrated/index)[粤公网安备44030502008569号](https://beian.mps.gov.cn/#/query/webSearch?code=44030502008569)

[腾讯云计算（北京）有限责任公司](https://qcloudimg.tencent-cloud.cn/raw/a2390663ee4a95ceeead8fdc34d4b207.jpg) 京ICP证150476号 |  [京ICP备11018762号](https://beian.miit.gov.cn/#/Integrated/index)

[问题归档](/developer/ask/archives.html)[专栏文章](/developer/column/archives.html)[快讯文章归档](/developer/news/archives.html)[关键词归档](/developer/information/all.html)[开发者手册归档](/developer/devdocs/archives.html)[开发者手册 Section 归档](/developer/devdocs/sections_p1.html)

Copyright © 2013 - 2026Tencent Cloud.

All Rights Reserved. 腾讯云 版权所有

登录 后参与评论