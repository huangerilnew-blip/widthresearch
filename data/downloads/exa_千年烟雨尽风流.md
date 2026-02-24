# 千年烟雨尽风流

**URL**:
https://www.cnblogs.com/studyLog-share/p/19289014

## 元数据
- 发布日期: 2026-02-24T22:27:15.427232

## 完整内容
---
LangGraph：add\_conditional\_edges详解 - 时空穿越者 - 博客园
[
![] 
] 
[![返回主页]] 
# [千年烟雨尽风流] 
## 专注于Java开发与分布式计算，涉猎PHP乐园，做一个快乐的程序猿^\_^
* [
博客园] 
* [
首页] 
* [
新随笔] 
* [
联系] 
* [
订阅] 
* [
管理] 
#
[
LangGraph：add\_conditional\_edges详解
] 
在 LangGraph 中，`add\_conditional\_edges`是构建动态工作流的关键，用于创建基于条件判断的分支路径；它允许工作流根据当前状态动态决定下一步的执行路径，这种模式使 LangGraph 能够处理复杂的、状态驱动的对话流程，特别是在需要工具调用和多次交互的场景中。
# 示例
```
    <span style="color: rgba(0, 128, 0, 1)">#</span><span style="color: rgba(0, 128, 0, 1)"> State Management</span>
    <span style="color: rgba(0, 0, 255, 1)">class</span><span style="color: rgba(0, 0, 0, 1)"> State(TypedDict):
        messages: Annotated[List[AnyMessage], add_messages]
​
    </span><span style="color: rgba(0, 128, 0, 1)">#</span><span style="color: rgba(0, 128, 0, 1)"> Nodes</span>
    <span style="color: rgba(0, 0, 255, 1)">def</span> chat_node(state: State) -><span style="color: rgba(0, 0, 0, 1)"> State:
        state[</span><span style="color: rgba(128, 0, 0, 1)">"</span><span style="color: rgba(128, 0, 0, 1)">messages</span><span style="color: rgba(128, 0, 0, 1)">"</span>] = chat_llm.invoke({<span style="color: rgba(128, 0, 0, 1)">"</span><span style="color: rgba(128, 0, 0, 1)">messages</span><span style="color: rgba(128, 0, 0, 1)">"</span>: state[<span style="color: rgba(128, 0, 0, 1)">"</span><span style="color: rgba(128, 0, 0, 1)">messages</span><span style="color: rgba(128, 0, 0, 1)">"</span><span style="color: rgba(0, 0, 0, 1)">]})
        </span><span style="color: rgba(0, 0, 255, 1)">return</span><span style="color: rgba(0, 0, 0, 1)"> state
​
    </span><span style="color: rgba(0, 128, 0, 1)">#</span><span style="color: rgba(0, 128, 0, 1)"> Building the graph</span>
    graph_builder =<span style="color: rgba(0, 0, 0, 1)"> StateGraph(State)
    graph_builder.add_node(</span><span style="color: rgba(128, 0, 0, 1)">"</span><span style="color: rgba(128, 0, 0, 1)">chat_node</span><span style="color: rgba(128, 0, 0, 1)">"</span><span style="color: rgba(0, 0, 0, 1)">, chat_node)
    graph_builder.add_node(</span><span style="color: rgba(128, 0, 0, 1)">"</span><span style="color: rgba(128, 0, 0, 1)">tool_node</span><span style="color: rgba(128, 0, 0, 1)">"</span>, ToolNode(tools=<span style="color: rgba(0, 0, 0, 1)">tools))
    graph_builder.add_edge(START, </span><span style="color: rgba(128, 0, 0, 1)">"</span><span style="color: rgba(128, 0, 0, 1)">chat_node</span><span style="color: rgba(128, 0, 0, 1)">"</span><span style="color: rgba(0, 0, 0, 1)">)
    graph_builder.add_conditional_edges(</span><span style="color: rgba(128, 0, 0, 1)">"</span><span style="color: rgba(128, 0, 0, 1)">chat_node</span><span style="color: rgba(128, 0, 0, 1)">"</span>, tools_condition, {<span style="color: rgba(128, 0, 0, 1)">"</span><span style="color: rgba(128, 0, 0, 1)">tools</span><span style="color: rgba(128, 0, 0, 1)">"</span>: <span style="color: rgba(128, 0, 0, 1)">"</span><span style="color: rgba(128, 0, 0, 1)">tool_node</span><span style="color: rgba(128, 0, 0, 1)">"</span>, <span style="color: rgba(128, 0, 0, 1)">"</span><span style="color: rgba(128, 0, 0, 1)">__end__</span><span style="color: rgba(128, 0, 0, 1)">"</span><span style="color: rgba(0, 0, 0, 1)">: END})
    graph_builder.add_edge(</span><span style="color: rgba(128, 0, 0, 1)">"</span><span style="color: rgba(128, 0, 0, 1)">tool_node</span><span style="color: rgba(128, 0, 0, 1)">"</span>, <span style="color: rgba(128, 0, 0, 1)">"</span><span style="color: rgba(128, 0, 0, 1)">chat_node</span><span style="color: rgba(128, 0, 0, 1)">"</span><span style="color: rgba(0, 0, 0, 1)">)
    graph </span>= graph_builder.compile(checkpointer=<span style="color: rgba(0, 0, 0, 1)">MemorySaver())
    </span><span style="color: rgba(0, 0, 255, 1)">return</span> graph
```
解读：
上述示例的执行流程如下：
![image] 
## 细节描述
执行工具节点
```
<span style="color: rgba(0, 0, 255, 1)">class</span><span style="color: rgba(0, 0, 0, 1)"> ToolNode:
    </span><span style="color: rgba(0, 0, 255, 1)">def</span> <span style="color: rgba(128, 0, 128, 1)">__init__</span><span style="color: rgba(0, 0, 0, 1)">(self, tools):
        self.tools </span>=<span style="color: rgba(0, 0, 0, 1)"> tools
    
    </span><span style="color: rgba(0, 0, 255, 1)">def</span> <span style="color: rgba(128, 0, 128, 1)">__call__</span>(self, state: State) -><span style="color: rgba(0, 0, 0, 1)"> State:
        </span><span style="color: rgba(0, 128, 0, 1)">#</span><span style="color: rgba(0, 128, 0, 1)"> 执行工具调用</span>
        tool_results =<span style="color: rgba(0, 0, 0, 1)"> []
        </span><span style="color: rgba(0, 0, 255, 1)">for</span> tool_call <span style="color: rgba(0, 0, 255, 1)">in</span> state[<span style="color: rgba(128, 0, 0, 1)">"</span><span style="color: rgba(128, 0, 0, 1)">messages</span><span style="color: rgba(128, 0, 0, 1)">"</span>][-1<span style="color: rgba(0, 0, 0, 1)">].tool_calls:
            tool </span>= self.tools[tool_call[<span style="color: rgba(128, 0, 0, 1)">"</span><span style="color: rgba(128, 0, 0, 1)">name</span><span style="color: rgba(128, 0, 0, 1)">"</span><span style="color: rgba(0, 0, 0, 1)">]]
            result </span>= tool.invoke(tool_call[<span style="color: rgba(128, 0, 0, 1)">"</span><span style="color: rgba(128, 0, 0, 1)">args</span><span style="color: rgba(128, 0, 0, 1)">"</span><span style="color: rgba(0, 0, 0, 1)">])
            tool_results.append(result)
        
        </span><span style="color: rgba(0, 0, 255, 1)">return</span> {<span style="color: rgba(128, 0, 0, 1)">"</span><span style="color: rgba(128, 0, 0, 1)">messages</span><span style="color: rgba(128, 0, 0, 1)">"</span>: tool_results}
```
状态更新：将工具执行结果作为新消息添加
工具节点执行后，通过 graph\_builder.add\_edge("tool\_node", "chat\_node") 返回聊天节点继续生成对工具结果的响应
## 重点关注
add\_conditional\_edges，这个方法包含三个核心参数
![image] 
A、源节点：条件分支的起点
B、条件函数：决定分支路径的函数
C、分支映射：将条件函数返回值映射到目标节点的字典
# 条件函数
条件函数是一个自定义函数，它接收当前状态作为输入，返回一个字符串值，表示下一步应该执行的路径。
在上面示例中，`tools\_condition`函数可能类似这样：
```
<span style="color: rgba(0, 0, 255, 1)">def</span> tools_condition(state: State) -><span style="color: rgba(0, 0, 0, 1)"> str:
    </span><span style="color: rgba(128, 0, 0, 1)">"""</span><span style="color: rgba(128, 0, 0, 1)">判断是否需要调用工具</span><span style="color: rgba(128, 0, 0, 1)">"""</span>
    <span style="color: rgba(0, 128, 0, 1)">#</span><span style="color: rgba(0, 128, 0, 1)"> 获取最后一条消息</span>
    last_message = state[<span style="color: rgba(128, 0, 0, 1)">"</span><span style="color: rgba(128, 0, 0, 1)">messages</span><span style="color: rgba(128, 0, 0, 1)">"</span>][-1<span style="color: rgba(0, 0, 0, 1)">]
    
    </span><span style="color: rgba(0, 128, 0, 1)">#</span><span style="color: rgba(0, 128, 0, 1)"> 检查是否是工具调用请求</span>
    <span style="color: rgba(0, 0, 255, 1)">if</span> hasattr(last_message, <span style="color: rgba(128, 0, 0, 1)">"</span><span style="color: rgba(128, 0, 0, 1)">tool_calls</span><span style="color: rgba(128, 0, 0, 1)">"</span>) <span style="color: rgba(0, 0, 255, 1)">and</span><span style="color: rgba(0, 0, 0, 1)"> last_message.tool_calls:
        </span><span style="color: rgba(0, 0, 255, 1)">return</span> <span style="color: rgba(128, 0, 0, 1)">"</span><span style="color: rgba(128, 0, 0, 1)">tools</span><span style="color: rgba(128, 0, 0, 1)">"</span>  <span style="color: rgba(0, 128, 0, 1)">#</span><span style="color: rgba(0, 128, 0, 1)"> 需要调用工具</span>
    <span style="color: rgba(0, 0, 255, 1)">else</span><span style="color: rgba(0, 0, 0, 1)">:
        </span><span style="color: rgba(0, 0, 255, 1)">return</span> <span style="color: rgba(128, 0, 0, 1)">"</span><span style="color: rgba(128, 0, 0, 1)">__end__</span><span style="color: rgba(128, 0, 0, 1)">"</span>  <span style="color: rgba(0, 128, 0, 1)">#</span><span style="color: rgba(0, 128, 0, 1)"> 结束对话</span>
```
## tools\_condition（LangGraph源码）
![image] 
![image] 
```
<span style="color: rgba(0, 0, 255, 1)">def</span><span style="color: rgba(0, 0, 0, 1)"> tools_condition(
    state: list[AnyMessage] </span>| dict[str, Any] |<span style="color: rgba(0, 0, 0, 1)"> BaseModel,
    messages_key: str </span>= <span style="color: rgba(128, 0, 0, 1)">"</span><span style="color: rgba(128, 0, 0, 1)">messages</span><span style="color: rgba(128, 0, 0, 1)">"</span><span style="color: rgba(0, 0, 0, 1)">,
) </span>-> Literal[<span style="color: rgba(128, 0, 0, 1)">"</span><span style="color: rgba(128, 0, 0, 1)">tools</span><span style="color: rgba(128, 0, 0, 1)">"</span>, <span style="color: rgba(128, 0, 0, 1)">"</span><span style="color: rgba(128, 0, 0, 1)">__end__</span><span style="color: rgba(128, 0, 0, 1)">"</span><span style="color: rgba(0, 0, 0, 1)">]:
    </span><span style="color: rgba(128, 0, 0, 1)">"""</span><span style="color: rgba(128, 0, 0, 1)">Conditional routing function for tool-calling workflows.

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
        messages_key: The key or attribute name containing the message list in the state.
            This allows customization for graphs using different state schemas.

    Returns:
        Either `'tools'` if tool calls are present in the last `AIMessage`, or `'__end__'`
            to terminate the workflow. These are the standard routing destinations


---
*数据来源: Exa搜索 | 获取时间: 2026-02-24 22:27:47*