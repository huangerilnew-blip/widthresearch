# 智能体短期记忆管理实战指南：LangGraph三剑客解析

**URL**:
https://www.h3blog.com/article/566/

## 元数据
- 发布日期: 2026-02-19T10:54:25.242405

## 完整内容
---
智能体短期记忆管理实战指南：LangGraph三剑客解析-资讯-何三笔记
**
**
**资讯**
* 其他* [告别单调黑白：用Python的rich库打造炫酷命令行应用] 
* [极简AI助手革命：99%精简代码量的nanobot，能否取代臃肿的Clawdbot？] 
* [Python Web 性能天花板?这个 Rust 驱动的框架太强了] 
* [GitHub 上43K星的爬虫项目,到底强在哪?] 
* [NiceGUI：用 Python 轻松构建现代化Web UI 的全能框架] 
* [这款OCR神器仅256M参数，0.35秒解析整页文档！] 
* [开源界「闪电战」：5人3小时复刻Manus，开发者集体上演「真·光速打脸」实录] 
* [从实习生到全能助手：Manus能否成为AI界的‘革命者’？] 
* [反超DeepSeek-R1，性能碾压Sora！这可能是2025年AI圈最炸裂的开源事件] 
* [wxauto框架入门指南：解锁微信自动化新姿势] 
* [从零到精通：Crawl4AI如何助力AI开发者高效提取网页数据] 
* [TraeAi编辑器国内暂无法登录？避不了的坑！] 
* [从零开始：掌握RAGFlow——企业级文档处理的秘密武器] 
* [21.7K star！几分钟搞定全栈 Web 应用，这个开源python框架厉害了！] 
* [Claude 3.7 深夜突袭：当编程AI 开始玩宝可梦会发生什么？] 
* [从代码到方向盘：一个北漂程序员的「单王」逆袭之路 ——三年赚70万，他如何用算法思维跑赢生活？] 
* [pycharm激活码免费分享2025最新] 
* [18.9K 星推荐！这个Python 库让开发AI 智能体像搭积木一样简单] 
* [清华大学出品，DeepSeek助你高效工作与财富增长！网络疯传的秘密武器] 
* [RIG：Google这次把大模型改造成了&#34;实时数据狂魔&#34;？] 
* [智能体短期记忆管理实战指南：LangGraph三剑客解析] 
* [一文让你了解什么是浏览器指纹？] 
* [Python 3.9.0a5 已可用于测试] 
# 智能体短期记忆管理实战指南：LangGraph三剑客解析
发表于2025年02月15日阅读 3280评论 0
![] 
在智能体系统设计中，短期记忆管理直接影响着对话质量与资源消耗。本文将通过**LangGraph**框架，演示三种渐进式的记忆优化策略，助你打造更高效的对话系统。
## 一、传统记忆机制的三大痛点当前主流的ChatML模板虽能自动拼接对话历史，但存在明显缺陷：
* ?**Token消耗失控**：每次交互携带完整历史，成本指数级增长
* ?**上下文窗口溢出**：超过模型处理上限（如GPT-4 Turbo的128k限制）
* ⏳**响应延迟加剧**：长文本处理耗时影响用户体验> > "记忆不是存储所有细节，而是保留关键脉络" ——本文核心设计理念> ## 二、LangGraph解决方案实战
### 策略1：滑动窗口记忆法（RemoveMessage）
```
`fromlanggraph.graphimportStateGraph,MessagesStatefromlangchain\_core.messagesimportRemoveMessagedeffilter\_messages(state):&quot;&quot;&quot;保留最近3轮对话的滑动窗口&quot;&quot;&quot;return{&quot;messages&quot;:[RemoveMessage(m.id)forminstate[&quot;messages&quot;][:-3]]}# 构建处理流程builder=StateGraph(MessagesState)builder.add\_node(&quot;&quot;filter\_messages&quot;&quot;,filter\_messages)builder.add\_node(&quot;&quot;chat\_model&quot;&quot;,lambdastate:{&quot;messages&quot;:llm.invoke(state[&quot;messages&quot;])})builder.add\_edge(START,&quot;&quot;filter\_messages&quot;&quot;)builder.add\_edge(&quot;&quot;filter\_messages&quot;&quot;,&quot;&quot;chat\_model&quot;&quot;)builder.add\_edge(&quot;&quot;chat\_model&quot;&quot;,END)graph=builder.compile()`
```
**特点**：
✅固定内存占用⚠️可能丢失关键历史信息### 策略2：动态Token裁剪法（trim\_messages）
```
`fromlangchain\_core.messagesimporttrim\_messagesdefsmart\_filter(state):&quot;&quot;&quot;按Token预算智能裁剪&quot;&quot;&quot;processed=trim\_messages(state[&quot;messages&quot;],max\_tokens=1000,# 根据模型窗口调整strategy=&quot;last&quot;,# 保留尾部对话token\_counter=ChatOpenAI(model=&quot;gpt-3.5-turbo&quot;))return{&quot;messages&quot;:processed}# 替换基础策略中的filter\_messages节点builder.add\_node(&quot;&quot;smart\_filter&quot;&quot;,smart\_filter)`
```
**优势**：
? 自适应模型上下文窗口⚖️平衡信息完整性与资源消耗### 策略3：增量摘要记忆法
```
`defsummary\_processor(state):&quot;&quot;&quot;每6轮对话生成增量摘要&quot;&quot;&quot;summary=state.get(&quot;summary&quot;,&quot;&quot;)prompt=f&quot;现有摘要：{summary}\\n根据新对话更新摘要：&quot;ifsummaryelse&quot;创建对话摘要：&quot;messages=state[&quot;messages&quot;][-2:]+[HumanMessage(content=prompt)]new\_summary=llm.invoke(messages).contentreturn{&quot;summary&quot;:new\_summary,&quot;messages&quot;:[RemoveMessage(m.id)forminstate[&quot;messages&quot;][:-2]]}defshould\_summarize(state):return&quot;summarize&quot;iflen(state[&quot;messages&quot;])&gt;6elseEND# 构建带条件判断的工作流workflow=StateGraph(State)workflow.add\_conditional\_edges(&quot;conversation&quot;,should\_summarize,{&quot;summarize&quot;:&quot;&quot;summary\_processor&quot;&quot;,END:END})`
```
**技术要点**：
? 定期提炼对话要点? 保留关键上下文脉络⏲️通过条件触发避免过度计算## 三、方案选型指南|策略|适用场景|性能影响|信息完整性|
滑动窗口|短对话场景|★★☆|★☆☆|
Token裁剪|资源敏感型项目|★★★|★★☆|
增量摘要|长对话深度交互|★☆☆|★★★|
*注：★数量表示性能/完整性等级，最高为★★★*
## 四、进阶优化建议1. **混合策略**：根据对话阶段动态切换策略
2. **分级存储**：将关键信息存入长期记忆库
3. **元数据标注**：为消息添加重要性标记
**延伸阅读**：
-[LangGraph官方文档] (https://langchain.com/langgraph) -[OpenAI上下文管理白皮书] (https://langchain.com/langgraph)
> **> 版权声明：**> 如无特殊说明，文章均为[> 何三笔记] > 原创，转载请注明出处> **> 本文链接：**[> https://www.h3blog.com/article/566/
] 
> **如果文章对你有所帮助，可以赞助本站**
微信![微信赞助码] 
支付宝![支付宝赞助码] 
**目录**
* [一、传统记忆机制的三大痛点] 
* [二、LangGraph解决方案实战] 
* [策略1：滑动窗口记忆法（RemoveMessage）] 
* [策略2：动态Token裁剪法（trim\_messages）] 
* [策略3：增量摘要记忆法] 
* [三、方案选型指南] 
* [四、进阶优化建议] 
![image] 
##### 请使用支付宝支付×请使用支付宝扫一


---
*数据来源: Exa搜索 | 获取时间: 2026-02-19 10:55:13*