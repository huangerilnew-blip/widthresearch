# [火山引擎 ADG 社区](https://adg.csdn.net "火山引擎 ADG 社区")

## 登录社区云

### 火山引擎 ADG 社区

欢迎加入社区

[火山引擎 ADG 社区](https://adg.csdn.net)   LangGraph持久化机制详解：让AI智能体拥有记忆能力，从入门到实践

# LangGraph持久化机制详解：让AI智能体拥有记忆能力，从入门到实践

### [AGI大模型老王](https://devpress.csdn.net/user/2401_85390073)

[996人浏览 · 2025-12-16 14:45:23](https://devpress.csdn.net/user/2401_85390073)

 [AGI大模型老王](https://devpress.csdn.net/user/2401_85390073)  ·  2025-12-16 14:45:23 发布

本文详细介绍了LangGraph的持久化机制，通过Thread和Checkpoint概念，使AI智能体具备记忆能力。持久化机制支持多轮对话、状态恢复、人工介入和时间旅行等场景，提供了InMemorySaver、SqliteSaver、PostgresSaver和RedisSaver等多种实现方式。理解这些核心概念对于构建高质量AI智能体应用至关重要。

---

本文为 LangGranph 系列的第三篇，介绍 LangGraph 的持久化机制，看看它是如何让 AI 智能体拥有"记忆"能力的，主要内容如下：

1. AI智能体为什么需要持久化
2. LangGraph 的持久化机制的相关概念介绍
3. 持久化实现的编程示例
4. 持久化机制的应用场景

#### 为什么需要持久化？

在实际的 AI 智能体应用中，经常会遇到这样的场景：

* 💬 **多轮对话**：用户问"我的名字是什么？"，智能体需要记住之前用户说过的话
* 🔄 **状态恢复**：智能体执行到一半出错了，需要从上次成功的地方继续
* 🕐 **时间旅行**：想要回看智能体之前的执行过程，用于调试和分析
* 👤 **人工介入**：在关键步骤需要人工审核和干预

这些场景都离不开一个核心能力：**状态持久化**。LangGraph 通过一套完整的持久化机制，让这些需求成为可能。

#### 理解 LangGraph 的基础概念

在深入持久化机制之前，需要先理解几个核心概念，这些概念是理解持久化机制的基础。

##### Graph（图）

在 LangGraph 中，Graph 是一个有向图结构，由节点（Node）和边（Edge）组成。每个节点代表一个处理单元，边定义了节点之间的执行顺序。

```
from langgraph.graph import StateGraph, START, END# 创建一个图builder = StateGraph(State)# 添加节点builder.add_node("node_a", function_a)builder.add_node("node_b", function_b)# 添加边，定义执行流程builder.add_edge(START, "node_a") # 从开始到节点 Abuilder.add_edge("node_a", "node_b") # 从节点 A 到节点 Bbuilder.add_edge("node_b", END) # 从节点 B 到结束# 编译图graph = builder.compile() 
```

图定义了智能体的执行流程，就像一个工作流引擎，按照预定义的路径执行各个节点。

##### Super-steps（超级步骤）

Super-step 是 LangGraph 执行图的一个关键概念。理解 super-step 需要区分两种情况：

**情况一：简单线性图（一个 super-step = 一个节点）**

在简单的线性图中，每个 super-step 通常只执行一个节点：

```
# 简单的线性图：START -> node_a -> node_b -> ENDbuilder.add_edge(START, "node_a")builder.add_edge("node_a", "node_b")builder.add_edge("node_b", END)# 执行过程：# Super-step 1: 执行 node_a，保存 checkpoint_1# Super-step 2: 执行 node_b，保存 checkpoint_2 
```

这种情况下，一个 super-step 确实对应一个节点的执行。

**情况二：复杂图（一个 super-step = 多个并行节点）**

在复杂的图中，如果多个节点没有依赖关系，它们可以在同一个 super-step 中并行执行：

```
# 复杂图：START -> node_a -> [node_b, node_c] -> node_d -> ENDbuilder.add_edge(START, "node_a")builder.add_edge("node_a", "node_b") # node_b 依赖 node_abuilder.add_edge("node_a", "node_c") # node_c 也依赖 node_abuilder.add_edge("node_b", "node_d") # node_d 依赖 node_bbuilder.add_edge("node_c", "node_d") # node_d 也依赖 node_c# 执行过程：# Super-step 1: 执行 node_a，保存 checkpoint_1# Super-step 2: 并行执行 node_b 和 node_c（它们都依赖 node_a，但彼此独立），保存 checkpoint_2# Super-step 3: 执行 node_d（等待 node_b 和 node_c 都完成），保存 checkpoint_3 
```

这种情况下，Super-step 2 包含了两个节点的并行执行。

**Super-step 的执行过程**

无论哪种情况，每个 super-step 都包含以下过程：

1. **读取当前状态**：从上一个 checkpoint 恢复状态
2. **确定可执行节点**：找出所有依赖已满足、可以执行的节点
3. **执行节点**：执行这些节点（可能是一个，也可能是多个并行）
4. **合并状态**：将各个节点的输出合并到状态中
5. **保存 checkpoint**：将当前状态保存为新的 checkpoint

**关键理解**：Super-step 不是按节点数量定义的，而是按"所有依赖都满足后，执行所有准备好的节点"这个逻辑定义的。在简单情况下，可能只有一个节点准备好；在复杂情况下，可能有多个节点可以并行执行。

每个 super-step 都会自动保存一个 checkpoint，这就是持久化机制的基础。即使程序中断，也能从最后一个 super-step 的 checkpoint 恢复执行。

##### StateSnapshot（状态快照）

StateSnapshot 是 checkpoint 的具体表示形式，它完整记录了图在某个时间点的状态信息。每个 StateSnapshot 包含以下关键属性：

* `values`：状态通道的当前值，这是图的核心数据
* `next`：下一步要执行的节点名称元组
* `config`：配置信息，包括 thread\_id 和 checkpoint\_id
* `metadata`：元数据，记录执行信息，如步骤号、写入的节点等
* `created_at`：checkpoint 的创建时间
* `parent_config`：父 checkpoint 的配置信息
* `tasks`：待执行的任务信息

```
# 获取一个 StateSnapshot 示例snapshot = graph.get_state({"configurable": {"thread_id": "1"}})print(snapshot.values) # {'messages': [...], 'foo': 'bar'}print(snapshot.next) # ('node_a', 'node_b') 或 () 表示执行完成print(snapshot.metadata) # {'step': 2, 'writes': {...}, 'source': 'loop'}print(snapshot.config) # {'configurable': {'thread_id': '1', ...}} 
```

StateSnapshot 不仅保存了状态数据，还保存了执行上下文，这使得时间旅行和状态恢复成为可能。

##### 三者之间的关系

这三个概念紧密相关：

图定义了执行流程，super-step 是执行单位，StateSnapshot 记录状态，checkpoint 将状态持久化保存。

#### 核心概念：Thread 和 Checkpoint

理解了基础概念后，现在来看持久化机制的两个核心概念：

##### Thread（线程）

Thread 可以理解为一个对话会话的唯一标识符。每次调用图时，需要指定一个 `thread_id`，所有相关的状态都会被保存到这个线程中。

```
config = {"configurable": {"thread_id": "conversation_1"}}graph.invoke(input_data, config) 
```

不同的 `thread_id` 对应不同的会话，它们之间互不干扰。这样就能同时处理多个用户的对话，每个用户都有自己独立的对话历史。

##### Checkpoint（检查点）

Checkpoint 是图在某个时间点的状态快照。LangGraph 会在每个 super-step（超级步骤）自动保存一个 checkpoint，记录下当前的状态值、下一步要执行的节点、元数据等信息。

一个简单的图执行过程可能会产生多个 checkpoint：

```
1. 初始 checkpoint（空状态，准备执行 START 节点）2. 用户输入后的 checkpoint（包含输入数据）3. 节点 A 执行后的 checkpoint（包含节点 A 的输出）4. 节点 B 执行后的 checkpoint（包含节点 B 的输出）5. 最终 checkpoint（执行完成） 
```

每个 checkpoint 都是一个完整的 `StateSnapshot` 对象，包含：

* `values`：当前状态的值
* `next`：下一步要执行的节点
* `metadata`：元数据信息
* `config`：配置信息
* `created_at`：创建时间

#### 编程示例

让我们通过一个完整的例子来理解持久化机制是如何工作的。

##### 基础示例：让智能体记住对话

首先，创建一个简单的对话智能体：

```
from langchain.chat_models import init_chat_modelfrom langgraph.checkpoint.memory import InMemorySaverfrom langgraph.graph import StateGraph, MessagesState, STARTimport os# 初始化模型llm = init_chat_model( model="qwen-plus", model_provider='openai', api_key=os.getenv("DASHSCOPE_API_KEY"), base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")# 定义节点函数def call_model(state: MessagesState): response = llm.invoke(state["messages"]) return {"messages": response}# 创建 checkpointercheckpointer = InMemorySaver()# 构建图builder = StateGraph(MessagesState)builder.add_node("agent", call_model)builder.add_edge(START, "agent")# 编译图时传入 checkpointergraph = builder.compile(checkpointer=checkpointer) 
```

关键点在于最后一行：`builder.compile(checkpointer=checkpointer)`。这行代码启用了持久化机制。

现在来测试一下记忆功能：

```
# 第一次对话config = {"configurable": {"thread_id": "user_123"}}response1 = graph.invoke( {"messages": [{"role": "user", "content": "你好，我的名字是张三"}]}, config)print(f"AI: {response1['messages'][-1].content}")# 第二次对话（相同 thread_id）response2 = graph.invoke( {"messages": [{"role": "user", "content": "我的名字是什么？"}]}, config # 使用相同的 thread_id)print(f"AI: {response2['messages'][-1].content}") 
```

运行这段代码，会发现第二次调用时，AI 能够准确回答"你的名字是张三"。这就是持久化机制在起作用：第二次调用时，checkpointer 自动恢复了第一次对话的历史记录。

##### 查看状态历史

持久化机制还提供了查看历史状态的能力：

```
# 获取最新状态current_state = graph.get_state(config)print(f"当前消息数: {len(current_state.values['messages'])}")# 获取完整历史history = list(graph.get_state_history(config))print(f"总共有 {len(history)} 个 checkpoint")# 遍历历史记录for i, snapshot in enumerate(history): print(f"\nCheckpoint {i}:") print(f" 时间: {snapshot.created_at}") print(f" 消息数: {len(snapshot.values['messages'])}") print(f" 下一步节点: {snapshot.next}") 
```

这个功能在调试时非常有用，可以清楚地看到图执行的每一步。

##### Checkpointer 的实现方式

LangGraph 提供了多种 checkpointer 实现，适用于不同的场景：

**📦 InMemorySaver（内存存储）**

适合开发和测试，数据保存在内存中，程序重启后丢失：

```
from langgraph.checkpoint.memory import InMemorySavercheckpointer = InMemorySaver()graph = builder.compile(checkpointer=checkpointer) 
```

**💾 SqliteSaver（SQLite 数据库）**

适合本地开发和实验，数据持久化到 SQLite 文件：

```
from langgraph.checkpoint.sqlite import SqliteSaverimport sqlite3conn = sqlite3.connect("checkpoints.db")checkpointer = SqliteSaver(conn)checkpointer.setup() # 首次使用需要初始化graph = builder.compile(checkpointer=checkpointer) 
```

**🗄️ PostgresSaver（PostgreSQL 数据库）**

适合生产环境，性能好，支持并发：

```
from langgraph.checkpoint.postgres import PostgresSaverDB_URI = "postgresql://user:password@localhost:5432/dbname"checkpointer = PostgresSaver.from_conn_string(DB_URI)checkpointer.setup() # 首次使用需要初始化graph = builder.compile(checkpointer=checkpointer) 
```

**🔴 RedisSaver（Redis 存储）**

适合需要高性能缓存的场景：

```
from langgraph.checkpoint.redis import RedisSaverDB_URI = "redis://localhost:6379"checkpointer = RedisSaver.from_conn_string(DB_URI)checkpointer.setup()graph = builder.compile(checkpointer=checkpointer) 
```

#### 持久化带来的强大能力（应用场景）

持久化机制不仅仅是保存状态那么简单，它开启了四个强大的能力：

##### 🧠 Memory（记忆）

这是最直观的应用。通过 thread\_id，智能体可以记住之前的对话内容，实现真正的多轮对话。

```
# 第一次对话graph.invoke( {"messages": [{"role": "user", "content": "我喜欢 Python"}]}, {"configurable": {"thread_id": "chat_1"}})# 第二次对话，智能体记得之前的信息graph.invoke( {"messages": [{"role": "user", "content": "我刚才说了我喜欢什么？"}]}, {"configurable": {"thread_id": "chat_1"}}) 
```

##### 👤 Human-in-the-loop（人工介入）

持久化让人工介入成为可能。可以在关键步骤暂停执行，等待人工审核。但这里有一个重要的机制需要理解：**状态更新与 reducer 函数的关系**。

###### 理解 update\_state 的行为

当使用 `update_state` 更新状态时，LangGraph 会采用与节点更新相同的处理方式：

**关键规则**：

* **有 reducer 的通道**：更新值会传递给 reducer 函数处理

* 不会直接覆盖，而是通过 reducer 函数合并
* 例如：`messages: Annotated[list, add_messages]` 会追加消息，而不是替换

* **没有 reducer 的通道**：更新值会直接覆盖

* 直接替换原有的值

这意味着 `update_state`**不会自动覆盖所有通道的值**，而是根据每个通道是否定义了 reducer 来决定处理方式。

**实际例子**

```
from typing import Annotatedfrom typing_extensions import TypedDictfrom langgraph.graph.message import add_messages# 定义状态，包含有 reducer 和没有 reducer 的通道class State(TypedDict): messages: Annotated[list, add_messages] # 有 reducer：追加 counter: int # 没有 reducer：直接覆盖 user_name: str # 没有 reducer：直接覆盖# 假设当前状态current_state = { "messages": [{"role": "user", "content": "Hello"}], "counter": 5, "user_name": "Alice"}# 使用 update_state 更新graph.update_state( config, { "messages": [{"role": "assistant", "content": "Hi"}], # 会追加，不会替换 "counter": 10, # 会直接覆盖为 10 "user_name": "Bob"# 会直接覆盖为 "Bob" })# 更新后的状态：# {# "messages": [# {"role": "user", "content": "Hello"}, # 保留原有# {"role": "assistant", "content": "Hi"} # 追加新的# ],# "counter": 10, # 被覆盖# "user_name": "Bob" # 被覆盖# } 
```

###### 理解 as\_node 参数：控制执行流程

`update_state` 还有一个重要的可选参数 `as_node`，它用于控制下一步要执行的节点。

**关键机制**：

* **下一步执行哪个节点**取决于最后一个更新状态的节点
* 图的边（edges）定义了从某个节点到其他节点的路径
* 通过 `as_node` 参数，可以"伪装"更新来自某个特定节点，从而控制执行流程

**行为规则**：

* 如果提供了 `as_node`：更新会被当作来自该节点的更新
* 如果没有提供 `as_node`：会使用最后一个更新状态的节点（如果不模糊）
* 如果无法确定（模糊情况）：需要显式指定 `as_node`

###### 实际例子：控制执行路径

**（1）情况 A：条件边（Conditional Edge）**

```
# 假设图结构如下（条件边）：# START -> node_a -> [条件判断] -> node_b 或 node_c# node_a 有条件边，根据条件选择 node_b 或 node_c# 场景 1：不指定 as_node（使用默认行为）state = graph.get_state(config)graph.update_state(config, {"counter": 10})# 下一步会从最后一个更新状态的节点继续执行# 场景 2：指定 as_node，控制执行路径graph.update_state( config, {"counter": 10}, as_node="node_a"# 指定更新来自 node_a)# 下一步会从 node_a 的条件边继续执行（根据条件选择 node_b 或 node_c，只执行其中一个） 
```

**（2）情况 B：多条普通边（并行执行）**

```
# 假设图结构如下（多条普通边）：# START -> node_a -> node_b# -> node_c# node_a 有两条普通边分别指向 node_b 和 node_c# 指定 as_node 为 node_agraph.update_state( config, {"counter": 10}, as_node="node_a" # 指定更新来自 node_a)# 下一步会从 node_a 的边继续执行# 由于 node_b 和 node_c 都依赖 node_a，且彼此独立，它们会在同一个 super-step 中并行执行 
```

**从特定节点重新开始**

```
# 从特定节点重新开始执行graph.update_state( config, {"messages": [{"role": "user", "content": "重新开始"}]}, as_node="node_b" # 指定更新来自 node_b)# 下一步会从 node_b 的边继续执行 
```

**关键区别**：

* **条件边**：根据条件选择其中一个节点执行（不并行）
* **多条普通边**：如果节点之间没有依赖关系，会在同一个 super-step 中并行执行

上述的机制在以下场景非常有用：

**场景一：人工修正后改变执行路径**

```
# 1. 获取当前状态state = graph.get_state(config)print(f"当前在节点: {state.next}")# 2. 人工审核发现需要改变执行路径# 假设原本应该执行 node_b，但人工决定改为执行 node_c# 3. 更新状态，并指定 as_node 为 node_a（分支节点）graph.update_state( config, {"decision": "go_to_c"}, # 修改决策 as_node="node_a"# 从 node_a 重新路由)# 4. 继续执行，现在会从 node_a 根据新的状态路由到 node_cgraph.invoke(updated_input, config) 
```

**场景二：从特定节点重新执行**

```
# 从某个中间节点重新开始执行graph.update_state( config, {"messages": [{"role": "user", "content": "重新处理"}]}, as_node="agent" # 从 agent 节点重新开始)# 下一步会从 agent 节点的边继续执行 
```

**场景三：创建执行分支（Fork）**

```
# 从某个 checkpoint 创建新分支old_state = graph.get_state({ "configurable": { "thread_id": "thread_1", "checkpoint_id": "checkpoint_2_id" }})# 更新状态，指定从特定节点开始graph.update_state( {"configurable": {"thread_id": "thread_1_fork"}}, old_state.values, as_node="node_a" # 从 node_a 开始新分支) 
```

###### 人工介入的完整流程

```
# 1. 获取当前状态state = graph.get_state(config)print(f"当前状态: {state.values}")print(f"下一步节点: {state.next}")# 2. 人工审核和修改updates = { "messages": [{"role": "user", "content": "修正后的消息"}], "counter": 0,}# 3. 更新状态，并控制执行路径graph.update_state( config, updates, as_node="agent"# 指定从 agent 节点继续执行)# 4. 从检查点继续执行# 现在会从 agent 节点的边继续执行graph.invoke(updated_input, config) 
```

**为什么这样设计？**

这种设计的好处：

* 🔄 **一致性**：`update_state` 和节点更新使用相同的规则，保证行为一致
* 🛡️ **安全性**：有 reducer 的通道不会被意外覆盖，保护累积的数据
* 🎯 **灵活性**：可以根据需要选择直接覆盖或通过 reducer 合并

理解这个机制，对于正确使用人工介入功能非常重要。特别是在修改包含 reducer 的通道时，需要明确知道是追加还是替换。

##### ⏰ Time Travel（时间旅行）

可以回放之前的执行过程，这对于调试和分析非常有用。但这里有一个重要的机制需要理解：**checkpoint 回放的分支行为**。

###### 理解 Checkpoint 回放机制

当从某个 `checkpoint_id` 回放执行时，LangGraph 会采用智能的回放策略：

**关键规则**：

* **checkpoint\_id 之前的步骤**：只"重放"（re-play），不重新执行

* LangGraph 知道这些步骤已经执行过
* 直接使用已保存的 checkpoint 数据，不会重新运行节点函数
* 这样可以节省计算资源，避免重复执行

* **checkpoint\_id 之后的步骤**：会重新执行，创建新分支

* 即使这些步骤之前执行过，也会重新运行
* 这相当于从该 checkpoint 创建了一个新的执行分支（fork）
* 允许探索不同的执行路径

```
# 假设执行历史如下：# Step 0: START -> checkpoint_0# Step 1: node_a -> checkpoint_1# Step 2: node_b -> checkpoint_2# Step 3: node_c -> checkpoint_3# 从 checkpoint_1 回放config = { "configurable": { "thread_id": "thread_1", "checkpoint_id": "checkpoint_1_id"# 指定回放起点 }}# 执行结果：# - checkpoint_0 和 checkpoint_1：直接使用已保存的数据（不重新执行）# - checkpoint_1 之后的步骤：重新执行 node_b 和 node_c（创建新分支）graph.invoke(new_input, config) 
```

###### 实际应用场景

这个机制在以下场景非常有用：

**场景一：探索不同的执行路径**

```
# 第一次执行config = {"configurable": {"thread_id": "explore_1"}}result1 = graph.invoke(input_data, config)# 获取历史，找到关键决策点history = list(graph.get_state_history(config))decision_point = history[2] # 假设这是某个决策节点# 从决策点重新执行，尝试不同的输入config_fork = { "configurable": { "thread_id": "explore_1", "checkpoint_id": decision_point.config["configurable"]["checkpoint_id"] }}result2 = graph.invoke(different_input, config_fork) # 创建新分支 
```

**场景二：调试和分析**

```
# 查看某个时间点的状态history = list(graph.get_state_history(config))old_state = graph.get_state({ "configurable": { "thread_id": "chat_1", "checkpoint_id": history[2].config["configurable"]["checkpoint_id"] }})# 分析该时间点的状态print(f"Step {old_state.metadata.get('step', 0)} 的状态:")print(f" 值: {old_state.values}")print(f" 下一步: {old_state.next}")# 如果需要，可以从这个点重新执行graph.invoke(modified_input, { "configurable": { "thread_id": "chat_1", "checkpoint_id": history[2].config["configurable"]["checkpoint_id"] }}) 
```

**场景三：错误恢复和重试**

```
# 执行过程中出错try: graph.invoke(input_data, config)except Exception as e: # 获取最后一个成功的 checkpoint last_state = graph.get_state(config) # 从该 checkpoint 重新执行（只重新执行之后的步骤） fixed_input = fix_input(input_data) graph.invoke(fixed_input, { "configurable": { "thread_id": config["configurable"]["thread_id"], "checkpoint_id": last_state.config["configurable"]["checkpoint_id"] } }) 
```

**性能优势**

这种设计带来的好处：

* ⚡ **节省计算**：已执行的步骤不会重复运行，直接使用保存的结果
* 🔀 **灵活分支**：可以从任意 checkpoint 创建新的执行路径
* 🐛 **便于调试**：可以精确控制从哪个点开始重新执行
* 💾 **状态一致**：确保回放时的状态与原始执行时完全一致

理解这个机制，对于充分利用 LangGraph 的时间旅行功能非常重要。

##### 🛡️ Fault-tolerance（容错）

当节点执行失败时，可以从最后一个成功的 checkpoint 恢复，不会丢失已完成的工作：

```
try: graph.invoke(input_data, config)except Exception as e: # 获取最后一个成功的状态 last_state = graph.get_state(config) # 从失败的地方重新开始 graph.invoke(updated_input, config) 
```

##### 实际应用场景

在实际项目中，持久化机制的应用场景非常广泛：

**场景一：多用户对话系统**

每个用户分配一个唯一的 thread\_id，实现用户之间的对话隔离：

```
def handle_user_message(user_id, message): config = {"configurable": {"thread_id": f"user_{user_id}"}} response = graph.invoke( {"messages": [{"role": "user", "content": message}]}, config ) return response 
```

**场景二：长时间运行的智能体**

对于需要长时间运行的智能体任务，持久化可以确保即使程序重启，也能从上次中断的地方继续：

```
# 第一次执行config = {"configurable": {"thread_id": "long_task_1"}}graph.invoke(initial_input, config)# ... 程序重启 ...# 恢复执行last_state = graph.get_state(config)graph.invoke(continue_input, config) 
```

**场景三：调试和分析**

通过查看 checkpoint 历史，可以分析智能体的决策过程：

```
def analyze_agent_behavior(thread_id): config = {"configurable": {"thread_id": thread_id}} history = list(graph.get_state_history(config)) for snapshot in history: print(f"Step {snapshot.metadata.get('step', 0)}:") print(f" State: {snapshot.values}") print(f" Next nodes: {snapshot.next}") print(f" Writes: {snapshot.metadata.get('writes', {})}") 
```

##### 性能考虑

在使用持久化机制时，需要注意一些性能问题：

* ⚡ **Checkpoint 频率**：每个 super-step 都会保存 checkpoint，对于高频调用的场景，需要考虑存储成本
* 💾 **存储选择**：生产环境建议使用 PostgreSQL 或 Redis，而不是内存存储
* 🔍 **历史清理**：定期清理旧的 checkpoint，避免存储空间无限增长

```
# 删除某个线程的所有 checkpointcheckpointer.delete_thread("old_thread_id") 
```

#### 总结

LangGraph 的持久化机制通过 checkpointer 和 thread 的概念，为 AI 智能体提供了强大的状态管理能力。它不仅解决了多轮对话的问题，还开启了人工介入、时间旅行、容错等高级功能。

在实际开发中，选择合适的 checkpointer 实现很重要：

* 开发测试：使用 `InMemorySaver`
* 本地部署：使用 `SqliteSaver`
* 生产环境：使用 `PostgresSaver` 或 `RedisSaver`

理解持久化机制，是构建高质量 AI 智能体应用的关键一步。希望这篇文章能帮助大家更好地理解和使用 LangGraph 的持久化功能。

---

### ​最后

我在一线科技企业深耕十二载，见证过太多因技术卡位而跃迁的案例。那些率先拥抱 AI 的同事，早已在效率与薪资上形成代际优势，我意识到有很多经验和知识值得分享给大家，也可以通过我们的能力和经验解答大家在大模型的学习中的很多困惑。

我整理出这套 AI 大模型突围资料包：

* ✅AI大模型学习路线图
* ✅Agent行业报告
* ✅100集大模型视频教程
* ✅大模型书籍PDF
* ✅DeepSeek教程
* ✅AI产品经理入门资料

**完整的大模型学习和面试资料已经上传带到CSDN的官方了，有需要的朋友可以扫描下方二维码免费领取【保证100%免费】👇👇**  
 ​​

### 为什么说现在普通人就业/升职加薪的首选是AI大模型？

人工智能技术的爆发式增长，正以不可逆转之势重塑就业市场版图。从DeepSeek等国产大模型引发的科技圈热议，到全国两会关于AI产业发展的政策聚焦，再到招聘会上排起的长队，AI的热度已从技术领域渗透到就业市场的每一个角落。

智联招聘的最新数据给出了最直观的印证：2025年2月，**AI领域求职人数同比增幅突破200%** ，远超其他行业平均水平；整个人工智能行业的求职增速达到33.4%，位居各行业榜首，其中人工智能工程师岗位的求职热度更是飙升69.6%。

AI产业的快速扩张，也让人才供需矛盾愈发突出。麦肯锡报告明确预测，到2030年中国AI专业人才需求将达600万人，**人才缺口可能高达400万人**，这一缺口不仅存在于核心技术领域，更蔓延至产业应用的各个环节。

​​

### 资料包有什么？

### **①从入门到精通的全套视频教程**⑤⑥

包含提示词工程、RAG、Agent等技术点

### **② AI大模型学习路线图（还有视频解说）**

全过程AI大模型学习路线

### **③学习电子书籍和技术文档**

市面上的大模型书籍确实太多了，这些是我精选出来的

### **④各大厂大模型面试题目详解**

### **⑤ 这些资料真的有用吗?**

这份资料由我和鲁为民博士共同整理，鲁为民博士先后获得了北京清华大学学士和美国加州理工学院博士学位，在包括IEEE Transactions等学术期刊和诸多国际会议上发表了超过50篇学术论文、取得了多项美国和中国发明专利，同时还斩获了吴文俊人工智能科学技术奖。目前我正在和鲁博士共同进行人工智能的研究。

所有的视频教程由智泊AI老师录制，且资料与智泊AI共享，相互补充。**这份学习大礼包应该算是现在最全面的大模型学习资料了。**

资料内容涵盖了从入门到进阶的各类视频教程和实战项目，无论你是小白还是有些技术基础的，这份资料都绝对能帮助你提升薪资待遇，转行大模型岗位。

智泊AI始终秉持着“**让每个人平等享受到优质教育资源**”的育人理念‌，通过动态追踪大模型开发、数据标注伦理等前沿技术趋势‌，构建起"**前沿课程+智能实训+精准就业**"的高效培养体系。

课堂上不光教理论，还带着学员做了十多个真实项目。学员要亲自上手搞数据清洗、模型调优这些硬核操作，把课本知识变成真本事‌！

​​​​

如果说你是以下人群中的其中一类，都可以来智泊AI学习人工智能，找到高薪工作，一次小小的“投资”换来的是终身受益！

应届毕业生‌：无工作经验但想要系统学习AI大模型技术，期待通过实战项目掌握核心技术。

零基础转型‌：非技术背景但关注AI应用场景，计划通过低代码工具实现“AI+行业”跨界‌。

业务赋能 ‌突破瓶颈：传统开发者（Java/前端等）学习Transformer架构与LangChain框架，向AI全栈工程师转型‌。

### 👉获取方式：

😝有需要的小伙伴，可以保存图片到wx扫描二v码免费领取【保证100%免费】🆓\*\*

​

[# 人工智能](https://devpress.csdn.net/tags/629eeed4512a562a42849836)

[火山引擎 ADG 社区](https://adg.csdn.net)

火山引擎开发者社区是火山引擎打造的AI技术生态平台，聚焦Agent与大模型开发，提供豆包系列模型（图像/视频/视觉）、智能分析与会话工具，并配套评测集、动手实验室及行业案例库。社区通过技术沙龙、挑战赛等活动促进开发者成长，新用户可领50万Tokens权益，助力构建智能应用。

更多推荐

* ·  [Chess用户界面设计：Tailwind CSS样式系统和组件库](https://adg.csdn.net/6973106b437a6b40336b7b60.html)
* ·  [终极指南：GPT-Engineer如何通过AI自动发现代码问题并提升质量](https://adg.csdn.net/69730d91437a6b40336b6a06.html)
* ·  [SatDump中的纠错编码技术：从RS码到Turbo码的完整实现指南](https://adg.csdn.net/6972f1c1437a6b40336b5477.html)

[Chess用户界面设计：Tailwind CSS样式系统和组件库

GitHub推荐项目精选中的ch/chess是一个类似chess.com的多人在线象棋平台，它采用现代化的前端技术栈构建，尤其在用户界面设计上通过Tailwind CSS样式系统和组件库实现了优雅且功能丰富的交互体验。本文将深入探讨该项目如何利用Tailwind CSS打造一致的设计语言和高效的组件系统，为象棋爱好者提供沉浸式的游戏界面。## 🎨 Tailwind CSS样式系统：构建统一视

[火山引擎 ADG 社区](https://adg.csdn.net)](https://adg.csdn.net/6973106b437a6b40336b7b60.html)

[GPT-Engineer是一款强大的AI驱动代码工具，它能帮助开发者自动检测潜在代码问题、优化代码质量，让编程效率提升3倍以上。无论是新手还是资深开发者，都能通过这款工具轻松发现代码中的隐藏缺陷，减少调试时间，释放更多精力在创造性工作上。## 一键发现代码问题：GPT-Engineer的AI审查魔力GPT-Engineer的核心能力在于其内置的智能代码分析系统。通过集成Python代码格式

[火山引擎 ADG 社区](https://adg.csdn.net)](https://adg.csdn.net/69730d91437a6b40336b6a06.html)

[在卫星数据传输过程中，信号往往会受到各种干扰，导致数据错误。SatDump作为一款通用卫星数据处理软件，集成了多种先进的纠错编码技术，确保从卫星接收到的数据能够准确解码。本文将深入解析SatDump中从Reed-Solomon（RS）码到Turbo码的实现细节，帮助读者理解这些技术如何保障卫星通信的可靠性。## 为什么纠错编码对卫星数据至关重要？卫星与地面站之间的通信链路面临着空间辐射、大

[火山引擎 ADG 社区](https://adg.csdn.net)](https://adg.csdn.net/6972f1c1437a6b40336b5477.html)

* 996
* 10
* 0
* 0
* 分享

### 所有评论(0)

您需要登录才能发言

欢迎加入社区

### [AGI大模型老王](https://devpress.csdn.net/user/2401_85390073)

回到  
顶部

欢迎加入社区