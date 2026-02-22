# 持久化 ¶

**URL**:
https://langgraph.com.cn/concepts/persistence.1.html

## 元数据
- 发布日期: 2026-02-22T20:37:58.521593

## 完整内容
---
概述 - LangChain 框架[跳过内容] 
**我们正在壮大，并为 LangChain、LangGraph 和LangSmith 招聘多个职位。[加入我们的团队！] **
[] # 持久化[¶] 
LangGraph 有一个内置的持久化层，通过检查点器实现。当你使用检查点器编译图时，检查点器会在每个超级步骤保存图状态的`checkpoint`。这些检查点保存到`thread`中，可以在图执行后访问。因为`threads`允许在执行后访问图的状态，所以人机协作、记忆、时间旅行和容错等多种强大功能都成为可能。请参阅[此操作指南] ，了解如何在图中添加和使用检查点器的端到端示例。下面，我们将更详细地讨论这些概念。
![Checkpoints] 
LangGraph API 自动处理检查点使用LangGraph API 时，你无需手动实现或配置检查点器。API 在幕后为你处理所有持久化基础设施。## 线程[¶] 
线程是分配给检查点器保存的每个检查点的唯一ID 或[线程标识符] 。当使用检查点器调用图时，你**必须**在配置的`configurable`部分中指定`thread\_id`
```
`[]<web_link>{"configurable":{"thread\_id":"1"}}`
```
## 检查点[¶] 
检查点是每个超级步骤保存的图状态的快照，由具有以下关键属性的`StateSnapshot`对象表示
* `config`：与此检查点关联的配置。
* `metadata`：与此检查点关联的元数据。
* `values`：此时状态通道的值。
* `next`：要在图中接下来执行的节点名称的元组。
* `tasks`：包含要执行的后续任务信息的`PregelTask`对象元组。如果该步骤之前曾尝试过，它将包含错误信息。如果图在节点内部被[动态] 中断，`tasks`将包含与中断相关的附加数据。
让我们看看以如下方式调用简单图时保存的检查点*API 参考：[StateGraph] |[START] |[END] |[InMemorySaver] *
```
`[]<web_link>fromlanggraph.graphimportStateGraph,START,END[]<web_link>fromlanggraph.checkpoint.memoryimportInMemorySaver[]<web_link>fromtypingimportAnnotated[]<web_link>fromtyping\_extensionsimportTypedDict[]<web_link>fromoperatorimportadd[]<web_link>[]<web_link>classState(TypedDict):[]<web_link>foo:str[]<web_link>bar:Annotated[list[str],add][]<web_link>[]<web_link>defnode\_a(state:State):[]<web_link>return{"foo":"a","bar":["a"]}[]<web_link>[]<web_link>defnode\_b(state:State):[]<web_link>return{"foo":"b","bar":["b"]}[]<web_link>[]<web_link>[]<web_link>workflow=StateGraph(State)[]<web_link>workflow.add\_node(node\_a)[]<web_link>workflow.add\_node(node\_b)[]<web_link>workflow.add\_edge(START,"node\_a")[]<web_link>workflow.add\_edge("node\_a","node\_b")[]<web_link>workflow.add\_edge("node\_b",END)[]<web_link>[]<web_link>checkpointer=InMemorySaver()[]<web_link>graph=workflow.compile(checkpointer=checkpointer)[]<web_link>[]<web_link>config={"configurable":{"thread\_id":"1"}}[]<web_link>graph.invoke({"foo":""},config)`
```
运行图后，我们预期会看到恰好4 个检查点* 空检查点，其中`START`是下一个要执行的节点
* 包含用户输入`{'foo': '', 'bar': []}`的检查点，`node\_a`是下一个要执行的节点
* 包含`node\_a`输出`{'foo': 'a', 'bar': ['a']}`的检查点，`node\_b`是下一个要执行的节点
* 包含`node\_b`输出`{'foo': 'b', 'bar': ['a', 'b']}`的检查点，并且没有要执行的下一个节点
请注意，`bar`通道的值包含来自两个节点的输出，因为我们为`bar`通道设置了 reducer。
### 获取状态[¶] 
当与保存的图状态交互时，你**必须**指定一个[线程标识符] 。你可以通过调用`graph.get\_state(config)`来查看图的\*最新\*状态。这将返回一个`StateSnapshot`对象，该对象对应于配置中提供的线程 ID 关联的最新检查点，或者如果提供了检查点ID，则返回与该线程的检查点 ID 关联的检查点。```
`[] # get the latest state snapshot[] config={"configurable":{"thread\_id":"1"}}[] graph.get\_state(config)[] [] # get a state snapshot for a specific checkpoint\_id[] config={"configurable":{"thread\_id":"1","checkpoint\_id":"1ef663ba-28fe-6528-8002-5a559208592c"}}[] graph.get\_state(config)`
```
在我们的示例中，`get\_state`的输出将如下所示
```
`[] StateSnapshot([] values={'foo': 'b', 'bar': ['a', 'b']},[] next=(),[] config={'configurable': {'thread\_id': '1', 'checkpoint\_ns': '', 'checkpoint\_id': '1ef663ba-28fe-6528-8002-5a559208592c'}},[] metadata={'source': 'loop', 'writes': {'node\_b': {'foo': 'b', 'bar': ['b']}}, 'step': 2},[] created\_at='2024-08-29T19:19:38.821749+00:00',[] parent\_config={'configurable': {'thread\_id': '1', 'checkpoint\_ns': '', 'checkpoint\_id': '1ef663ba-28f9-6ec4-8001-31981c2c39f8'}}, tasks=()[])`
```
### 获取状态历史[¶]<web_link>
你可以通过调用`graph.get\_state\_history(config)`获取给定线程的图执行的完整历史记录。这将返回一个与配置中提供的线程 ID 关联的`StateSnapshot`对象列表。重要的是，检查点将按时间顺序排列，最近的检查点 /`StateSnapshot`位于列表的首位。
```
`[] config={"configurable":{"thread\_id":"1"}}[] list(graph.get\_state\_history(config))`
```
在我们的示例中，`get\_state\_history`的输出将如下所示
```
`[] [[] StateSnapshot([] values={'foo': 'b', 'bar': ['a', 'b']},[] next=(),[] config={'configurable': {'thread\_id': '1', 'checkpoint\_ns': '', 'checkpoint\_id': '1ef663ba-28fe-6528-8002-5a559208592c'}},[] metadata={'source': 'loop', 'writes': {'node\_b': {'foo': 'b', 'bar': ['b']}}, 'step': 2},[] created\_at='2024-08-29T19:19:38.821749+00:00',[] parent\_config={'configurable': {'thread\_id': '1', 'checkpoint\_ns': '', 'checkpoint\_id': '1ef663ba-28f9-6ec4-8001-31981c2c39f8'}},[] tasks=(),[]),[] StateSnapshot([] values={'foo': 'a', 'bar': ['a']}, next=('node\_b',),[] config={'configurable': {'thread\_id': '1', 'checkpoint\_ns': '', 'checkpoint\_id': '1ef663ba-28f9-6ec4-8001-31981c2c39f8'}},[] metadata={'source': 'loop', 'writes': {'node\_a': {'foo': 'a', 'bar': ['a']}}, 'step': 1},[] created\_at='2024-08-29T19:19:38.819946+00:00',[] parent\_config={'configurable': {'thread\_id': '1', 'checkpoint\_ns': '', 'checkpoint\_id': '1ef663ba-28f4-6b4a-8000-ca575a13d36a'}},[] tasks=(PregelTask(id='6fb7314f-f114-5413-a1f3-d37dfe98ff44', name='node\_b', error=None, interrupts=()),),[]),[] StateSnapshot([] values={'foo': '', 'bar': []},[] next=('node\_a',),[] config={'configurable': {'thread\_id': '1', 'checkpoint\_ns': '', 'checkpoint\_id': '1ef663ba-28f4-6b4a-8000-ca575a13d36a'}},[] metadata={'source': 'loop', 'writes': None, 'step': 0},[] created\_at='2024-08-29T19:19:38.817813+00:00',[] parent\_config={'configurable': {'thread\_id': '1', 'checkpoint\_ns': '', 'checkpoint\_id': '1ef663ba-28f0-6c66-bfff-6723431e8481'}},[] tasks=(PregelTask(id='f1b14528-5ee5-579c-949b-23ef9bfbed58', name='node\_a', error=None, interrupts=()),),[]),[] StateSnapshot([] values={'bar': []},[] next=('\_\_start\_\_',),[] config={'configurable': {'thread\_id': '1', 'checkpoint\_ns': '', 'checkpoint\_id': '1ef663ba-28f0-6c66-bfff-6723431e8481'}},[] metadata={'source': 'input', 'writes': {'foo': ''}, 'step': -1},[] created\_at='2024-08-29T19:19:38.816205+00:00',[] parent\_config=None,[] tasks=(PregelTask(id='6d27aa2e-d72b-5504-a36f-8620e54a76dd', name='\_\_start\_\_', error=None, interrupts=()),),[])[]]`
```
![State]<image_link>
### 回放[¶]<web_link>
也可以回放之前的图执行。如果我们使用`thread\_id`和`checkpoint\_id`调用图，那么我们将\*回放\*`checkpoint\_id`对应的检查点\*之前\*已执行的步骤，并且只执行检查点\*之后\*的步骤。
* `thread\_id`是线程的 ID。
* `checkpoint\_id`是指线程中特定检查点的标识符。
在调用图时，你必须将这些作为配置的`configurable`部分传入
```
`[] config={"configurable":{"thread\_id":"1","checkpoint\_id":"0c62ca34-ac19-445d-bbb0-5b4984975b2a"}}[] graph.invoke(None,config=config)`
```
重要的是，LangGraph 知道特定步骤是否以前执行过。如果执行过，LangGraph 只会简单地在图中\*回放\*该特定步骤，而不会重新执行该步骤，但这仅适用于所提供的`checkpoint\_id`\*之前\*的步骤。`checkpoint\_id`\*之后\*的所有步骤都将被执行（即，一个新的分支），即使它们以前执行过。请参阅此[时间旅行操作指南，了解有关回放的更多信息]<web_link>。
![Replay]<image_link>
### 更新状态[¶]<web_link>
除了从特定的`checkpoints`回放图之外，我们还可以\*编辑\*图的状态。我们使用`graph.update\_state()`来实现。此方法接受三个不同的参数
#### `config`[¶]<web_link>
配置应包含`thread\_id`，指定要更新哪个线程。当只传递`thread\_id`时，我们更新（或分叉）当前状态。可选地，如果我们包含`checkpoint\_id`字段，那么我们分叉该选定的检查点。
#### `values`[¶]<web_link>
这些是将用于更新状态的值。请注意，此更新的处理方式与来自节点的任何更新完全相同。这意味着如果为图状态中的某些通道定义了reducer 函数，这些值将传递给[reducer]<web_link>函数。这意味着`update\_state`不会自动覆盖每个通道的通道值，而只覆盖没有 reducer 的通道。让我们通过一个例子来了解。假设你已经使用以下模式定义了图的状态（参见上面的完整示例）```
`[]<web_link>fromtypingimportAnnotated[]<web_link>fromtyping\_extensionsimportTypedDict[]<web_link>fromoperatorimportadd[]<web_link>[]<web_link>classState(TypedDict):[]<web_link>foo:int[]<web_link>bar:Annotated[list[str],add]`
```
现在假设图的当前状态是```
`[] {"foo": 1, "bar": ["a"]}`
```
如果你如下更新状态```
`[]<web_link>graph.update\_state(config, {"foo": 2, "bar": ["b"]})`
```
那么图的新状态将是```
`[] {"foo": 2, "bar": ["a", "b"]}`
```
`foo`键（通道）完全改变了（因为没有为该通道指定 reducer，所以`update\_state`会覆盖它）。然而，为`bar`键指定了一个 reducer，因此它将`"b"`附加到`bar`的状态。
#### `as\_node`[¶]<web_link>
调用`update\_state`时，你可以选择指定的最后一项是`as\_node`。如果你提供了它，更新将像来自节点`as\_node`一样应用。如果未提供`as\_node`，则在不模糊的情况下，它将被设置为最后更新状态的节点。这之所以重要，是因为接下来要执行的步骤取决于最后给出更新的节点，因此这可用于控制哪个节点接下来执行。请参阅此[时间旅行操作指南，了解有关分叉状态的更多信息]<web_link>。
![Update]<image_link>
## 记忆存储[¶]<web_link>
![Model of shared state]<image_link>
[状态模式]<web_link>指定了一组在图执行时填充的键。如上所述，状态可以通过检查点器在每个图步骤写入线程，从而实现状态持久化。
但是，如果我们要\*跨线程\*保留一些信息怎么办？考虑一个聊天机器人的情况，我们希望在与该用户进行的所有聊天对话（例如，线程）中保留有关该用户的特定信息！
仅凭检查点器，我们无法跨线程共享信息。这促使了对[`Store`]<web_link>接口的需求。为了说明这一点，我们可以定义一个`InMemoryStore`来存储用户在所有线程中的信息。我们只需像以前一样，使用检查点器和我们新的`in\_memory\_store`变量来编译我们的图。
LangGraph API 自动处理存储使用LangGraph API 时，你无需手动实现或配置存储。API 在幕后为你处理所有存储基础设施。### 基本用法[¶]<web_link>
首先，让我们在不使用LangGraph 的情况下单独展示这一点。```
`[]<web_link>fromlanggraph.store.memoryimportInMemoryStore[]<web_link>in\_memory\_store=InMemoryStore()`
```
记忆通过`tuple`进行命名空间管理，在此特定示例中为`(&lt;&lt;user\_id&gt;&gt;, "memories")`。命名空间可以是任意长度，并表示任何内容，不必是用户特定的。
```
`[]<web_link>user\_id="1"[]<web_link>namespace\_for\_memory=(user\_id,"memories")`
```
我们使用`store.put`方法将记忆保存到存储中的命名空间。当我们这样做时，我们指定命名空间（如上定义），以及记忆的键值对：键是记忆的唯一标识符（`memory\_id`），值（一个字典）是记忆本身。
```
`[]<web_link>memory\_id=str(uuid.uuid4())[]<web_link>memory={"food\_preference":"I like pizza"}[]<web_link>in\_memory\_store.put(namespace\_for\_memory,memory\_id,memory)`
```
我们可以使用`store.search`方法读取命名空间中的记忆，该方法将以列表形式返回给定用户的所有记忆。最近的记忆在列表的末尾。
```
`[]<web_link>memories=in\_memory\_store.search(namespace\_for\_memory)[]<web_link>memories[-1].dict()[]<web_link>{'value':{'food\_preference':'I like pizza'},[]<web_link>'key':'07e0caf4-1631-47b7-b15f-65515d4c1843',[]<web_link>'namespace':['1','memories'],[]<web_link>'created\_at':'2024-10-02T17:22:31.590602+00:00',[]<web_link>'updated\_at':'2024-10-02T17:22:31.590605+00:00'}`
```
每种记忆类型都是一个Python 类([`Item`])，具有特定属性。我们可以像上面那样通过`.dict`转换来将其作为字典访问。它具有的属性是
* `value`：此记忆的值（本身是一个字典）
* `key`：此记忆在此命名空间中的唯一键
* `namespace`：一个字符串列表，此记忆类型的命名空间
* `created\_at`：此记忆创建时的时间戳
* `updated\_at`：此记忆更新时的时间戳### 语义搜索[¶] 
除了简单检索，该存储还支持语义搜索，允许你根据含义而非精确匹配来查找记忆。要启用此功能，请使用嵌入模型配置存储*API


---
*数据来源: Exa搜索 | 获取时间: 2026-02-22 20:38:18*