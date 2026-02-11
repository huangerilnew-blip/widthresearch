# 记忆- LangChain 教程

**URL**:
https://github.langchain.ac.cn/langgraphjs/concepts/memory/

## 元数据
- 发布日期: 2026-02-10T21:58:14.085123

## 完整内容
---
记忆 - LangChain 教程[跳到内容] 
**我们的[使用LangGraph构建环境智能体] 课程现已在LangChain Academy上线！**
# 内存[¶] 
## 什么是记忆？[¶] 
AI 应用中的记忆指处理、存储和有效回忆过往交互信息的能力。有了记忆，您的智能体可以从反馈中学习并适应用户的偏好。本指南根据记忆召回的范围分为两个部分：短期记忆和长期记忆。**短期记忆**，或[线程] 范围的记忆，可以随时在与用户的单个对话线程**内**被召回。LangGraph 将短期记忆作为智能体[状态] 的一部分进行管理。状态使用[检查点] 持久化到数据库中，以便线程可以随时恢复。当图被调用或步骤完成时，短期记忆会更新，并且在每个步骤开始时读取状态。
**长期记忆**在对话线程**之间**共享。它可以\*随时\*且在**任何线程**中被召回。记忆可以限定在任何自定义命名空间内，而不仅仅是单个线程ID。LangGraph 提供[存储] （[参考文档] ）来让您保存和召回长期记忆。
理解并在您的应用程序中实现这两种记忆都非常重要。![] 
## 短期记忆[¶] 
短期记忆让您的应用程序能够记住单个[线程] 或对话中的先前交互。[线程] 在一个会话中组织多个交互，类似于电子邮件将消息分组到单个对话中的方式。
LangGraph 将短期记忆作为智能体状态的一部分进行管理，通过线程范围的检查点进行持久化。此状态通常可以包括对话历史以及其他有状态数据，例如上传的文件、检索到的文档或生成的工件。通过将这些存储在图的状态中，机器人可以访问给定对话的完整上下文，同时保持不同线程之间的分离。由于对话历史是表示短期记忆最常见的形式，因此在下一节中，我们将介绍当消息列表变得**冗长**时管理对话历史的技术。如果您想坚持高层概念，请继续阅读[长期记忆] 部分。
### 管理长对话历史[¶] 
长对话对当今的LLM 构成了挑战。完整的历史记录甚至可能无法完全适应LLM 的上下文窗口，从而导致不可恢复的错误。即使您的LLM 在技术上支持完整的上下文长度，大多数LLM 在长上下文中表现仍然不佳。它们会被陈旧或偏离主题的内容“分散注意力”，同时响应时间更慢且成本更高。管理短期记忆是平衡[准确率和召回率] 与您应用程序的其他性能要求（延迟和成本）的实践。一如既往，批判性地思考如何为您的 LLM 表示信息并查看您的数据非常重要。我们在下面介绍了几种管理消息列表的常见技术，并希望为您提供足够的上下文，以便您为应用程序选择最佳权衡方案。* [编辑消息列表] ：如何考虑在将消息列表传递给语言模型之前对其进行修剪和过滤。
* [总结过往对话] ：当您不仅仅想过滤消息列表时，一种常用的技术。### 编辑消息列表[¶] 
聊天模型使用[消息] 接受上下文，其中包括开发者提供的指令（系统消息）和用户输入（人类消息）。在聊天应用程序中，消息在人类输入和模型响应之间交替，导致消息列表随时间增长。由于上下文窗口有限且富含 token 的消息列表可能成本高昂，许多应用程序可以受益于使用手动删除或遗忘陈旧信息的技术。![] 
最直接的方法是从列表中删除旧消息（类似于[最近最少使用缓存] ）。
在LangGraph 中从列表中删除内容的典型技术是，从节点返回一个更新，告诉系统删除列表的某个部分。您可以定义此更新的外观，但一种常见的方法是让您返回一个对象或字典，指定要保留哪些值。```
`[] import{Annotation}from"@langchain/langgraph";[] [] constStateAnnotation=Annotation.Root({[] myList:Annotation&lt;any[]&gt;({[] reducer:([] existing:string[],[] updates:string[]|{type:string;from:number;to?:number}[])=&gt;{[] if(Array.isArray(updates)){[] // Normal case, add to the history[] return[...existing,...updates];[]}elseif(typeofupdates==="object"&amp;&amp;updates.type==="keep"){[] // You get to decide what this looks like.[] // For example, you could simplify and just accept a string "DELETE"[] // and clear the entire list.[] returnexisting.slice(updates.from,updates.to);[]}[] // etc. We define how to interpret updates[] returnexisting;[]},[] default:()=&gt;[],[]}),[]});[] [] typeState=typeofStateAnnotation.State;[] [] functionmyNode(state:State){[] return{[] // We return an update for the field "myList" saying to[] // keep only values from index -5 to the end (deleting the rest)[] myList:{type:"keep",from:-5,to:undefined},[]};[]}`
```
当在键“myList”下返回更新时，LangGraph 将调用“[reducer] ”函数。在该函数中，我们定义要接受的更新类型。通常，消息会添加到现有列表中（对话将增长）；但是，我们也添加了支持接受一个字典，让您可以“保留”状态的某些部分。这允许您以编程方式丢弃旧消息上下文。
另一种常见的方法是让您返回一个“删除”对象列表，指定要删除的所有消息的ID。如果您在 LangGraph 中使用LangChain 消息和[`messagesStateReducer`] reducer（或使用相同底层功能的[`MessagesAnnotation`] ），则可以使用`RemoveMessage`来完成此操作。
```
`[] import{RemoveMessage,AIMessage}from"@langchain/core/messages";[] import{MessagesAnnotation}from"@langchain/langgraph";[] [] typeState=typeofMessagesAnnotation.State;[] [] functionmyNode1(state:State){[] // Add an AI message to the `messages` list in the state[] return{messages:[newAIMessage({content:"Hi"})]};[]}[] [] functionmyNode2(state:State){[] // Delete all but the last 2 messages from the `messages` list in the state[] constdeleteMessages=state.messages[].slice(0,-2)[].map((m)=&gt;newRemoveMessage({id:m.id}));[] return{messages:deleteMessages};[]}`
```
在上面的示例中，`MessagesAnnotation`允许我们将新消息附加到`messages`状态键，如`myNode1`所示。当它看到`RemoveMessage`时，它将从列表中删除具有该ID的消息（然后该RemoveMessage将被丢弃）。有关LangChain特定消息处理的更多信息，请查看[此关于使用`RemoveMessage`的操作指南] 。
有关示例用法，请参阅此操作[指南] 。
### 总结过往对话[¶] 
如上所示，修剪或删除消息的问题在于，我们可能会因为筛选消息队列而丢失信息。因此，一些应用程序受益于使用聊天模型总结消息历史的更复杂方法。![] 
可以使用简单的提示和编排逻辑来实现这一点。例如，在LangGraph 中，我们可以扩展[`MessagesAnnotation`] 以包含`summary`键。
```
`[] import{MessagesAnnotation,Annotation}from"@langchain/langgraph";[] [] constMyGraphAnnotation=Annotation.Root({[]...MessagesAnnotation.spec,[] summary:Annotation&lt;string&gt;,[]});`
```
然后，我们可以生成聊天历史的摘要，使用任何现有摘要作为下一个摘要的上下文。此`summarizeConversation`节点可以在`messages`状态键中积累一定数量的消息后调用。
```
`[] import{ChatOpenAI}from"@langchain/openai";[] import{HumanMessage,RemoveMessage}from"@langchain/core/messages";[] [] typeState=typeofMyGraphAnnotation.State;[] [] asyncfunctionsummarizeConversation(state:State){[] // First, we get any existing summary[] constsummary=state.summary||"";[] [] // Create our summarization prompt[] letsummaryMessage:string;[] if(summary){[] // A summary already exists[] summaryMessage=[] `This is a summary of the conversation to date:${summary}\\n\\n`+[] "Extend the summary by taking into account the new messages above:";[]}else{[] summaryMessage="Create a summary of the conversation above:";[]}[] [] // Add prompt to our history[] constmessages=[[]...state.messages,[] newHumanMessage({content:summaryMessage}),[]];[] [] // Assuming you have a ChatOpenAI model instance[] constmodel=newChatOpenAI();[] constresponse=awaitmodel.invoke(messages);[] [] // Delete all but the 2 most recent messages[] constdeleteMessages=state.messages[].slice(0,-2)[].map((m)=&gt;newRemoveMessage({id:m.id}));[] [] return{[] summary:response.content,[] messages:deleteMessages,[]};[]}`
```
有关示例用法，请参见[此处] 。
### 知道**何时**删除消息[¶] 
大多数LLM 都有一个最大支持上下文窗口（以token 计）。决定何时截断消息的一个简单方法是计算消息历史中的token 数量，并在接近该限制时进行截断。朴素截断很容易自行实现，尽管有一些“陷阱”。某些模型API 进一步限制了消息类型的序列（必须以人类消息开头，不能有相同类型的连续消息等）。如果您正在使用LangChain，可以使用[`trimMessages`] 工具并指定要从列表中保留的 token 数量，以及用于处理边界的`strategy`（例如，保留最后`maxTokens`）。
下面是一个示例。```
`[] import{trimMessages}from"@langchain/core/messages";[] import{ChatOpenAI}from"@langchain/openai";[] [] trimMessages(messages,{[] // Keep the last &lt;&lt;= n\_count tokens of the messages.[] strategy:"last",[] // Remember to adjust based on your model[] // or else pass a custom token\_encoder[] tokenCounter:newChatOpenAI({modelName:"gpt-4"}),[] // Remember to adjust based on the desired conversation[] // length[] maxTokens:45,[] // Most chat models expect that chat history starts with either:[] // (1) a HumanMessage or[] // (2) a SystemMessage followed by a HumanMessage[] startOn:"human",[] // Most chat models expect that chat history ends with either:[] // (1) a HumanMessage or[] // (2) a ToolMessage[] endOn:["human","tool"],[] // Usually, we want to keep the SystemMessage[] // if it's present in the original history.[] // The SystemMessage has special instructions for the model.[] includeSystem:true,[]});`
```
## 长期记忆[¶] 
LangGraph 中的长期记忆允许系统在不同对话或会话中保留信息。与线程范围的短期记忆不同，长期记忆保存在自定义的“命名空间”中。LangGraph 将长期记忆作为JSON 文档存储在[存储] （[参考文档] ）中。每个记忆都组织在一个自定义的`namespace`（类似于文件夹）和一个独特的`key`（像文件名）下。命名空间通常包含用户或组织ID或其他标签，以便更容易组织信息。这种结构支持记忆的层次化组织。然后通过内容过滤器支持跨命名空间搜索。请参见下面的示例。
```
`[] import{InMemoryStore}from"@langchain/langgraph";[] [] // InMemoryStore saves data to an in-memory dictionary. Use a DB-backed store in production use.[] conststore=newInMemoryStore();[] constuserId="my-user";[] constapplicationContext="chitchat";[] constnamespace=[userId,applicationContext];[] awaitstore.put(namespace,"a-memory",{[] rules:[[] "User likes short, direct language",[] "User only speaks English &amp; TypeScript",[]],[] "my-key":"my-value",[]});[] // get the "memory" by ID[] constitem=awaitstore.get(namespace,"a-memory");[] // list "memories" within this namespace, filtering on content equivalence[] constitems=awaitstore.search(namespace,{[] filter:{"my-key":"my-value"},[]});`
```
当向智能体添加长期记忆时，重要的是要考虑如何**写入记忆**、如何**存储和管理记忆更新**，以及如何为应用程序中的 LLM**召回和表示记忆**。这些问题都是相互关联的：您希望如何为 LLM 召回和格式化记忆，决定了您应该存储什么以及如何管理它。此外，每种技术都有其权衡。正确的方法在很大程度上取决于您应用程序的需求。LangGraph 旨在为您提供低级原语，以便您根据记忆[存储] 直接控制应用程序的长期记忆。
长期记忆远非一个已解决的问题。虽然很难提供通用建议，但我们在下面提供了一些可靠的模式供您在实现长期记忆时参考。**您希望在“主路径”中写入记忆还是在“后台”写入记忆？**
记忆可以作为主要应用程序逻辑的一部分（例如，在应用程序的“主路径”上）或作为后台任务（作为根据主要应用程序状态生成记忆的独立函数）进行更新。我们在[下面的写入记忆部分] 中记录了每种方法的一些权衡。
**您希望将记忆作为单个档案管理还是作为文档集合管理？**
我们提供了两种管理长期记忆的主要方法：单个持续更新的文档（称为“档案”或“模式”）或文档集合。每种方法都有其自身的好处，具体取决于您需要存储的信息类型以及您打算如何访问它。当您希望记住有关用户、组织或其他实体（包括智能体本身）的范围明确、具体的信息时，将记忆作为单个、持续更新的“档案”或“模式”进行管理非常有用。您可以预先定义档案的模式，然后使用LLM 根据交互进行更新。查询“记忆”很容易，因为它只是对JSON 文档的简单GET 操作。我们在[记住档案] 中更详细地解释了这一点。这种技术可以提供更高的准确性（在已知信息用例中），但召回率较低（因为您必须预测和建模您的领域，并且文档更新倾向于以更高的频率删除或重写旧信息）。
另一方面，将长期记忆作为文档集合进行管理，可以存储无限量的信息。当您希望在长时间范围内重复提取和记住项目时，这项技术非常有用，但随着时间的推移，查询和管理可能会更复杂。与“档案”记忆类似，您仍然为每个记忆定义模式。您将插入新文档（并在此过程中可能更新或重新情境化现有文档），而不是覆盖单个文档。我们在[“管理记忆集合”] 中更详细地解释了这种方法。
**您希望将记忆作为更新的指令还是作为少量样本示例呈现给您的智能体？**
记忆通常作为系统提示的一部分提供给LLM。为 LLM“框架”记忆的一些常见方式包括提供原始信息，如“与用户 A 之前交互的记忆”，作为系统指令或规则，或作为少量样本示例。将记忆框定为“学习规则或指令”通常意味着将系统提示的一部分专门用于LLM 可以自行管理的指令。在每次对话后，您可以提示LLM 评估其性能并更新指令，


---
*数据来源: Exa搜索 | 获取时间: 2026-02-10 21:59:05*