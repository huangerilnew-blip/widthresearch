# 如何从你的图中流式传输大语言模型（LLM）的令牌

**URL**:
https://www.langgraphcn.org/how-tos/streaming-tokens/

## 元数据
- 发布日期: 2025-01-01T00:00:00+00:00

## 完整内容
---
[Skip to content] 

# 如何从你的图中流式传输大语言模型（LLM）的令牌 [¶] 

前提条件

本指南假设你熟悉以下内容：

- [流式传输] 
- [聊天模型] 

在使用 LangGraph 构建大语言模型（LLM）应用程序时，你可能希望从 LangGraph 节点内的大语言模型调用中流式传输单个大语言模型令牌。你可以通过 `graph.stream(..., stream_mode="messages")` 来实现这一点：

```
fromlanggraph.graphimport StateGraph
fromlangchain_openaiimport ChatOpenAI

model = ChatOpenAI()
defcall_model(state: State):
    model.invoke(...)
    ...

graph = (
    StateGraph(State)
    .add_node(call_model)
    ...
    .compile()

for msg, metadata in graph.stream(inputs, stream_mode="messages"):
    print(msg)

```

流式输出将是 `(消息块, 元数据)` 元组：

- 消息块是大语言模型流式传输的令牌
- 元数据是一个字典，包含有关调用大语言模型的图节点的信息以及大语言模型调用元数据

不使用 LangChain 的情况

如果你需要 **不使用 LangChain** 来流式传输大语言模型令牌，可以使用 [`stream_mode="custom"`] 直接从大语言模型提供商客户端流式传输输出。查看下面的 [示例] 以了解更多信息。

Python 版本低于 3.11 时的异步操作

当在 Python 版本低于 3.11 的环境中使用异步代码时，请确保在调用聊天模型时手动传递 `RunnableConfig`，如下所示： `model.ainvoke(..., config)`。
流方法使用作为回调传递的流式跟踪器从嵌套代码中收集所有事件。在 Python 3.11 及更高版本中，这通过 [contextvars] 自动处理；在 3.11 之前， [asyncio 的任务] 缺乏对 `contextvar` 的适当支持，这意味着只有在你手动传递配置时，回调才会传播。我们在下面的 `call_model` 函数中进行了这样的操作。

## 安装设置 [¶] 

首先，我们需要安装所需的软件包。

```
%%capture --no-stderr
%pip install --quiet -U langgraph langchain_openai

```

接下来，我们需要为 OpenAI（我们将使用的大语言模型）设置 API 密钥。

```
importgetpass
importos

def_set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")

_set_env("OPENAI_API_KEY")

```

为 LangGraph 开发设置 [LangSmith] 

注册 LangSmith 以快速发现问题并提升你的 LangGraph 项目的性能。LangSmith 允许你使用跟踪数据来调试、测试和监控使用 LangGraph 构建的大语言模型应用程序 — 点击 [此处] 了解更多关于如何开始使用的信息。

Note

请注意，在下面的 `call_model(state: State, config: RunnableConfig):` 中，我们 a) 在节点函数中接受 [`RunnableConfig`] ，并且 b) 将其作为 `model.ainvoke(..., config)` 的第二个参数传入。对于 Python >= 3.11 版本，这是可选操作。

## 示例 [¶] 

下面我们展示一个在单个节点中进行两次大语言模型（LLM）调用的示例。

