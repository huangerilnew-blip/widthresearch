# LangGraph实战教程(6)：Human-in-the-loop 实现，大模型入门到精通

**URL**:
https://modelengine.csdn.net/690c4f4c5511483559e2a5b8.html

## 元数据
- 发布日期: 2025-09-26T00:00:00+00:00

## 完整内容
---
LangGraph实战教程(6)：Human-in-the-loop 实现，大模型入门到精通，收藏这篇就足够了！_人工智能_Python老猿-ModelEngine社区

[ModelEngine社区] LangGraph实战教程(6)：Human-in-the-loop 实现，大模型入门到精通，收藏这篇就足够了！

# LangGraph实战教程(6)：Human-in-the-loop 实现，大模型入门到精通，收藏这篇就足够了！

Human-in-the-loop（HITL，人在回路/人机协同/人类监督）是一种AI系统设计范式，强调在关键决策点引入人类干预，形成“人工监督-AI执行-反馈优化”的闭环机制。

### Python老猿

[1649人浏览 · 2025-09-26 11:02:17] 

[Python老猿] · 2025-09-26 11:02:17 发布

### 一、什么是Human-in-the-loop

Human-in-the-loop（HITL，人在回路/人机协同/人类监督）是一种AI系统设计范式，强调在关键决策点引入人类干预，形成“人工监督-AI执行-反馈优化”的闭环机制。在大模型智能体应用中，HITL能显著提升复杂任务的可靠性、可解释性与合规性，尤其在金融、医疗等高敏感领域。

#### 核心目的

风险控制：防止AI的偏见、错误或不可预测行为，如自动执行高风险工具、AP的I调用，特别是一些产生数据更新的调用。知识增强：人类提供专业经验，弥补AI在上下文理解上的不足，修正AI的输出结果，AI远远不是万能的，输出结果可能存在幻觉和错误的推理，通过人工的监督反馈，引导AI修正错误的输出结果。

工作流闭环：

```
是

否
AI自主执行
需人工干预？
暂停并请求人类输入
人工审核/编辑/反馈
更新状态并继续执行
完成输出

```

### 二、LangGraph实现Human-in-the-loop

LangGraph主要使用中断+恢复的机制来实现HITL，其中提供了两种中断图流程的方法：

- • 静态中断: 使用interrupt_before和interrupt_after在定义的点暂停图形，在节点执行之前或之后。
- • 动态中断: 根据图的当前状态，使用中断从特定节点内部暂停图。

#### 动态中断

LangGraph主要使用中断interrupt 和Command来实现动态中断。

1. 创建中断点interrupt: interrupt之前需要使用checkpointer来保存节点执行的每一步状态，如果需要随时恢复，则建议使用能持久化的checkpointer,如数据库。

```
from typing import TypedDictimport uuidfrom langgraph.checkpoint.memory import InMemorySaverfrom langgraph.constants import STARTfrom langgraph.graph import StateGraphfrom langgraph.types import interrupt, Commandclass State(TypedDict):    messsage: str    age: str# Human node进行中断def human_node(state: State):    value = interrupt(         {            "messsage": state["messsage"]         }    )    return {        "age": value     }# Build the graphgraph_builder = StateGraph(State)graph_builder.add_node("human_node", human_node)graph_builder.add_edge(START, "human_node")checkpointer = InMemorySaver() graph = graph_builder.compile(checkpointer=checkpointer)# Pass a thread ID to the graph to run it.config = {"configurable": {"thread_id": uuid.uuid4()}}# Run the graph until the interrupt is hit.result = graph.invoke({"messsage": "我的年龄是多少？"}, config=config) print(result['__interrupt__']) #输出[Interrupt(value={'messsage': '我的年龄是多少？'}, resumable=True, ns=['human_node:1a8de8ea-e477-7583-30aa-263f8e02571f'])]#使用Command原语来恢复print(graph.invoke(Command(resume="25"), config=config)) #输出：{'messsage': '我的年龄是多少？', 'age': '25'}

```

1. 创建恢复命令command:

当使用interrupt()方法后，流程就会中断，此时可以通过Command原语来恢复流程执行。Command原语需要在图的invoke、ainvoke、stream或者astream方法中调用。

