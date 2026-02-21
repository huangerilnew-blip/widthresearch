LangGraph中State的定义模式_langgraph获取state-CSDN博客
===============

[![Image 1: CSDN首页](https://img-home.csdnimg.cn/images/20201124032511.png)](https://www.csdn.net/)

*   [博客](https://blog.csdn.net/)
*   [下载](https://download.csdn.net/)
*   [社区](https://devpress.csdn.net/)
*   [![Image 2](https://img-home.csdnimg.cn/images/20240829093757.png)GitCode](https://link.csdn.net/?target=https%3A%2F%2Fgitcode.com%3Futm_source%3Dcsdn_toolbar)
*   [![Image 3](https://i-operation.csdnimg.cn/images/3c66245675ae423e9cc897dc790b8ac9.png)GPU算力 ![Image 4](https://i-operation.csdnimg.cn/images/d8d2f104eeeb4a428045d2b34d72ed13.png)](https://ai.csdn.net/)
*   [更多](https://blog.csdn.net/qq_43588095/article/details/147479946)[会议](https://www.bagevent.com/event/9117243 "会议")[学习](https://edu.csdn.net/?utm_source=zhuzhantoolbar "高质量课程·大会云会员")[![Image 5](https://i-operation.csdnimg.cn/images/77c4dd7a760a493498bee1d336b064c0.png)InsCode](https://inscode.net/?utm_source=csdn_blog_top_bar "InsCode") 

搜索
AI 搜索

[登录](https://blog.csdn.net/qq_43588095/article/details/147479946)

登录后您可以：

*   复制代码和一键运行
*   与博主大V深度互动
*   解锁海量精选资源
*   获取前沿技术资讯

[立即登录](https://blog.csdn.net/qq_43588095/article/details/147479946)

[![Image 6](https://i-operation.csdnimg.cn/images/f9098e9320264ddc85f274234b2f0c6a.png)新客开通会员 立减60![Image 7](https://i-operation.csdnimg.cn/images/97f199b02b604390ab516e4897fb5bfe.png)](https://mall.csdn.net/vip?utm_source=dl_hover)

[会员·新人礼包 ![Image 8](https://i-operation.csdnimg.cn/images/105eda9d414f4250a7c3fe45be3cd15f.png)](https://mall.csdn.net/vip?utm_source=260206_vip_toolbarhyzx_hy)

[消息](https://i.csdn.net/#/msg/index)

[创作中心](https://mp.csdn.net/ "创作中心")

[创作](https://mp.csdn.net/edit)

[![Image 9](https://i-operation.csdnimg.cn/images/6e41bd372d1f4ec39b3cd36ab95046c4.png)](https://mp.csdn.net/edit)![Image 10](https://i-operation.csdnimg.cn/images/43349e98a45341699652b0b6fa4ea541.png)![Image 11](https://i-operation.csdnimg.cn/images/0f13ec529b6b4195ad99894f76653e56.png)

LangGraph中State的定义模式
====================

最新推荐文章于 2025-12-01 20:03:17 发布

原创 于 2025-04-24 15:32:41 发布·897 阅读

·![Image 12](https://csdnimg.cn/release/blogv2/dist/pc/img/newHeart2023Active.png)![Image 13](https://csdnimg.cn/release/blogv2/dist/pc/img/newHeart2023Black.png) 5 

·[![Image 14](https://csdnimg.cn/release/blogv2/dist/pc/img/tobarCollect2.png)![Image 15](https://csdnimg.cn/release/blogv2/dist/pc/img/tobarCollectionActive2.png) 5](https://blog.csdn.net/qq_43588095/article/details/147479946)·

CC 4.0 BY-SA版权

 版权声明：本文为博主原创文章，遵循[CC 4.0 BY-SA](http://creativecommons.org/licenses/by-sa/4.0/)版权协议，转载请附上原文出处链接和本声明。 

文章标签：
[#人工智能](https://so.csdn.net/so/search/s.do?q=%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD&t=all&o=vip&s=&l=&f=&viparticle=&from_tracking_code=tag_word&from_code=app_blog_art)[#大模型](https://so.csdn.net/so/search/s.do?q=%E5%A4%A7%E6%A8%A1%E5%9E%8B&t=all&o=vip&s=&l=&f=&viparticle=&from_tracking_code=tag_word&from_code=app_blog_art)[#Agent](https://so.csdn.net/so/search/s.do?q=Agent&t=all&o=vip&s=&l=&f=&viparticle=&from_tracking_code=tag_word&from_code=app_blog_art)[#LangGraph](https://so.csdn.net/so/search/s.do?q=LangGraph&t=all&o=vip&s=&l=&f=&viparticle=&from_tracking_code=tag_word&from_code=app_blog_art)

[![Image 16](https://i-blog.csdnimg.cn/columns/default/20201014180756724.png?x-oss-process=image/resize,m_fixed,h_224,w_224)大模型Agent开发 专栏收录该内容](https://blog.csdn.net/qq_43588095/category_12933023.html "大模型Agent开发")

53 篇文章

[订阅专栏](https://blog.csdn.net/qq_43588095/article/details/147479946)

#### [](https://blog.csdn.net/qq_43588095/article/details/147479946)[](https://blog.csdn.net/qq_43588095/article/details/147479946)一、LangGraph 框架核心要点回顾

1.   **底层原理与优势**
    *   LangGraph采用图结构替代LangChain构建AI Agent运行状态，契合大模型技术发展趋势。
    *   凭借循环图和分支状态，能灵活构建agent内部流转过程，适用于复杂AI Agent应用开发。

2.   **核心组件解析**
    *   **节点（Node）**：作为独立函数，可根据业务需求调用大模型或其他逻辑，封装具体执行逻辑。
    *   **边（Edge）**：用于连接各个节点，明确业务流的执行顺序。
    *   **状态（State）**：负责在节点间传递信息，对维持图的持续运行起着关键作用 。

3.   **应用场景复杂度差异**
    *   **简单场景**：如大模型问答流程，可由START - Node - END构成，在Node中封装大模型接入逻辑即可。
    *   **复杂场景**：涉及多任务处理、多数据流程以及多agent协同工作，借助分支和循环实现。分支依据用户输入选择不同处理逻辑，循环则在节点输出不预期时，使节点返回重新处理。

#### [](https://blog.csdn.net/qq_43588095/article/details/147479946)[](https://blog.csdn.net/qq_43588095/article/details/147479946)二、State的关键作用及[消息传递](https://so.csdn.net/so/search?q=%E6%B6%88%E6%81%AF%E4%BC%A0%E9%80%92&spm=1001.2101.3001.7020)机制

1.   **核心地位凸显**

    *   LangGraph底层图算法依靠消息传递机制定义和执行图的交互流程，State作为消息传递的载体，直接决定图能否持续运行。
    *   State与工具调用、人机交互、上下文历史信息管理等高级功能密切相关。

2.   **消息传递详细过程**：以简单图状态为例，START节点接收用户输入。![Image 17: 在这里插入图片描述](https://i-blog.csdnimg.cn/direct/34c5cd13225746f28209b80e750f3d85.png#pic_center)

    *   初始状态假设为`{"message":[{"x":10}]}`,消息经边传递至Node 1。
    *   Node 1对`x`进行加一操作，状态更新为`{"message":[{"x":10},{"x":11}]}`,随后传递到Node 2。
    *   Node 2接收到更新后的状态，对`x`执行减二操作得到`y=9` ，最终状态变为`{"message":[{"x":10},{"x":11},{"y":9}]}`,通过END节点输出给用户端。

3.   **广播机制解析**

    *   LangGraph的状态为共享状态，每个节点都具备读取和写入权限。
    *   当某个节点更新状态时，会通过广播机制通知其他节点，使其他节点能够据此调整自身行为。

#### [](https://blog.csdn.net/qq_43588095/article/details/147479946)[](https://blog.csdn.net/qq_43588095/article/details/147479946)三、State的定义模式与代码实现示例

1.   **基于字典类型的定义模式**：从开发者视角看，State本质上是一个字典，其键值为列表。每次更新时，会向列表中添加新值，以此支撑后续节点的运行。
2.   **代码实现步骤**
    *   使用`StateGraph`类定义状态，创建`StateGraph`实例。

    *   定义`addition`和`subtraction`函数，分别实现对状态的加一和减二操作。

    *   通过`add_node`方法添加节点，利用`add_edge`方法连接节点。

    *   最后调用`compile`方法，将`StateGraph`转换为可运行的图结构。

[关注博主即可阅读全文![Image 18](https://csdnimg.cn/release/blogv2/dist/pc/img/arrowDownAttend.png)](https://blog.csdn.net/qq_43588095/article/details/147479946)

![Image 19](https://csdnimg.cn/release/blogv2/dist/pc/img/vip-limited-close-newWhite.png)

 确定要放弃本次机会？ 

福利倒计时

_:_ _:_

![Image 20](https://csdnimg.cn/release/blogv2/dist/pc/img/vip-limited-close-roup.png)立减 ¥

普通VIP年卡可用

[立即使用](https://mall.csdn.net/vip)

[![Image 21](https://profile-avatar.csdnimg.cn/12627a5b12dd4935a293f4608c5806d4_qq_43588095.jpg!1) 上有晨光](https://blog.csdn.net/qq_43588095)

[关注](javascript:;)[关注](https://blog.csdn.net/qq_43588095/article/details/147479946)

*   [![Image 22](https://csdnimg.cn/release/blogv2/dist/pc/img/tobarThumbUpactive.png)![Image 23](https://csdnimg.cn/release/blogv2/dist/pc/img/toolbar/like-active.png)![Image 24](https://csdnimg.cn/release/blogv2/dist/pc/img/toolbar/like.png) 5](https://blog.csdn.net/qq_43588095/article/details/147479946)点赞 
*   [![Image 25](https://csdnimg.cn/release/blogv2/dist/pc/img/toolbar/unlike-active.png)![Image 26](https://csdnimg.cn/release/blogv2/dist/pc/img/toolbar/unlike.png)](https://blog.csdn.net/qq_43588095/article/details/147479946)踩 
*   [![Image 27](https://csdnimg.cn/release/blogv2/dist/pc/img/toolbar/collect-active.png)![Image 28](https://csdnimg.cn/release/blogv2/dist/pc/img/toolbar/collect.png)![Image 29](https://csdnimg.cn/release/blogv2/dist/pc/img/newCollectActive.png) 5](javascript:;) 收藏    觉得还不错?  一键收藏 ![Image 30](https://csdnimg.cn/release/blogv2/dist/pc/img/collectionCloseWhite.png)  
*   [![Image 31](https://csdnimg.cn/release/blogv2/dist/pc/img/toolbar/comment.png) 0](https://blog.csdn.net/qq_43588095/article/details/147479946#commentBox)评论 
*   [![Image 32](https://csdnimg.cn/release/blogv2/dist/pc/img/toolbar/share.png)分享](javascript:;)[复制链接](https://blog.csdn.net/qq_43588095/article/details/147479946) [分享到 QQ](https://blog.csdn.net/qq_43588095/article/details/147479946) [分享到新浪微博](https://blog.csdn.net/qq_43588095/article/details/147479946) ![Image 33](https://blog.csdn.net/qq_43588095/article/details/147479946) ![Image 34](https://csdnimg.cn/release/blogv2/dist/pc/img/share/icon-wechat.png)扫一扫     
*   [![Image 35](https://csdnimg.cn/release/blogv2/dist/pc/img/toolbar/more.png)](https://blog.csdn.net/qq_43588095/article/details/147479946)[![Image 36](https://csdnimg.cn/release/blogv2/dist/pc/img/toolbar/report.png)举报](https://blog.csdn.net/qq_43588095/article/details/147479946) [![Image 37](https://csdnimg.cn/release/blogv2/dist/pc/img/toolbar/report.png)举报](https://blog.csdn.net/qq_43588095/article/details/147479946)  

[专栏目录](https://blog.csdn.net/qq_43588095/article/details/147479946)

![Image 38](https://kunyu.csdn.net/1.png?p=58&adBlockFlag=0&adId=1083251&a=1083251&c=3768339&k=LangGraph%E4%B8%ADState%E7%9A%84%E5%AE%9A%E4%B9%89%E6%A8%A1%E5%BC%8F&spm=1001.2101.3001.5002&articleId=147479946&d=1&t=3&u=3b9ed406de834dd990615eddf4447285)

[_LangGraph_ 中 _State_ 状态 _模式_ 详解](https://blog.csdn.net/qq_52053775/article/details/154745080)

[qq_52053775的博客](https://blog.csdn.net/qq_52053775)

11-12![Image 39](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png) 219 

[_LangGraph_ 框架通过节点、边和状态的组合构建AI代理，其中状态（_State_）作为核心载体实现信息传递和功能支撑。状态采用共享字典数据结构，节点可读写状态并广播更新，确保数据流动。框架支持多种可视化方法（Mermaid/Graphviz/Pyppeteer）展现节点关系。Reducer函数机制允许为状态键 _定义_ 独立更新逻辑（覆盖/累加等），结合TypedDict保障类型安全，适用于对话历史管理等场景。专用MessageGraph子类通过add_messages Reducer智能合并消息列表，优化对话应用](https://blog.csdn.net/qq_52053775/article/details/154745080)

[](https://blog.csdn.net/qq_43588095/article/details/147479946)

参与评论 您还未登录，请先 登录 后发表或查看评论

[_LangGraph_ 简单讲解示例——_State_、Node、Edge_ _langgraph_ 示例](https://blog.csdn.net/m0_50481455/article/details/156418156)

2-11

[_LangGraph_ 简单讲解示例——_State_、Node、Edge _LangGraph_ 的核心主要是Graph,它是⼀个有向⽆环图,⽤于描述任务之间的依赖关系。 主要包含三个基本元素: · _State_:一种数据结构 ·Node:处理数据的节点,_LangGraph_ 中通常是一个python函数,以 _State_ 为输入,经过一些操作处理后,返回更新后的 _State_](https://blog.csdn.net/m0_50481455/article/details/156418156)

[收藏备用!_LangGraph_ 核心之 _State_ 状态管理全解析,小白也能上手 _大模型_ 开发...](https://blog.csdn.net/m0_57081622/article/details/156422976)

2-1

[from _langgraph_.graph import _State_ Graph, START, END # _定义_ 第一个节点:加法 def addition(_state_): """ 这个函数会收到当前的 _state_(一个字典)从里面取出x的值,加1后返回 """ print(f"加法节点收到的 _state_: {_state_}") current_x = _state_["x"] new_x = current_x + 1 # 只返回更新的部分,不用...](https://blog.csdn.net/m0_57081622/article/details/156422976)

[_LangGraph_ 学习笔记 — _LangGraph_ 中 _State_ 状态 _模式_](https://blog.csdn.net/Lucky_mzc/article/details/149914049)

[Lucky_mzc的博客](https://blog.csdn.net/Lucky_mzc)

08-05![Image 40](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png) 2064 

[本文深入解析了 _LangGraph_ 框架中的状态管理机制，重点探讨了 _State_ 和Reducer函数的核心作用。_LangGraph_ 通过节点(Node)和边(Edge)构建工作流，其中状态(_State_)作为关键载体在节点间传递信息。文章详细介绍了三种状态 _定义_ 方式：字典类型、TypedDict类型和MessageGraph专用类型，并分析了Reducer函数如何控制状态更新逻辑。特别阐述了add_messages这一高级Reducer函数的实现原理，它能智能处理消息的追加和更新。通过多个代码示例展示了不同场景下的状态](https://blog.csdn.net/Lucky_mzc/article/details/149914049)

[_LangGraph_ 节点返回 _State_ ， 数据自动拼接原理](https://blog.csdn.net/weixin_44705554/article/details/147470995)

[AI Agent 首席体验官](https://blog.csdn.net/weixin_44705554)

04-24![Image 41](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png) 1251 

[_定义_ 状态合并函数# _定义_ 状态类型messages: Annotated[List[BaseMessage], add_messages] # 使用注解指定合并策略# 节点函数 _定义_"""分类用户请求的类型"""# 提示模板用于分类任务("system", "你是一个任务分类器。根据用户的请求，确定它是哪种类型的任务。\n输出格式必须是JSON，包含字段'task_type'，值为'search'(搜索类)、'calculation'(计算类)或'general'(一般问答)。"),](https://blog.csdn.net/weixin_44705554/article/details/147470995)

[_LangGraph_ 系列3：_State_ 与Graph基础——_LangGraph_ 的智能工作流引擎 最新发布](https://devpress.csdn.net/v1/article/detail/155461000)

[沛哥儿的专栏](https://blog.csdn.net/m290345792)

12-01![Image 42](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png) 1274 

[在 _LangGraph_ 中，**状态（_State_）** 和 **图（Graph）** 不是辅助概念，而是整个智能体系统的“骨架”与“神经系统”。许多开发者误以为 _LangGraph_ 只是“把函数连起来”，结果在复杂场景中遭遇状态混乱、流程失控、调试无门。实际上，_LangGraph_ 的核心优势在于：**通过强类型状态 + 显式图结构，将 LLM 的不确定性行为约束在可验证、可中断、可重放的确定性框架内**。本文将带你穿透 API 表层，理解 _State_ 与 Graph 的设计哲学，并掌握构建健壮 AI 工作流](https://devpress.csdn.net/v1/article/detail/155461000)

[【_LangGraph_】什么是 _State_ Graph](https://devpress.csdn.net/v1/article/detail/147962997)

[彬彬侠的博客](https://blog.csdn.net/u013172930)

05-14![Image 43](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png) 2237 

[_langgraph_.graph._State_ Graph 是 _LangGraph_ 库中的核心类，用于 _定义_ 和管理基于状态的有向图工作流。它是 _LangGraph_ 的主要构建块，允许开发者通过节点（Nodes）、边（Edges）和状态（_State_）构造复杂的工作流，特别适合与大型语言模型（LLM）结合的场景。关键点包括：使用 TypedDict 或类 _定义_ 状态。通过 add_node 和 add_edge 构建图。支持条件边和循环，适应动态逻辑。编译后通过 invoke 或 stream 执行。通过代码示例，可以看到](https://devpress.csdn.net/v1/article/detail/147962997)

[【小白教程】从零开始学 Dify - 万字详解 Dify 循环和迭代的实现机制，建议收藏！！！](https://devpress.csdn.net/v1/article/detail/149931957)

[bugyinyin的博客](https://blog.csdn.net/bugyinyin)

08-05![Image 44](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png) 2660 

[Dify 是一个强大的 AI 应用开发平台，其工作流引擎支持复杂的循环和迭代操作。接下来将深入分析 Dify 中循环和迭代的实现机制。](https://devpress.csdn.net/v1/article/detail/149931957)

[【_LangGraph_】_langgraph_.graph._State_ Graph 类的属性和方法](https://devpress.csdn.net/v1/article/detail/147963138)

[彬彬侠的博客](https://blog.csdn.net/u013172930)

05-14![Image 45](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png) 2158 

[_langgraph_.graph._State_ Graph 是 _LangGraph_ 的核心类，用于 _定义_ 基于状态的工作流图。其主要功能包括：通过 add_node 和 add_edge 构建图结构。通过 add_conditional_edges 实现动态分支。通过 set_entry_point 和 set_finish_point 指定执行路径。通过 compile 生成可执行的 CompiledGraph。](https://devpress.csdn.net/v1/article/detail/147963138)

[_LangGraph_ 中的 _State_ 管理](https://blog.csdn.net/qq_41472205/article/details/144097203)

[The cure for boredom is curiosity. This is the log of its adventures.](https://blog.csdn.net/qq_41472205)

11-27![Image 46](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png) 3266 

[_定义_ 整个图的状态（这是在节点间共享的公共状态）a: strreturn {"a": 123 # 无效# _定义_ 输入状态的架构# _定义_ 输出状态的架构# _定义_ 整体架构，结合输入和输出pass# 示例答案和一个额外的键# 整个图的状态（这是在节点间共享的公共状态）a: str# node_1的输出包含私有数据，不属于整体状态。](https://blog.csdn.net/qq_41472205/article/details/144097203)

[_LangGraph_ 框架中怎样 _定义_ 工具tools](https://blog.csdn.net/qq_41185191/article/details/147717846)

[ai agent知识](https://blog.csdn.net/qq_41185191)

05-05![Image 47](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png) 1446 

[工具是一种封装函数及其输入 _模式_ 的方法，可以将其传递给支持工具调用的聊天模型。这使得模型能够通过特定的输入请求执行该函数。](https://blog.csdn.net/qq_41185191/article/details/147717846)

[【_langgraph_ 系列-1---概念详解】什么是 _State_|Nodes|EdgesNode|Reducers](https://blog.csdn.net/weixin_45222582/article/details/143637608)

[weixin_45222582的博客](https://blog.csdn.net/weixin_45222582)

11-09![Image 48](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png) 971 

[【代码】【_langgraph_ 名词详细解释】什么是 _State_|Nodes|EdgesNode|_State_|Reducers。](https://blog.csdn.net/weixin_45222582/article/details/143637608)

[_LangGraph_ 父子图 _模式_ 详解](https://blog.csdn.net/Cheer_RIO/article/details/151192412)

[Cheer_RIO的博客](https://blog.csdn.net/Cheer_RIO)

09-04![Image 49](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png) 637 

[_LangGraph_ 父子图 _模式_ 是一种模块化架构，允许父图和子图拥有不同的状态结构。关键点包括： 状态隔离：父图和子图各自 _定义_ 状态 _模式_（如Parent _State_ 和SubgraphMessages _State_） 节点调用：父图中专门节点（call_subgraph）负责： 转换父图状态为子图格式 调用子图处理 将子图输出转回父图格式 核心优势： 模块化设计，子图可复用 状态结构解耦 支持复杂处理流程 典型应用场景：多代理系统、分阶段工作流、数据处理管道等 该 _模式_ 通过状态转换实现灵活集成，是构建复杂 _LangGraph_](https://blog.csdn.net/Cheer_RIO/article/details/151192412)

[[_LangGraph_ 教程]_LangGraph_ 05——_LangGraph_ 状态 _模式_ _State_ 详解](https://blog.csdn.net/m0_69281817/article/details/147600438)

[m0_69281817的博客](https://blog.csdn.net/m0_69281817)

04-29![Image 50](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png) 2565 

[在 _LangGraph_ 框架里，不管构建的代理是简单还是复杂，归根结底都是借助节点（Node）和边（Edge）来构建一个完整的图（Graph）。但 _LangGraph_ 的核心从来不在于如何去界定节点与边，而是在于。_LangGraph_ 的底层图算法依托机制来 _定义_ 和执行图中的交互流程，在这一过程中，状态（_State_）组件担当着关键的载体角色，主要负责在图的各个节点之间传递信息，像核心功能中的工具使用、记忆能力以及人机交互等，都得依仗 _State_ 来达成并加以维护。](https://blog.csdn.net/m0_69281817/article/details/147600438)

[【AI开发】_LangGraph_ 基础](https://blog.csdn.net/qq_44899247/article/details/139657152)

[qq_44899247的博客](https://blog.csdn.net/qq_44899247)

06-14![Image 51](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png) 3287 

[在 _LangGraph_ 中有三个重要元素。](https://blog.csdn.net/qq_44899247/article/details/139657152)

[深入解析 _LangGraph_ 核心技术：状态（_State_）](https://jigang.blog.csdn.net/article/details/152449616)

[没事学AI的博客](https://blog.csdn.net/ZuanShi1111)

10-04![Image 52](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png) 956 

[摘要： _LangGraph_ 框架中的“状态（_State_）”是工作流的核心数据枢纽，承担动态记忆、数据流转和一致性保障的关键角色。其结构化键值对设计支持多种数据类型，并通过预 _定义_ 与自 _定义_ 字段适应不同场景。状态具备动态更新、版本追溯和灵活扩展三大特性，确保节点间数据实时同步，支持历史状态回溯，并能随业务需求扩展字段。理解状态的 _定义_、结构与管理机制，是优化 _LangGraph_ 工作流设计与故障排查的基础。](https://jigang.blog.csdn.net/article/details/152449616)

[深入理解 _LangGraph_：智能体工作流的图模型设计与实践](https://devpress.csdn.net/v1/article/detail/148798103)

[佑瞻的博客](https://blog.csdn.net/The_Thieves)

06-20![Image 53](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png) 1611 

[边是流程的 "导航系统"，根据状态决定下一个执行的节点：python运行# 根据处理阶段选择下一个节点else:边可以是固定转移或条件分支，决定了节点间的执行顺序。核心关系总结：节点负责处理业务逻辑，边控制流程走向，状态则是贯穿始终的信息载体。这种设计让复杂循环流程变得可控，就像用电路图规划电流路径。使用 Annotated 为字段指定 Reducer 函数，例如列表追加：python运行# 使用add函数实现列表合并# 初始状态 _state_ = {"logs": ["系统启动"]}](https://devpress.csdn.net/v1/article/detail/148798103)

[LangChain 最近发布的一个重要功能：_LangGraph_](https://blog.csdn.net/2301_78285120/article/details/136028408)

[2301_78285120的博客](https://blog.csdn.net/2301_78285120)

02-04![Image 54](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png) 3599 

[next: str。](https://blog.csdn.net/2301_78285120/article/details/136028408)

[_LangGraph_：构建复杂智能体应用的全面指南](https://devpress.csdn.net/v1/article/detail/139862000)

[全世界的博客](https://blog.csdn.net/qq_40999403)

06-21![Image 55](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png) 6790 

[图（Graph）是一种数据结构，由节点（Node）和边（Edge）组成。节点表示实体或对象，边表示节点之间的关系。图可以用于表示复杂的关系和流程，广泛应用于计算机科学和 _人工智能_ 领域。在 _LangGraph_ 中，图被用于表示和构建复杂的智能体应用。每个节点代表一个操作或步骤，边表示节点之间的依赖关系。通过 _定义_ 节点和边，开发者可以构建复杂的流程和逻辑。# _定义_ 一个图# 添加节点# 添加边# 运行图在这个例子中，我们 _定义_ 了一个简单的图，它包含三个节点和两条边。](https://devpress.csdn.net/v1/article/detail/139862000)

[【LLM _大模型_】LangChain框架：_Agent_ 之 _LangGraph_ 的使用](https://devpress.csdn.net/v1/article/detail/140799030)

[DEVELOPERAA的博客](https://blog.csdn.net/DEVELOPERAA)

07-30![Image 56](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png) 3402 

[LangChain的核心优势在于其能够轻松构建自 _定义_ 链，这些链通常是线性的，类似于有向无环图（DAG），每个步骤都严格按顺序执行，每个任务只有一个输出和一个后续任务，形成一个没有循环的线性流程。](https://devpress.csdn.net/v1/article/detail/140799030)

[_langGraph_ _state_ 构建](https://wenku.csdn.net/answer/6jxfhfex3v)

08-27

[<think>我们正在讨论如何构建 _LangGraph_ 的状态。根据引用内容，_LangGraph_ 用于构建有状态的多智能体应用程序，其核心概念之一是状态图(_State_ Graph)。状态图需要 _定义_ 一个状态对象，该对象会在图的各个节点之间传递和更新。 在 _LangGraph_ 中，构建状态通常涉及以下步骤： 1. _定义_ 状态 _模式_（_State_ Schema）：一个自 _定义_ 的类，用于描述状态中包含哪些字段。每个字段表示智能体工作流中的一部分数据。 2. 初始化状态图：使用 _定义_ 的状态 _模式_ 创建一个 _State_ Graph实例。 3. 添加节点：节点是处理状态的函数，每个节点可以读取和修改状态中的特定字段。 4. _定义_ 边：包括条件边（conditional edges）和普通边，用于控制流程的走向。 下面我们详细说明如何构建状态。 ### 1. _定义_ 状态 _模式_ 状态 _模式_ 是一个类，通常使用`TypedDict`或普通的类（但需要继承自`typing.TypedDict`）来 _定义_。在 _LangGraph_ 中，状态是一个字典般的对象，其键是字符串，值可以是任意类型，但通常我们会明确指定每个字段的类型。 例如，假设我们正在构建一个简单的聊天机器人，状态可能包含用户输入和聊天历史。我们可以这样 _定义_ 状态： ```python from typing import TypedDict, List, Annotated from _langgraph_.graph.message import add_messages class _State_(TypedDict): user_input: str chat_history: Annotated[List[str], add_messages] ``` 注意：这里使用了`Annotated`类型，这是为了在状态更新时使用特定的更新策略。`add_messages`是 _LangGraph_ 提供的一种更新策略，用于在列表中追加消息（而不是覆盖）。_LangGraph_ 支持多种更新策略，如覆盖、追加等。 ### 2. 初始化状态图 创建状态图实例，并传入状态类作为参数： ```python from _langgraph_.graph import _State_ Graph graph = _State_ Graph(_State_) ``` ### 3. 添加节点 节点是一个函数，它接收当前状态（一个字典，包含状态 _模式_ 中 _定义_ 的字段）作为输入，并返回一个包含更新后状态字段的字典（或直接返回更新后的状态对象）。这个返回的字典将用于更新整个状态（根据更新策略）。 例如，我们添加一个节点来处理用户输入： ```python def process_input(_state_: _State_) -> dict: # 这里可以处理用户输入，例如调用LLM等 processed = _state_['user_input'].upper() # 简单示例：将输入转为大写 return {'processed_input': processed} # 注意：这里返回的字段需要与状态 _模式_ 匹配？但注意，我们 _定义_ 的状态 _模式_ 中并没有'processed_input'，所以我们需要调整状态 _模式_ 或节点行为。 # 调整状态 _模式_：如果我们希望状态中包含处理后的输入，我们需要在状态 _模式_ 中增加字段。 ``` 因此，我们需要重新考虑状态 _模式_ 的设计。通常，状态 _模式_ 应该包含工作流中所有节点可能读写的数据。所以，我们修改状态 _模式_： ```python class _State_(TypedDict): user_input: str chat_history: Annotated[List[str], add_messages] processed_input: str # 新增字段 ``` 然后调整节点函数： ```python def process_input(_state_: _State_) -> dict: processed = _state_['user_input'].upper() return {'processed_input': processed} # 返回要更新的字段 ``` 然后将节点添加到图中： ```python graph.add_node("process_input", process_input) ``` ### 4. _定义_ 边 我们需要设置起始节点和边，以及条件边（如果需要循环）。例如： ```python graph.set_entry_point("process_input") # 设置入口节点 graph.set_finish_point("process_input") # 如果只有一个节点，可以直接设置为结束点 # 如果有多个节点，我们需要添加边来连接它们，例如： # graph.add_edge('node1', 'node2') ``` ### 5. 编译图 最后，编译图以创建可执行的工作流： ```python app = graph.compile() ``` ### 6. 执行图 使用初始状态调用图： ```python initial_ _state_ = _State_(user_input="hello", chat_history=[], processed_input="") result = app.invoke(initial_ _state_) ``` ### 注意事项 - 状态更新策略：在 _定义_ 状态字段时，使用`Annotated`可以指定更新策略。例如，`add_messages`表示追加消息，而默认策略是覆盖（如果不用`Annotated`，则直接覆盖）。 - 节点函数返回的字典中的每个键必须与状态 _模式_ 中的某个字段名对应，并且值类型要匹配。返回的字典中只需要包含需要更新的字段，不需要返回整个状态。 ### 示例：带条件边的循环 假设我们想让智能体在满足条件时循环执行。我们可以添加一个条件边。 首先，_定义_ 两个节点：一个处理节点，一个判断是否结束的节点。 ```python def should_continue(_state_: _State_) -> str: # 根据状态判断是否继续 if _state_['processed_input'] == "QUIT": return "end" else: return "continue" def process_node(_state_: _State_) -> dict: # 这里模拟处理，每次将processed_input加上一个感叹号，直到遇到QUIT new_processed = _state_['processed_input'] + "!" return {'processed_input': new_processed} # 添加节点 graph.add_node("process", process_node) graph.add_node("check_end", should_continue) # 注意：这个节点实际上是一个条件函数，但也可以作为节点添加 # 设置入口 graph.set_entry_point("process") # 添加边：从process到check_end graph.add_edge("process", "check_end") # 添加条件边：根据check_end节点的返回值决定下一步 graph.add_conditional_edges( "check_end", should_continue, # 这个函数返回字符串，表示下一个节点或结束 { "continue": "process", # 如果返回"continue"，则回到process节点 "end": END # 结束 } ) ``` 注意：条件边函数（`should_continue`）的返回值是字符串，这些字符串映射到下一个节点的名称或`END`（表示结束）。 ### 总结 构建 _LangGraph_ 状态的关键步骤： 1. 设计状态 _模式_（TypedDict），包含所有需要传递的数据字段。 2. 创建状态图实例。 3. 添加节点（处理函数），每个节点负责更新状态的一部分。 4. 设置边（包括条件边）以控制流程。 5. 编译并执行。 以上步骤可以帮助你构建 _LangGraph_ 的状态图。 §§相关问题§§ 1. _LangGraph_ 状态 _模式_ 中如何 _定义_ 字段的更新策略？ 2. 在 _LangGraph_ 中，如何实现多个智能体之间的状态共享？ 3. _LangGraph_ 的状态图与传统的有限状态机(FSM)有何区别？ 4. 在 _LangGraph_ 中，如何处理状态更新时的并发冲突？</think>### _LangGraph_ 状态构建指南 在 _LangGraph_ 中构建状态是实现有状态多智能体系统的核心，以下是构建步骤和关键概念： #### 1. **_定义_ 状态 _模式_（_State_ Schema）** 状态 _模式_ 是一个自 _定义_ 类，用于描述智能体工作流中的数据结构和类型： ```python from typing import TypedDict, Annotated, Sequence from _langgraph_.graph.message import add_messages class _Agent_ _State_(TypedDict): user_query: str _agent_ _response: Annotated[str, lambda x, y: y] # 覆盖式更新 chat_history: Annotated[Sequence[str], add_messages] # 追加式更新 tools_used: list ``` **关键特性**： - **字段类型声明**：每个字段 _定义_ 数据类型（如`str`, `list`等） - **更新策略**（通过`Annotated`指定）： - `add_messages`：追加数据（适合聊天历史） - `lambda x, y: y`：覆盖更新（适合最新结果） - **状态持久化**：状态会在节点间自动传递和更新[^1] #### 2. **初始化状态图** ```python from _langgraph_.graph import _State_ Graph # 创建状态图实例 graph = _State_ Graph(_Agent_ _State_) # 添加节点（智能体功能单元） graph.add_node("query_analyzer", analyze_query) graph.add_node("tool_executor", execute_tools) graph.add_node("response_generator", generate_response) # 设置节点关系 graph.add_edge("query_analyzer", "tool_executor") graph.add_edge("tool_executor", "response_generator") graph.set_finish_point("response_generator") # 编译可执行图 app = graph.compile() ``` #### 3. **节点函数设计** 每个节点接收当前状态，返回状态更新： ```python def execute_tools(_state_: _Agent_ _State_) -> dict: """工具执行节点示例""" tools = select_tools(_state_["user_query"]) results = [tool.run() for tool in tools] return { "tools_used": tools, # 更新工具列表 "_agent_ _response": results[0] # 更新最新结果 } ``` #### 4. **执行状态工作流** ```python # 初始化状态 initial_ _state_ = _Agent_ _State_( user_query="如何计算GDP？", _agent_ _response="", chat_history=[], tools_used=[] ) # 执行工作流 final_ _state_ = app.invoke(initial_ _state_) print(final_ _state_["_agent_ _response"]) ``` #### 5. **高级功能** - **条件分支**：使用`add_conditional_edges`实现动态路由 ```python graph.add_conditional_edges( "query_analyzer", decide_next_node, # 返回"tool_executor"或"response_generator" {"need_tools": "tool_executor", "direct_answer": "response_generator"} ) ``` - **循环控制**：通过`add_edge`创建循环实现多轮交互 - **多智能体协作**：不同节点可对应不同智能体，共享状态对象 #### 最佳实践 1. **状态最小化**：只存储必要数据，避免过度复杂的状态结构 2. **更新策略**：根据字段特性选择追加（历史数据）或覆盖（最新结果） 3. **错误处理**：在节点中添加状态回滚机制 4. **状态快照**：定期持久化状态，支持断点续跑 > 示例应用场景：客户服务系统可包含`问题分类`→`数据库查询`→`结果生成`三个节点，状态对象传递用户问题、查询结果、回复内容等数据[^1]。](https://wenku.csdn.net/answer/6jxfhfex3v)

*   [关于我们](https://www.csdn.net/company/index.html#about)
*   [招贤纳士](https://www.csdn.net/company/index.html#recruit)
*   [商务合作](https://fsc-p05.txscrm.com/T8PN8SFII7W)
*   [寻求报道](https://marketing.csdn.net/questions/Q2202181748074189855)
*   ![Image 57](https://g.csdnimg.cn/common/csdn-footer/images/tel.png)400-660-0108
*   ![Image 58](https://g.csdnimg.cn/common/csdn-footer/images/email.png)[kefu@csdn.net](mailto:webmaster@csdn.net)
*   ![Image 59](https://g.csdnimg.cn/common/csdn-footer/images/cs.png)[在线客服](https://csdn.s2.udesk.cn/im_client/?web_plugin_id=29181)
*    工作时间 8:30-22:00 

*   ![Image 60](https://g.csdnimg.cn/common/csdn-footer/images/badge.png)[公安备案号11010502030143](http://www.beian.gov.cn/portal/registerSystemInfo?recordcode=11010502030143)
*   [京ICP备19004658号](http://beian.miit.gov.cn/publish/query/indexFirst.action)
*   [京网文〔2020〕1039-165号](https://csdnimg.cn/release/live_fe/culture_license.png)
*   [经营性网站备案信息](https://csdnimg.cn/cdn/content-toolbar/csdn-ICP.png)
*   [北京互联网违法和不良信息举报中心](http://www.bjjubao.org/)
*   [家长监护](https://download.csdn.net/tutelage/home)
*   [网络110报警服务](https://cyberpolice.mps.gov.cn/)
*   [中国互联网举报中心](http://www.12377.cn/)
*   [Chrome商店下载](https://chrome.google.com/webstore/detail/csdn%E5%BC%80%E5%8F%91%E8%80%85%E5%8A%A9%E6%89%8B/kfkdboecolemdjodhmhmcibjocfopejo?hl=zh-CN)
*   [账号管理规范](https://blog.csdn.net/blogdevteam/article/details/126135357)
*   [版权与免责声明](https://www.csdn.net/company/index.html#statement)
*   [版权申诉](https://blog.csdn.net/blogdevteam/article/details/90369522)
*   [出版物许可证](https://img-home.csdnimg.cn/images/20250103023206.png)
*   [营业执照](https://img-home.csdnimg.cn/images/20250103023201.png)
*   ©1999-2026北京创新乐知网络技术有限公司

[![Image 61](https://profile-avatar.csdnimg.cn/12627a5b12dd4935a293f4608c5806d4_qq_43588095.jpg!1)](https://blog.csdn.net/qq_43588095)

[上有晨光](https://blog.csdn.net/qq_43588095 "上有晨光")

博客等级 ![Image 62](https://csdnimg.cn/identity/blog5.png)

码龄7年

[91 原创](https://blog.csdn.net/qq_43588095)1604 点赞 1588 收藏 5330 粉丝

[关注](https://blog.csdn.net/qq_43588095/article/details/147479946)

[私信](https://im.csdn.net/chat/qq_43588095)

[![Image 63](https://i-operation.csdnimg.cn/images/d5d144f1d1904560adf54c48ec13c5b4.png)](https://ai.csdn.net/workbench/wallet?utm_source=xtai_slb_bloglb)

[](https://wwads.cn/click/bait)[![Image 64: 万维广告联盟](https://cdn.wwads.cn/creatives/ocZcBmiI9GrrBWWbGauozCvDuNbfUf79yINPx1AP.jpg)](https://wwads.cn/click/bundle?code=OjwIpJp7uaB2SfOUMJIHqtYLJzicsH)

[免部署\运维\账号\支付系统开发，让你用Cursor制作可收费的AI智能体！](https://wwads.cn/click/bundle?code=OjwIpJp7uaB2SfOUMJIHqtYLJzicsH)[![Image 65](https://blog.csdn.net/qq_43588095/article/details/147479946)广告](https://wwads.cn/?utm_source=property-175&utm_medium=footer "点击了解万维广告联盟")

[](https://blog.csdn.net/qq_43588095/article/details/147479946 "隐藏广告")

![Image 66](https://kunyu.csdn.net/1.png?p=56&adId=1071043&adBlockFlag=0&a=1071043&c=0&k=LangGraph%E4%B8%ADState%E7%9A%84%E5%AE%9A%E4%B9%89%E6%A8%A1%E5%BC%8F&spm=1001.2101.3001.5000&articleId=147479946&d=1&t=3&u=a5d2e34815a24cb4879456c525bd7633)

### 热门文章

*   [DeepSeek 模型对比（R1 vs V3 vs V3-0324） ![Image 67](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png)7257](https://blog.csdn.net/qq_43588095/article/details/146748702)
*   [LLaMA - Factory安装部署及微调流程 ![Image 68](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png)4255](https://blog.csdn.net/qq_43588095/article/details/146547831)
*   [LLamaFactory后端PPO微调实操 ![Image 69](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png)3995](https://blog.csdn.net/qq_43588095/article/details/146604113)
*   [LLaMA-Factory 模型微调指令参数详解 ![Image 70](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png)3772](https://blog.csdn.net/qq_43588095/article/details/146572550)
*   [LangGraph中的事件流 ![Image 71](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png)2433](https://blog.csdn.net/qq_43588095/article/details/147635246)

### 分类专栏

*   [![Image 72](https://i-blog.csdnimg.cn/columns/default/20201014180756724.png?x-oss-process=image/resize,m_fixed,h_64,w_64) 大模型Agent开发](https://blog.csdn.net/qq_43588095/category_12933023.html)53篇
*   [![Image 73](https://i-blog.csdnimg.cn/columns/default/20201014180756738.png?x-oss-process=image/resize,m_fixed,h_64,w_64) DeepSeek系列笔记](https://blog.csdn.net/qq_43588095/category_12931550.html)8篇
*   [![Image 74](https://i-blog.csdnimg.cn/columns/default/20201014180756930.png?x-oss-process=image/resize,m_fixed,h_64,w_64) 微调课程笔记](https://blog.csdn.net/qq_43588095/category_12928611.html)30篇

 上一篇： [LangGraph中如何接入大模型做问答流程](https://blog.csdn.net/qq_43588095/article/details/147479709) 下一篇： [LangGraph中使用字典类型定义状态构建图结构](https://blog.csdn.net/qq_43588095/article/details/147479990)

### 最新评论

*   [LangGraph之Tool Calling Agent 中ToolNode的使用](https://blog.csdn.net/qq_43588095/article/details/147633960#comments_37789141)
[木帛:](https://blog.csdn.net/u010380026)好文！但是result_1和2的生成代码是不是有点问题

### 大家在看

*   [2006年Hinton论文：深度学习破冰起点 ![Image 75](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png)986](https://blog.csdn.net/jeffsonfu/article/details/158152445)
*   [Flask+Vue3学生信息管理系统](https://blog.csdn.net/caoli201314/article/details/158234142)
*   [Transformer：跨模态AI核心架构 ![Image 76](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png)1093](https://blog.csdn.net/jeffsonfu/article/details/157688935)
*   [神经网络六十年演进史](https://blog.csdn.net/jeffsonfu/article/details/158208812)
*   [梯度下降及主流优化算法详解](https://blog.csdn.net/jeffsonfu/article/details/158234538)

### 最新文章

*   [LangGraph中的事件流](https://blog.csdn.net/qq_43588095/article/details/147635246)
*   [LangGraph中如何使用流式输出](https://blog.csdn.net/qq_43588095/article/details/147635070)
*   [LangGraph案例实操：构建复杂工具应用的ReAct自治代理（含代码）](https://blog.csdn.net/qq_43588095/article/details/147634669)

[2025年 91篇](https://blog.csdn.net/qq_43588095?type=blog&year=2025&month=04)

![Image 77](https://kunyu.csdn.net/1.png?p=57&adId=1086623&adBlockFlag=0&a=1086623&c=0&k=LangGraph%E4%B8%ADState%E7%9A%84%E5%AE%9A%E4%B9%89%E6%A8%A1%E5%BC%8F&spm=1001.2101.3001.5001&articleId=147479946&d=1&t=3&u=45ac8718cd754d28a20ea1e56f2520e9)

### 目录

1.   [一、LangGraph框架核心要点回顾](https://blog.csdn.net/qq_43588095/article/details/147479946#t0)
2.   [二、State的关键作用及消息传递机制](https://blog.csdn.net/qq_43588095/article/details/147479946#t1)
3.   [三、State的定义模式与代码实现示例](https://blog.csdn.net/qq_43588095/article/details/147479946#t2)

展开全部![Image 78](https://csdnimg.cn/release/blogv2/dist/pc/img/arrowup-line-bot-White.png)

收起![Image 79](https://csdnimg.cn/release/blogv2/dist/pc/img/arrowup-line-top-White.png)

![Image 80](https://kunyu.csdn.net/1.png?p=530&adId=1086624&adBlockFlag=0&a=1086624&c=0&k=LangGraph%E4%B8%ADState%E7%9A%84%E5%AE%9A%E4%B9%89%E6%A8%A1%E5%BC%8F&spm=1001.2101.3001.4647&articleId=147479946&d=1&t=3&u=e41726bf44e74f4d9f03f7a1cb21f59e)

### 目录

1.   [一、LangGraph框架核心要点回顾](https://blog.csdn.net/qq_43588095/article/details/147479946#t0)
2.   [二、State的关键作用及消息传递机制](https://blog.csdn.net/qq_43588095/article/details/147479946#t1)
3.   [三、State的定义模式与代码实现示例](https://blog.csdn.net/qq_43588095/article/details/147479946#t2)

展开全部![Image 81](https://csdnimg.cn/release/blogv2/dist/pc/img/arrowup-line-bot-White.png)

收起![Image 82](https://csdnimg.cn/release/blogv2/dist/pc/img/arrowup-line-top-White.png)

[](https://wwads.cn/click/bait)[![Image 83: 万维广告联盟](https://cdn.wwads.cn/creatives/ocZcBmiI9GrrBWWbGauozCvDuNbfUf79yINPx1AP.jpg)](https://wwads.cn/click/bundle?code=OjwIpJp7uaB2SfOUMJIHqtYLJzicsH)

[免部署\运维\账号\支付系统开发，让你用Cursor制作可收费的AI智能体！](https://wwads.cn/click/bundle?code=OjwIpJp7uaB2SfOUMJIHqtYLJzicsH)[![Image 84](https://blog.csdn.net/qq_43588095/article/details/147479946)广告](https://wwads.cn/?utm_source=property-175&utm_medium=footer "点击了解万维广告联盟")

[](https://blog.csdn.net/qq_43588095/article/details/147479946 "隐藏广告")

![Image 85](https://kunyu.csdn.net/1.png?p=479&adId=1071044&adBlockFlag=0&a=1071044&c=0&k=LangGraph%E4%B8%ADState%E7%9A%84%E5%AE%9A%E4%B9%89%E6%A8%A1%E5%BC%8F&spm=1001.2101.3001.4834&articleId=147479946&d=1&t=3&u=56412dcc2f554eaba763e3b763a50e70)

 上一篇： [LangGraph中如何接入大模型做问答流程](https://blog.csdn.net/qq_43588095/article/details/147479709) 下一篇： [LangGraph中使用字典类型定义状态构建图结构](https://blog.csdn.net/qq_43588095/article/details/147479990)

### 分类专栏

*   [![Image 86](https://i-blog.csdnimg.cn/columns/default/20201014180756724.png?x-oss-process=image/resize,m_fixed,h_64,w_64) 大模型Agent开发](https://blog.csdn.net/qq_43588095/category_12933023.html)53篇
*   [![Image 87](https://i-blog.csdnimg.cn/columns/default/20201014180756738.png?x-oss-process=image/resize,m_fixed,h_64,w_64) DeepSeek系列笔记](https://blog.csdn.net/qq_43588095/category_12931550.html)8篇
*   [![Image 88](https://i-blog.csdnimg.cn/columns/default/20201014180756930.png?x-oss-process=image/resize,m_fixed,h_64,w_64) 微调课程笔记](https://blog.csdn.net/qq_43588095/category_12928611.html)30篇

[展开全部![Image 89](https://csdnimg.cn/release/blogv2/dist/pc/img/arrowup-line-bot-White.png)](https://blog.csdn.net/qq_43588095/article/details/147479946)[收起![Image 90](https://csdnimg.cn/release/blogv2/dist/pc/img/arrowup-line-top-White.png)](https://blog.csdn.net/qq_43588095/article/details/147479946)

登录后您可以享受以下权益：

*   ![Image 91](blob:http://localhost/e891c3a7c1a92038da15617ead1c0096)免费复制代码
*   ![Image 92](blob:http://localhost/3d84693e43989ca72c63590d38052fc8)和博主大V互动
*   ![Image 93](blob:http://localhost/a746ba3bd4746d1ec8acd6b5071ccf00)下载海量资源
*   ![Image 94](blob:http://localhost/7cd6e3cbe7e0076d0b9199193b4b832d)发动态/写文章/加入社区

×立即登录

评论![Image 95](https://csdnimg.cn/release/blogv2/dist/pc/img/closeBt.png)

![Image 96](https://csdnimg.cn/release/blogv2/dist/pc/img/commentArrowLeftWhite.png)被折叠的 条评论 [为什么被折叠?](https://blogdev.blog.csdn.net/article/details/122245662)[![Image 97](https://csdnimg.cn/release/blogv2/dist/pc/img/iconPark.png)到【灌水乐园】发言](https://bbs.csdn.net/forums/FreeZone)

[查看更多评论![Image 98](https://csdnimg.cn/release/blogv2/dist/pc/img/commentArrowDownWhite.png)](https://blog.csdn.net/qq_43588095/article/details/147479946)

 添加红包 [](https://blog.csdn.net/qq_43588095/article/details/147479946)

祝福语 

[](https://blog.csdn.net/qq_43588095/article/details/147479946)

请填写红包祝福语或标题

红包数量 

个

红包个数最小为10个

红包总金额 

元

红包金额最低5元

余额支付 

 当前余额 3.43 元 [前往充值 >](https://i.csdn.net/#/wallet/balance/recharge)

 需支付：10.00 元 

取消 确定

![Image 99](https://blog.csdn.net/qq_43588095/article/details/147479946)

成就一亿技术人!

 领取后你会自动成为博主和红包主的粉丝 [规则](https://blogdev.blog.csdn.net/article/details/128932621)

[![Image 100](https://profile-avatar.csdnimg.cn/default.jpg!2)](https://blog.csdn.net/qq_43588095/article/details/147479946)

hope_wisdom

 发出的红包 

实付 元

[使用余额支付](javascript:;)

![Image 101](https://csdnimg.cn/release/blogv2/dist/pc/img/pay-time-out.png)点击重新获取

![Image 102](https://csdnimg.cn/release/blogv2/dist/pc/img/weixin.png)![Image 103](https://csdnimg.cn/release/blogv2/dist/pc/img/zhifubao.png)![Image 104](https://csdnimg.cn/release/blogv2/dist/pc/img/jingdong.png)扫码支付

钱包余额 0

![Image 105](https://csdnimg.cn/release/blogv2/dist/pc/img/pay-help.png)

抵扣说明：

1.余额是钱包充值的虚拟货币，按照1:1的比例进行支付金额的抵扣。

 2.余额无法直接购买下载，可以购买VIP、付费专栏及课程。

[![Image 106](https://csdnimg.cn/release/blogv2/dist/pc/img/recharge.png)余额充值](https://i.csdn.net/#/wallet/balance/recharge)

![Image 107](https://blog.csdn.net/qq_43588095/article/details/147479946)

确定 取消![Image 108](https://csdnimg.cn/release/blogv2/dist/pc/img/closeBt.png)

举报

![Image 109](https://csdnimg.cn/release/blogv2/dist/pc/img/closeBlack.png)

选择你想要举报的内容（必选）

*   内容涉黄
*   政治相关
*   内容抄袭
*   涉嫌广告
*   内容侵权
*   侮辱谩骂
*   样式问题
*   其他

原文链接（必填）

请选择具体原因（必选）

*   包含不实信息
*   涉及个人隐私

请选择具体原因（必选）

*   侮辱谩骂
*   诽谤

请选择具体原因（必选）

*   搬家样式
*   博文样式

补充说明（选填）

取消

确定

[![Image 110](https://i-operation.csdnimg.cn/images/23189f0255c74da0aead8ae1842c6f39.gif)](https://ai.csdn.net/workbench/wallet?utm_source=xtai_slb_blogxf_ty)[![Image 111](https://csdnimg.cn/release/blogv2/dist/pc/img/toolbar/Group.png)点击体验 DeepSeekR1满血版](https://ai.csdn.net/chat?utm_source=cknow_pc_blogdetail&spm=1001.2101.3001.10583)[![Image 112](https://g.csdnimg.cn/side-toolbar/3.6/images/mobile.png) 下载APP ![Image 113: 程序员都在用的中文IT技术交流社区](https://g.csdnimg.cn/side-toolbar/3.6/images/qr_app.png) 程序员都在用的中文IT技术交流社区 公众号 ![Image 114: 专业的中文 IT 技术社区，与千万技术人共成长](https://g.csdnimg.cn/side-toolbar/3.6/images/qr_wechat.png) 专业的中文 IT 技术社区，与千万技术人共成长 视频号 ![Image 115: 关注【CSDN】视频号，行业资讯、技术分享精彩不断，直播好礼送不停！](https://g.csdnimg.cn/side-toolbar/3.6/images/qr_video.png) 关注【CSDN】视频号，行业资讯、技术分享精彩不断，直播好礼送不停！](https://blog.csdn.net/qq_43588095/article/details/147479946)[![Image 116](https://g.csdnimg.cn/side-toolbar/3.6/images/customer.png)客服](https://blog.csdn.net/qq_43588095/article/details/147479946)[![Image 117](https://g.csdnimg.cn/side-toolbar/3.6/images/totop.png)返回顶部](https://blog.csdn.net/qq_43588095/article/details/147479946)

[![Image 118](https://csdnimg.cn/release/blogv2/dist/pc/img/quoteClose1White.png)](https://blog.csdn.net/qq_43588095/article/details/147479946)

![Image 119](https://i-blog.csdnimg.cn/direct/34c5cd13225746f28209b80e750f3d85.png#pic_center)

-还原+1:1 还原