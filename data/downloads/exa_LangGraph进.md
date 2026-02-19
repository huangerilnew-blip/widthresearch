# LangGraph进阶：条件边与工具调用Agent实现

**URL**:
https://www.cnblogs.com/muzinan110/p/18540008

## 元数据
- 发布日期: 2024-12-26T00:00:00+00:00

## 完整内容
---
LangGraph进阶：条件边与工具调用Agent实现 - muzinan110 - 博客园[![]] 
[![返回主页]] # [muzinan110] 
## * [博客园] 
* [首页] 
* [新随笔] 
* [联系] 
* [订阅] 
* [管理] 
# [LangGraph进阶：条件边与工具调用Agent实现] 
在前两篇文章中,我们讨论了LCEL和AgentExecutor的局限性,以及LangGraph的基础概念。今天,我们将深入探讨LangGraph的高级特性,重点关注条件边的使用和如何实现一个完整的工具调用Agent。
## 条件边的高级用法条件边是LangGraph中最强大的特性之一,它允许我们基于状态动态决定执行流程。让我们深入了解一些高级用法。
### 1. 多条件路由```
fromtypingimportList, Dict, LiteralfrompydanticimportBaseModelfromlanggraph.graphimportStateGraph, ENDclassAgentState(BaseModel):
messages: List[Dict[str, str]]=[]
current\_input: str=""tools\_output: Dict[str, str]={}
status: str="RUNNING"error\_count: int=0defroute\_by\_status(state: AgentState) -&gt;&gt; Literal["process","retry","error","end"]:"""复杂的路由逻辑"""ifstate.status =="SUCCESS":return"end"elifstate.status =="ERROR":ifstate.error\_count &gt;&gt;= 3:return"error"return"retry"elifstate.status =="NEED\_TOOL":return"process"return"process"#构建图结构workflow =StateGraph(AgentState)#添加条件边workflow.add\_conditional\_edges("check\_status",
route\_by\_status,
{"process":"execute\_tool","retry":"retry\_handler","error":"error\_handler","end": END
}
)
```
### 2. 并行执行LangGraph支持并行执行多个节点,这在处理复杂任务时特别有用:
```
asyncdefparallel\_tools\_execution(state: AgentState) -&gt;&gt;AgentState:"""并行执行多个工具"""tools=identify\_required\_tools(state.current\_input)
asyncdefexecute\_tool(tool):
result=await tool.ainvoke(state.current\_input)return{tool.name: result}#并行执行所有工具results = await asyncio.gather(\*[execute\_tool(tool)fortoolintools])#合并结果tools\_output ={}forresultinresults:
tools\_output.update(result)returnAgentState(
messages=state.messages,
current\_input=state.current\_input,
tools\_output=tools\_output,
status="SUCCESS")
```
## 实现完整的工具调用Agent
让我们通过实现一个完整的工具调用Agent来展示LangGraph的强大功能。这个Agent能够:
1. 理解用户输入2. 选择合适的工具3. 执行工具调用4. 生成最终响应![]<image_link>
### 1. 定义状态和工具```
fromtypingimportList, Dict, OptionalfrompydanticimportBaseModelfromlangchain.toolsimportBaseToolfromlangchain.tools.calculatorimportCalculatorToolfromlangchain.tools.wikipediaimportWikipediaQueryRunfromlangchain\_core.language\_modelsimportChatOpenAIclassTool(BaseModel):
name: str
description: str
func: callableclassAgentState(BaseModel):
messages: List[Dict[str, str]]=[]
current\_input: str=""thought: str=""selected\_tool: Optional[str]=None
tool\_input: str=""tool\_output: str=""final\_answer: str=""status: str="STARTING"#定义可用工具tools =[
Tool(
name="calculator",
description="用于执行数学计算",
func=CalculatorTool()
),
Tool(
name="wikipedia",
description="用于查询维基百科信息",
func=WikipediaQueryRun()
)
]
```
### 2. 实现核心节点```
asyncdefthink(state: AgentState) -&gt;AgentState:"""思考下一步行动"""prompt= f"""基于用户输入和当前对话历史，思考下一步行动。
用户输入: {state.current\_input}
可用工具: {[t.name + ': ' + t.description for t in tools]}
请决定:
1. 是否需要使用工具2. 如果需要，选择哪个工具3. 使用什么参数调用工具以JSON格式返回: {{"thought": "思考过程", "need\_tool": true/false, "tool": "工具名", "tool\_input": "参数"}}"""llm= ChatOpenAI(temperature=0)
response=await llm.ainvoke(prompt)
result=json.loads(response)returnAgentState(\*\*state.dict(),
thought=result["thought"],
selected\_tool=result.get("tool"),
tool\_input=result.get("tool\_input"),
status="NEED\_TOOL"ifresult["need\_tool"]else"GENERATE\_RESPONSE")
asyncdefexecute\_tool(state: AgentState) -&gt;&gt;AgentState:"""执行工具调用"""tool= next((tfortintoolsift.name ==state.selected\_tool), None)ifnottool:returnAgentState(\*\*state.dict(),
status="ERROR",
thought="Selected tool not found")try:
result=await tool.func.ainvoke(state.tool\_input)returnAgentState(\*\*state.dict(),
tool\_output=str(result),
status="GENERATE\_RESPONSE")exceptException as e:returnAgentState(\*\*state.dict(),
status="ERROR",
thought=f"Tool execution failed: {str(e)}")
asyncdefgenerate\_response(state: AgentState) -&gt;&gt;AgentState:"""生成最终响应"""prompt= f"""基于以下信息生成对用户的回复:
用户输入: {state.current\_input}
思考过程: {state.thought}
工具输出: {state.tool\_output}
请生成一个清晰、有帮助的回复。"""llm= ChatOpenAI(temperature=0.7)
response=await llm.ainvoke(prompt)returnAgentState(\*\*state.dict(),
final\_answer=response,
status="SUCCESS")
```
### 3. 构建完整的工作流```
#创建图结构workflow =StateGraph(AgentState)#添加节点workflow.add\_node("think", think)
workflow.add\_node("execute\_tool", execute\_tool)
workflow.add\_node("generate\_response", generate\_response)#定义路由函数defroute\_next\_step(state: AgentState) -&gt;&gt;str:ifstate.status =="ERROR":return"error"elifstate.status =="NEED\_TOOL":return"execute\_tool"elifstate.status =="GENERATE\_RESPONSE":return"generate\_response"elifstate.status =="SUCCESS":return"end"return"think"#添加条件边workflow.add\_conditional\_edges("think",
route\_next\_step,
{"execute\_tool":"execute\_tool","generate\_response":"generate\_response","error":"error\_handler","end": END
}
)
workflow.add\_conditional\_edges("execute\_tool",
route\_next\_step,
{"generate\_response":"generate\_response","error":"error\_handler","end": END
}
)
workflow.add\_edge("generate\_response", END)#编译图app = workflow.compile()
```
### 4. 使用示例```
asyncdefrun\_agent(user\_input: str):
state= AgentState(current\_input=user\_input)
final\_state=await app.ainvoke(state)returnfinal\_state.final\_answer#使用示例asyncdefmain():
questions=["计算23乘以45等于多少？","谁发明了相对论？","计算圆周率乘以10等于多少？"]forquestioninquestions:print(f"\\n问题: {question}")
answer=await run\_agent(question)print(f"回答: {answer}")#运行示例importasyncio
asyncio.run(main())
```
## 高级特性和技巧### 1. 状态持久化LangGraph支持将状态持久化到数据库中:
```
fromlanggraph.persistimportGraphStatePersistclassDBStatePersist(GraphStatePersist):
asyncdefpersist(self, state: AgentState):#实现状态持久化逻辑passasyncdefload(self) -&gt;AgentState:#实现状态加载逻辑pass#使用持久化workflow = StateGraph(AgentState, persist\_handler=DBStatePersist())
```
### 2. 流式输出支持实时显示执行过程:
```
asyncdefstream\_handler(state: AgentState):"""处理流式输出"""yieldf"思考中: {state.thought}\\n"ifstate.selected\_tool:yieldf"使用工具: {state.selected\_tool}\\n"ifstate.tool\_output:yieldf"工具输出: {state.tool\_output}\\n"yieldf"最终答案: {state.final\_answer}\\n"#在图中启用流式输出workflow.set\_stream\_handler(stream\_handler)
```
### 3. 错误处理和重试机制```
asyncdeferror\_handler(state: AgentState) -&gt;&gt;AgentState:"""处理错误情况"""ifstate.error\_count &lt;&lt; 3:returnAgentState(\*\*state.dict(),
error\_count=state.error\_count + 1,
status="RETRY")returnAgentState(\*\*state.dict(),
final\_answer="抱歉，我无法完成这个任务。",
status="ERROR")#添加错误处理节点workflow.add\_node("error\_handler", error\_handler)
```
## 结语通过这个完整的工具调用Agent实现,我们可以看到LangGraph在处理复杂LLM应用时的强大能力:
1. 灵活的流程控制: 通过条件边实现复杂的决策逻辑2. 状态管理: 清晰的状态定义和转换3. 错误处理: 完善的错误处理和重试机制4. 可扩展性: 易于添加新的工具和功能LangGraph不仅解决了传统方法的局限性,还提供了一个更加强大和灵活的框架来构建复杂的LLM应用。通过合理使用这些高级特性,我们可以构建出更加智能和可靠的AI应用。
posted @2024-11-11 16:30[muzinan110] 
阅读(5587)
评论(0)
[收藏] [举报] 
[刷新页面] [返回顶部] 
[![]] 
### 公告[博客园] &copy;&copy; 2004-2026
[![] 浙公网安备 33010602011771号] [浙ICP备2021040463号-3]


---
*数据来源: Exa搜索 | 获取时间: 2026-02-19 20:08:35*