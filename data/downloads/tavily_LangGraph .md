LangGraph 的 内存/记忆 机制总结 - 知乎
===============
[![Image 1](https://zhuanlan.zhihu.com/p/1915604388443031303)](javascript:void(0))

[](https://www.zhihu.com/)

[关注](https://www.zhihu.com/signin?next=%2Ffollow)[推荐](https://www.zhihu.com/signin?next=%2F)[热榜](https://www.zhihu.com/signin?next=%2Fhot)[专栏](https://www.zhihu.com/signin?next=%2Fcolumn-square)[圈子 New](https://www.zhihu.com/signin?next=%2Fring-feeds)[付费咨询](https://www.zhihu.com/consult)[知学堂](https://www.zhihu.com/education/learning)

​ 

[直答](https://zhida.zhihu.com/)

切换模式

登录/注册

LangGraph 的 内存/记忆 机制总结

首发于[Agent：AGI上路](https://www.zhihu.com/column/c_1310246938189443072)

切换模式

LangGraph 的 内存/记忆 机制总结
======================

[![Image 2: 王几行XING](https://pic1.zhimg.com/v2-116fdf676fa3d6a4f718e79e1cdbc326_l.jpg?source=32738c0c&needBackground=1)](https://www.zhihu.com/people/brycewang1898)

[王几行XING](https://www.zhihu.com/people/brycewang1898)

[​![Image 3](https://pica.zhimg.com/v2-2ddc5cc683982648f6f123616fb4ec09_l.png?source=32738c0c)](https://www.zhihu.com/question/48510028)

北京大学 计算机技术硕士

[收录于 · Agent：AGI上路](https://www.zhihu.com/column/c_1310246938189443072)

60 人赞同了该文章

​

目录

[LangGraph](https://zhida.zhihu.com/search?content_id=258826500&content_type=Article&match_order=1&q=LangGraph&zd_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ6aGlkYV9zZXJ2ZXIiLCJleHAiOjE3NzA1NDk5NDcsInEiOiJMYW5nR3JhcGgiLCJ6aGlkYV9zb3VyY2UiOiJlbnRpdHkiLCJjb250ZW50X2lkIjoyNTg4MjY1MDAsImNvbnRlbnRfdHlwZSI6IkFydGljbGUiLCJtYXRjaF9vcmRlciI6MSwiemRfdG9rZW4iOm51bGx9.mosUuxHdf4LMhoXIyamVDibKASWzMFmDMUzD0r3IE8U&zhida_source=entity) 的内存机制是一个核心功能，旨在为 AI 代理提供在不同交互中存储、检索和利用信息的能力。它区分了两种主要的内存类型：**[短期记忆](https://zhida.zhihu.com/search?content_id=258826500&content_type=Article&match_order=1&q=%E7%9F%AD%E6%9C%9F%E8%AE%B0%E5%BF%86&zd_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ6aGlkYV9zZXJ2ZXIiLCJleHAiOjE3NzA1NDk5NDcsInEiOiLnn63mnJ_orrDlv4YiLCJ6aGlkYV9zb3VyY2UiOiJlbnRpdHkiLCJjb250ZW50X2lkIjoyNTg4MjY1MDAsImNvbnRlbnRfdHlwZSI6IkFydGljbGUiLCJtYXRjaF9vcmRlciI6MSwiemRfdG9rZW4iOm51bGx9.wTTVEyTTEA2NiZvc29y3kDYxe_19FjDPNnI6ZI8zeUc&zhida_source=entity)（Short-term memory）** 和 **[长期记忆](https://zhida.zhihu.com/search?content_id=258826500&content_type=Article&match_order=1&q=%E9%95%BF%E6%9C%9F%E8%AE%B0%E5%BF%86&zd_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ6aGlkYV9zZXJ2ZXIiLCJleHAiOjE3NzA1NDk5NDcsInEiOiLplb_mnJ_orrDlv4YiLCJ6aGlkYV9zb3VyY2UiOiJlbnRpdHkiLCJjb250ZW50X2lkIjoyNTg4MjY1MDAsImNvbnRlbnRfdHlwZSI6IkFydGljbGUiLCJtYXRjaF9vcmRlciI6MSwiemRfdG9rZW4iOm51bGx9.dBnP3pQZW3OWZZBugZ95tAOM-6o-wwAPDWOsxNeQZpg&zhida_source=entity)（Long-term memory）**。

![Image 4](https://pica.zhimg.com/v2-706f18915006d5d65dafccbf8f16fb3e_1440w.jpg)

**1. 短期记忆（Short-term Memory / Thread-scoped Memory）**

*   **定义与范围：** 短期记忆是针对单个对话线程（或会话）的，可以在该线程内的任何时间被回忆。它类似于人类在一次对话中记住的内容。
*   **管理方式：** LangGraph 将短期记忆作为代理状态（State）**的一部分进行管理。这个状态会通过**[检查点](https://zhida.zhihu.com/search?content_id=258826500&content_type=Article&match_order=1&q=%E6%A3%80%E6%9F%A5%E7%82%B9&zd_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ6aGlkYV9zZXJ2ZXIiLCJleHAiOjE3NzA1NDk5NDcsInEiOiLmo4Dmn6XngrkiLCJ6aGlkYV9zb3VyY2UiOiJlbnRpdHkiLCJjb250ZW50X2lkIjoyNTg4MjY1MDAsImNvbnRlbnRfdHlwZSI6IkFydGljbGUiLCJtYXRjaF9vcmRlciI6MSwiemRfdG9rZW4iOm51bGx9.h09CmRiL-xtEPkmujcQ-JDM7ejDAyPBRBPdcjiMKPGM&zhida_source=entity)（Checkpointer）持久化到数据库中，这意味着即使会话中断，也可以随时恢复。
*   **更新机制：** 短期记忆在图被调用或某个步骤完成时更新，并在每个步骤开始时读取。
*   **典型应用：** 最常见的短期记忆形式是**对话历史（conversation history）**。
*   **长对话历史管理：** 针对长对话可能导致的上下文窗口限制和性能下降问题，LangGraph 提供了以下策略： 

    *   **编辑消息列表（Editing message lists）：**

    
        *   **直接删除：** 可以通过定义一个“reducer”函数（如 `manage_list`）来编程性地删除旧消息，例如保留最近的 N 条消息。
        *   **`RemoveMessage`：** 如果使用 LangChain 消息和 `add_messages` reducer，可以通过返回 `RemoveMessage` 对象来根据消息 ID 删除特定消息。

```python
def manage_list(existing: list, updates: Union[list, dict]):
    if isinstance(updates, list):
        # Normal case, add to the history
        return existing + updates
    elif isinstance(updates, dict) and updates["type"] == "keep":
        # You get to decide what this looks like.
        # For example, you could simplify and just accept a string "DELETE"
        # and clear the entire list.
        return existing[updates["from"]:updates["to"]]
    # etc. We define how to interpret updates

class State(TypedDict):
    my_list: Annotated[list, manage_list]

def my_node(state: State):
    return {
        # We return an update for the field "my_list" saying to
        # keep only values from index -5 to the end (deleting the rest)
        "my_list": {"type": "keep", "from": -5, "to": None}
    }
```

    *   **总结过去对话（Summarizing past conversations）：** 通过调用 [LLM](https://zhida.zhihu.com/search?content_id=258826500&content_type=Article&match_order=1&q=LLM&zd_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ6aGlkYV9zZXJ2ZXIiLCJleHAiOjE3NzA1NDk5NDcsInEiOiJMTE0iLCJ6aGlkYV9zb3VyY2UiOiJlbnRpdHkiLCJjb250ZW50X2lkIjoyNTg4MjY1MDAsImNvbnRlbnRfdHlwZSI6IkFydGljbGUiLCJtYXRjaF9vcmRlciI6MSwiemRfdG9rZW4iOm51bGx9.o_0EuAP9oT1XB9iopYd6GQLQ5sLIwV6Uqjn7aVtkxeI&zhida_source=entity) 对历史对话进行摘要，并将摘要作为新的上下文传入，以减少消息数量同时保留关键信息。这通常需要一个 `summary` 字段来存储和更新摘要。

![Image 5](https://pic1.zhimg.com/v2-1f20a420f724dea313f7bee52f96c7e0_1440w.jpg)

```python
from langgraph.graph import MessagesState
class State(MessagesState):
    summary: str

def summarize_conversation(state: State):

    # First, we get any existing summary
    summary = state.get("summary", "")

    # Create our summarization prompt
    if summary:

        # A summary already exists
        summary_message = (
            f"This is a summary of the conversation to date: {summary}\n\n"
            "Extend the summary by taking into account the new messages above:"
        )

    else:
        summary_message = "Create a summary of the conversation above:"

    # Add prompt to our history
    messages = state["messages"] + [HumanMessage(content=summary_message)]
    response = model.invoke(messages)

    # Delete all but the 2 most recent messages
    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
    return {"summary": response.content, "messages": delete_messages}
```

    *   **知道何时移除消息（Knowing when to remove messages）：**

    
        *   **令牌计数：** 基于消息历史的令牌数量来决定何时截断。
        *   **`trim_messages` 工具：** LangChain 提供了 `trim_messages` 工具，可以根据指定的策略（如 `last`）、令牌限制、模型要求（如 `start_on` 和 `end_on`）以及是否包含系统消息来修剪消息列表。

```python
from langchain_core.messages import RemoveMessage, AIMessage
from langgraph.graph import add_messages
# ... other imports

class State(TypedDict):
    # add_messages will default to upserting messages by ID to the existing list
    # if a RemoveMessage is returned, it will delete the message in the list by ID
    messages: Annotated[list, add_messages]

def my_node_1(state: State):
    # Add an AI message to the `messages` list in the state
    return {"messages": [AIMessage(content="Hi")]}

def my_node_2(state: State):
    # Delete all but the last 2 messages from the `messages` list in the state
    delete_messages = [RemoveMessage(id=m.id) for m in state['messages'][:-2]]
    return {"messages": delete_messages}
```

**2. 长期记忆（Long-term Memory）**

![Image 6](https://pic1.zhimg.com/v2-1f20a420f724dea313f7bee52f96c7e0_1440w.jpg)

*   **定义与范围：** 长期记忆是跨对话线程共享的，可以在任何时间、任何线程中被回忆。它不像短期记忆那样局限于单个会话。
*   **存储方式：** LangGraph 将长期记忆存储为 JSON 文档，并使用**存储（Store）**（如 `InMemoryStore` 或生产环境中的数据库支持的存储）进行管理。
*   **组织结构：** 每个记忆都组织在一个自定义的命名空间（namespace）**和一个唯一的**键（key）下。命名空间通常包含用户 ID、组织 ID 或其他标签，便于分层组织信息，并支持跨命名空间的搜索（通过内容过滤器）。
*   **长期记忆的思考框架：**

    *   **记忆类型：**

    
        *   **语义记忆（Semantic Memory）：** 存储事实和概念。 

        
            *   **Profile（档案）：** 将关于用户、组织或代理自身的特定信息存储为一个持续更新的 JSON 文档。需要模型能够生成新的档案或 JSON 补丁来更新现有档案。
            *   **Collection（集合）：** 将记忆存储为一组独立的文档，每个文档范围更窄。易于生成，但搜索和更新（删除或修改现有文档）可能更复杂，且可能难以捕获记忆间的完整上下文。 

        *   **情景记忆（Episodic Memory）：** 存储过去的事件或行为经验。常通过少样本示例（few-shot example prompting）实现，代理通过学习过去的序列来正确执行任务。LangSmith Dataset 也可以用于存储少样本示例并支持动态检索。
        *   **程序记忆（Procedural Memory）：** 存储执行任务的规则或指令。通常通过修改代理自身的提示（prompt）**来实现，例如通过**“反射”（Reflection）或元提示，让代理根据对话和用户反馈来改进其指令。

    *   **记忆更新时机：**

    
        *   **[热路径](https://zhida.zhihu.com/search?content_id=258826500&content_type=Article&match_order=1&q=%E7%83%AD%E8%B7%AF%E5%BE%84&zd_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ6aGlkYV9zZXJ2ZXIiLCJleHAiOjE3NzA1NDk5NDcsInEiOiLng63ot6_lvoQiLCJ6aGlkYV9zb3VyY2UiOiJlbnRpdHkiLCJjb250ZW50X2lkIjoyNTg4MjY1MDAsImNvbnRlbnRfdHlwZSI6IkFydGljbGUiLCJtYXRjaF9vcmRlciI6MSwiemRfdG9rZW4iOm51bGx9.32SDWah_BgskDscCuoW6dyeM72_d8kIFCcP304-nyNg&zhida_source=entity)（Hot Path）：** 在代理的应用程序逻辑运行时实时创建记忆。优点是实时更新和透明度，但可能增加复杂性、延迟，并影响记忆的数量和质量。例如 ChatGPT 使用 `save_memories` 工具。
        *   **[后台](https://zhida.zhihu.com/search?content_id=258826500&content_type=Article&match_order=1&q=%E5%90%8E%E5%8F%B0&zd_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ6aGlkYV9zZXJ2ZXIiLCJleHAiOjE3NzA1NDk5NDcsInEiOiLlkI7lj7AiLCJ6aGlkYV9zb3VyY2UiOiJlbnRpdHkiLCJjb250ZW50X2lkIjoyNTg4MjY1MDAsImNvbnRlbnRfdHlwZSI6IkFydGljbGUiLCJtYXRjaF9vcmRlciI6MSwiemRfdG9rZW4iOm51bGx9.WoEdcjSRNYL17ho_5lK46_-Ioz64uH3azNrmrV-AqtQ&zhida_source=entity)（Background）：** 作为单独的异步任务创建记忆。优点是避免主应用延迟、分离逻辑，并允许更聚焦的任务完成。挑战在于确定更新频率和触发时机（例如，按时间、Cron 任务或手动触发）。

LangGraph 内存机制与主流 Agent 框架的对比
-----------------------------

**1. 细粒度的内存类型区分：**

*   **LangGraph 的优势：** LangGraph 明确区分了短期记忆（会话级）和长期记忆（跨会话），并进一步将长期记忆细化为语义记忆（事实）、情景记忆（经验）和程序记忆（规则）。这种细粒度的区分和管理方式在主流框架中相对不常见。许多框架可能提供单一的“记忆”组件，但其内部实现和用途不如 LangGraph 这样有明确的心理学类比和对应策略。
*   **对比：**

    *   **LangChain Agents：** LangChain 提供了多种记忆组件，如 `ConversationBufferMemory`（短期记忆），`ConversationSummaryBufferMemory`（带总结的短期记忆），以及通过向量存储实现的 `VectorStoreRetrieverMemory`（长期记忆）。虽然功能类似，但 LangGraph 更系统地将这些归类到短期/长期/子类型中，并提供了更直接的图内状态管理和更新机制。LangChain 的记忆组件通常是独立的模块，需要手动集成到 Agent 执行链中。
    *   **AutoGen：** AutoGen 更侧重于多代理协作和对话管理。其记忆机制主要体现在消息传递和历史记录中，以便代理可以参考之前的对话。对于长期记忆，通常需要结合外部数据库或向量存储来实现，不像 LangGraph 这样直接集成到其核心的“状态”和“存储”概念中。AutoGen 更多的是通过“对话历史”来维持上下文，缺乏 LangGraph 对“语义”、“情景”和“程序”记忆的明确区分和内置处理策略。
    *   **CrewAI：** CrewAI 专注于多代理协作和任务执行。它的记忆主要通过“共享上下文”和“任务历史”来体现，代理可以访问这些信息以完成任务。对于长期记忆，也需要结合外部工具和存储，其内置的记忆管理不如 LangGraph 这样具有明确的类型和更新流程。

**2. 基于图的状态管理（短期记忆）：**

*   **LangGraph 的优势：** LangGraph 将短期记忆作为其核心**图状态（Graph State）**的一部分进行管理，并通过内置的“reducer”函数实现状态的原子性更新。这种基于图的状态机模式使得管理对话历史和相关上下文（如上传文件、检索文档）变得非常自然和强大。检查点机制保证了会话的可恢复性。
*   **对比：**

    *   **LangChain Agents：** LangChain Agent 通常通过将记忆组件集成到 Agent 的 `memory` 参数中来管理短期记忆。虽然也能实现类似功能，但 LangGraph 的状态管理更加声明式和集成化，直接在图的节点中定义如何修改状态，包括记忆。
    *   **AutoGen / CrewAI：** 这些框架的短期记忆管理通常依赖于消息传递和历史记录列表。虽然它们也维护了会话上下文，但不如 LangGraph 的“状态”概念那样灵活和可编程，可以轻松地包含除了消息以外的其他状态数据。

**3. 内置的长期记忆存储和管理：**

*   **LangGraph 的优势：** LangGraph 提供了一个明确的 `Store` 抽象，用于存储和检索长期记忆（JSON 文档）。它支持命名空间和内容过滤/向量相似性搜索，并提供了“profile”和“collection”两种不同的语义记忆管理模式。这种抽象使得长期记忆的集成更为直接。
*   **对比：**

    *   **LangChain Agents：** LangChain 同样支持与向量存储和各种数据库集成以实现长期记忆，但通常是通过“检索器（Retrievers）”和“文档加载器（Document Loaders）”等工具来实现。LangGraph 的 `Store` 概念更像一个内置的“记忆数据库”抽象，专门为长期记忆设计，并提供更直接的 Put/Get/Search 接口。
    *   **AutoGen / CrewAI：** 通常需要用户自行集成外部数据库或向量存储来管理长期记忆。这些框架本身更侧重于代理的逻辑和协作，而不是记忆的存储和检索细节。LangGraph 在这方面提供了更“开箱即用”的长期记忆解决方案。 

**4. 明确的记忆写入策略：**

*   **LangGraph 的优势：** LangGraph 提出了“热路径”和“后台”两种记忆写入策略，并讨论了它们的优缺点。这为开发者提供了关于何时以及如何将信息提交到长期记忆的明确指导。
*   **对比：** 大多数其他框架可能不会如此明确地提出和讨论记忆写入的策略。开发者通常需要根据自己的应用逻辑来决定何时更新记忆，这可能需要更多的自定义实现。

**总结而言，LangGraph 的内存机制具有以下特点，使其在某些方面优于其他主流 Agent 框架：**

*   **更系统、更细致的内存分类和管理：** 明确区分短期和长期，并细化长期记忆类型。
*   **基于图的状态管理：** 短期记忆与图的状态紧密结合，提供了强大的状态更新和持久化能力。
*   **内置的长期记忆存储抽象：** 提供了一套用于存储和检索长期记忆的标准化接口和概念。
*   **明确的记忆写入策略指导：** 帮助开发者更好地设计记忆更新流程。

* * *

LangGraph 记忆机制的具体实现
-------------------

LangGraph 记忆机制的实现方式主要围绕其短期记忆（作为图状态的一部分）和长期记忆（通过 `Store` 抽象）来展开。

LangGraph 记忆机制的快速总结实现方式：

1.   **短期记忆（Short-term Memory）**

*   **作为图的状态（Graph State）的一部分：**

    *   **`TypedDict` 定义状态：** 定义一个 `TypedDict` 来表示代理的整个状态，其中包含一个列表（通常是 `messages`）来存储对话历史。
    *   **`Annotated` 和 Reducer 函数：** 使用 `Annotated` 结合自定义的 "reducer" 函数（如 `manage_list` 或 LangGraph 内置的 `add_messages`）来定义状态字段（例如消息列表）如何被更新。
    *   **节点返回更新：** 在图的节点中，返回一个字典，其中包含要更新的状态字段及其新的值或更新指令。reducer 函数会根据这些指令处理列表的增、删、改。

*   **持久化：**

    *   **`Checkpointer`：** 配置一个 `Checkpointer`（例如 `SQLiteSaver` 或其他数据库支持的 Saver）来自动将图的状态持久化到数据库中，实现会话的恢复。

*   **长对话管理：**

    *   **编程删除：** 在 reducer 函数中实现逻辑，根据索引、数量或其他条件删除旧消息。
    *   **`RemoveMessage` 对象：** 如果使用 LangChain 消息，在节点中返回 `RemoveMessage(id=...)` 对象，`add_messages` reducer 会根据 ID 删除消息。
    *   **LLM 摘要：** 设计一个专门的图节点，调用 LLM 对消息历史进行摘要，并将摘要作为状态的一部分（如 `summary` 字段）保存。然后可以删除部分旧消息，减少上下文长度。
    *   **`trim_messages` 工具：** 使用 LangChain 的 `trim_messages` 效用函数，根据令牌限制、策略（如 `last`）、模型要求等智能地截断消息列表。 

2. **长期记忆（Long-term Memory）**

    *   **`Store` 抽象：**

    
        *   **实例化 Store：** 使用 `langgraph.store.memory.InMemoryStore` 进行测试，或使用专门的数据库集成 Store（例如针对生产环境的向量数据库集成）来存储长期记忆。
        *   **命名空间和键：** 在 `store.put()`、`store.get()` 和 `store.search()` 方法中，使用元组作为 `namespace`（例如 `(user_id, application_context)`）和字符串作为 `key` 来组织和识别记忆。

    *   **记忆内容的存储：**

    
        *   **JSON 文档：** 长期记忆以 JSON 文档的形式存储在 `Store` 中，允许存储结构化或非结构化的事实、经验或规则。 

    *   **记忆的写入（在图节点中实现）：**

    
        *   **热路径：** 在图的一个节点中直接调用 `store.put()` 来写入记忆。这通常涉及到让代理（通过 LLM 调用）决定何时以及如何写入记忆，并可能作为工具调用。
        *   **后台：** 通过异步任务、定时任务（cron job）或在图之外的单独服务中，调用 `store.put()` 来写入记忆，不阻塞主应用流程。 

    *   **记忆的检索（在图节点中实现）：**

    
        *   **`store.get()`：** 根据命名空间和键精确获取记忆。
        *   **`store.search()`：** 根据命名空间、内容过滤器和/或向量相似性查询来搜索相关记忆。这通常需要 `Store` 配置一个嵌入函数 (`embed`) 来支持语义搜索。

    *   **记忆的应用：**

    
        *   **语义记忆：** 将检索到的事实（`Profile` 或 `Collection`）作为上下文或系统指令的一部分传递给 LLM，用于个性化响应或回答事实性问题。
        *   **情景记忆：** 检索相关的少样本示例，将其添加到 LLM 的提示中，以指导模型完成任务（即“演示”行为）。
        *   **程序记忆：** 检索更新后的系统提示或指令，将其用于 LLM 的调用中。代理也可以在节点中根据反馈修改并更新自己的指令，再存回 `Store`。

总的来说，LangGraph 通过其灵活的**图状态管理**和抽象的**`Store` 接口**，为 AI 代理提供了全面且可定制的短期和长期记忆实现方式。

* * *

对话记录的保存和调用
----------

方法一：state 中添加历史字段（如 history），完美地概括了 LangGraph 实现对话历史记录的核心机制。

1.   **将对话历史作为图状态（Graph State）的一部分：**

*   在 LangGraph 中，整个代理的“记忆”或上下文被封装在一个被称为**“图状态”（Graph State）**的特殊字典（通常是 `TypedDict`）中。
*   为了记录对话历史，你需要在 `Graph State` 中定义一个特定的字段来保存消息列表。比如我们可以 使用`history` 字段。
*   **示例 (`AgentState` 定义)：**

```python
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage # 或其他你使用的消息类型

class AgentState(TypedDict):
    # history 字段用于存储对话消息的列表
    history: Annotated[list[BaseMessage], some_reducer_function]
    # 可以有其他字段，例如例子中提到的 'gov_message' 或其他需要跨轮次传递的数据
    gov_message: str
    # ... 其他状态字段
```

    *   **解释：** 这里的 `history` 字段就承载了 LangGraph 的“短期记忆”功能。它是一个列表，随着对话的进行，新的消息会被添加到这个列表中。

2. **通过节点（Node）来更新历史字段：**

    *   LangGraph 中的每个“节点”（Node）都是图中的一个处理单元（一个 Python 函数）。当一个节点执行完毕后，它可以返回一个字典，其中的键值对表示对图状态的更新。
    *   **核心逻辑举例：**`state["history"] = state.get("history", []) + [f"政府: {state['gov_message']}"]`

    
        *   **`state.get("history", [])`：** 这表示节点首先**读取**当前图状态中的 `history` 字段。如果这是第一次，`history` 可能不存在，所以 `get` 方法会返回一个空列表 `[]` 作为默认值。
        *   **`+ [f"政府: {state['gov_message']}"]`：** 节点然后将新的消息（这里是一个格式化的字符串，可能是来自一个名为 `gov_message` 的状态字段）**追加**到读取到的现有 `history` 列表中。
        *   **`state["history"] = ...`：** 最后，将更新后的整个列表赋值回 `history` 字段。 

    *   **LangGraph 内部的实现：** 在实际的 LangGraph 代码中，这种追加行为通常通过**“Reducer 函数”**自动化。你不需要手动写 `state.get(...) + [...]`。当你定义 `history: Annotated[list[BaseMessage], add_messages]` 时，LangGraph 会自动调用 `add_messages` 这个 reducer，它会处理消息的追加、更新和删除。 

    
        *   一个节点只需返回：`{"history": [AIMessage(content="新的回复")]}`。
        *   `add_messages` reducer 会负责将其正确添加到 `AgentState` 中的 `history` 列表中。

3. **在构建 Prompt 时利用历史记录：**

    *   `每个 node 在构建 prompt 时读取 history 并追加新的输入`
    *   当需要调用大型语言模型（LLM）时，下游的节点会从 `Graph State` 中**读取**`history` 字段，将其作为完整的对话上下文（prompt 的一部分）传递给 LLM。
    *   LLM 能够根据之前的对话内容生成连贯且相关的回复。

4. **持久化（LangGraph 的额外能力）：**

    *    LangGraph 提供 `Checkpointer` 机制。这意味着上述存储在 `history` 字段中的对话记录，可以被自动持久化到数据库（如 SQLite 或其他外部数据库）中。
    *   这使得即使应用程序重启或用户断开连接，对话历史也能被保存和恢复，从而实现“真正的多轮记忆”。

**总结来说，LangGraph 实现对话历史记录的核心流程是：**

1.   **状态定义：** 在 LangGraph 的 `Graph State` 中，定义一个专门的列表字段（如 `history` 或 `messages`）来承载对话消息。
2.   **自动更新：** 节点返回的新消息会通过与该字段关联的“reducer”函数（如 `add_messages`）自动追加到历史列表中。Reducer 还能处理消息的更新和删除。
3.   **上下文利用：** 任何需要对话上下文的节点（特别是调用 LLM 的节点）都会读取这个历史列表，将其作为构建 LLM prompt 的一部分。
4.   **持久化：** 通过 `Checkpointer`，整个包含对话历史在内的图状态可以被保存和恢复，确保记忆的连续性。

这种方法相比 LangChain 的 ConversationBufferMemory -- 虽然 LangChain 的 Memory 类提供了封装好的功能，但 LangGraph 的方法更底层、更集成在它的状态机范式中，提供了更细粒度的控制和更高的灵活性，尤其是在多代理、复杂流程中管理状态时。

（文章结束）

编辑于 2025-06-09 21:44・美国

[langgraph](https://www.zhihu.com/topic/30114083)

[LangChain](https://www.zhihu.com/topic/27269779)

[大模型](https://www.zhihu.com/topic/25402720)

[多知识任务还在排队做？腾讯ima同步处理省时间 微信文件一键转存至腾讯ima知识库，让你想用的时候随时都能用，还能对知识库里的文件进行深层次解析哦 查看详情 微信文件一键转存至腾讯ima知识库，让你想用的时候随时都能用，还能对知识库里的文件进行深层次解析哦 查看详情 ![Image 7: 用户头像](https://pic1.zhimg.com/v2-6bcab51aab5519d3e668f35b0a210fc3_xl.webp?source=d6434cab) ima 的广告](https://ima.qq.com/download/?webFrom=10000435&channel=10000435&cb=https%3A%2F%2Fsugar.zhihu.com%2Fplutus_adreaper_callback%3Fsi%3Dc0734dd9-e648-451f-a722-324ee8ff627c%26os%3D3%26zid%3D1629%26zaid%3D3691187%26zcid%3D3655473%26cid%3D3655421%26event%3D__EVENTTYPE__%26value%3D__EVENTVALUE__%26ts%3D__TIMESTAMP__%26cts%3D__TS__%26mh%3D__MEMBERHASHID__%26adv%3D703838%26ocg%3D4%26cp%3D2500%26ocs%3D1%26aic%3D0%26atp%3D0%26ct%3D2%26ed%3DGiBNJgVzfCMmUW9XIVDVNQZREwA%3D&spu=biz%3D0%26ci%3D3655473%26si%3Dcbbc0405-3256-41a8-aacf-92b44f654247%26ts%3D1770377150%26zid%3D1629)

​赞同 60​​2 条评论

​分享

​喜欢​收藏​申请转载​

​

![Image 8](https://pic1.zhimg.com/v2-d41c2ceaed8f51999522f903672a521f_l.jpeg)

未登录用户

2 条评论

默认

最新

[![Image 9: 时空猫的问答盒](https://picx.zhimg.com/v2-f42e799e51867bb6d8d3c1e7900f3d8c_l.jpg?source=06d4cd63)](https://www.zhihu.com/people/ee64df39e8371d47f77034ec313bf885)

[时空猫的问答盒](https://www.zhihu.com/people/ee64df39e8371d47f77034ec313bf885)

​![Image 10](https://pic1.zhimg.com/v2-2ddc5cc683982648f6f123616fb4ec09_l.png?source=32738c0c)

![Image 11: [感谢]](https://pic1.zhimg.com/v2-694cac2ec9f3c63f774e723f77d8c840.png)![Image 12: [感谢]](https://pic1.zhimg.com/v2-694cac2ec9f3c63f774e723f77d8c840.png)![Image 13: [感谢]](https://pic1.zhimg.com/v2-694cac2ec9f3c63f774e723f77d8c840.png)

2025-06-10 · 上海

​回复​2

[![Image 14: 厘米](https://pic1.zhimg.com/v2-abed1a8c04700ba7d72b45195223e0ff_l.jpg?source=06d4cd63)](https://www.zhihu.com/people/90295ed6598ceb9fa1dbf8f0ee104928)

[厘米](https://www.zhihu.com/people/90295ed6598ceb9fa1dbf8f0ee104928)

请问如果我从pgsql种读取了历史的state，可以实现修改某个节点再replay吗

2025-07-19 · 江苏

​回复​1

[](https://zhuanlan.zhihu.com/p/1915604388443031303)

关于作者

[![Image 15: 王几行XING](https://pic1.zhimg.com/v2-116fdf676fa3d6a4f718e79e1cdbc326_l.jpg?source=32738c0c&needBackground=1)](https://www.zhihu.com/people/brycewang1898)

[王几行XING](https://www.zhihu.com/people/brycewang1898)

Go fast or go home.

[​](https://zhuanlan.zhihu.com/p/96956163)

北京大学 计算机技术硕士

[回答 **192**](https://www.zhihu.com/people/brycewang1898/answers)[文章 **981**](https://www.zhihu.com/people/brycewang1898/posts)[关注者 **15,432**](https://www.zhihu.com/people/brycewang1898/followers)

​关注他​发私信

大家都在搜

换一换

[快手被罚款1.191亿元 399 万](https://www.zhihu.com/search?q=%E5%BF%AB%E6%89%8B%E8%A2%AB%E7%BD%9A%E6%AC%BE1.191%E4%BA%BF%E5%85%83&search_source=Trending&utm_content=search_hot&utm_medium=organic&utm_source=zhihu&type=content)新

[小洛熙事件最新通报 399 万](https://www.zhihu.com/search?q=%E5%B0%8F%E6%B4%9B%E7%86%99%E4%BA%8B%E4%BB%B6%E6%9C%80%E6%96%B0%E9%80%9A%E6%8A%A5&search_source=Trending&utm_content=search_hot&utm_medium=organic&utm_source=zhihu&type=content)热

[美司法部公布爱泼斯坦案剩余文件 398 万](https://www.zhihu.com/search?q=%E7%BE%8E%E5%8F%B8%E6%B3%95%E9%83%A8%E5%85%AC%E5%B8%83%E7%88%B1%E6%B3%BC%E6%96%AF%E5%9D%A6%E6%A1%88%E5%89%A9%E4%BD%99%E6%96%87%E4%BB%B6&search_source=Trending&utm_content=search_hot&utm_medium=organic&utm_source=zhihu&type=content)热

[克林顿夫妇为爱泼斯坦案作证 336 万](https://www.zhihu.com/search?q=%E5%85%8B%E6%9E%97%E9%A1%BF%E5%A4%AB%E5%A6%87%E4%B8%BA%E7%88%B1%E6%B3%BC%E6%96%AF%E5%9D%A6%E6%A1%88%E4%BD%9C%E8%AF%81&search_source=Trending&utm_content=search_hot&utm_medium=organic&utm_source=zhihu&type=content)热

[美团拟7.17亿美元收购叮咚 318 万](https://www.zhihu.com/search?q=%E7%BE%8E%E5%9B%A2%E6%8B%9F7.17%E4%BA%BF%E7%BE%8E%E5%85%83%E6%94%B6%E8%B4%AD%E5%8F%AE%E5%92%9A&search_source=Trending&utm_content=search_hot&utm_medium=organic&utm_source=zhihu&type=content)热

[我国明年起禁隐藏式车门把手 300 万](https://www.zhihu.com/search?q=%E6%88%91%E5%9B%BD%E6%98%8E%E5%B9%B4%E8%B5%B7%E7%A6%81%E9%9A%90%E8%97%8F%E5%BC%8F%E8%BD%A6%E9%97%A8%E6%8A%8A%E6%89%8B&search_source=Trending&utm_content=search_hot&utm_medium=organic&utm_source=zhihu&type=content)热

[立陶宛新总理承认对华犯大错 285 万](https://www.zhihu.com/search?q=%E7%AB%8B%E9%99%B6%E5%AE%9B%E6%96%B0%E6%80%BB%E7%90%86%E6%89%BF%E8%AE%A4%E5%AF%B9%E5%8D%8E%E7%8A%AF%E5%A4%A7%E9%94%99&search_source=Trending&utm_content=search_hot&utm_medium=organic&utm_source=zhihu&type=content)

[周生生涉事挂坠送检结果为足金 276 万](https://www.zhihu.com/search?q=%E5%91%A8%E7%94%9F%E7%94%9F%E6%B6%89%E4%BA%8B%E6%8C%82%E5%9D%A0%E9%80%81%E6%A3%80%E7%BB%93%E6%9E%9C%E4%B8%BA%E8%B6%B3%E9%87%91&search_source=Trending&utm_content=search_hot&utm_medium=organic&utm_source=zhihu&type=content)热

[老人给婴儿喂酒致肝损伤 252 万](https://www.zhihu.com/search?q=%E8%80%81%E4%BA%BA%E7%BB%99%E5%A9%B4%E5%84%BF%E5%96%82%E9%85%92%E8%87%B4%E8%82%9D%E6%8D%9F%E4%BC%A4&search_source=Trending&utm_content=search_hot&utm_medium=organic&utm_source=zhihu&type=content)

[小洛熙事件医方存在多项过失 249 万](https://www.zhihu.com/search?q=%E5%B0%8F%E6%B4%9B%E7%86%99%E4%BA%8B%E4%BB%B6%E5%8C%BB%E6%96%B9%E5%AD%98%E5%9C%A8%E5%A4%9A%E9%A1%B9%E8%BF%87%E5%A4%B1&search_source=Trending&utm_content=search_hot&utm_medium=organic&utm_source=zhihu&type=content)

[广告 专业问题想找定制答案？腾讯ima知识库来匹配 ![Image 16: 广告](https://pic2.zhimg.com/v2-4fc62378de2f9878c53fc658e678609e.webp?source=d6434cab)](https://ima.qq.com/download/?webFrom=10000435&channel=10000435&cb=https%3A%2F%2Fsugar.zhihu.com%2Fplutus_adreaper_callback%3Fsi%3D5374d167-aec2-46b2-bca5-7b11b4511a7b%26os%3D3%26zid%3D6001%26zaid%3D3671866%26zcid%3D3629654%26cid%3D3629654%26event%3D__EVENTTYPE__%26value%3D__EVENTVALUE__%26ts%3D__TIMESTAMP__%26cts%3D__TS__%26mh%3D__MEMBERHASHID__%26adv%3D703838%26ocg%3D4%26cp%3D2500%26ocs%3D1%26aic%3D0%26atp%3D0%26ct%3D2%26ed%3DGiBNJgVzfCMmUW9XIVDVNQZREwA%3D&spu=biz%3D0%26ci%3D3629654%26si%3D3001e117-1a6e-4678-a236-2ebfc3e26632%26ts%3D1770377151%26zid%3D6001)

### 推荐阅读

[![Image 17: 机器如何拥有长期记忆？DeepMind解读，最新长程记忆模型和数据库](https://pic1.zhimg.com/v2-d0d27802e550ce017a85e6e1f8d9a42e_250x0.jpg?source=172ae18b) 机器如何拥有长期记忆？DeepMind解读，最新长程记忆模型和数据库 ================================== 量子位 发表于量子位](https://zhuanlan.zhihu.com/p/106550091)[利用LSTM(长短期记忆网络)来处理脑电数据 ====================== 文章来源于公众号&#34;脑机接口社区&#34; 利用LSTM(长短期记忆网络)来处理脑电数据Rose小哥今天介绍一下用LSTM来处理脑电数据。 LSTMs(Long Short Term Memory networks，长短期记忆网络)简… 脑机接口社...发表于脑机接口社...](https://zhuanlan.zhihu.com/p/111687451)[![Image 18: 4k窗口长度就能读长文，陈丹琦高徒联手Meta推出大模型记忆力增强新方法](https://pic1.zhimg.com/v2-5ef59a2ea0777ea4afaa7cca617d56f9_250x0.jpg?source=172ae18b) 4k窗口长度就能读长文，陈丹琦高徒联手Meta推出大模型记忆力增强新方法 ==================================== 量子位 发表于量子位](https://zhuanlan.zhihu.com/p/663060958)[![Image 19: DeepSeek V4 发布在即，Engram 框架提前开源，为何能修复 LLM 失忆症](https://pic1.zhimg.com/v2-5645644ad57f711a82300bdcb95f9d1f_250x0.jpg?source=172ae18b) DeepSeek V4 发布在即，Engram 框架提前开源，为何能修复 LLM 失忆症 ============================================ 人工智能研究所](https://zhuanlan.zhihu.com/p/1999218832183681108)

_想来知乎工作？请发送邮件到 jobs@zhihu.com_

打开知乎App

在「我的页」右上角打开扫一扫

![Image 20](https://picx.zhimg.com/v2-9e41ea16bdfbe9cf4896617ecad5b4ca.png)

其他扫码方式：微信

下载知乎App

无障碍模式

验证码登录

密码登录

[开通机构号](https://zhuanlan.zhihu.com/org/signup)

中国 +86

获取短信验证码

获取语音验证码

登录/注册

其他方式登录

未注册手机验证后自动登录，注册即代表同意[《知乎协议》](https://www.zhihu.com/term/zhihu-terms)[《隐私保护指引》](https://www.zhihu.com/term/privacy)

扫码下载知乎 App

关闭二维码

打开知乎App

在「我的页」右上角打开扫一扫

![Image 21](https://picx.zhimg.com/v2-9e41ea16bdfbe9cf4896617ecad5b4ca.png)

其他扫码方式：微信

下载知乎App

无障碍模式

验证码登录

密码登录

[开通机构号](https://zhuanlan.zhihu.com/org/signup)

中国 +86

获取短信验证码

获取语音验证码

登录/注册

其他方式登录

未注册手机验证后自动登录，注册即代表同意[《知乎协议》](https://www.zhihu.com/term/zhihu-terms)[《隐私保护指引》](https://www.zhihu.com/term/privacy)

扫码下载知乎 App

关闭二维码