```
fromtypingimport TypedDict
fromlanggraph.graphimport START, StateGraph, MessagesState
fromlangchain_openaiimport ChatOpenAI

# Note: we're adding the tags here to be able to filter the model outputs down the line
joke_model = ChatOpenAI(model="gpt-4o-mini", tags=["joke"])
poem_model = ChatOpenAI(model="gpt-4o-mini", tags=["poem"])

classState(TypedDict):
    topic: str
    joke: str
    poem: str

async defcall_model(state, config):
    topic = state["topic"]
    print("Writing joke...")
    # Note: Passing the config through explicitly is required for python < 3.11
    # Since context var support wasn't added before then: https://docs.python.org/3/library/asyncio-task.html#creating-tasks
    joke_response = await joke_model.ainvoke(
        [{"role": "user", "content": f"Write a joke about {topic}"}],
        config,
    )
    print("\n\nWriting poem...")
    poem_response = await poem_model.ainvoke(
        [{"role": "user", "content": f"Write a short poem about {topic}"}],
        config,
    )
    return {"joke": joke_response.content, "poem": poem_response.content}

graph = StateGraph(State).add_node(call_model).add_edge(START, "call_model").compile()

```

```
async for msg, metadata in graph.astream(
    {"topic": "cats"},
    stream_mode="messages",
):
    if msg.content:
        print(msg.content, end="|", flush=True)

```

```
Writing joke...
Why| was| the| cat| sitting| on| the| computer|?

|Because| it| wanted| to| keep| an| eye| on| the| mouse|!|

Writing poem...
In| sun|lit| patches|,| sleek| and| sly|,|
|Wh|isk|ers| twitch| as| shadows| fly|.|
|With| velvet| paws| and| eyes| so| bright|,|
|They| dance| through| dreams|,| both| day| and| night|.|

|A| playful| p|ounce|,| a| gentle| p|urr|,|
|In| every| leap|,| a| soft| allure|.|
|Cur|led| in| warmth|,| a| silent| grace|,|
|Each| furry| friend|,| a| warm| embrace|.|

|Myst|ery| wrapped| in| fur| and| charm|,|
|A| soothing| presence|,| a| gentle| balm|.|
|In| their| gaze|,| the| world| slows| down|,|
|For| in| their| realm|,| we're| all| ren|own|.|

```

```
metadata

```

```
{'langgraph_step': 1,
 'langgraph_node': 'call_model',
 'langgraph_triggers': ['start:call_model'],
 'langgraph_path': ('__pregel_pull', 'call_model'),
 'langgraph_checkpoint_ns': 'call_model:6ddc5f0f-1dd0-325d-3014-f949286ce595',
 'checkpoint_ns': 'call_model:6ddc5f0f-1dd0-325d-3014-f949286ce595',
 'ls_provider': 'openai',
 'ls_model_name': 'gpt-4o-mini',
 'ls_model_type': 'chat',
 'ls_temperature': 0.7,
 'tags': ['poem']}

```

### 过滤到特定的大语言模型（LLM）调用 [¶] 

你可以看到，我们正在从所有大语言模型（LLM）调用中流式传输令牌。现在，让我们对流式传输的令牌进行过滤，使其仅包含特定的大语言模型调用。我们可以使用流式传输的元数据，并利用之前添加到大语言模型中的标签来过滤事件：

```
async for msg, metadata in graph.astream(
    {"topic": "cats"},
    stream_mode="messages",
):
    if msg.content and "joke" in metadata.get("tags", []):
        print(msg.content, end="|", flush=True)

```

```
Writing joke...
Why| was| the| cat| sitting| on| the| computer|?

|Because| it| wanted| to| keep| an| eye| on| the| mouse|!|

Writing poem...

```

## 不使用 LangChain 的示例 [¶] 

