# 如何创建用于并行节点执行的分支 - LangChain 框架

**URL**:
https://github.langchain.ac.cn/langgraphjs/how-tos/branching

## 元数据
- 发布日期: 2025-02-01T00:00:00+00:00

## 完整内容
---
如何创建用于并行节点执行的分支 - LangChain 教程[跳到内容] 
**我们的[使用LangGraph构建环境智能体] 课程现已在LangChain Academy上线！**
# 如何创建用于并行节点执行的分支[¶] 
LangGraph 原生支持使用常规边或[条件边 (conditionalEdges)] 进行扇出和扇入。
这使您能够并行运行节点，以加快整个图的执行速度。下面是一些示例，展示了如何创建适合您的分支数据流。## 设置[¶] 
首先，安装LangGraph.js
```
`[]<web_link>yarnadd@langchain/langgraph@langchain/core`
```
本指南将使用OpenAI 的GPT-4o 模型。我们可以选择设置用于[LangSmith 追踪] 的 API 密钥，这将为我们提供一流的可观察性。```
`[] // process.env.OPENAI\_API\_KEY = "sk\_...";[] [] // Optional, add tracing in LangSmith[] // process.env.LANGCHAIN\_API\_KEY = "ls\_\_..."[] // process.env.LANGCHAIN\_CALLBACKS\_BACKGROUND = "true";[] process.env.LANGCHAIN\_CALLBACKS\_BACKGROUND="true";[] process.env.LANGCHAIN\_TRACING\_V2="true";[] process.env.LANGCHAIN\_PROJECT="Branching: LangGraphJS";`
```
```
`[] Branching: LangGraphJS`
```
## 扇出、扇入[¶]<web_link>
首先，我们将创建一个简单的图，它会向外分支并再合并回来。当合并回来时，所有分支的状态更新都将通过您的**归约器 (reducer)**（下面的 `aggregate` 方法）应用。```
`[]<web_link>import{END,START,StateGraph,Annotation}from"@langchain/langgraph";[]<web_link>[]<web_link>constStateAnnotation=Annotation.Root({[]<web_link>aggregate:Annotation&lt;string[]&gt;({[]<web_link>reducer:(x,y)=&gt;x.concat(y),[]<web_link>})[]<web_link>});[]<web_link>[]<web_link>// Create the graph[]<web_link>constnodeA=(state:typeofStateAnnotation.State)=&gt;{[]<web_link>console.log(`Adding I'm A to${state.aggregate}`);[]<web_link>return{aggregate:[`I'm A`]};[]<web_link>};[]<web_link>constnodeB=(state:typeofStateAnnotation.State)=&gt;{[]<web_link>console.log(`Adding I'm B to${state.aggregate}`);[]<web_link>return{aggregate:[`I'm B`]};[]<web_link>};[]<web_link>constnodeC=(state:typeofStateAnnotation.State)=&gt;{[]<web_link>console.log(`Adding I'm C to${state.aggregate}`);[]<web_link>return{aggregate:[`I'm C`]};[]<web_link>};[]<web_link>constnodeD=(state:typeofStateAnnotation.State)=&gt;{[]<web_link>console.log(`Adding I'm D to${state.aggregate}`);[]<web_link>return{aggregate:[`I'm D`]};[]<web_link>};[]<web_link>[]<web_link>constbuilder=newStateGraph(StateAnnotation)[]<web_link>.addNode("a",nodeA)[]<web_link>.addEdge(START,"a")[]<web_link>.addNode("b",nodeB)[]<web_link>.addNode("c",nodeC)[]<web_link>.addNode("d",nodeD)[]<web_link>.addEdge("a","b")[]<web_link>.addEdge("a","c")[]<web_link>.addEdge("b","d")[]<web_link>.addEdge("c","d")[]<web_link>.addEdge("d",END);[]<web_link>[]<web_link>constgraph=builder.compile();`
```
```
`[]<web_link>import\*astslabfrom"tslab";[]<web_link>[]<web_link>constrepresentation=graph.getGraph();[]<web_link>constimage=awaitrepresentation.drawMermaidPng();[]<web_link>constarrayBuffer=awaitimage.arrayBuffer();[]<web_link>[]<web_link>awaittslab.display.png(newUint8Array(arrayBuffer));`
```
```
`[]<web_link>// Invoke the graph[]<web_link>constbaseResult=awaitgraph.invoke({aggregate:[]});[]<web_link>console.log("Base Result: ",baseResult);`
```
```
`[]<web_link>Adding I'm A to[]<web_link>Adding I'm B to I'm A[]<web_link>Adding I'm C to I'm A[]<web_link>Adding I'm D to I'm A,I'm B,I'm C[]<web_link>Base Result: { aggregate: [ "I'm A", "I'm B", "I'm C", "I'm D" ] }`
```
## 条件分支[¶] 
如果您的扇出不是确定性的，您可以直接使用[addConditionalEdges] ，如下所示
```
`[]<web_link>constConditionalBranchingAnnotation=Annotation.Root({[]<web_link>aggregate:Annotation&lt;string[]&gt;({[]<web_link>reducer:(x,y)=&gt;x.concat(y),[]<web_link>}),[]<web_link>which:Annotation&lt;string&gt;({[]<web_link>reducer:(x:string,y:string)=&gt;(y??x),[]<web_link>})[]<web_link>})[]<web_link>[]<web_link>// Create the graph[]<web_link>constnodeA2=(state:typeofConditionalBranchingAnnotation.State)=&gt;{[]<web_link>console.log(`Adding I'm A to${state.aggregate}`);[]<web_link>return{aggregate:[`I'm A`]};[]<web_link>};[]<web_link>constnodeB2=(state:typeofConditionalBranchingAnnotation.State)=&gt;{[]<web_link>console.log(`Adding I'm B to${state.aggregate}`);[]<web_link>return{aggregate:[`I'm B`]};[]<web_link>};[]<web_link>constnodeC2=(state:typeofConditionalBranchingAnnotation.State)=&gt;{[]<web_link>console.log(`Adding I'm C to${state.aggregate}`);[]<web_link>return{aggregate:[`I'm C`]};[]<web_link>};[]<web_link>constnodeD2=(state:typeofConditionalBranchingAnnotation.State)=&gt;{[]<web_link>console.log(`Adding I'm D to${state.aggregate}`);[]<web_link>return{aggregate:[`I'm D`]};[]<web_link>};[]<web_link>constnodeE2=(state:typeofConditionalBranchingAnnotation.State)=&gt;{[]<web_link>console.log(`Adding I'm E to${state.aggregate}`);[]<web_link>return{aggregate:[`I'm E`]};[]<web_link>};[]<web_link>[]<web_link>// Define the route function[]<web_link>functionrouteCDorBC(state:typeofConditionalBranchingAnnotation.State):string[]{[]<web_link>if(state.which==="cd"){[]<web_link>return["c","d"];[]<web_link>}[]<web_link>return["b","c"];[]<web_link>}[]<web_link>[]<web_link>constbuilder2=newStateGraph(ConditionalBranchingAnnotation)[]<web_link>.addNode("a",nodeA2)[]<web_link>.addEdge(START,"a")[]<web_link>.addNode("b",nodeB2)[]<web_link>.addNode("c",nodeC2)[]<web_link>.addNode("d",nodeD2)[]<web_link>.addNode("e",nodeE2)[]<web_link>// Add conditional edges[]<web_link>// Third parameter is to support visualizing the graph[]<web_link>.addConditionalEdges("a",routeCDorBC,["b","c","d"])[]<web_link>.addEdge("b","e")[]<web_link>.addEdge("c","e")[]<web_link>.addEdge("d","e")[]<web_link>.addEdge("e",END);[]<web_link>[]<web_link>constgraph2=builder2.compile();`
```
```
`[]<web_link>import\*astslabfrom"tslab";[]<web_link>[]<web_link>constrepresentation2=graph2.getGraph();[]<web_link>constimage2=awaitrepresentation2.drawMermaidPng();[]<web_link>constarrayBuffer2=awaitimage2.arrayBuffer();[]<web_link>[]<web_link>awaittslab.display.png(newUint8Array(arrayBuffer2));`
```
```
`[]<web_link>// Invoke the graph[]<web_link>letg2result=awaitgraph2.invoke({aggregate:[],which:"bc"});[]<web_link>console.log("Result 1: ",g2result);`
```
```
`[]<web_link>Adding I'm A to[]<web_link>Adding I'm B to I'm A[]<web_link>Adding I'm C to I'm A[]<web_link>Adding I'm E to I'm A,I'm B,I'm C[]<web_link>Result 1: { aggregate: [ "I'm A", "I'm B", "I'm C", "I'm E" ], which: 'bc' }`
```
```
`[]<web_link>g2result=awaitgraph2.invoke({aggregate:[],which:"cd"});[]<web_link>console.log("Result 2: ",g2result);`
```
```
`[]<web_link>Adding I'm A to[]<web_link>Adding I'm C to I'm A[]<web_link>Adding I'm D to I'm A[]<web_link>Adding I'm E to I'm A,I'm C,I'm D[]<web_link>``````output[]<web_link>Result 2: { aggregate: [ "I'm A", "I'm C", "I'm D", "I'm E" ], which: 'cd' }`
```
## 稳定排序[¶] 
当扇出时，节点将作为单个“超步”并行运行。一旦超步完成，每个超步的更新将按顺序应用于状态。如果您需要从并行超步中获得一致的、预定的更新顺序，您应该将输出（以及识别键）写入状态中的一个单独字段，然后通过从每个扇出节点到汇合点添加常规的`edge`，在“汇集”节点中组合它们。
例如，假设我想按“可靠性”对并行步骤的输出进行排序。```
`[] typeScoredValue={[] value:string;[] score:number;[]};[] [] constreduceFanouts=(left?:ScoredValue[],right?:ScoredValue[])=&gt;{[] if(!left){[] left=[];[]}[] if(!right||right?.length===0){[] // Overwrite. Similar to redux.[] return[];[]}[] returnleft.concat(right);[]};[] [] constStableSortingAnnotation=Annotation.Root({[] aggregate:Annotation&lt;string[]&gt;({[] reducer:(x,y)=&gt;x.concat(y),[]}),[] which:Annotation&lt;string&gt;({[] reducer:(x:string,y:string)=&gt;(y??x),[]}),[] fanoutValues:Annotation&lt;ScoredValue[]&gt;({[] reducer:reduceFanouts,[]}),[]})[] [] [] classParallelReturnNodeValue{[] private\_value:string;[] private\_score:number;[] [] constructor(nodeSecret:string,score:number){[] this.\_value=nodeSecret;[] this.\_score=score;[]}[] [] publiccall(state:typeofStableSortingAnnotation.State){[] console.log(`Adding${this.\_value}to${state.aggregate}`);[] return{fanoutValues:[{value:this.\_value,score:this.\_score}]};[]}[]}[] [] // Create the graph[] [] constnodeA3=(state:typeofStableSortingAnnotation.State)=&gt;{[] console.log(`Adding I'm A to${state.aggregate}`);[] return{aggregate:["I'm A"]};[]};[] [] constnodeB3=newParallelReturnNodeValue("I'm B",0.1);[] constnodeC3=newParallelReturnNodeValue("I'm C",0.9);[] constnodeD3=newParallelReturnNodeValue("I'm D",0.3);[] [] constaggregateFanouts=(state:typeofStableSortingAnnotation.State)=&gt;{[] // Sort by score (reversed)[] state.fanoutValues.sort((a,b)=&gt;b.score-a.score);[] return{[] aggregate:state.fanoutValues.map((v)=&gt;v.value).concat(["I'm E"]),[] fanoutValues:[],[]};[]};[] [] // Define the route function[] functionrouteBCOrCD(state:typeofStableSortingAnnotation.State):string[]{[] if(state.which==="cd"){[] return["c","d"];[]}[] return["b","c"];[]}[] [] constbuilder3=newStateGraph(StableSortingAnnotation)[].addNode("a",nodeA3)[].addEdge(START,"a")[].addNode("b",nodeB3.call.bind(nodeB3))[].addNode("c",nodeC3.call.bind(nodeC3))[].addNode("d",nodeD3.call.bind(nodeD3))[].addNode("e",aggregateFanouts)[].addConditionalEdges("a",routeBCOrCD,["b","c","d"])[].addEdge("b","e")[].addEdge("c","e")[].addEdge("d","e")[].addEdge("e",END);[] [] constgraph3=builder3.compile();[] [] // Invoke the graph[] letg3result=awaitgraph3.invoke({aggregate:[],which:"bc"});[] console.log("Result 1: ",g3result);`
```
```
`[] Adding I'm A to[] Adding I'm B to I'm A[] Adding I'm C to I'm A[] Result 1: {[] aggregate: [ "


---
*数据来源: Exa搜索 | 获取时间: 2026-02-19 20:08:35*