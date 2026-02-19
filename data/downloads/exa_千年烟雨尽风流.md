# 千年烟雨尽风流

**URL**:
https://www.cnblogs.com/studyLog-share/p/19289014

## 元数据
- 发布日期: 2026-02-19T20:07:27.040725

## 完整内容
---
LangGraph：add\_conditional\_edges详解 - 时空穿越者- 博客园[![]] 
[![返回主页]] # [千年烟雨尽风流] 
## 专注于Java开发与分布式计算，涉猎PHP乐园，做一个快乐的程序猿^\_^
* [博客园] 
* [首页] 
* [新随笔] 
* [联系] 
* [订阅] 
* [管理] 
# [LangGraph：add\_conditional\_edges详解] 
在LangGraph 中，`add\_conditional\_edges`是构建动态工作流的关键，用于创建基于条件判断的分支路径；它允许工作流根据当前状态动态决定下一步的执行路径，这种模式使 LangGraph 能够处理复杂的、状态驱动的对话流程，特别是在需要工具调用和多次交互的场景中。# 示例```
#State ManagementclassState(TypedDict):
messages: Annotated[List[AnyMessage], add\_messages]
​#Nodesdefchat\_node(state: State) -&gt;&gt;State:
state["messages"] = chat\_llm.invoke({"messages": state["messages"]})returnstate
​#Building the graphgraph\_builder =StateGraph(State)
graph\_builder.add\_node("chat\_node", chat\_node)
graph\_builder.add\_node("tool\_node", ToolNode(tools=tools))
graph\_builder.add\_edge(START,"chat\_node")
graph\_builder.add\_conditional\_edges("chat\_node", tools\_condition, {"tools":"tool\_node","\_\_end\_\_": END})
graph\_builder.add\_edge("tool\_node","chat\_node")
graph= graph\_builder.compile(checkpointer=MemorySaver())returngraph
```
解读：上述示例的执行流程如下：![image]<image_link>
## 细节描述执行工具节点```
classToolNode:def\_\_init\_\_(self, tools):
self.tools=toolsdef\_\_call\_\_(self, state: State) -&gt;State:#执行工具调用tool\_results =[]fortool\_callinstate["messages"][-1].tool\_calls:
tool= self.tools[tool\_call["name"]]
result= tool.invoke(tool\_call["args"])
tool\_results.append(result)return{"messages": tool\_results}
```
状态更新：将工具执行结果作为新消息添加工具节点执行后，通过graph\_builder.add\_edge("tool\_node", "chat\_node") 返回聊天节点继续生成对工具结果的响应## 重点关注add\_conditional\_edges，这个方法包含三个核心参数
![image] 
A、源节点：条件分支的起点
B、条件函数：决定分支路径的函数
C、分支映射：将条件函数返回值映射到目标节点的字典
# 条件函数条件函数是一个自定义函数，它接收当前状态作为输入，返回一个字符串值，表示下一步应该执行的路径。在上面示例中，`tools\_condition`函数可能类似这样：
```
deftools\_condition(state: State) -&gt;&gt;str:"""判断是否需要调用工具"""#获取最后一条消息last\_message = state["messages"][-1]#检查是否是工具调用请求ifhasattr(last\_message,"tool\_calls")andlast\_message.tool\_calls:return"tools"#需要调用工具else:return"\_\_end\_\_"#结束对话
```
## tools\_condition（LangGraph源码）
![image] 
![image] 
```
deftools\_condition(
state: list[AnyMessage]| dict[str, Any] |BaseModel,
messages\_key: str="messages",
)-&gt; Literal["tools","\_\_end\_\_"]:"""Conditional routing function for tool-calling workflows.
This utility function implements the standard conditional logic for ReAct-style
agents: if the last `AIMessage` contains tool calls, route to the tool execution
node; otherwise, end the workflow. This pattern is fundamental to most tool-calling
agent architectures.
The function handles multiple state formats commonly used in LangGraph applications,
making it flexible for different graph designs while maintaining consistent behavior.
Args:
state: The current graph state to examine for tool calls. Supported formats:
- Dictionary containing a messages key (for `StateGraph`)
- `BaseModel` instance with a messages attribute
messages\_key: The key or attribute name containing the message list in the state.
This allows customization for graphs using different state schemas.
Returns:
Either `'tools'` if tool calls are present in the last `AIMessage`, or `'\_\_end\_\_'`
to terminate the workflow. These are the standard routing destinations for
tool-calling conditional edges.
Raises:
ValueError: If no messages can be found in the provided state format.
Example:
Basic usage in a ReAct agent:
```python
from langgraph.graph import StateGraph
from langchain.tools import ToolNode
from langchain.tools.tool\_node import tools\_condition
from typing\_extensions import TypedDict
class State(TypedDict):
messages: list
graph = StateGraph(State)
graph.add\_node("llm", call\_model)
graph.add\_node("tools", ToolNode([my\_tool]))
graph.add\_conditional\_edges(
"llm",
tools\_condition, # Routes to "tools" or "\_\_end\_\_"
{"tools": "tools", "\_\_end\_\_": "\_\_end\_\_"},
)
```
Custom messages key:
```python
def custom\_condition(state):
return tools\_condition(state, messages\_key="chat\_history")
```
!!! note
This function is designed to work seamlessly with `ToolNode` and standard
LangGraph patterns. It expects the last message to be an `AIMessage` when
tool calls are present, which is the standard output format for tool-calling
language models."""ifisinstance(state, list):
ai\_message= state[-1]elif(isinstance(state, dict)and(messages := state.get(messages\_key, [])))or(
messages :=getattr(state, messages\_key, [])
):
ai\_message= messages[-1]else:
msg= f"No messages found in input state to tool\_edge: {state}"raiseValueError(msg)ifhasattr(ai\_message,"tool\_calls")andlen(ai\_message.tool\_calls) &gt;&gt;0:return"tools"return"\_\_end\_\_"
```
# 分支映射分支映射是一个字典，将条件函数的返回值映射到具体的节点或特殊端点：```
{"tools":"tool\_node",#当条件返回 "tools" 时，跳转到tool\_node"\_\_end\_\_": END#当条件返回 "\_\_end\_\_" 时，结束工作流}
```
特殊端点：* `START`：工作流起点
* `END`：工作流终点
# 条件分支的高级应用## 多分支条件可以创建包含多个可能路径的条件分支```
defadvanced\_condition(state: State) -&gt;&gt;str:
last\_message= state["messages"][-1]if"help"inlast\_message.content:return"help\_flow"elif"purchase"inlast\_message.content:return"checkout\_flow"elif"cancel"inlast\_message.content:return"cancellation\_flow"else:return"\_\_end\_\_"graph\_builder.add\_conditional\_edges("chat\_node",
advanced\_condition,
{"help\_flow":"help\_node","checkout\_flow":"checkout\_node","cancellation\_flow":"cancellation\_node","\_\_end\_\_": END
}
)
```
## 嵌套条件分支```
#第一层条件分支graph\_builder.add\_conditional\_edges("initial\_node",
determine\_flow\_type,
{"support":"support\_flow","sales":"sales\_flow"}
)#支持流中的子分支graph\_builder.add\_conditional\_edges("support\_flow",
support\_condition,
{"technical":"tech\_support\_node","billing":"billing\_support\_node"}
)#销售流中的子分支graph\_builder.add\_conditional\_edges("sales\_flow",
sales\_condition,
{"new":"new\_customer\_node","existing":"existing\_customer\_node"}
)
```
# 最佳实践## 保持条件函数纯净只读取状态，不修改状态避免副作用## 明确的返回值使用描述性的字符串作为返回值确保返回值在分支映射中有对应项## 错误处理```
defsafe\_condition(state: State) -&gt;&gt;str:try:#业务逻辑exceptException as e:#记录错误state["errors"].append(str(e))return"error\_handling"
```
## 状态设计确保状态包含条件判断所需的所有信息使用清晰的字段命名# 扩展阅读[使用Graph API | LangChain 中文文档]<web_link>
![image]<image_link>
posted @2025-11-30 13:47[时空穿越者]<web_link>
阅读(176)
评论(0)
[收藏]<web_link>[举报]<web_link>
[刷新页面]<web_link>[返回顶部]<web_link>
[![]<image_link>]<web_link>
### 公告[博客园]<web_link>&copy;&copy; 2004-2026
[![]<image_link>浙公网安备 33010602011771号]<web_link>[浙ICP备2021040463号-3]<web_link>


---
*数据来源: Exa搜索 | 获取时间: 2026-02-19 20:08:35*