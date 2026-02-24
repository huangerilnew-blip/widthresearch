# 讲解LangGraph 构造中的进阶用法- 53AI-AI知识库

**URL**:
https://www.53ai.com/news/qianyanjishu/1393.html

## 元数据
- 发布日期: 2024-04-26T00:00:00+00:00

## 完整内容
---
- [首页] 
- [产品服务] 
- [客户案例] 
- [AI知识库] 
- [关于我们] 

热门场景

工作+AI

业务+AI

AIx业务

[大模型咨询] 

[大模型开发] 

热门产品

[53AI Hub开源\
\
三分钟搭建出独立的企业AI门户] [53AI Studio\
\
高准确率的企业级智能体开发平台] [53AI KM\
\
让企业知识在人与AI之间流动起来] [53AI Browser\
\
“AI专家”效率倍增的秘密武器\
\
敬请期待...] 

[行业案例] [场景案例] 

[前沿技术] [Agent框架] [行业应用] [企业落地] 

[公司介绍] [渠道合作] 

53AI知识库

学习大模型的前沿技术与行业应用场景

[立即咨询] [预约演示] 

[首页] [AI知识库] [前沿技术] 

我要投稿

# 讲解 LangGraph 构造中的进阶用法

发布日期：2024-04-26 07:58:19浏览次数： 4858

作者：同学小张

微信搜一搜，关注“同学小张”

书接上文（ [【AI Agent】【LangGraph】0. 快速上手：协同LangChain，LangGraph帮你用图结构轻松构建多智能体] ），前面我们了解了 LangGraph 的概念和基本构造方法，今天我们来看下 LangGraph 构造中的进阶用法：给边加个条件 - 条件分支（Conditional edges）。