```
fromopenaiimport AsyncOpenAI

openai_client = AsyncOpenAI()
model_name = "gpt-4o-mini"

async defstream_tokens(model_name: str, messages: list[dict]):
    response = await openai_client.chat.completions.create(
        messages=messages, model=model_name, stream=True
    )

    role = None
    async for chunk in response:
        delta = chunk.choices[0].delta

        if delta.role is not None:
            role = delta.role

        if delta.content:
            yield {"role": role, "content": delta.content}

async defcall_model(state, config, writer):
    topic = state["topic"]
    joke = ""
    poem = ""

    print("Writing joke...")
    async for msg_chunk in stream_tokens(
        model_name, [{"role": "user", "content": f"Write a joke about {topic}"}]
    ):
        joke += msg_chunk["content"]
        metadata = {**config["metadata"], "tags": ["joke"]}
        chunk_to_stream = (msg_chunk, metadata)
        writer(chunk_to_stream)

    print("\n\nWriting poem...")
    async for msg_chunk in stream_tokens(
        model_name, [{"role": "user", "content": f"Write a short poem about {topic}"}]
    ):
        poem += msg_chunk["content"]
        metadata = {**config["metadata"], "tags": ["poem"]}
        chunk_to_stream = (msg_chunk, metadata)
        writer(chunk_to_stream)

    return {"joke": joke, "poem": poem}

graph = StateGraph(State).add_node(call_model).add_edge(START, "call_model").compile()

```

stream\_mode="自定义"

当不使用 LangChain 流式传输大语言模型（LLM）的令牌时，我们建议使用 [`stream_mode="custom"`] 。这使你能够明确控制将大语言模型提供商 API 中的哪些数据包含在 LangGraph 流式输出中，包括任何额外的元数据。

```
async for msg, metadata in graph.astream(
    {"topic": "cats"},
    stream_mode="custom",
):
    print(msg["content"], end="|", flush=True)

```

```
Writing joke...
Why| was| the| cat| sitting| on| the| computer|?

|Because| it| wanted| to| keep| an| eye| on| the|

Writing poem...
 mouse|!|In| sun|lit| patches|,| they| stretch| and| y|awn|,|
|With| whispered| paws| at| the| break| of| dawn|.|
|Wh|isk|ers| twitch| in| the| morning| light|,|
|Sil|ken| shadows|,| a| graceful| sight|.|

|The| gentle| p|urr|s|,| a| soothing| song|,|
|In| a| world| of| comfort|,| where| they| belong|.|
|M|yster|ious| hearts| wrapped| in| soft|est| fur|,|
|F|eline| whispers| in| every| p|urr|.|

|Ch|asing| dreams| on| a| moon|lit| chase|,|
|With| a| flick| of| a| tail|,| they| glide| with| grace|.|
|Oh|,| playful| spirits| of| whisk|ered| cheer|,|
|In| your| quiet| company|,| the| world| feels| near|.|  |

```

```
metadata

```

```
{'langgraph_step': 1,
 'langgraph_node': 'call_model',
 'langgraph_triggers': ['start:call_model'],
 'langgraph_path': ('__pregel_pull', 'call_model'),
 'langgraph_checkpoint_ns': 'call_model:3fa3fbe1-39d8-5209-dd77-0da38d4cc1c9',
 'tags': ['poem']}

```

要筛选到特定的大语言模型（LLM）调用，你可以使用流式元数据：

```
async for msg, metadata in graph.astream(
    {"topic": "cats"},
    stream_mode="custom",
):
    if "poem" in metadata.get("tags", []):
        print(msg["content"], end="|", flush=True)

```

```
Writing joke...

Writing poem...
In| shadows| soft|,| they| weave| and| play|,|
|With| whispered| paws|,| they| greet| the| day|.|
|Eyes| like| lantern|s|,| bright| and| keen|,|
|Guard|ians| of| secrets|,| unseen|,| serene|.|

|They| twist| and| stretch| in| sun|lit| beams|,|
|Ch|asing| the| echoes| of| half|-|formed| dreams|.|
|With| p|urring| songs| that| soothe| the| night|,|
|F|eline| spirits|,| pure| delight|.|

|On| windows|ills|,| they| perch| and| stare|,|
|Ad|vent|urers| bold| with| a| graceful| flair|.|
|In| every| leap| and| playful| bound|,|
|The| magic| of| cats|—|where| love| is| found|.|

```

## Comments

Back to top


---
*数据来源: Exa搜索 | 获取时间: 2026-02-19 20:08:35*