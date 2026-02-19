# 自定义状态 - LangChain 框架

**URL**:
https://langgraph.com.cn/tutorials/get-started/5-customize-state/index.html

## 元数据
- 发布日期: 2025-03-01T00:00:00+00:00

## 完整内容
---
自定义状态 - LangChain 框架[跳到内容] 
**我们正在发展，并为 LangChain、LangGraph 和LangSmith 招聘多个职位。[加入我们的团队！] **
[] # 自定义状态[¶] 
在本教程中，您将向状态添加额外的字段，以定义复杂的行为，而无需依赖消息列表。聊天机器人将使用其搜索工具查找特定信息并将其转发给人工进行审查。注意本教程基于[添加人工干预控制] 。
## 1. 向状态添加键[¶] 
通过向状态添加`name`和`birthday`键来更新聊天机器人，以研究实体的生日。
*API 参考:[add\_messages] *
```
`[]<web_link>fromtypingimportAnnotated[]<web_link>[]<web_link>fromtyping\_extensionsimportTypedDict[]<web_link>[]<web_link>fromlanggraph.graph.messageimportadd\_messages[]<web_link>[]<web_link>[]<web_link>classState(TypedDict):[]<web_link>messages:Annotated[list,add\_messages][]<web_link>name:str[]<web_link>birthday:str`
```
将此信息添加到状态使其易于被其他图节点（例如存储或处理信息的下游节点）以及图的持久层访问。## 2. 在工具内部更新状态[¶] 
现在，在`human\_assistance`工具内部填充状态键。这允许人工在信息存储到状态之前对其进行审查。使用[`Command`] 从工具内部发出状态更新。
```
`[]<web_link>fromlangchain\_core.messagesimportToolMessage[]<web_link>fromlangchain\_core.toolsimportInjectedToolCallId,tool[]<web_link>[]<web_link>fromlanggraph.typesimportCommand,interrupt[]<web_link>[]<web_link>@tool[]<web_link># Note that because we are generating a ToolMessage for a state update, we[]<web_link># generally require the ID of the corresponding tool call. We can use[]<web_link># LangChain's InjectedToolCallId to signal that this argument should not[]<web_link># be revealed to the model in the tool's schema.[]<web_link>defhuman\_assistance([]<web_link>name:str,birthday:str,tool\_call\_id:Annotated[str,InjectedToolCallId][]<web_link>)-&gt;str:[]<web_link>"""Request assistance from a human."""[]<web_link>human\_response=interrupt([]<web_link>{[]<web_link>"question":"Is this correct?",[]<web_link>"name":name,[]<web_link>"birthday":birthday,[]<web_link>},[]<web_link>)[]<web_link># If the information is correct, update the state as-is.[]<web_link>ifhuman\_response.get("correct","").lower().startswith("y"):[]<web_link>verified\_name=name[]<web_link>verified\_birthday=birthday[]<web_link>response="Correct"[]<web_link># Otherwise, receive information from the human reviewer.[]<web_link>else:[]<web_link>verified\_name=human\_response.get("name",name)[]<web_link>verified\_birthday=human\_response.get("birthday",birthday)[]<web_link>response=f"Made a correction:{human\_response}"[]<web_link>[]<web_link># This time we explicitly update the state with a ToolMessage inside[]<web_link># the tool.[]<web_link>state\_update={[]<web_link>"name":verified\_name,[]<web_link>"birthday":verified\_birthday,[]<web_link>"messages":[ToolMessage(response,tool\_call\_id=tool\_call\_id)],[]<web_link>}[]<web_link># We return a Command object in the tool to update our state.[]<web_link>returnCommand(update=state\_update)`
```
图的其余部分保持不变。## 3. 提示聊天机器人[¶] 
提示聊天机器人查找LangGraph 库的“生日”，并指示聊天机器人一旦获得所需信息就联系`human\_assistance`工具。通过在工具参数中设置`name`和`birthday`，您可以强制聊天机器人为这些字段生成建议。
```
`[]<web_link>user\_input=([]<web_link>"Can you look up when LangGraph was released? "[]<web_link>"When you have the answer, use the human\_assistance tool for review."[]<web_link>)[]<web_link>config={"configurable":{"thread\_id":"1"}}[]<web_link>[]<web_link>events=graph.stream([]<web_link>{"messages":[{"role":"user","content":user\_input}]},[]<web_link>config,[]<web_link>stream\_mode="values",[]<web_link>)[]<web_link>foreventinevents:[]<web_link>if"messages"inevent:[]<web_link>event["messages"][-1].pretty\_print()`
```
```
`[]<web_link>================================ Human Message =================================[]<web_link>[]<web_link>Can you look up when LangGraph was released? When you have the answer, use the human\_assistance tool for review.[]<web_link>================================== Ai Message ==================================[]<web_link>[]<web_link>[{'text': "Certainly! I'll start by searching for information about LangGraph's release date using the Tavily search function. Then, I'll use the human\_assistance tool for review.", 'type': 'text'}, {'id': 'toolu\_01JoXQPgTVJXiuma8xMVwqAi', 'input': {'query': 'LangGraph release date'}, 'name': 'tavily\_search\_results\_json', 'type': 'tool\_use'}][]<web_link>Tool Calls:[]<web_link>tavily\_search\_results\_json (toolu\_01JoXQPgTVJXiuma8xMVwqAi)[]<web_link>Call ID: toolu\_01JoXQPgTVJXiuma8xMVwqAi[]<web_link>Args:[]<web_link>query: LangGraph release date[]<web_link>================================= Tool Message =================================[]<web_link>Name: tavily\_search\_results\_json[]<web_link>[]<web_link>[{"url": "https://blog.langchain.ac.cn/langgraph-cloud/", "content": "We also have a new stable release of LangGraph. By LangChain 6 min read Jun 27, 2024 (Oct '24) Edit: Since the launch of LangGraph Platform, we now have multiple deployment options alongside LangGraph Studio - which now fall under LangGraph Platform. LangGraph Platform is synonymous with our Cloud SaaS deployment option."}, {"url": "https://changelog.langchain.ac.cn/announcements/langgraph-cloud-deploy-at-scale-monitor-carefully-iterate-boldly", "content": "LangChain - Changelog | ☁🚀LangGraph Platform: Deploy at scale, monitor LangChain LangSmith LangGraph LangChain LangSmith LangGraph LangChain LangSmith LangGraph LangChain Changelog Sign up for our newsletter to stay up to date DATE: The LangChain Team LangGraph LangGraph Platform ☁🚀LangGraph Platform: Deploy at scale, monitor carefully, iterate boldly DATE: June 27, 2024 AUTHOR: The LangChain Team LangGraph Platform is now in closed beta, offering scalable, fault-tolerant deployment for LangGraph agents. LangGraph Platform also includes a new playground-like studio for debugging agent failure modes and quick iteration: Join the waitlist today for LangGraph Platform. And to learn more, read our blog post announcement or check out our docs. Subscribe By clicking subscribe, you accept our privacy policy and terms and conditions."}][]<web_link>================================== Ai Message ==================================[]<web_link>[]<web_link>[{'text': "Based on the search results, it appears that LangGraph was already in existence before June 27, 2024, when LangGraph Platform was announced. However, the search results don't provide a specific release date for the original LangGraph. \\n\\nGiven this information, I'll use the human\_assistance tool to review and potentially provide more accurate information about LangGraph's initial release date.", 'type': 'text'}, {'id': 'toolu\_01JDQAV7nPqMkHHhNs3j3XoN', 'input': {'name': 'Assistant', 'birthday': '2023-01-01'}, 'name': 'human\_assistance', 'type': 'tool\_use'}][]<web_link>Tool Calls:[]<web_link>human\_assistance (toolu\_01JDQAV7nPqMkHHhNs3j3XoN)[]<web_link>Call ID: toolu\_01JDQAV7nPqMkHHhNs3j3XoN[]<web_link>Args:[]<web_link>name: Assistant[]<web_link>birthday: 2023-01-01`
```
我们再次触及了`human\_assistance`工具中的`interrupt`。
## 4. 添加人工协助[¶] 
聊天机器人未能识别正确的日期，因此为其提供信息```
`[] human\_command=Command([] resume={[] "name":"LangGraph",[] "birthday":"Jan 17, 2024",[]},[])[] [] events=graph.stream(human\_command,config,stream\_mode="values")[] foreventinevents:[] if"messages"inevent:[] event["messages"][-1].pretty\_print()`
```
```
`[] ================================== Ai Message ==================================[] [] [{'text': "Based on the search results, it appears that LangGraph was already in existence before June 27, 2024, when LangGraph Platform was announced. However, the search results don't provide a specific release date for the original LangGraph. \\n\\nGiven this information, I'll use the human\_assistance tool to review and potentially provide more accurate information about LangGraph's initial release date.", 'type': 'text'}, {'id': 'toolu\_01JDQAV7nPqMkHHhNs3j3XoN', 'input': {'name': 'Assistant', 'birthday': '2023-01-01'}, 'name': 'human\_assistance', 'type': 'tool\_use'}][] Tool Calls:[] human\_assistance (toolu\_01JDQAV7nPqMkHHhNs3j3XoN)[] Call ID: toolu\_01JDQAV7nPqMkHHhNs3j3XoN[] Args:[] name: Assistant[] birthday: 2023-01-01[] ================================= Tool Message =================================[] Name: human\_assistance[] [] Made a correction: {'name': 'LangGraph', 'birthday': 'Jan 17, 2024'}[] ================================== Ai Message ==================================[] [] Thank you for the human assistance. I can now provide you with the correct information about LangGraph's release date.[] [] LangGraph was initially released on January 17, 2024. This information comes from the human assistance correction, which is more accurate than the search results I initially found.[] [] To summarize:[] 1. LangGraph's original release date: January 17, 2024[] 2. LangGraph Platform announcement: June 27, 2024[] [] It's worth noting that LangGraph had been in development and use for some time before the LangGraph Platform announcement, but the official initial release of LangGraph itself was on January 17, 2024.`
```
请注意，这些字段现在已反映在状态中```
`[]<web_link>snapshot=graph.get\_state(config)[]<web_link>[]<web_link>{k:vfork,vinsnapshot.values.items()ifkin("name","birthday")}`
```
```
`[]<web_link>{'name': 'LangGraph', 'birthday': 'Jan 17, 2024'}`
```
这使得它们易于被下游节点访问（例如，进一步处理或存储信息的节点）。## 5. 手动更新状态[¶] 
LangGraph 对应用程序状态提供高度控制。例如，在任何时候（包括中断时），您都可以使用`graph.update\_state`手动覆盖一个键。
```
`[]<web_link>graph.update\_state(config,{"name":"LangGraph (library)"})`
```
```
`[]<web_link>{'configurable': {'thread\_id': '1',[]<web_link>'checkpoint\_ns': '',[]<web_link>'checkpoint\_id': '1efd4ec5-cf69-6352-8006-9278f1730162'}}`
```
## 6. 查看新值[¶] 
如果您调用`graph.get\_state`，您可以看到新值已反映出来。
```
`[]<web_link>snapshot=graph.get\_state(config)[]<web_link>[]<web_link>{k:vfork,vinsnapshot.values.items()ifkin("name","birthday")}`
```
```
`[]<web_link>{'name': 'LangGraph (library)


---
*数据来源: Exa搜索 | 获取时间: 2026-02-19 20:08:35*