```
graph.invoke(Command(resume={"age": "25"}), thread_config)

```

#### 静态中断

静态中断（也称为静态断点）在节点执行之前或之后触发。一般建议静态中断只在调试和测试中使用。

```
from typing_extensions import TypedDictfrom langgraph.checkpoint.memory import InMemorySaver from langgraph.graph import StateGraph, START, ENDclass State(TypedDict):    input: strdef step_1(state):    print("---Step 1---")    passdef step_2(state):    print("---Step 2---")    passdef step_3(state):    print("---Step 3---")    passbuilder = StateGraph(State)builder.add_node("step_1", step_1)builder.add_node("step_2", step_2)builder.add_node("step_3", step_3)builder.add_edge(START, "step_1")builder.add_edge("step_1", "step_2")builder.add_edge("step_2", "step_3")builder.add_edge("step_3", END)# Set up a checkpointer checkpointer = InMemorySaver() # (1)!graph = builder.compile(    checkpointer=checkpointer, # (2)!    # interrupt_after=["step_1"] # 执行step1后，中断!    interrupt_before=["step_3"], # 执行step3前，中断!)# Inputinitial_input = {"input": "hello world"}# Threadthread = {"configurable": {"thread_id": "1"}}# Run the graph until the first interruptionfor event in graph.stream(initial_input, thread, stream_mode="values"):    print(event)# This will run until the breakpoint# You can get the state of the graph at this pointprint(graph.get_state(thread))# 可以输入 `None` 恢复流程 for event in graph.stream(None, thread, stream_mode="values"):    print(event)    # print(graph.get_state(thread))# for event in graph.stream(None, thread, stream_mode="values"):#     print(event)

```

### 三、4种典型的Human-in-the-loop场景

#### 1. 人工审批

在一个关键步骤前中断流程，如一个工具调用，要求反馈用户同意或拒绝才继续执行流程。

```
from typing importLiteral, TypedDictimport uuidfrom langgraph.constants import START, ENDfrom langgraph.graph import StateGraphfrom langgraph.types import interrupt, Commandfrom langgraph.checkpoint.memory import MemorySaver# Define the shared graph stateclass State(TypedDict):    llm_output: str    decision: str# Simulate an LLM output nodedef generate_llm_output(state: State) -> State:    return {"llm_output": "This is the generated output."}# 人工中断审核节点def human_approval(state: State) -> Command[Literal["approved_path", "rejected_path"]]:    decision = interrupt({        "question": "Do you approve the following output?",        "llm_output": state["llm_output"]    })# 人工审核通过    if decision == "approve":        return Command(goto="approved_path", update={"decision": "approved"})# 人工审核拒绝    else:        return Command(goto="rejected_path", update={"decision": "rejected"})# Next steps after approvaldef approved_node(state: State) -> State:    print("✅ Approved path taken.")    return state# Alternative path after rejectiondef rejected_node(state: State) -> State:    print("❌ Rejected path taken.")    return state# Build the graphbuilder = StateGraph(State)builder.add_node("generate_llm_output", generate_llm_output)builder.add_node("human_approval", human_approval)builder.add_node("approved_path", approved_node)builder.add_node("rejected_path", rejected_node)builder.set_entry_point("generate_llm_output")builder.add_edge("generate_llm_output", "human_approval")builder.add_edge("approved_path", END)builder.add_edge("rejected_path", END)checkpointer = MemorySaver()graph = builder.compile(checkpointer=checkpointer)# Run until interruptconfig = {"configurable": {"thread_id": uuid.uuid4()}}result = graph.invoke({}, config=config)print(result["__interrupt__"])# Output:# Interrupt(value={'question': 'Do you approve the following output?', 'llm_output': 'This is the generated output.'}, ...)# 模拟人审核通过# 测试拒绝, 则替换 resume="approve" with resume="reject"final_result = graph.invoke(Command(resume="approve"), config=config)print(final_result)

```

#### 2. 审查和修改状态

用户可以查看和编辑图的状态。这对于纠正错误或使用附加信息更新状态非常有用。

