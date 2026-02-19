# 使用LangGraph 与LangChain 构建多工具有状态智能体 - Jimmy Song

**URL**:
https://jimmysong.io/zh/book/ai-handbook/agent/langgraph/

## 元数据
- 发布日期: 2025-11-02T00:00:00+00:00

## 完整内容
---
使用 LangGraph 与LangChain 构建多工具有状态智能体| Jimmy Song
[跳转到主要内容] [跳转到导航] [跳转到页脚] 
从云原生走向AI 原生：一套面向未来的架构方法论[→ 阅读《AI 原生基础设施》] 
**
#### **站内搜索
**
**搜索
类型:
**所有类型**当前图书**博客**AI**图书**公告**播客
**键盘导航:**
Tab下一个结果|Shift+Tab上一个结果|↑↓导航|Enter打开链接|Esc关闭
# 使用LangGraph 与LangChain 构建多工具有状态智能体**草稿
**
**内容导航
**
**图书内部搜索...
> 智能体开发进入“有状态”时代，LangGraph 让多工具智能体既可控又灵活，助你打造真正工程级AI 系统。本文将指导高级AI 工程开发者，如何基于**LangChain**的扩展库**LangGraph**，使用 Python 构建一个具备多工具调用能力的**有状态智能体（Multi-Tool Agent）**。我们将详述如何设计有状态的智能体工作流（如检索 - 计划- 执行- 验证等阶段），如何在智能体中注册和选择不同工具、处理记忆模块，以及如何实现并发、分支和回退控制流程。教程还将涵盖观察调试智能体的方法（日志追踪、链路Trace、决策记录），以及如何进行错误注入与回放来提高智能体的健壮性。最后，我们提供一个端到端示例任务（包含所有可运行的代码片段），并通过 Mermaid 图表直观展示智能体的决策流程与工具链路。请注意，本教程所有代码均采用Python，实现均兼容本地部署的大语言模型（如 Qwen 或Ollama），未依赖 OpenAI/Claude 等闭源模型。## LangGraph 简介：让智能体工作流进入“有状态”时代**LangGraph**是由 LangChain 团队推出的用于构建**循环图工作流**的库，可以视作 LangChain 在智能体编排上的一个重要扩展模块。传统的LangChain Chain 是**无环的**（DAG 形式），而LangGraph 允许在链中**引入循环**，从而实现更复杂的智能体行为（例如让 LLM 在工具调用失败时重新规划、在多轮对话中持续决策等）。这种循环能力本质上就是让LLM 在一个类似`for`循环的结构中不断根据状态进行推理和行动选择。
LangGraph 将智能体的流程视为**状态机（state machine）**。开发者可以手动规定智能体的决策流程（如先调用哪个工具、在什么条件下循环/分支），而不仅仅依赖 LLM 的自由推理。这种显式的流程控制对于生产环境尤为重要：例如你可能希望**强制智能体首先调用某个工具**，或者根据当前状态采用不同的提示 (prompt)。通过 LangGraph，我们可以将这些流程以**图（graph）**的形式声明出来，构建出兼具**灵活推理**和**可控流程**的智能体系统。
**StateGraph**是 LangGraph 的核心概念，它表示一个状态驱动的图。StateGraph 有一个全局共享的**状态对象（state）**，在图的各节点之间传递和更新。节点可以看作对状态的一个操作：每个节点接收当前状态（通常是一个字典）作为输入，执行计算后输出一个字典，用于更新全局状态的一部分。状态的每个字段可以配置为**覆盖**更新或**累加**更新。当字段设置为累加（例如一个用于记录行动步骤的列表），多个节点循环更新时会自动将新结果附加在列表后面。
使用LangGraph 定义智能体的基本步骤包括：* **定义状态结构**：使用`TypedDict`指定 State 对象的字段和类型，以及哪些字段是累加List 需要用`operator.add`标记。
* **添加节点**：使用`graph.add\_node(name, func)`注册节点。每个节点要么是一个 Python 函数，要么是LangChain Runnable，负责完成一个步骤的逻辑。
* **添加边（Edges）**：用`graph.set\_entry\_point(node)`指定图的起始节点，然后通过`graph.add\_edge`添加普通顺序边，或通过`graph.add\_conditional\_edge`添加条件分支边。条件边可以让某个节点根据状态判断下一步跳转到哪一个节点。
* **指定结束**：LangGraph 提供特殊的`END`节点表示结束，务必保证循环流程有退出条件。
* **编译运行**：调用`graph.compile()`将定义的图编译为一个可调用的对象（实现了`.invoke()`等方法），然后即可像调用链那样调用智能体。
下面将结合这些概念，设计我们的有状态多工具Agent，并在各环节介绍实现细节。
## 设计有状态智能体的阶段编排与控制流程为了构建一个多工具Agent，我们采用**分阶段的流程设计**：例如包含“需求分析/检索 →计划→工具执行→验证”的流水线。在LangGraph 中，这些阶段对应为一系列节点按某种逻辑连接成图。我们将用一个示意性任务来说明——**根据用户查询决定是否需要检索外部数据、调用计算工具，并最终生成答案**。这个任务中，Agent 可能需要经过以下决策步骤：1. **分析需求（Plan）**：解析用户输入，判断是否需要调用工具（以及调用哪些工具）。如果不需要工具，直接生成答案；如果需要，决定下一步要用的工具及其输入。
2. **执行工具（Execute Tool）**：调用所选工具并获取结果。如果有多个子任务，可能重复调用不同工具。
3. **（可选）验证或后处理（Verify）**：检查工具结果是否满足要求，是否需要再次调用其他工具或调整计划。如果结果不理想，可以回退到上一步重新规划。
4. **最终回答（Finalize）**：整合所有信息，形成给用户的最终答复。
在我们的示例中，我们将实现一个智能体能够**查询国家的人口并计算总和**。这个智能体会动态决定使用两个工具：
* 一个**检索工具**：查找给定国家的人口数据。
* 一个**计算工具**：对获得的数值执行算术计算。
我们会让智能体针对用户的问题自动决定调用上述工具的顺序和次数。例如用户问：“法国和日本的人口总和是多少？”，Agent 将判断需要查找法国人口、查找日本人口，然后加总。这一过程中，Agent 会经历**循环**：LLM 先规划调用检索工具，获取法国人口；接着再次规划调用检索工具获取日本人口；然后规划调用计算工具求和；最后生成答案。### 节点设计：Plan 与Tools
我们为上述流程设计两个主要节点：* **Plan 节点**（如同智能体的“大脑”）：使用 LLM 或规则逻辑，根据当前状态决定下一步动作（调用工具或输出答案）。该节点会更新状态中的指令，例如选定工具及其输入参数，或者直接写入最终答案。* **Tools 节点**（工具执行器）：根据 Plan 节点提供的指令，实际调用相应的工具函数，将结果写回状态（供下次Plan 决策使用）。此外，可以视需要添加其他节点，例如用于验证或回退的节点。本例中我们简化，将验证逻辑融合在Plan 节点里，根据需要重复工具调用或结束。### 状态设计：共享信息和累积中间结果我们通过定义State 对象的字段来实现节点间的信息共享和状态跟踪。对于本示例，我们定义状态包含：* `input`：用户的原始查询（字符串）。
* `targets`：待查询的信息目标列表（如[&ldquo;France&rdquo;,&ldquo;Japan&rdquo;]）。在 Plan 节点首次运行时，从`input`中解析填充。
* `index`：当前已处理的目标计数（整数）。用于跟踪已完成了几个工具调用。
* `collected`：已收集的中间结果列表（如已获取的人口数字列表）。定义为累加列表，这样工具节点每返回一个结果就附加其值。
* `answer`：最终答案（字符串）。Plan 节点在确定完成所有步骤后写入此字段。上述字段中，`collected`使用了`operator.add`设置为累加模式，其他字段则用默认覆盖模式。这样`collected`会自动累计工具输出，而不是被覆盖。定义状态的代码如下：
```
`fromtypingimportTypedDict,Annotated,ListimportoperatorclassState(TypedDict):input:str# 用户输入targets:List[str]# 待检索的目标列表collected:Annotated[List[int],operator.add]# 累计收集的数值结果index:int# 已处理目标计数answer:str# 最终答案`
```
### Plan 节点实现：LLM 计划与决策Plan 节点的职责是分析当前状态，决定下一步做什么。这里我们可以**借助大语言模型**根据提示来决定行动，也可以简化为规则逻辑。在不依赖 OpenAI API 的前提下，我们示范一种**规则+LLM 结合**的思路：
* **需求解析**：当 Plan 节点第一次接收用户输入时，可通过简单规则或提示调用LLM，从中提取需要查询的目标。例如检测输入中是否包含“&mldr;的**人口**”，如果有则识别国家名称列表。如果没有外部信息需求，则可以直接回答。
* **动态决策**：根据当前已收集的数据 (`collected`) 与目标列表(`targets`)，决定下一步。如果还有未查询的目标，则设置下一步调用检索工具查询下一个目标；如果目标都已查询完且有多个数值，需要汇总，则选择计算工具；如果已经获得最终结果或不需要工具，则直接产生日志和答案。
下面是Plan 节点函数的示例实现（不依赖外部LLM API，而是用规则逻辑模拟决策）：
```
`defplan\_node\_fn(state:dict)-&gt;dict:# 提取当前状态信息query=state.get(&#39;input&#39;,&#39;&#39;)targets=state.get(&#39;targets&#39;)idx=state.get(&#39;index&#39;,0)values=state.get(&#39;collected&#39;,[])# 若已经计算出最终结果（collected 比targets 多一个值，则最后一个为汇总结果）iftargetsisnotNoneandlen(values)&gt;len(targets):final\_val=values[-1]return{&#39;answer&#39;:f&#34;总人口为{final\_val}万人。&#34;}# 首次运行：解析输入找出目标列表iftargetsisNone:targets=[]# 简单解析：寻找&#34;人口 of X&#34; 模式text=query.lower()if&#34;population of&#34;intext:parts=text.split(&#34;population of&#34;)forpartinparts[1:]:token=part.strip().split()[0]iftoken:targets.append(token.capitalize())# 处理&#34;X and Y&#34; 的情况if&#34; and &#34;inqueryandtargets:last=query.split(&#34; and &#34;)[-1].strip()iflast:country=last.split()[0].capitalize()ifcountryandcountrynotintargets:targets.append(country)# 初始化状态字段state[&#39;targets&#39;]=targetsstate[&#39;index&#39;]=0state[&#39;collected&#39;]=[]idx=0values=[]# 如未找到任何目标，则不需要工具，直接给出回答（这里简单返回一句话）ifnottargets:return{&#39;answer&#39;:&#34;这个问题不需要调用工具，可直接回答。&#34;}# 如果仍有目标未查询，选择调用检索工具查询下一个目标ifidx&lt;len(targets):country=targets[idx]return{&#39;tool&#39;:&#39;&#39;search\_population&#39;&#39;,&#39;&#39;tool\_query&#39;&#39;:country}# 如果所有目标都已查询且存在多个数值，调用计算工具求和ifidx==len(targets)andlen(values)&gt;1:expr=&#34; + &#34;.join(str(val)forvalinvalues)return{&#39;tool&#39;:&#39;calculator&#39;,&#39;&#39;tool\_query&#39;&#39;:expr}# 如果所有目标查询完且只有单个值，则直接输出答案ifidx==len(targets):ifvalues:return{&#39;answer&#39;:f&#34;{targets[0]}的人口为{values[0]}万人。&#34;}else:return{&#39;answer&#39;:&#34;未找到相关数据。&#34;}# 默认返回空（正常情况下不会走到这里）return{}`
```
**实现要点**：
* 初次运行时，`targets`为空，我们解析用户输入中的关键词填充目标列表（如找到“France”“Japan”两国），并将它们存入状态。这个解析过程可以用 LangChain 的提示模板结合LLM 完成，如让模型从问句中提取实体列表；但这里为简明直接用字符串分析。* 每次决策，根据`index`和`targets`列表判断进度：若`index`尚未到达`targets`末尾，则还有国家未查询，于是返回指示调用`search\_population`工具（并指定查询国家名）；若已收集多个数值，则需要求和，于是返回调用`calculator`工具的指令；若只收集了一个值且无进一步操作，则直接准备输出答案。
* 当检测到状态中`collected`数量比`targets`数多时，说明上一步计算工具已经算出了最终汇总结果，我们便直接构造最终回答放入`answer`字段。### Tools 节点实现：多工具执行与结果写回Tools 节点负责根据Plan 给出的指令实际调用工具函数，并把结果更新到状态中。首先需要**注册工具**：在 LangChain 中通常将工具封装为Tool 对象，但在此我们直接用普通的Python 函数模拟工具功能：* `search\_population(country: str)`：检索某国家人口。本例中我们用预设的字典模拟数据库。例如`population\_data = {"France": 67, "Japan": 125}`表示法国人口 67 百万人、日本125 百万人。函数返回找到的人口数字（为了简化计算，我们返回整数部分）。* `calculator(expression: str)`：计算算术表达式结果。可以用 Python 的`eval`来处理简单加法表达式（但实际场景应谨慎处理安全）。本例中，我们传入的表达式格式如`"67 + 125"`，计算后得到整数结果`192`。
工具执行函数完成后，要将结果写入状态。根据之前状态设计，我们希望：* 检索工具得到的人口数字追加到`collected`列表，并将`index`递增 1（表示一个目标已完成）。
* 计算工具得到的总和结果也追加到`collected`列表。此时列表将比原目标数多一个元素，方便 Plan 节点识别已经完成汇总。下面是Tools 节点的示例实现：```
`# 模拟数据库population\_data={&#34;France&#34;:67,&#34;Japan&#34;:125}deftool\_node\_fn(state:dict)-&gt;dict:tool\_name=state.get(&#39;tool&#39;)query=state.get(&#39;&#39;tool\_query&#39;&#39;)iftool\_name==&#39;&#39;search\_population&#39;&#39;:country=queryifcountryinpopulation\_data:result=population\_data[country]# 将结果追加到collected 列表（LangGraph 累加机制会自动append）return{&#39;collected&#39;:[result],&#39;index&#39;:state.get(&#39;index&#39;,0)+1}else:# 没找到数据，返回错误信息return{&#39;error&#39;:f&#34;未找到{country}的人口数据&#34;}eliftool\_name==&#39;calculator&#39;:expr=query# 形如&#34;67 + 125&#34;try:calc\_result=eval(expr)exceptExceptionase:return{&#39;error&#39;:f&#34;计算出错：{e}&#34;}# 将计算结果也加入collectedreturn{&#39;collected&#39;:[int(calc\_result)]}else:return{&#39;error&#39;:f&#34;未知工具:{tool\_name}&#34;}`
```
**实现要点**：
* 根据状态中的`tool`字段分发到对应的工具逻辑。
* 每个工具通过返回字典来更新状态。对于`collected`字段，由于我们在 State 定义中标记了`operator.add`，LangGraph 会自动将新列表元素添加到已有列表后面。* `search\_population`成功时还返回更新后的`index`（旧值 +1）。`calculator`完成汇总后不增 index，因为此时`index`已经等于目标数，汇总结果只是附加信息。
* 如果出现错误（如没有找到数据，或表达式计算异常），这里简单地将错误信息写入状态的`error`字段。后续我们可以通过检测`error`实现异常分支处理。### 构建状态图（StateGraph）并添加控制边
有了Plan 和Tools 两个节点函数，我们就可以把它们加入StateGraph 并连成工作流：```
`fromlanggraph.graphimportStateGraph,END# 初始化状态图graph=StateGraph(State)# 添加节点graph.add\_node(&#34;plan&#34;,plan\_node\_fn)graph.add\_node(&#34;tools&#34;,tool\_node\_fn)# 指定入口节点graph.set\_entry\_point(&#34;plan&#34;)# 添加普通边：工具节点执行后回到计划节点（形成循环）graph.add\_edge(&#34;tools&#34;,&#34;plan&#34;)# 添加条件边：plan 节点根据返回结果决定下一步去向defshould\_continue(state:dict)-&gt;str:# 若Plan 返回了最终答案，则结束，否则进入工具执行return&#34;end&#34;ifstate.get(&#39;answer&#39;)else&#34;continue&#34;graph.add\_conditional\_edge(&#34;plan&#34;,should\_continue,{&#34;end&#34;:END,&#34;continue&#34;:&#34;tools&#34;})# 编译图为可调用应用app=graph.compile()`
```
在上述代码中，我们建立了如下流程关系：![图 1: 流程关系图] 图 1: 流程关系图如上图所示，Agent 从Plan 节点开始：Plan 节点要么决定直接结束（生成最后回答），要么指定需要调用某个工具然后进入Tools 节点。Tools 节点执行完，再回到Plan 重新决策。这个循环会持续，直到Plan 给出结束条件（即state 中出现`answer`）跳转到 End 节点。在我们的示例中，循环可能经历多次工具调用（如两次检索，一次计算）再结束。### 并发执行与分支：高级控制流LangGraph 除了支持上述顺序循环，还支持更复杂的**并发和分支**控制流。通过一个节点连接出**多个后继节点**即可形成**分叉**（fan-out），LangGraph 可并行执行这些分支节点，然后在某处**汇合**（fan-in）它们的结果。例如，我们可以改进前述 Agent，让它**并行地查询多个国家的人口**以加速流程。当 Plan 节点识别出多个目标时，不是依次一个个调用检索工具，而是同时分叉出多个检索节点，然后汇总结果再进行计算。下图展示了这种并行分支结构的雏形：![图 2: 高级控制流] 图 2: 高级控制流在LangGraph 实现并行，可以为一个节点添加**多条普通边**指向不同后继节点，如：`graph.add\_edge("plan", "searchA"); graph.add\_edge("plan", "searchB")`。当 Plan 节点执行后，LangGraph 将在同一轮中并发执行`searchA`和`searchB`两个节点，并分别更新状态。为正确汇总并行结果，需在状态定义中为共享字段设置**自定义合并函数**。例如让两个检索节点各自返回一个结果列表，然后在汇合节点前通过 reducer 函数合并它们。LangGraph 允许我们在State 定义时提供自定义`reducer`来合并并行分支的输出。完成 fan-in 后，再继续后续节点（如计算和输出）。需要注意，并行工具调用会增加实现复杂度，如处理结果顺序和可能的异步I/O 等，在实际应用中应根据需要权衡使用。除了并行，LangGraph 也支持**条件分支**：通过`add\_conditional\_edge`可以让某节点根据状态选择不同分支路径（如不同工具、不同应对策略）。这类条件可以由 LLM 决定，也可以由规则函数决定。例如，我们可以在智能体某步引入**验证节点**：检查先前答案是否符合要求，如果不符合则走分支调用其它工具重试，符合则直接结束。这相当于实现了一种**回退/回放机制**。总之，通过组合**循环、并行、条件**三种边类型，LangGraph 能表达几乎任意复杂的智能体流程。## 多工具调用机制有状态智能体的优势在于可以灵活地选择并调用多个工具。接下来，我们讨论如何管理**多工具的注册与调度**，并确保每次工具调用的输入输出正确、错误可控。
### 工具注册与封装在LangChain 框架中，工具通常被封装为`Tool`对象，包含名称、描述和实际执行函数。但在 LangGraph 中，我们无需特别封装，直接在Tools 节点里按照`state['tool']`判定来调用相应函数即可（如上所示）。当然，在更复杂情况下，


---
*数据来源: Exa搜索 | 获取时间: 2026-02-19 20:54:46*