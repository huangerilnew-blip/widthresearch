# LangGraph从新手到老师傅 - 4 - StateGraph条件边详解

**URL**:
https://juejin.cn/post/7545886696912928802

## 元数据
- 发布日期: 2025-09-04T00:00:00+00:00

## 完整内容
---
LangGraph从新手到老师傅 - 4 - StateGraph条件边详解前言 在LangGraph中，条件边（Con - 掘金![稀土掘金]![稀土掘金] 
# LangGraph从新手到老师傅 - 4 - StateGraph条件边详解
[在钱塘江] 
2025-09-04481阅读7分钟
## 前言在LangGraph中，条件边（Conditional Edges）是一个强大的特性，它允许我们根据状态的值动态地选择执行路径。这使得我们可以构建具有决策能力的工作流，根据不同的输入或中间状态执行不同的处理逻辑。本文将通过分析示例，深入讲解条件边的概念、实现方式和应用场景。
## 条件边基础概念条件边是StateGraph中的一种特殊边，它不直接连接两个节点，而是根据一个路由函数（router function）的返回值来决定下一步执行哪个节点。这种机制使得我们可以在工作流中实现条件分支逻辑，类似于编程语言中的`if-else`语句或`switch-case`语句。
条件边的核心组件包括：1. **路由函数**：根据当前状态返回目标节点名称的函数
2. **映射关系**：将路由函数的返回值映射到实际节点名称的字典## 示例代码```
`fromtyping\_extensionsimportTypedDictfromlanggraph.graphimportStateGraph, START, ENDfromlangchain\_core.runnables.graph\_mermaidimportMermaidDrawMethodprint("======= 示例2: 使用条件边=======")# 定义状态类型classConditionalState(TypedDict):
number:intpath:strresult:str# 定义节点函数defcheck\_number(state: ConditionalState) -\> ConditionalState:"""检查数字的节点"""returnstate# 这个节点仅用于路由，不改变状态defprocess\_even(state: ConditionalState) -\>dict:"""处理偶数的节点"""result =f"{state['number']}是偶数，已乘以2:{state['number'] \*2}"return{"result": result,"path":"even"}defprocess\_odd(state: ConditionalState) -\>dict:"""处理奇数的节点"""result =f"{state['number']}是奇数，已加1:{state['number'] +1}"return{"result": result,"path":"odd"}# 创建StateGraphconditional\_graph = StateGraph(ConditionalState)# 添加节点conditional\_graph.add\_node("check\_number", check\_number)
conditional\_graph.add\_node("process\_even", process\_even)
conditional\_graph.add\_node("process\_odd", process\_odd)# 添加边conditional\_graph.add\_edge(START,"check\_number")# 添加条件边defrouter(state: ConditionalState) -\>str:"""根据数字奇偶性路由到不同节点"""ifstate["number"] %2==0:return"process\_even"else:return"process\_odd"conditional\_graph.add\_conditional\_edges("check\_number",# 起始节点router,# 路由函数{"process\_even":"process\_even","process\_odd":"process\_odd"}# 映射关系)
conditional\_graph.add\_edge("process\_even", END)
conditional\_graph.add\_edge("process\_odd", END)# 编译图compiled\_conditional\_graph = conditional\_graph.compile()# 执行图- 测试偶数result\_even = compiled\_conditional\_graph.invoke({"number":4,"path":"","result":""})print(f"输入偶数: {{'number': 4, 'path': '', 'result': ''}}")print(f"输出:{result\_even}")# 执行图- 测试奇数result\_odd = compiled\_conditional\_graph.invoke({"number":5,"path":"","result":""})print(f"输入奇数: {{'number': 5, 'path': '', 'result': ''}}")print(f"输出:{result\_odd}")# 示例说明：# 1. 这个示例展示了如何使用条件边根据状态值动态选择执行路径# 2. 定义了一个router函数，根据输入数字的奇偶性决定执行哪个处理节点# 3. 使用add\_conditional\_edges方法配置条件路由# 4. 可以看到对于偶数和奇数输入，会得到不同的处理结果`
```
## 代码解析：条件边的实现与应用### 1. 定义状态类型```
`classConditionalState(TypedDict):
number:intpath:strresult:str`
```
这个状态类型定义了三个字段：* `number`：整数类型，用于存储要判断的数字
* `path`：字符串类型，用于记录执行路径（"even"或"odd"）
* `result`：字符串类型，用于存储处理结果### 2. 定义节点函数```
`defcheck\_number(state: ConditionalState) -\> ConditionalState:"""检查数字的节点"""returnstate# 这个节点仅用于路由，不改变状态defprocess\_even(state: ConditionalState) -\>dict:"""处理偶数的节点"""result =f"{state['number']}是偶数，已乘以2:{state['number'] \*2}"return{"result": result,"path":"even"}defprocess\_odd(state: ConditionalState) -\>dict:"""处理奇数的节点"""result =f"{state['number']}是奇数，已加1:{state['number'] +1}"return{"result": result,"path":"odd"}`
```
这里定义了三个节点函数：* `check\_number`：一个特殊的节点，它不改变状态，仅作为路由的起点
* `process\_even`：处理偶数的节点，将数字乘以2并更新结果
* `process\_odd`：处理奇数的节点，将数字加1并更新结果### 3. 创建和配置StateGraph
```
`# 创建StateGraphconditional\_graph = StateGraph(ConditionalState)# 添加节点conditional\_graph.add\_node("check\_number", check\_number)
conditional\_graph.add\_node("process\_even", process\_even)
conditional\_graph.add\_node("process\_odd", process\_odd)# 添加边conditional\_graph.add\_edge(START,"check\_number")`
```
这部分代码创建了StateGraph实例并添加了三个节点，然后从`START`节点连接到`check\_number`节点。
### 4. 添加条件边```
`# 定义路由函数defrouter(state: ConditionalState) -\>str:"""根据数字奇偶性路由到不同节点"""ifstate["number"] %2==0:return"process\_even"else:return"process\_odd"# 配置条件边conditional\_graph.add\_conditional\_edges("check\_number",# 起始节点router,# 路由函数{"process\_even":"process\_even","process\_odd":"process\_odd"}# 映射关系)
conditional\_graph.add\_edge("process\_even", END)
conditional\_graph.add\_edge("process\_odd", END)`
```
这是条件边实现的核心部分：1. 首先定义了一个`router`函数，它接收当前状态，根据`number`字段的奇偶性返回目标节点的名称
2. 然后使用`add\_conditional\_edges`方法配置条件边：
* 第一个参数是起始节点名称（"check\_number"）
* 第二个参数是路由函数（`router`）
* 第三个参数是映射关系字典，将路由函数的返回值映射到实际的节点名称* 最后，从`process\_even`和`process\_odd`节点分别连接到`END`节点### 5. 编译和执行图```
`# 编译图compiled\_conditional\_graph = conditional\_graph.compile()# 执行图- 测试偶数result\_even = compiled\_conditional\_graph.invoke({"number":4,"path":"","result":""})print(f"输入偶数: {{'number': 4, 'path': '', 'result': ''}}")print(f"输出:{result\_even}")# 执行图- 测试奇数result\_odd = compiled\_conditional\_graph.invoke({"number":5,"path":"","result":""})print(f"输入奇数: {{'number': 5, 'path': '', 'result': ''}}")print(f"输出:{result\_odd}")`
```
编译图后，我们分别用偶数（4）和奇数（5）测试了图的执行。从输出结果可以看到，对于不同的输入，图会执行不同的处理节点，产生不同的结果。
## 执行流程分析让我们详细分析一下整个图的执行流程：### 对于偶数输入（例如4）：
1. **初始化**：`invoke()`方法接收初始状态`{"number": 4, "path": "", "result": ""}`
2. **执行`check\_number`节点**：从`START`开始，首先执行`check\_number`节点，返回原始状态
3. **执行路由函数**：调用`router`函数检查数字的奇偶性，返回"process\_even"
4. **执行`process\_even`节点**：根据路由函数的返回值，执行`process\_even`节点，将`number`乘以2并更新`result`和`path`字段
5. **结束**：从`process\_even`节点连接到`END`节点，执行结束并返回最终状态### 对于奇数输入（例如5）：
1. **初始化**：`invoke()`方法接收初始状态`{"number": 5, "path": "", "result": ""}`
2. **执行`check\_number`节点**：从`START`开始，首先执行`check\_number`节点，返回原始状态
3. **执行路由函数**：调用`router`函数检查数字的奇偶性，返回"process\_odd"
4. **执行`process\_odd`节点**：根据路由函数的返回值，执行`process\_odd`节点，将`number`加1并更新`result`和`path`字段
5. **结束**：从`process\_odd`节点连接到`END`节点，执行结束并返回最终状态## 为什么使用条件边？条件边为StateGraph带来了以下优势：
1. **动态决策**：可以根据运行时的状态值动态选择执行路径
2. **逻辑分离**：将不同条件下的处理逻辑分离到不同的节点中
3. **可扩展性**：可以轻松添加新的条件分支，而不需要修改现有代码
4. **可视化**：条件分支逻辑可以通过图的可视化清晰地展示出来## 条件边的实际应用场景1. **智能对话系统**：根据用户的意图或问题类型选择不同的处理流程
2. **工作流引擎**：根据任务状态或条件选择下一步操作
3. **决策系统**：实现基于规则的决策逻辑
4. **数据处理管道**：根据数据特征选择不同的处理算法## 总结通过本文的学习，我们了解了LangGraph中条件边的概念、实现方式和应用场景。条件边是StateGraph中的一个强大特性，它允许我们根据状态的值动态地选择执行路径，从而构建具有决策能力的工作流。
这个示例展示了如何使用条件边实现基于数字奇偶性的简单路由，但条件边的应用远不止于此。在实际应用中，你可以根据业务需求实现更复杂的路由逻辑，构建更加智能和灵活的工作流系统。## 扩展阅读* [LangGraph官方文档 - 条件边]<web_link>
* [LangGraph GitHub仓库]<web_link>
* [LangChain官方文档]<web_link>
[
![avatar]<image_link>
在钱塘江]<web_link>
[
59
文章]<web_link>[
11k
阅读]<web_link>[
29
粉丝]<web_link>


---
*数据来源: Exa搜索 | 获取时间: 2026-02-20 20:40:44*