LangGraph 构造的是个图的数据结构，有节点(node) 和边(edge），那它的边也可以是带条件的。如何给边加入条件呢？可以通过 `add_conditional_edges` 函数添加带条件的边。

# 1\. 完整代码及运行

废话不多说，先上完整代码，和运行结果。先跑起来看看效果再说。

```
from langchain_openai importChatOpenAIfrom langchain_core.messages importHumanMessage,BaseMessagefrom langgraph.graph import END,MessageGraphimport jsonfrom langchain_core.messages importToolMessagefrom langchain_core.tools import toolfrom langchain_core.utils.function_calling import convert_to_openai_toolfrom typing importList@tooldefmultiply(first_number:int, second_number:int):"""Multiplies two numbers together."""return first_number * second_numbermodel =ChatOpenAI(temperature=0)model_with_tools = model.bind(tools=[convert_to_openai_tool(multiply)])graph =MessageGraph()definvoke_model(state:List[BaseMessage]):return model_with_tools.invoke(state)graph.add_node("oracle", invoke_model)definvoke_tool(state:List[BaseMessage]):    tool_calls = state[-1].additional_kwargs.get("tool_calls",[])    multiply_call =Nonefor tool_call in tool_calls:if tool_call.get("function").get("name")=="multiply":            multiply_call = tool_callif multiply_call isNone:raiseException("No adder input found.")    res = multiply.invoke(        json.loads(multiply_call.get("function").get("arguments")))returnToolMessage(        tool_call_id=multiply_call.get("id"),        content=res)graph.add_node("multiply", invoke_tool)graph.add_edge("multiply", END)graph.set_entry_point("oracle")defrouter(state:List[BaseMessage]):    tool_calls = state[-1].additional_kwargs.get("tool_calls",[])iflen(tool_calls):return"multiply"else:return"end"graph.add_conditional_edges("oracle", router,{"multiply":"multiply","end": END,})runnable = graph.compile()response = runnable.invoke(HumanMessage("What is 123 * 456?"))print(response)
```

运行结果如下：

# 2\. 代码详解

下面对上面的代码进行详细解释。

## 2.1 add\_conditional\_edges

首先，我们知道了可以通过 `add_conditional_edges` 来对边进行条件添加。这部分代码如下：

```
graph.add_conditional_edges("oracle", router,{"multiply":"multiply","end": END,})
```

`add_conditional_edges` 接收三个参数：

- • 第一个为这条边的第一个node的名称

- • 第二个为这条边的条件

- • 第三个为条件返回结果的映射（根据条件结果映射到相应的node）


如上面的代码，意思就是往 “oracle” node上添加边，这个node有两条边，一条是往“multiply” node上走，一条是往“END”上走。怎么决定往哪个方向去：条件是 router（后面解释），如果 router 返回的是“multiply”，则往“multiply”方向走，如果 router 返回的是 “end”，则走“END”。

来看下这个函数的源码：

```
defadd_conditional_edges(    self,    start_key:str,    condition:Callable[...,str],    conditional_edge_mapping:Optional[Dict[str,str]]=None,)->None:if self.compiled:        logger.warning("Adding an edge to a graph that has already been compiled. This will ""not be reflected in the compiled graph.")if start_key notin self.nodes:raiseValueError(f"Need to add_node `{start_key}` first")if iscoroutinefunction(condition):raiseValueError("Condition cannot be a coroutine function")if conditional_edge_mapping andset(        conditional_edge_mapping.values()).difference([END]).difference(self.nodes):raiseValueError(f"Missing nodes which are in conditional edge mapping. Mapping "f"contains possible destinations: "f"{list(conditional_edge_mapping.values())}. Possible nodes are "f"{list(self.nodes.keys())}.")    self.branches[start_key].append(Branch(condition, conditional_edge_mapping))
```

重点是这一句： `self.branches[start_key].append(Branch(condition, conditional_edge_mapping))`，给当前node添加分支Branch。

## 2.2 条件 router

条件代码如下：判断执行结果中是否有 tool\_calls 参数，如果有，则返回"multiply"，没有，则返回“end”。

```
defrouter(state:List[BaseMessage]):    tool_calls = state[-1].additional_kwargs.get("tool_calls",[])iflen(tool_calls):return"multiply"else:return"end"
```

## 2.3 各node的定义

（1）起始node：oracle

```
@tooldefmultiply(first_number:int, second_number:int):"""Multiplies two numbers together."""return first_number * second_numbermodel =ChatOpenAI(temperature=0)model_with_tools = model.bind(tools=[convert_to_openai_tool(multiply)])graph =MessageGraph()definvoke_model(state:List[BaseMessage]):return model_with_tools.invoke(state)graph.add_node("oracle", invoke_model)
```

这个node是一个带有Tools 的 ChatOpenAI。在LangChain中使用Tools的详细教程请看这篇文章： [【AI大模型应用开发】【LangChain系列】5. LangChain入门：智能体Agents模块的实战详解] 。简单解释就是：这个node的执行结果，将返回是否应该使用绑定的Tools。

（2）multiply

```
definvoke_tool(state:List[BaseMessage]):    tool_calls = state[-1].additional_kwargs.get("tool_calls",[])    multiply_call =Nonefor tool_call in tool_calls:if tool_call.get("function").get("name")=="multiply":            multiply_call = tool_callif multiply_call isNone:raiseException("No adder input found.")    res = multiply.invoke(        json.loads(multiply_call.get("function").get("arguments")))returnToolMessage(        tool_call_id=multiply_call.get("id"),        content=res)graph.add_node("multiply", invoke_tool)
```

这个node的作用就是执行Tools。

## 2.4 总体流程

分享：

53AI，企业落地大模型首选服务商

**产品**：场景落地咨询+大模型应用平台+行业解决方案

**承诺**：免费POC验证，效果达标后再合作。 **零风险落地应用大模型**，已交付160+中大型企业

[上一篇：欢迎提出优化建议部分读者反馈：] [下一篇：如何使用 Llama 3 免费进行数据分析和可视化] 

[返回列表] 

相关资讯

[2024-07-10\
\
科研助力神器：Scholar GPT，百倍提升你的研究效率！] [2024-07-09\
\
Doc2X：一款功能超级强大的文档解析与转换工具] [2024-07-06\
\
我对多智能体协作过程自动演化架构设计] [2024-07-06\
\
可穿戴AI，底层逻辑的变化] [2024-07-06\
\
一文彻底搞懂Transformer - Word Embedding（词嵌入）] [2024-07-06\
\
AI动态 \| 腾讯元宝AI搜索能力升级：深度搜索模式上线] [2024-07-06\
\
智能手表 \+ AI ，都已经这么智能了？？] [2024-07-06\
\
死磕10万卡GPU算力集群，腾讯星脉网络2.0有什么秘密武器？] 

[了解更多] 

[了解更多] 

160+中大型企业正在使用53AI

[立即咨询] [预约演示] 

[把握AI发展的机遇，共同探索、共同进步\
\
2025-01-22] [如何打造基于GenAI的员工服务机器人\
\
2025-01-22] 

热点资讯

[DeepSeek-V3.1 发布，迈向 Agent 时代的第一步\
\
2025-08-21] [DeepSeek V3.1 Base / Instruct 发布\
\
2025-08-20] [阿里Qoder vs Trae vs Cursor：谁才是2025年程序猿的效率之王？\
\
2025-09-07] [DeepSeekV3.1 提到的 UE8M0 FP8 Scale 是什么？下一代国产芯片设计？\
\
2025-08-21] [DeepSeek V3.1 测评\
\
2025-08-19] [新版 GPT-5 刚刚发布，最卷 AI 连肝代码 7 小时，编程工具大洗牌开始了\
\
2025-09-16] [实测 Sora 2 ：AI视频的“ChatGPT时刻”来了？八大场景教你解锁各种玩法（附邀请码）\
\
2025-10-02] [AI大家说 \| 下一代AI创业的机会在哪里？定价趋势是什么？\
\
2025-09-08] [从需求场景出发的AI应用项目落地方法论\
\
2025-09-19] [DeepSeek-V3.1-Base来了！MoE架构+128K上下文，性能再进化​\
\
2025-08-20] 

大家都在问

[多智能体设计模式和智能体框架，你会了么？\
\
2025-11-12] [我们为什么选择 Spring AI 开发智能体，而不是 Dify？\
\
2025-11-12] [开源安全审核模型终极PK：Qwen3Guard、OpenAI-SafeGuard、Llama4-Guard谁才是王者？\
\
2025-11-10] [大模型一体机\|“昙花一现”，还是必然趋势？\
\
2025-11-10] [95% 企业 AI 落地失败当下，另外 5% 的 CIO 在谈什么？\
\
2025-11-09] [火了大半年的Agent，还能整出啥新花样？\
\
2025-11-09] [一年花上千块来录音，是韭菜还是真有用？\
\
2025-11-08] [打败GPT5的Kimi K2 Thinking，真就只会写代码吗？\
\
2025-11-08] 

热门标签

[内容创作] [大模型技术] [个人提效] [langchain] [llamaindex] [多模态技术] [RAG技术] [智能客服] [知识图谱] [模型微调] [RAGFlow] [coze] [Dify] [Fastgpt] [Bisheng] [Qanything] [AI+汽车] [AI+金融] [AI+工业] [AI+培训] [AI+SaaS] [提示词框架] [提示词技巧] [AI+电商] [AI面试] [数字员工] [ChatBI] [知识管理] [开源大模型] [智能营销] [智能硬件] [智能化改造] [AI+医疗] [MaxKB] 

[应聘简历请发送至： ceo@53ai.com] 

联系我们

售前咨询

[186 6662 7370] 

预约演示

[185 8882 0121] 

微信扫码

添加专属顾问

回到顶部

加载中...

扫码咨询

[预约演示] [微信咨询] [电话咨询]


---
*数据来源: Exa搜索 | 获取时间: 2026-02-24 22:27:47*