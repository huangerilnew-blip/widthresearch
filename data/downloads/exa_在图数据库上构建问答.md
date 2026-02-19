# 在图数据库上构建问答应用程序 | 🦜️🔗 LangChain 框架

**URL**:
https://python.langchain.ac.cn/docs/tutorials/graph

## 元数据
- 发布日期: 2025-02-01T00:00:00+00:00

## 完整内容
---
在图数据库上构建问答应用程序 | 🦜️🔗LangChain Python 教程[跳到主要内容] 
**我们的[使用 LangGraph 构建环境智能体] 课程现已在 LangChain Academy 上线！**
本页内容[![Open In Colab]] [![Open on GitHub]] 
# 构建基于图数据库的问答应用程序在本指南中，我们将介绍在图数据库上创建问答链的基本方法。这些系统将使我们能够针对图数据库中的数据提出问题并获得自然语言答案。首先，我们将展示一个简单的开箱即用选项，然后使用LangGraph 实现一个更复杂的版本。## ⚠️安全注意事项⚠️[​] 
构建图数据库问答系统需要执行模型生成的图查询。这样做存在固有风险。请确保您的数据库连接权限始终尽可能地限制在链/代理所需范围内。这将减轻但不能消除构建模型驱动系统的风险。有关一般安全最佳实践的更多信息，请[参阅此处] 。
## 架构[​] 
从高层次来看，大多数图链的步骤是：1. **将问题转换为图数据库查询**：模型将用户输入转换为图数据库查询（例如 Cypher）。
2. **执行图数据库查询**：执行图数据库查询。
3. **回答问题**：模型使用查询结果响应用户输入。
![sql_usecase.png] 
## 设置[​] 
首先，获取所需软件包并设置环境变量。在此示例中，我们将使用Neo4j 图数据库。```
`%pip install--upgrade--quiet langchain langchain-neo4j langchain-openai langgraph
`
```
本指南中我们默认使用OpenAI 模型。```
`importgetpass
importos
if"OPENAI\_API\_KEY"notinos.environ:
os.environ["OPENAI\_API\_KEY"]=getpass.getpass("Enter your OpenAI API key: ")
# Uncomment the below to use LangSmith. Not required.
# os.environ["LANGSMITH\_API\_KEY"] = getpass.getpass()
# os.environ["LANGSMITH\_TRACING"] = "true"
`
```
```
`Enter your OpenAI API key: ········`
```
接下来，我们需要定义Neo4j 凭据。按照[这些安装步骤] 设置 Neo4j 数据库。```
`os.environ["NEO4J\_URI"]="bolt://:7687"
os.environ["NEO4J\_USERNAME"]="neo4j"
os.environ["NEO4J\_PASSWORD"]="password"
`
```
以下示例将与Neo4j 数据库建立连接，并用有关电影及其演员的示例数据填充它。```
`fromlangchain\_neo4jimportNeo4jGraph
graph=Neo4jGraph()
# Import movie information
movies\_query="""
LOAD CSV WITH HEADERS FROM
'https://raw.githubusercontent.com/tomasonjo/blog-datasets/main/movies/movies\_small.csv'
AS row
MERGE (m:Movie {id:row.movieId})
SET m.released = date(row.released),
m.title = row.title,
m.imdbRating = toFloat(row.imdbRating)
FOREACH (director in split(row.director, '|') |
MERGE (p:Person {name:trim(director)})
MERGE (p)-[:DIRECTED]-&gt;(m))
FOREACH (actor in split(row.actors, '|') |
MERGE (p:Person {name:trim(actor)})
MERGE (p)-[:ACTED\_IN]-&gt;&gt;(m))
FOREACH (genre in split(row.genres, '|') |
MERGE (g:Genre {name:trim(genre)})
MERGE (m)-[:IN\_GENRE]-&gt;&gt;(g))
"""
graph.query(movies\_query)
`
```
**API 参考：**[Neo4jGraph] 
```
`[]
`
```
## 图模式[​] 
为了让大型语言模型（LLM）能够生成 Cypher 语句，它需要图模式信息。当您实例化图对象时，它会检索图模式信息。如果您稍后对图进行了任何更改，可以运行`refresh\_schema`方法来刷新模式信息。
```
`graph.refresh\_schema()
print(graph.schema)
`
```
```
`Node properties:
Person {name: STRING}
Movie {id: STRING, released: DATE, title: STRING, imdbRating: FLOAT}
Genre {name: STRING}
Chunk {id: STRING, embedding: LIST, text: STRING, question: STRING, query: STRING}
Relationship properties:
The relationships:
(:Person)-[:DIRECTED]-&gt;(:Movie)
(:Person)-[:ACTED\_IN]-&gt;&gt;(:Movie)
(:Movie)-[:IN\_GENRE]-&gt;&gt;(:Genre)
`
```
对于更复杂的模式信息，您可以使用`enhanced\_schema`选项。
```
`enhanced\_graph=Neo4jGraph(enhanced\_schema=True)
print(enhanced\_graph.schema)
`
```
```
`Received notification from DBMS server: {severity: WARNING} {code: Neo.ClientNotification.Statement.FeatureDeprecationWarning} {category: DEPRECATION} {title: This feature is deprecated and will be removed in future versions.} {description: The procedure has a deprecated field. ('config' used by 'apoc.meta.graphSample' is deprecated.)} {position: line: 1, column: 1, offset: 0} for query: "CALL apoc.meta.graphSample() YIELD nodes, relationships RETURN nodes, [rel in relationships | {name:apoc.any.property(rel, 'type'), count: apoc.any.property(rel, 'count')}] AS relationships"
``````output
Node properties:
- \*\*Person\*\*
- `name`: STRING Example: "John Lasseter"
- \*\*Movie\*\*
- `id`: STRING Example: "1"
- `released`: DATE Min: 1964-12-16, Max: 1996-09-15
- `title`: STRING Example: "Toy Story"
- `imdbRating`: FLOAT Min: 2.4, Max: 9.3
- \*\*Genre\*\*
- `name`: STRING Example: "Adventure"
- \*\*Chunk\*\*
- `id`: STRING Available options: ['d66006059fd78d63f3df90cc1059639a', '0e3dcb4502853979d12357690a95ec17', 'c438c6bcdcf8e4fab227f29f8e7ff204', '97fe701ec38057594464beaa2df0710e', 'b54f9286e684373498c4504b4edd9910', '5b50a72c3a4954b0ff7a0421be4f99b9', 'fb28d41771e717255f0d8f6c799ede32', '58e6f14dd2e6c6702cf333f2335c499c']
- `text`: STRING Available options: ['How many artists are there?', 'Which actors played in the movie Casino?', 'How many movies has Tom Hanks acted in?', "List all the genres of the movie Schindler's List", 'Which actors have worked in movies from both the c', 'Which directors have made movies with at least thr', 'Identify movies where directors also played a role', 'Find the actor with the highest number of movies i']
- `question`: STRING Available options: ['How many artists are there?', 'Which actors played in the movie Casino?', 'How many movies has Tom Hanks acted in?', "List all the genres of the movie Schindler's List", 'Which actors have worked in movies from both the c', 'Which directors have made movies with at least thr', 'Identify movies where directors also played a role', 'Find the actor with the highest number of movies i']
- `query`: STRING Available options: ['MATCH (a:Person)-[:ACTED\_IN]-&gt;&gt;(:Movie) RETURN coun', "MATCH (m:Movie {title: 'Casino'})&lt;&lt;-[:ACTED\_IN]-(a)", "MATCH (a:Person {name: 'Tom Hanks'})-[:ACTED\_IN]-&gt;&gt;", "MATCH (m:Movie {title: 'Schindler's List'})-[:IN\_G", 'MATCH (a:Person)-[:ACTED\_IN]-&gt;&gt;(:Movie)-[:IN\_GENRE]', 'MATCH (d:Person)-[:DIRECTED]-&gt;&gt;(m:Movie)&lt;&lt;-[:ACTED\_I', 'MATCH (p:Person)-[:DIRECTED]-&gt;&gt;(m:Movie), (p)-[:ACT', 'MATCH (a:Actor)-[:ACTED\_IN]-&gt;&gt;(m:Movie) RETURN a.na']
Relationship properties:
The relationships:
(:Person)-[:DIRECTED]-&gt;(:Movie)
(:Person)-[:ACTED\_IN]-&gt;&gt;(:Movie)
(:Movie)-[:IN\_GENRE]-&gt;&gt;(:Genre)
`
```
`enhanced\_schema`选项通过包含浮点数和日期的最小值和最大值，以及字符串属性的示例值等详细信息，丰富了属性信息。这种额外的上下文有助于引导 LLM 生成更准确和有效的查询。太棒了！我们已经有了一个可以查询的图数据库。现在让我们尝试将其连接到LLM。
## GraphQACypherChain[​] 
让我们使用一个简单的开箱即用链，它接收一个问题，将其转换为Cypher 查询，执行查询，并使用结果回答原始问题。![graph_chain.webp] 
LangChain 提供了一个内置链，用于此工作流，专门为Neo4j 设计：[GraphCypherQAChain] 
```
`fromlangchain\_neo4jimportGraphCypherQAChain
fromlangchain\_openaiimportChatOpenAI
llm=ChatOpenAI(model="gpt-4o",temperature=0)
chain=GraphCypherQAChain.from\_llm(
graph=enhanced\_graph,llm=llm,verbose=True,allow\_dangerous\_requests=True
)
response=chain.invoke({"query":"What was the cast of the Casino?"})
response
`
```
**API 参考：**[GraphCypherQAChain] |[ChatOpenAI] 
```
`
[1m&gt; Entering new GraphCypherQAChain chain...[0m
Generated Cypher:
[32;1m[1;3mcypher
MATCH (p:Person)-[:ACTED\_IN]-&gt;&gt;(m:Movie {title: "Casino"})
RETURN p.name
[0m
Full Context:
[32;1m[1;3m[{'p.name': 'Robert De Niro'}, {'p.name': 'Joe Pesci'}, {'p.name': 'Sharon Stone'}, {'p.name': 'James Woods'}][0m
[1m&gt; Finished chain.[0m
`
```
```
`{'query': 'What was the cast of the Casino?',
'result': 'Robert De Niro, Joe Pesci, Sharon Stone, and James Woods were the cast of Casino.'}
`
```
## 使用LangGraph 进行高级实现[​] 
虽然GraphCypherQAChain 对于快速演示是有效的，但在生产环境中可能会面临挑战。过渡到LangGraph 可以增强工作流，但在生产中实现自然语言到查询的流程仍然是一项复杂的任务。尽管如此，仍有几种策略可以显著提高准确性和可靠性，我们将在接下来进行探讨。这是我们将要实现的LangGraph 可视化流程：![langgraph_text2cypher] 
我们将从定义LangGraph 应用程序的输入、输出和总体状态开始。```
`fromoperatorimportadd
fromtypingimportAnnotated,List
fromtyping\_extensionsimportTypedDict
classInputState(TypedDict):
question:str
classOverallState(TypedDict):
question:str
next\_action:str
cypher\_statement:str
cypher\_errors:List[str]
database\_records:List[dict]
steps:Annotated[List[str],add]
classOutputState(TypedDict):
answer:str
steps:List[str]
cypher\_statement:str
`
```
第一步是一个简单的`guardrails`步骤，我们在此验证问题是否与电影或其演员有关。如果不相关，我们会通知用户我们无法回答任何其他问题。否则，我们将进入 Cypher 生成步骤。```
`fromtypingimportLiteral
fromlangchain\_core.promptsimportChatPromptTemplate
frompydanticimportBaseModel,Field
guardrails\_system="""
As an intelligent assistant, your primary objective is to decide whether a given question is related to movies or not.
If the question is related to movies, output "movie". Otherwise, output "end".
To make this decision, assess the content of the question and determine if it refers to any movie, actor, director, film industry,
or related topics. Provide only the specified output: "movie" or "end".
"""
guardrails\_prompt=ChatPromptTemplate.from\_messages(
[
(
"system",
guardrails\_system,
),
(
"human",
("{question}"),
),
]
)
classGuardrailsOutput(BaseModel):
decision:Literal["movie","end"]=Field(
description="Decision on whether the question is related to movies"
)
guardrails\_chain=guardrails\_prompt|llm.with\_structured\_output(GuardrailsOutput)
defguardrails(state:InputState)-&gt;OverallState:
"""
Decides if the question is related to movies or not.
"""
guardrails\_output=guardrails\_chain.invoke({"question":state.get("question")})
database\_records=None
ifguardrails\_output.decision=="end":
database\_records="This questions is not about movies or their cast. Therefore I cannot answer this question."
return{
"next\_action":guardrails\_output.decision,
"database\_records":database\_records,
"steps":["guardrail"],
}
`
```
**API 参考：**[ChatPromptTemplate] 
### 少样本提示[​] 
将自然语言转换为准确的查询是一项挑战。一种增强此过程的方法是提供相关的少样本示例，以指导大型语言模型（LLM）进行查询生成。为了实现这一点，我们将使用`SemanticSimilarityExampleSelector`动态选择最相关的示例。
```
`fromlangchain\_core.example\_selectorsimportSemanticSimilarityExampleSelector
fromlangchain\_neo4jimportNeo4jVector
fromlangchain\_openaiimportOpenAIEmbeddings
examples=[
{
"question":"How many artists are there?",
"query":"MATCH (a:Person)-[:ACTED\_IN]-&gt;&gt;(:Movie) RETURN count(DISTINCT a)",
},
{
"question":"Which actors played in the movie Casino?",
"query":"MATCH (m:Movie {title: 'Casino'})&lt;&lt;-[:ACTED\_IN]-(a) RETURN a.name",
},
{
"question":"How many movies has Tom Hanks acted in?",
"query":"MATCH (a:Person {name: 'Tom Hanks'})-[:ACTED\_IN]-&gt;&gt;(m:Movie) RETURN count(m)",
},
{
"question":"List all the genres of the movie Schindler's List",
"query":"MATCH (m:Movie {title: 'Schindler's List'})-[:IN\_GENRE]-&gt;&gt;(g:Genre) RETURN g.name",
},
{
"question":"


---
*数据来源: Exa搜索 | 获取时间: 2026-02-19 20:54:46*