```
from typing import TypedDictimport uuidfrom langgraph.constants import START, ENDfrom langgraph.graph import StateGraphfrom langgraph.types import interrupt, Commandfrom langgraph.checkpoint.memory import MemorySaverfrom typing import TypedDictimport uuidfrom langgraph.constants import START, ENDfrom langgraph.graph import StateGraphfrom langgraph.types import interrupt, Commandfrom langgraph.checkpoint.memory import MemorySaver# Define the graph stateclass State(TypedDict):    summary: str# Simulate an LLM summary generationdef generate_summary(state: State) -> State:    return {        "summary": "The cat sat on the mat and looked at the stars."    }# 用户审查和修改节点函数def human_review_edit(state: State) -> State:    result = interrupt({        "task": "Please review and edit the generated summary if necessary.",        "generated_summary": state["summary"]    })    # 返回人工重新编辑修改summary    return {        "summary": result["edited_summary"]    }# Simulate downstream use of the edited summarydef downstream_use(state: State) -> State:    print(f"✅ Using edited summary: {state['summary']}")    return state# Build the graphbuilder = StateGraph(State)builder.add_node("generate_summary", generate_summary)builder.add_node("human_review_edit", human_review_edit)builder.add_node("downstream_use", downstream_use)builder.set_entry_point("generate_summary")builder.add_edge("generate_summary", "human_review_edit")builder.add_edge("human_review_edit", "downstream_use")builder.add_edge("downstream_use", END)# Set up in-memory checkpointing for interrupt supportcheckpointer = MemorySaver()graph = builder.compile(checkpointer=checkpointer)# Invoke the graph until it hits the interruptconfig = {"configurable": {"thread_id": uuid.uuid4()}}result = graph.invoke({}, config=config)# Output interrupt payloadprint(result["__interrupt__"])# Example output:# Interrupt(#   value={#     'task': 'Please review and edit the generated summary if necessary.',#     'generated_summary': 'The cat sat on the mat and looked at the stars.'#   },#   resumable=True,#   ...# )# Resume the graph with human-edited inputedited_summary = "The cat lay on the rug, gazing peacefully at the night sky."resumed_result = graph.invoke(    Command(resume={"edited_summary": edited_summary}),    config=config)print(resumed_result)

```

#### 3. 审核工具调用

用户可以在调用工具之前进行检查和编辑LLM的输出，特别是在在LLM请求的工具调用可能很敏感或需要人工监督的应用程序中，如果轻易的任大模型调用有数据更新的工具或者API，可能会产生严重的后果。

```
from langgraph.checkpoint.memory import InMemorySaverfrom langgraph.types import interruptfrom langgraph.prebuilt import create_react_agentfrom dotenv import load_dotenv  # 用于加载环境变量load_dotenv()  # 加载 .env 文件中的环境变量# An example of a sensitive tool that requires human review / approvaldef book_hotel(hotel_name: str):    """Book a hotel"""    # 调用预订酒店API时中断点，等待用户确认    response = interrupt(          f"Trying to call `book_hotel` with args {{'hotel_name': {hotel_name}}}. "        "Please approve or suggest edits."    )    if response["type"] == "accept":        pass    elif response["type"] == "edit":        hotel_name = response["args"]["hotel_name"]    else:        raise ValueError(f"Unknown response type: {response['type']}")    return f"Successfully booked a stay at {hotel_name}."checkpointer = InMemorySaver() agent = create_react_agent(    model="deepseek:deepseek-chat",    tools=[book_hotel],    checkpointer=checkpointer, )config = {   "configurable": {      "thread_id": "1"   }}for chunk in agent.stream(    {"messages": [{"role": "user", "content": "book a stay at McKittrick hotel"}]},    config):    print(chunk)    print("\n")    from langgraph.types import Commandfor chunk in agent.stream(    Command(resume={"type": "accept"}),      # Command(resume={"type": "edit", "args": {"hotel_name": "McKittrick Hotel"}}),    config):    print(chunk)    print("\n")

```

以上在工具实现函数调用前进行中断，实现起来比较侵入性比较强，


---
*数据来源: Exa搜索 | 获取时间: 2026-02-24 22:28:27*