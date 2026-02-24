![](https://csdnimg.cn/release/blogv2/dist/mobile/img/iconLeftArrow.png)
![](https://i-avatar.csdnimg.cn/ad99a7ca73ca4704a0ff6a0f920f61e3_The_Thieves.jpg!1)

# 深入解析 LangGraph 子图：从架构设计到复杂系统构建的全实践指南 原创

![](https://csdnimg.cn/release/blogv2/dist/mobile/img/renewal.png)

![](https://csdnimg.cn/release/blogv2/dist/mobile/img/wap-articleReadEyes2.png)
阅读量1.2k

![](https://csdnimg.cn/release/blogv2/dist/mobile/img/wap-articleReadEyes2.png)

![](https://csdnimg.cn/release/blogv2/dist/mobile/img/wap-tobarCollect2.png)
![](https://csdnimg.cn/release/blogv2/dist/mobile/img/wap-tobarCollect2-act.png)
收藏
13

![](https://csdnimg.cn/release/blogv2/dist/mobile/img/wap-tobarCollect2.png)
![](https://csdnimg.cn/release/blogv2/dist/mobile/img/wap-tobarCollect2-act.png)
![](https://csdnimg.cn/release/blogv2/dist/mobile/img/hotHeart.png)
![](https://i-avatar.csdnimg.cn/ad99a7ca73ca4704a0ff6a0f920f61e3_The_Thieves.jpg!1)

佑瞻
![](https://csdnimg.cn/identity/blog7.png)

![](https://csdnimg.cn/identity/blog7.png)

码龄9年

在构建智能化应用系统时，我们常常会面临一个核心挑战：如何将复杂的逻辑拆解为可复用、可独立维护的组件，同时又能确保整体系统的无缝协同。LangGraph 中的子图（Subgraphs）机制为我们提供了完美的解决方案 —— 这种将 "图作为节点" 的封装设计，就像为复杂系统搭建了一套标准化的 "积木模块"。今天，我们就来深入拆解子图的核心概念与实战应用，看看它如何让多智能体系统构建、团队协作开发等场景变得高效可控。

### 一、子图的核心概念：图结构的 "俄罗斯套娃" 哲学

子图的本质是一种 "图中嵌图" 的架构设计 —— 当一个图被当作另一个图的节点使用时，它就成为了子图。这种设计背后蕴含着封装与抽象的编程思想：我们可以将复杂的功能模块封装为独立子图，对外仅暴露输入输出接口，从而实现 "复杂系统的分层构建"。

想象一下搭建神经网络的过程：我们可以把卷积层、池化层等功能模块分别定义为子图，然后在主图中像拼接积木一样组合这些子图。LangGraph 的子图机制正是遵循了这种思路，让我们能够：

### 二、父子图通信的两种核心模式

当我们在主图中引入子图时，最关键的问题是解决两者的状态通信。根据状态模式的不同，存在两种典型的通信场景，我们通过代码实例来具体分析：

#### 2.1 共享状态模式：最简捷的信息传递

当主图与子图的状态模式包含共享键时，通信变得非常直接。以多智能体系统中常用的消息交互为例：

python

`from langgraph.graph import StateGraph, MessagesState, START
# 定义子图：处理消息的核心逻辑
def call_model(state: MessagesState):
response = model.invoke(state["messages"]) # 调用模型处理消息
return {"messages": response} # 返回处理后的消息
# 构建并编译子图
subgraph_builder = StateGraph(State)
subgraph_builder.add_node(call_model)
subgraph = subgraph_builder.compile()
# 构建主图：直接将子图作为节点添加
builder = StateGraph(State)
builder.add_node("subgraph_node", subgraph) # 子图作为主图的一个节点
builder.add_edge(START, "subgraph_node")
graph = builder.compile()
# 调用主图，状态会通过共享的"messages"键在父子图间传递
graph.invoke({"messages": [{"role": "user", "content": "hi!"}]})`

这种模式下，主图与子图通过共享的状态键（如 "messages"）直接传递数据，就像两个齿轮通过相同的齿纹咬合转动，是最简洁高效的通信方式。

#### 2.2 不同状态模式：灵活的状态转换方案

当父子图的状态模式完全不同时，我们需要通过节点函数来完成状态转换。例如主图使用 "foo" 键而子图使用 "bar" 键的场景：

python

`from typing_extensions import TypedDict
from langgraph.graph.state import StateGraph, START
# 子图状态定义：使用"bar"键
class SubgraphState(TypedDict):
bar: str
# 子图逻辑：处理bar状态
def subgraph_node_1(state: SubgraphState):
return {"bar": "hi! " + state["bar"]}
subgraph_builder = StateGraph(SubgraphState)
subgraph_builder.add_node(subgraph_node_1)
subgraph = subgraph_builder.compile()
# 主图状态定义：使用"foo"键
class State(TypedDict):
foo: str
# 主图中的转换节点：负责状态转换
def call_subgraph(state: State):
# 主图状态转换为子图状态
subgraph_input = {"bar": state["foo"]}
subgraph_output = subgraph.invoke(subgraph_input)
# 子图输出转换回主图状态
return {"foo": subgraph_output["bar"]}
builder = StateGraph(State)
builder.add_node("node_1", call_subgraph)
graph = builder.compile()`

这种情况下，我们通过在主图中定义转换函数，就像在两种不同语言之间设置翻译官，实现了状态的双向转换。这种设计让我们可以自由定义子图的内部状态，极大提升了系统设计的灵活性。

### 三、子图在复杂系统中的实战应用

#### 3.1 多智能体系统构建

子图最典型的应用场景就是多智能体系统。每个智能体可以作为独立子图封装自己的对话历史和决策逻辑，主图则负责协调多个智能体的交互流程。例如：

通过子图机制，我们可以让不同智能体独立维护自己的状态（如专属的 message 历史），同时通过主图定义它们的交互流程，实现复杂的多步决策系统。

#### 3.2 团队协作开发

当多个团队协作开发大型系统时，子图机制可以实现完美的分工协作：

这种 "契约式开发" 模式极大提升了大型项目的开发效率，就像汽车制造中不同厂商生产零部件，最终在总装厂完成组装。

### 四、子图的持久化与状态管理

#### 4.1 持久化机制实现

在实际应用中，我们常常需要保存图的状态，以便断点续传或状态恢复。LangGraph 的子图持久化非常便捷：

python

`from langgraph.graph import START, StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from typing_extensions import TypedDict
class State(TypedDict):
foo: str
# 子图定义
def subgraph_node_1(state: State):
return {"foo": state["foo"] + "bar"}
subgraph_builder = StateGraph(State)
subgraph_builder.add_node(subgraph_node_1)
subgraph = subgraph_builder.compile()
# 主图编译时传入checkpointer，子图会自动继承持久化配置
builder = StateGraph(State)
builder.add_node("node_1", subgraph)
checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)`

值得注意的是，如果希望子图拥有独立的记忆空间，可以在编译子图时设置`checkpointer=True`，这在多智能体系统中非常有用，可以让每个智能体维护自己的内部历史。

`checkpointer=True`

#### 4.2 子图状态查看

当启用持久化后，我们可以通过以下方式查看状态：

`graph.get_state(config)`
`graph.get_state(config, subgraphs=True)`

需要注意的是：**子图状态仅在中断时可见**，一旦恢复图的执行，将无法访问子图状态。这就像调试程序时的断点状态，只有暂停时才能查看内部变量。

#### 4.3 子图输出流式处理

在需要实时获取子图输出的场景中，我们可以通过流式处理实现：

python

`# 在主图流式调用中设置subgraphs=True
for chunk in graph.stream(
{"foo": "foo"},
subgraphs=True,
stream_mode="updates",
):
print(chunk) # 同时获取主图和子图的流式输出`

这种设置让我们能够实时获取子图的处理结果，就像在生产线中实时监控每个零部件的加工进度。

### 五、总结与实践建议

通过本文的解析，我们可以看到子图机制为 LangGraph 带来了强大的分层设计能力：

如果本文对你有帮助，别忘了点赞收藏，关注我，一起探索更高效的开发方式～

![](https://csdnimg.cn/release/blogv2/dist/mobile/img/doubleArrow.png)

![](https://csdnimg.cn/release/blogv2/dist/mobile/img/doubleArrow.png)
![](https://csdnimg.cn/release/blogv2/dist/mobile/img/arrowdown-line.png)

#### 基于大模型智能体Agent的*Lan*g*Graph*入门与实战

#### *Lan*g*Graph* *父子**图*模式详解

#### *Lan*g*Graph*系列10：高级模式：*子图*、循环控制、错误处理 —— 90% 的 *Lan*g*Graph* 崩溃源于忽视这 3 个高级模式

![](https://i-blog.csdnimg.cn/direct/175bbbba0eef4300938b7aab07507089.png)

#### *lan*gchain系列（九）- *Lan*g*Graph* *子图*详解

![](https://i-blog.csdnimg.cn/direct/9b78aa1c886a47fdb3d92f3dd8af127f.png)

#### *Lan*g*Graph*--基础学习(Sub*graph*s *子图*)

#### *Lan*g*graph* *子图*调用

#### 探索*Lan*g*Graph*：*构建*多专家协作模型

![](https://img-blog.csdnimg.cn/img_convert/8ef4a0ee70b4fcb5fa335d82f715d484.webp)

#### [【毕业设计项目开发】智能技术融合创新*实践**指南*：从需求分析到*系统*架构的*全*流程*解析*](https://download.csdn.net/download/2301_78256053/91734821)

#### [【Python工程化】*构建*企业级日志分析服务：从*架构设计*到性能优化的*全*流程*实践*](https://download.csdn.net/download/michael_jovi/91044754)

#### [最新发布 【*系统**架构设计*】基于经典题库与高频考点的知识体系*构建*：*系统**架构设计*师考试核心领域关键技术*解析*与应试策略研究](https://download.csdn.net/download/blog_programb/92555301)

#### [后端工程微服务架构演进路径与核心技术*解析*：从单体到分布式*系统*的高可用服务设计*实践*](https://download.csdn.net/download/weixin_42300449/92488361)

#### [软件架构核心*实践**指南*](https://download.csdn.net/download/ttt77/92410271)

#### *Lan*g*Graph*-*子图*（sub*graph*s）

#### *Lan*g*Graph* - Hierarchical Agent Teams

![](https://i-blog.csdnimg.cn/direct/13b2c5dfd0d54f088bffde2f584a69f8.png)

#### *Lan*g*Graph*：基于*图*结构的大模型智能体开发框架

![](https://i-blog.csdnimg.cn/direct/1309e98e14aa40339bc6cff7e8b338c6.png)

#### *Lan*gChain - 使用多代理协作 *构建*终极AI自动化

![](https://img-blog.csdnimg.cn/direct/44ef836c6cac4231a6898e586f341a3f.png)

#### [【移动应用开发】VIP*系统*实战进阶资源合集：面向中高级开发者的*架构设计*与工程化能力提升*指南*](https://download.csdn.net/download/qq_39020934/92481511)

#### [微服务设计模式：*构建*高效微服务架构的关键技术*解析*](https://download.csdn.net/download/wjianwei666/90021013)

#### [2020年*系统**架构设计*师案例分析、论文真题及*解析*.zip](https://download.csdn.net/download/q68261935/14022121)

![](https://csdnimg.cn/release/blogv2/dist/mobile/img/writeIcon@2x.png)
![](https://csdnimg.cn/release/blogv2/dist/pc/img/commentFlag@2x.png)
![](https://csdnimg.cn/release/blogv2/dist/mobile/img/uncollect@2x.png)
![](https://csdnimg.cn/release/blogv2/dist/mobile/img/collect@2x.png)
![](https://csdnimg.cn/release/blogv2/dist/mobile/img/unheart@2x.png)
![](https://csdnimg.cn/release/blogv2/dist/mobile/img/heart@2x.png)
![](https://csdnimg.cn/release/blogv2/dist/mobile/img/stepUnLike.png)
![](https://csdnimg.cn/release/blogv2/dist/mobile/img/stepLike.png)
![](https://csdnimg.cn/release/blogv2/dist/mobile/img/unshare@2x.png)
![](https://csdnimg.cn/release/blogv2/dist/mobile/img/closeBt.png)
![]()
![](https://csdnimg.cn/release/blogv2/dist/mobile/img/closeBt.png)
![](https://csdnimg.cn/release/blogv2/dist/mobile/img/closeBt.png)
![](https://csdnimg.cn/release/blogv2/dist/mobile/img/closeBt.png)
![红包](https://csdnimg.cn/release/blogv2/dist/pc/img/commentReward.png)

请填写红包祝福语或标题

红包个数最小为10个

![](https://csdnimg.cn/release/blogv2/dist/mobile/img/arrowRight.png)

红包金额最低5元

未领取的红包，将于96小时后发起退款

![]()

成就一亿技术人!

![](https://profile-avatar.csdnimg.cn/default.jpg!2)
![](https://csdnimg.cn/release/blogv2/dist/mobile/img/csdnIcon@2x.png)

CSDN

C知道答疑一步到位

![](https://csdnimg.cn/release/blogv2/dist/mobile/img/chromeIcon@2x.png)
![](https://csdnimg.cn/release/blogv2/dist/mobile/img/closeBt.png)

APP 内打开