# Conditional Workflow in LangGraph: A Complete Developer Guide | by Akash Shinde | Jan, 2026 | Medium

**URL**:
https://medium.com/%40shindeakash412/conditional-workflow-in-langgraph-a-complete-developer-guide-5483f05c221e

## 元数据
- 发布日期: 2026-01-25T00:00:00+00:00

## 完整内容
---
Conditional Workflow in LangGraph: A Complete Developer Guide | by Akash Shinde | Jan, 2026 | Medium
[Sitemap] 
[Open in app] 
Sign up
[Sign in] 
[Medium Logo] 
[
Write
] 
[
Search
] 
Sign up
[Sign in] 
![] 
# Conditional Workflow in LangGraph: A Complete Developer Guide
[
![Akash Shinde] 
] 
[Akash Shinde] 
5 min read
·Jan 25, 2026
[
] 
--
[] 
Listen
Share
Building intelligent AI agents requires more than just a linear “input-to-output” chain. To create truly autonomous systems, you need a way for the workflow to make decisions, handle errors, and route queries dynamically.
In**LangGraph**, this is achieved through**Conditional Edges**. Unlike standard edges in[**Sequential workflow**] **(we learned in our previous blog)**that connect**Node A**to**Node B**directly, conditional edges act as the “brain” of your graph, deciding which path to take at runtime based on the current state.
## What Is a Conditional Workflow in LangGraph?
> A **> conditional workflow
**> is a workflow where the next step is chosen **> based on a condition or decision
**> .
Press enter or click to view image in full size
![] 
## Components :
There are three components which required to build a conditional workflow.
1. **Nodes**: Python functions that perform tasks (e.g., calling an LLM or a tool).
2. **State**: A shared memory object (usually a`TypedDict`) that stores the data flowing through the graph.
3. **The Routing Function**: A function that inspects the state or check the condition and returns a string representing the next node to visit.### How Conditional Workflows Differ from Sequential Ones
**Sequential Workflow**
```
START →Step A →Step B →END
```
**Conditional Workflow**
```
┌─→Step A
START →Router ┤└─→Step B
↓END
```
## Examples
### 1. Let’s look at our first example of a Conditional workflow without using LLM.
We will be checking a simple loan status on the basis of the salary of the loan applicant.
***If the loan applicant’s salary is less than 25k then loan status should be “rejected”. If the salary is greater than 25k and less than 50k then it should be “Manual review required” and if the salary is more than 50k then status should be “approved”.***
```
from langgraph.graph import StateGraph, START, END
from typing import TypedDict
class LoanState(TypedDict):
salary: int
decision: str
def evaluate\_loan\_requirement(state: LoanState):
print(&quot;Evaluating requirement.....&quot;)
salary = state[&#x27;salary&#x27;]
return {&#x27;salary&#x27;: salary}
def check\_loan\_decision(state: LoanState):
print(&#x27;salary&#x27;, state[&#x27;salary&#x27;])
salary = state[&#x27;salary&#x27;]
if salary &lt; 25000:
return &quot;reject&quot;
elif salary &lt; 50000:
return &quot;review&quot;
else:
return &quot;approve&quot;
def approve\_loan(state: LoanState):
return {&quot;decision&quot;: &quot;Loan approved&quot;}
def review\_loan(state: LoanState):
return {&quot;decision&quot;: &quot;Manual Review Required&quot;}
def reject\_loan(state: LoanState):
return {&quot;decision&quot;: &quot;Loan Rejected&quot;}
graph = StateGraph(LoanState)
graph.add\_node(&#x27;&#x27;evaluate\_loan\_requirement&#x27;&#x27;,evaluate\_loan\_requirement),
graph.add\_node(&#x27;&#x27;approve&#x27;&#x27;, approve\_loan)
graph.add\_node(&#x27;&#x27;review&#x27;&#x27;, review\_loan)
graph.add\_node(&#x27;&#x27;reject&#x27;&#x27;, reject\_loan)
graph.add\_edge(START, &#x27;&#x27;evaluate\_loan\_requirement&#x27;&#x27;)
graph.add\_conditional\_edges(
&#x27;&#x27;evaluate\_loan\_requirement&#x27;&#x27;,
check\_loan\_decision,
{
&#x27;approve&#x27;: &#x27;approve&#x27;,
&#x27;review&#x27;: &#x27;review&#x27;,
&#x27;reject&#x27;: &#x27;reject&#x27;
}
)
graph.add\_edge(&#x27;&#x27;approve&#x27;&#x27;, END)
graph.add\_edge(&#x27;&#x27;review&#x27;&#x27;, END)
graph.add\_edge(&#x27;&#x27;reject&#x27;&#x27;, END)
workflow = graph.compile()
workflow
initial\_state = {&#x27;&#x27;salary&#x27;&#x27;: 49000}
result = workflow.invoke(initial\_state)
print(result)
```
**Output:**
Press enter or click to view image in full size
![] 
**Workflow:**
![] 
### 2. Let’s look at the second example of a conditional workflow with using LLM.
Let’s assume you have a product that is featured online. Users are writing feedback to the product. Our workflow will check the sentiment of the user’s feedback. If the feedback is ‘**positive**’ then workflow will end and if the feedback is**‘negative’,**we will run the diagnosis on the review and check the**tone**,**type**of the issue and**urgency**of the issue.
```
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal
from langchain\_groq import ChatGroq
from dotenv import load\_dotenv
from pydantic import BaseModel, Field
import os
load\_dotenv()
model = ChatGroq(api\_key=os.getenv(&quot;&quot;GROQ\_API\_KEY&quot;&quot;), model=&quot;&quot;qwen/qwen3-32b&quot;&quot;, temperature=0)
class SentimentSchema(BaseModel):
sentiment: Literal[&quot;positive&quot;, &quot;negative&quot;] = Field(description=&quot;sentiment of the review&quot;)
class DiagnosisSchema(BaseModel):
issue\_type: Literal[&quot;&quot;UX&quot;&quot;, &quot;&quot;Performance&quot;&quot;, &quot;&quot;Bug&quot;&quot;, &quot;&quot;Support&quot;&quot;, &quot;&quot;Other&quot;&quot;] = Field(description=&#x27;&#x27;The category of issue mentioned in the review&#x27;&#x27;)
tone: Literal[&quot;angry&quot;, &quot;frustrated&quot;, &quot;disappointed&quot;, &quot;calm&quot;] = Field(description=&#x27;The emotional tone expressed by the user&#x27;)
urgency: Literal[&quot;low&quot;, &quot;medium&quot;, &quot;high&quot;] = Field(description=&#x27;How urgent or critical the issue appears to be&#x27;)
structured\_model = model.with\_structured\_output(SentimentSchema)
dignosisStructured\_model = model.with\_structured\_output(DiagnosisSchema)
class ReviewState(TypedDict):
review: str
sentiment: Literal[&quot;positive&quot;, &quot;negative&quot;]
diagnosis: dict
response: str
def find\_sentiment(state: ReviewState):
review = state[&#x27;review&#x27;]
prompt = f&quot;&quot;For the following review find out the sentiment \\n {review}&quot;&quot;
sentiment = structured\_model.invoke(prompt).sentiment
return {&#x27;sentiment&#x27;: sentiment}
def check\_sentiment(state: ReviewState) -&gt;&gt; Literal[&quot;&quot;positive\_response&quot;&quot;, &quot;&quot;run\_diagnosis&quot;&quot;]:
sentiment = state[&#x27;sentiment&#x27;]
if sentiment == &#x27;positive&#x27;:
return &quot;&quot;positive\_response&quot;&quot;
else:
return &quot;&quot;run\_diagnosis&quot;&quot;
def positive\_response(state: ReviewState):
review = state[&#x27;review&#x27;]
prompt = f&quot;&quot;&quot;&quot;&quot;&quot;Write a warm thank you message in response to this review: \\n\\n &quot;&quot;{review}\\&quot;&quot;\\n
Also, Kindly ask the user to the leave the feedback on the website.
&quot;&quot;&quot;
response = model.invoke(prompt).content
return {&quot;response&quot;: response}
def run\_diagnosis(state: ReviewState):
review = state[&#x27;review&#x27;]
prompt = f&quot;&quot;&quot;&quot;&quot;&quot;Diagnose this negative review:\\n\\n{review}\\n&quot;&quot;
&quot;&quot;Return issue\_type, tone, and urgency. &quot;&quot;&quot;&quot;&quot;&quot;
response = dignosisStructured\_model.invoke(prompt)
return {&quot;&quot;diagnosis&quot;&quot;: response.model\_dump()}
def negative\_response(state: ReviewState):
diagnosis = state[&#x27;diagnosis&#x27;]
prompt = f&quot;&quot;&quot;You are a support assistant.
The user had a &#x27;&#x27;{diagnosis[&#x27;&#x27;issue\_type&#x27;&#x27;]}&#x27;&#x27; issue, sounded &#x27;&#x27;{diagnosis[&#x27;&#x27;tone&#x27;&#x27;]}&#x27;&#x27;, and marked urgency as &#x27;&#x27;{diagnosis[&#x27;&#x27;urgency&#x27;&#x27;]}&#x27;&#x27;.
Write an empathetic, helpful resolution message.
&quot;&quot;&quot;
response = model.invoke(prompt).content
return {&quot;response&quot;: response}
graph = StateGraph(ReviewState)
graph.add\_node(&#x27;&#x27;find\_sentiment&#x27;&#x27;, find\_sentiment)
graph.add\_node(&#x27;&#x27;positive\_response&#x27;&#x27;, positive\_response)
graph.add\_node(&#x27;&#x27;run\_diagnosis&#x27;&#x27;, run\_diagnosis)
graph.add\_node(&#x27;&#x27;negative\_response&#x27;&#x27;, negative\_response)
graph.add\_edge(START, &#x27;&#x27;find\_sentiment&#x27;&#x27;)
graph.add\_conditional\_edges(&#x27;&#x27;find\_sentiment&#x27;&#x27;, check\_sentiment)
graph.add\_edge(&#x27;&#x27;positive\_response&#x27;&#x27;, END)
graph.add\_edge(&#x27;&#x27;run\_diagnosis&#x27;&#x27;, &#x27;&#x27;negative\_response&#x27;&#x27;)
graph.add\_edge(&#x27;&#x27;negative\_response&#x27;&#x27;, END)
workflow = graph.compile()
intial\_state={
&#x27;review&#x27;: &quot;The product is not good at all&quot;
}
workflow.invoke(intial\_state)
```
**Output:**
Press enter or click to view image in full size
![] 
**Workflow:**
![] 
**Note: In standard LLM calls, you get back a string of text. For a workflow to make decisions (like routing to a “Negative” or “Positive” path), the code needs data it can rely on.**
**Usage of Schema**: It transforms unstructured human language into structured machine data.
`*DiagnosisSchema*`*or*`*SentimentSchema*`*ensures the LLM doesn&#x27;t just &quot;talk&quot; about the problem, but extracts specific metadata (*`*issue\_type*`*,*`*tone*`*,*`*urgency*`*) or (*`*positive*`*,*`*negative*`*) that the system can actually use in downstream logic.*
**Usage of model.with\_structured\_output :**This tells the LLM, “You must respond**only**in this exact structure.”
The line`model.with\_structured\_output(SentimentSchema)`is where the magic happens. This forces the LLM to skip the long text answers and return a Python object. eg: {“sentiment”: “positive”}
## 💡Why This Matters for Agentic AI
### Conditional workflows are essential when:
* **Different inputs need different handling:**Conditional


---
*数据来源: Exa搜索 | 获取时间: 2026-02-21 19:57:01*