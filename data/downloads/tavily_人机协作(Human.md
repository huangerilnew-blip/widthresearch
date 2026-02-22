* [用例](#use-cases)
* [中断](#interrupt)
* [要求](#requirements)
* [设计模式](#design-patterns) 

  + [批准或拒绝](#approve-or-reject)
  + [审查与编辑状态](#review-edit-state)
  + [审查工具调用](#review-tool-calls)
  + [多轮对话](#multi-turn-conversation)
  + [验证人类输入](#validating-human-input)
* [Command 原语](#the-command-primitive)
* [与 invoke 结合使用](#using-with-invoke)
* [从中断恢复如何工作？](#how-does-resuming-from-an-interrupt-work)
* [常见陷阱](#common-pitfalls) 

  + [副作用](#side-effects)
  + [作为函数调用的子图](#subgraphs-called-as-functions)
  + [使用多个中断](#using-multiple-interrupts)
* [附加资源 📚](#additional-resources)

1. [LangGraph](../..)
2. [指南](../../how-tos/)
3. [概念](../)
4. [LangGraph](../../concepts#langgraph)

# 人机协作 (Human-in-the-loop)[¶](#human-in-the-loop "Permanent link")

本指南使用新的 `interrupt` 函数。

自 LangGraph 0.2.31 起，推荐使用 [`interrupt` 函数](/langgraphjs/reference/functions/langgraph.interrupt-1.html) 来设置断点，因为它简化了**人机协作（human-in-the-loop）**模式。

如果您正在寻找此概念指南的先前版本，该版本依赖于静态断点和 `NodeInterrupt` 异常，请点击[此处](../v0-human-in-the-loop/)。

**人机协作（human-in-the-loop）**（或“在环”）工作流将人类输入集成到自动化流程中，允许在关键阶段进行决策、验证或更正。这在**基于 LLM 的应用程序**中尤其有用，因为底层模型可能会偶尔产生不准确的内容。在合规、决策或内容生成等低容错场景中，人类参与通过允许审查、更正或覆盖模型输出来确保可靠性。

## 用例[¶](#use-cases "Permanent link")

基于 LLM 应用程序中**人机协作**工作流的主要用例包括：

1. [**🛠️ 审查工具调用**](#review-tool-calls)：人类可以在工具执行前审查、编辑或批准 LLM 请求的工具调用。
2. **✅ 验证 LLM 输出**：人类可以审查、编辑或批准 LLM 生成的内容。
3. **💡 提供上下文**：使 LLM 能够明确请求人类输入以进行澄清或提供额外细节，或支持多轮对话。

## `interrupt`[¶](#interrupt "Permanent link")

LangGraph 中的 [`interrupt` 函数](/langgraphjs/reference/functions/langgraph.interrupt-1.html) 通过在特定节点暂停图，向人类呈现信息，并用他们的输入恢复图，从而实现人机协作工作流。此函数对于批准、编辑或收集额外输入等任务非常有用。[`interrupt` 函数](/langgraphjs/reference/functions/langgraph.interrupt-1.html) 与 [`Command`](/langgraphjs/reference/classes/langgraph.Command.html) 对象结合使用，以人类提供的值恢复图。

```
import { interrupt } from "@langchain/langgraph"; import  { interrupt  }  from  "@langchain/langgraph";  function humanNode(state: typeof GraphAnnotation.State) { function  humanNode(state:  typeof  GraphAnnotation. State)  { const value = interrupt(  const  value  =  interrupt( // Any JSON serializable value to surface to the human.  // Any JSON serializable value to surface to the human. // For example, a question or a piece of text or a set of keys in the state  // For example, a question or a piece of text or a set of keys in the state {  { text_to_revise: state.some_text,  text_to_revise:  state.some_text, }  } );  ); // Update the state with the human's input or route the graph based on the input  // Update the state with the human's input or route the graph based on the input return {  return  { some_text: value,  some_text:  value, };  };} }  const graph = workflow.compile({ const  graph  =  workflow. compile({ checkpointer, // Required for `interrupt` to work  checkpointer,  // Required for `interrupt` to work}); });  // Run the graph until the interrupt // Run the graph until the interruptconst threadConfig = { configurable: { thread_id: "some_id" } }; const  threadConfig  =  { configurable:  { thread_id:  "some_id"  }  };await graph.invoke(someInput, threadConfig); await  graph. invoke(someInput,  threadConfig);  // Below code can run some amount of time later and/or in a different process // Below code can run some amount of time later and/or in a different process  // Human input // Human inputconst valueFromHuman = "..."; const  valueFromHuman  =  "...";  // Resume the graph with the human's input // Resume the graph with the human's inputawait graph.invoke(new Command({ resume: valueFromHuman }), threadConfig); await  graph. invoke(new  Command({ resume:  valueFromHuman  }),  threadConfig);
```

```
{ { some_text: "Edited text";  some_text:  "Edited text";} }
```

 完整代码

以下是关于如何在图中使用 `interrupt` 的完整示例，如果您想查看代码的实际运行情况。

```
import { MemorySaver, Annotation, interrupt, Command, StateGraph } from "@langchain/langgraph"; import  { MemorySaver,  Annotation,  interrupt,  Command,  StateGraph  }  from  "@langchain/langgraph";  // Define the graph state // Define the graph stateconst StateAnnotation = Annotation.Root({ const  StateAnnotation  =  Annotation. Root({ some_text: Annotation<string>()  some_text:  Annotation< string>()}); });  function humanNode(state: typeof StateAnnotation.State) { function  humanNode(state:  typeof  StateAnnotation. State)  { const value = interrupt(  const  value  =  interrupt( // Any JSON serializable value to surface to the human.  // Any JSON serializable value to surface to the human. // For example, a question or a piece of text or a set of keys in the state  // For example, a question or a piece of text or a set of keys in the state {  { text_to_revise: state.some_text  text_to_revise:  state.some_text }  } );  ); return {  return  { // Update the state with the human's input  // Update the state with the human's input some_text: value  some_text:  value };  };} }  // Build the graph // Build the graphconst workflow = new StateGraph(StateAnnotation) const  workflow  =  new  StateGraph(StateAnnotation)// Add the human-node to the graph // Add the human-node to the graph .addNode("human_node", humanNode)  . addNode("human_node",  humanNode) .addEdge("__start__", "human_node")  . addEdge("__start__",  "human_node")  // A checkpointer is required for `interrupt` to work. // A checkpointer is required for `interrupt` to work.const checkpointer = new MemorySaver(); const  checkpointer  =  new  MemorySaver();const graph = workflow.compile({ const  graph  =  workflow. compile({ checkpointer  checkpointer}); });  // Using stream() to directly surface the `__interrupt__` information. // Using stream() to directly surface the `__interrupt__` information.for await (const chunk of await graph.stream( for  await  (const  chunk  of  await  graph. stream( { some_text: "Original text" },  { some_text:  "Original text"  },  threadConfig  threadConfig)) { ))  { console.log(chunk);  console. log(chunk);} }  // Resume using Command // Resume using Commandfor await (const chunk of await graph.stream( for  await  (const  chunk  of  await  graph. stream( new Command({ resume: "Edited text" }),  new  Command({ resume:  "Edited text"  }),  threadConfig  threadConfig)) { ))  { console.log(chunk);  console. log(chunk);} }
```

```
{ { __interrupt__: [  __interrupt__:  [ {  { value: { question: 'Please revise the text', some_text: 'Original text' },  value:  { question:  'Please revise the text',  some_text:  'Original text'  }, resumable: true,  resumable:  true, ns: ['human_node:10fe492f-3688-c8c6-0d0a-ec61a43fecd6'],  ns:  ['human_node:10fe492f-3688-c8c6-0d0a-ec61a43fecd6'], when: 'during'  when:  'during' }  } ]  ]} }{ human_node: { some_text: 'Edited text' } } { human_node:  { some_text:  'Edited text'  }  }
```

## 要求[¶](#requirements "永久链接")

要在图中使用 `interrupt`，您需要：

1. [**指定检查点**](../persistence/#checkpoints) 以在每一步之后保存图状态。
2. 在适当的位置**调用 `interrupt()`**。请参阅[设计模式](#design-patterns)部分以获取示例。
3. 使用[**线程 ID**](../persistence/#threads) **运行图**，直到触发 `interrupt`。
4. 使用 `invoke`/`stream` **恢复执行**（请参阅[**`Command` 原语**](#the-command-primitive)）。

## 设计模式[¶](#design-patterns "Permanent link")

通常，您可以通过人机协作工作流执行三种不同的**操作**：

1. **批准或拒绝**：在关键步骤（例如 API 调用）之前暂停图，以审查和批准操作。如果操作被拒绝，您可以阻止图执行该步骤，并可能采取替代操作。此模式通常涉及根据人类的输入对图进行**路由**。
2. **编辑图状态**：暂停图以审查和编辑图状态。这对于纠正错误或使用附加信息更新状态很有用。此模式通常涉及使用人类的输入**更新**状态。
3. **获取输入**：在图的特定步骤中明确请求人类输入。这对于收集额外信息或上下文以指导代理的决策过程或支持**多轮对话**很有用。

下面我们展示了可以使用这些**操作**实现的不同设计模式。

**注意：** `interrupt` 函数通过抛出特殊的 `GraphInterrupt` 错误来传播。因此，您应该避免在 `interrupt` 函数周围使用 `try/catch` 块——如果确实使用了，请确保在 `catch` 块中再次抛出 `GraphInterrupt` 错误。

### 批准或拒绝[¶](#approve-or-reject "Permanent link")

在关键步骤（例如 API 调用）之前暂停图，以审查和批准操作。如果操作被拒绝，您可以阻止图执行该步骤，并可能采取替代操作。

```
import { interrupt, Command } from "@langchain/langgraph"; import  { interrupt,  Command  }  from  "@langchain/langgraph";  function humanApproval(state: typeof GraphAnnotation.State): Command { function  humanApproval(state:  typeof  GraphAnnotation. State):  Command  { const isApproved = interrupt({  const  isApproved  =  interrupt({ question: "Is this correct?",  question:  "Is this correct?", // Surface the output that should be  // Surface the output that should be // reviewed and approved by the human.  // reviewed and approved by the human. llm_output: state.llm_output,  llm_output:  state.llm_output, });  });   if (isApproved) {  if  (isApproved)  { return new Command({ goto: "some_node" });  return  new  Command({ goto:  "some_node"  }); } else {  }  else  { return new Command({ goto: "another_node" });  return  new  Command({ goto:  "another_node"  }); }  }} }  // Add the node to the graph in an appropriate location // Add the node to the graph in an appropriate location// and connect it to the relevant nodes. // and connect it to the relevant nodes.const graph = graphBuilder const  graph  =  graphBuilder .addNode("human_approval", humanApproval)  . addNode("human_approval",  humanApproval) .compile({ checkpointer });  . compile({ checkpointer  });  // After running the graph and hitting the interrupt, the graph will pause. // After running the graph and hitting the interrupt, the graph will pause.// Resume it with either an approval or rejection. // Resume it with either an approval or rejection.const threadConfig = { configurable: { thread_id: "some_id" } }; const  threadConfig  =  { configurable:  { thread_id:  "some_id"  }  };await graph.invoke(new Command({ resume: true }), threadConfig); await  graph. invoke(new  Command({ resume:  true  }),  threadConfig);
```

有关更详细的示例，请参阅[如何审查工具调用](/langgraphjs/how-tos/review-tool-calls)。

### 审查与编辑状态[¶](#review-edit-state "Permanent link")

```
import { interrupt } from "@langchain/langgraph"; import  { interrupt  }  from  "@langchain/langgraph";  function humanEditing(state: typeof GraphAnnotation.State): Command { function  humanEditing(state:  typeof  GraphAnnotation. State):  Command  { const result = interrupt({  const  result  =  interrupt({ // Interrupt information to surface to the client.  // Interrupt information to surface to the client. // Can be any JSON serializable value.  // Can be any JSON serializable value. task: "Review the output from the LLM and make any necessary edits.",  task:  "Review the output from the LLM and make any necessary edits.", llm_generated_summary: state.llm_generated_summary,  llm_generated_summary:  state.llm_generated_summary, });  });   // Update the state with the edited text  // Update the state with the edited text return {  return  { llm_generated_summary: result.edited_text,  llm_generated_summary:  result.edited_text, };  };} }  // Add the node to the graph in an appropriate location // Add the node to the graph in an appropriate location// and connect it to the relevant nodes. // and connect it to the relevant nodes.const graph = graphBuilder const  graph  =  graphBuilder .addNode("human_editing", humanEditing)  . addNode("human_editing",  humanEditing) .compile({ checkpointer });  . compile({ checkpointer  });  // After running the graph and hitting the interrupt, the graph will pause. // After running the graph and hitting the interrupt, the graph will pause.// Resume it with the edited text. // Resume it with the edited text.const threadConfig = { configurable: { thread_id: "some_id" } }; const  threadConfig  =  { configurable:  { thread_id:  "some_id"  }  };await graph.invoke( await  graph. invoke( new Command({ resume: { edited_text: "The edited text" } }),  new  Command({ resume:  { edited_text:  "The edited text"  }  }),  threadConfig  threadConfig); );
```

有关更详细的示例，请参阅[如何使用中断等待用户输入](/langgraphjs/how-tos/wait-user-input)。

### 审查工具调用[¶](#review-tool-calls "Permanent link")

```
import { interrupt, Command } from "@langchain/langgraph"; import  { interrupt,  Command  }  from  "@langchain/langgraph";  function humanReviewNode(state: typeof GraphAnnotation.State): Command { function  humanReviewNode(state:  typeof  GraphAnnotation. State):  Command  { // This is the value we'll be providing via Command.resume()  // This is the value we'll be providing via Command.resume() const humanReview = interrupt({  const  humanReview  =  interrupt({ question: "Is this correct?",  question:  "Is this correct?", // Surface tool calls for review  // Surface tool calls for review tool_call: toolCall,  tool_call:  toolCall, });  });   const [reviewAction, reviewData] = humanReview;  const  [reviewAction,  reviewData]  =  humanReview;   // Approve the tool call and continue  // Approve the tool call and continue if (reviewAction === "continue") {  if  (reviewAction  ===  "continue")  { return new Command({ goto: "run_tool" });  return  new  Command({ goto:  "run_tool"  }); }  } // Modify the tool call manually and then continue  // Modify the tool call manually and then continue else if (reviewAction === "update") {  else  if  (reviewAction  ===  "update")  { const updatedMsg = getUpdatedMsg(reviewData);  const  updatedMsg  =  getUpdatedMsg(reviewData); // Remember that to modify an existing message you will need  // Remember that to modify an existing message you will need // to pass the message with a matching ID.  // to pass the message with a matching ID. return new Command({  return  new  Command({ goto: "run_tool",  goto:  "run_tool", update: { messages: [updatedMsg] },  update:  { messages:  [updatedMsg]  }, });  }); }  } // Give natural language feedback, and then pass that back to the agent  // Give natural language feedback, and then pass that back to the agent else if (reviewAction === "feedback") {  else  if  (reviewAction  ===  "feedback")  { const feedbackMsg = getFeedbackMsg(reviewData);  const  feedbackMsg  =  getFeedbackMsg(reviewData); return new Command({  return  new  Command({ goto: "call_llm",  goto:  "call_llm", update: { messages: [feedbackMsg] },  update:  { messages:  [feedbackMsg]  }, });  }); }  }} }
```

有关更详细的示例，请参阅[如何审查工具调用](/langgraphjs/how-tos/review-tool-calls)。

### 多轮对话[¶](#multi-turn-conversation "Permanent link")

**多轮对话**涉及代理和人类之间的多次来回交互，这可以允许代理以对话方式从人类那里收集额外信息。

这种设计模式在由[多个代理](../multi_agent/)组成的 LLM 应用程序中很有用。一个或多个代理可能需要与人类进行多轮对话，其中人类在对话的不同阶段提供输入或反馈。为简单起见，下面的代理实现被说明为单个节点，但实际上它可能是由多个节点组成的更大图的一部分，并包含条件边。

在此模式中，每个代理都有自己的人类节点用于收集用户输入。

这可以通过为人类节点使用唯一名称（例如，“代理 1 的人类节点”，“代理 2 的人类节点”）或使用子图（其中子图包含人类节点和代理节点）来实现。

```
import { interrupt } from "@langchain/langgraph"; import  { interrupt  }  from  "@langchain/langgraph";  function humanInput(state: typeof GraphAnnotation.State) { function  humanInput(state:  typeof  GraphAnnotation. State)  { const humanMessage = interrupt("human_input");  const  humanMessage  =  interrupt("human_input");   return {  return  { messages: [  messages:  [ {  { role: "human",  role:  "human", content: humanMessage  content:  humanMessage }  } ]  ] };  };} }  function agent(state: typeof GraphAnnotation.State) { function  agent(state:  typeof  GraphAnnotation. State)  { // Agent logic  // Agent logic // ...  // ...} }  const graph = graphBuilder const  graph  =  graphBuilder .addNode("human_input", humanInput)  . addNode("human_input",  humanInput) .addEdge("human_input", "agent")  . addEdge("human_input",  "agent") .compile({ checkpointer });  . compile({ checkpointer  });  // After running the graph and hitting the interrupt, the graph will pause. // After running the graph and hitting the interrupt, the graph will pause.// Resume it with the human's input. // Resume it with the human's input.await graph.invoke( await  graph. invoke( new Command({ resume: "hello!" }),  new  Command({ resume:  "hello!"  }),  threadConfig  threadConfig); );
```

在此模式中，单个人类节点用于收集多个代理的用户输入。活动代理从状态中确定，因此在收集人类输入后，图可以路由到正确的代理。

```
import { interrupt, Command, MessagesAnnotation } from "@langchain/langgraph"; import  { interrupt,  Command,  MessagesAnnotation  }  from  "@langchain/langgraph";  function humanNode(state: typeof MessagesAnnotation.State): Command { function  humanNode(state:  typeof  MessagesAnnotation. State):  Command  { /**  /** * A node for collecting user input.  * A node for collecting user input. */  */ const userInput = interrupt("Ready for user input.");  const  userInput  =  interrupt("Ready for user input.");   // Determine the **active agent** from the state, so  // Determine the **active agent** from the state, so // we can route to the correct agent after collecting input.  // we can route to the correct agent after collecting input. // For example, add a field to the state or use the last active agent.  // For example, add a field to the state or use the last active agent. // or fill in `name` attribute of AI messages generated by the agents.  // or fill in `name` attribute of AI messages generated by the agents. const activeAgent = ...;  const  activeAgent  =  ...;   return new Command({  return  new  Command({ goto: activeAgent,  goto:  activeAgent, update: {  update:  { messages: [{  messages:  [{ role: "human",  role:  "human", content: userInput,  content:  userInput, }]  }] }  } });  });} }
```

有关更详细的示例，请参阅[如何实现多轮对话](/langgraphjs/how-tos/multi-agent-multi-turn-convo)。

### 验证人类输入[¶](#validating-human-input "Permanent link")

如果您需要在图本身中（而不是在客户端）验证人类提供的输入，可以通过在单个节点中使用多个中断调用来实现。

```
import { interrupt } from "@langchain/langgraph"; import  { interrupt  }  from  "@langchain/langgraph";  function humanNode(state: typeof GraphAnnotation.State) { function  humanNode(state:  typeof  GraphAnnotation. State)  { /**  /** * Human node with validation.  * Human node with validation. */  */ let question = "What is your age?";  let  question  =  "What is your age?";   while (true) {  while  (true)  { const answer = interrupt(question);  const  answer  =  interrupt(question);   // Validate answer, if the answer isn't valid ask for input again.  // Validate answer, if the answer isn't valid ask for input again. if (typeof answer !== "number" || answer < 0) {  if  (typeof  answer  !==  "number"  ||  answer  <  0)  { question = `'${answer}' is not a valid age. What is your age?`;  question  =  `'${answer}' is not a valid age. What is your age?`; continue;  continue; } else {  }  else  { // If the answer is valid, we can proceed.  // If the answer is valid, we can proceed. break;  break; }  } }  }   console.log(`The human in the loop is ${answer} years old.`);  console. log(`The human in the loop is ${answer} years old.`);   return {  return  { age: answer,  age:  answer, };  };} }
```

## Command 原语[¶](#the-command-primitive "Permanent link")

当使用 `interrupt` 函数时，图将在中断处暂停并等待用户输入。

图的执行可以使用 [Command](/langgraphjs/reference/classes/langgraph.Command.html) 原语恢复，该原语可以通过 `invoke` 或 `stream` 方法传递。

`Command` 原语提供了几个选项来控制和修改恢复期间图的状态：

1. **将值传递给 `interrupt`**：使用 `new Command({ resume: value })` 向图提供数据，例如用户的响应。执行从使用 `interrupt` 的节点的开头恢复，但是，这次 `interrupt(...)` 调用将返回在 `new Command({ resume: value })` 中传递的值，而不是暂停图。

```
// Resume graph execution with the user's input. // Resume graph execution with the user's input.await graph.invoke(new Command({ resume: { age: "25" } }), threadConfig); await  graph. invoke(new  Command({ resume:  { age:  "25"  }  }),  threadConfig);
```

1. **更新图状态**：使用 `Command({ goto: ..., update: ... })` 修改图状态。请注意，恢复从使用 `interrupt` 的节点的开头开始。执行从使用 `interrupt` 的节点的开头恢复，但带有更新后的状态。

```
// Update the graph state and resume. // Update the graph state and resume.// You must provide a `resume` value if using an `interrupt`. // You must provide a `resume` value if using an `interrupt`.await graph.invoke( await  graph. invoke( new Command({ resume: "Let's go!!!", update: { foo: "bar" } }),  new  Command({ resume:  "Let's go!!!",  update:  { foo:  "bar"  }  }),  threadConfig  threadConfig); );
```

通过利用 `Command`，您可以恢复图的执行，处理用户输入，并动态调整图的状态。

## 与 `invoke` 结合使用[¶](#using-with-invoke "Permanent link")

当您使用 `stream` 运行图时，您将收到一个 `Interrupt` 事件，它会通知您 `interrupt` 已被触发。

`invoke` 不会返回中断信息。要访问此信息，您必须在调用 `invoke` 后使用 [getState](/langgraphjs/reference/classes/langgraph.CompiledStateGraph.html#getState) 方法检索图状态。

```
// Run the graph up to the interrupt // Run the graph up to the interruptconst result = await graph.invoke(inputs, threadConfig); const  result  =  await  graph. invoke(inputs,  threadConfig);  // Get the graph state to get interrupt information. // Get the graph state to get interrupt information.const state = await graph.getState(threadConfig); const  state  =  await  graph. getState(threadConfig);  // Print the state values // Print the state valuesconsole.log(state.values); console. log(state. values);  // Print the pending tasks // Print the pending tasksconsole.log(state.tasks); console. log(state. tasks);  // Resume the graph with the user's input. // Resume the graph with the user's input.await graph.invoke(new Command({ resume: { age: "25" } }), threadConfig); await  graph. invoke(new  Command({ resume:  { age:  "25"  }  }),  threadConfig);
```

```
{ { foo: "bar";  foo:  "bar";} // State values }  // State values  [ [ {  { id: "5d8ffc92-8011-0c9b-8b59-9d3545b7e553",  id:  "5d8ffc92-8011-0c9b-8b59-9d3545b7e553", name: "node_foo",  name:  "node_foo", path: ["__pregel_pull", "node_foo"],  path:  ["__pregel_pull",  "node_foo"], error: null,  error:  null, interrupts: [  interrupts:  [ {  { value: "value_in_interrupt",  value:  "value_in_interrupt", resumable: true,  resumable:  true, ns: ["node_foo:5d8ffc92-8011-0c9b-8b59-9d3545b7e553"],  ns:  ["node_foo:5d8ffc92-8011-0c9b-8b59-9d3545b7e553"], when: "during",  when:  "during", },  }, ],  ], state: null,  state:  null, result: null,  result:  null, },  },]; // Pending tasks. interrupts ];  // Pending tasks. interrupts
```

## 从中断恢复如何工作？[¶](#how-does-resuming-from-an-interrupt-work "Permanent link")

使用 `interrupt` 的一个关键方面是理解恢复的工作原理。当您在 `interrupt` 后恢复执行时，图的执行从上次触发 `interrupt` 的**图节点**的**开头**开始。

从节点开头到 `interrupt` 的**所有**代码都将重新执行。

```
let counter = 0; let  counter  =  0;  function node(state: State) { function  node(state:  State)  { // All the code from the beginning of the node to the interrupt will be re-executed  // All the code from the beginning of the node to the interrupt will be re-executed // when the graph resumes.  // when the graph resumes. counter += 1;  counter  +=  1;   console.log(`> Entered the node: ${counter} # of times`);  console. log(`> Entered the node: ${counter}  # of times`);   // Pause the graph and wait for user input.  // Pause the graph and wait for user input. const answer = interrupt();  const  answer  =  interrupt();   console.log("The value of counter is:", counter);  console. log("The value of counter is:",  counter); // ...  // ...} }
```

在**恢复**图时，计数器将第二次递增，导致以下输出：

```
> Entered the node: 2 # of times >  Entered  the  node:  2  #  of  timesThe value of counter is: 2 The  value  of  counter  is:  2
```

## 常见陷阱[¶](#common-pitfalls "永久链接")

### 副作用[¶](#side-effects "Permanent link")

将带有副作用的代码（例如 API 调用）放在 `interrupt` **之后**，以避免重复，因为这些代码在每次节点恢复时都会重新触发。

当节点从 `interrupt` 恢复时，此代码将再次重新执行 API 调用。如果 API 调用不是幂等的或者成本很高，这可能会导致问题。

```
import { interrupt } from "@langchain/langgraph"; import  { interrupt  }  from  "@langchain/langgraph";  function humanNode(state: typeof GraphAnnotation.State) { function  humanNode(state:  typeof  GraphAnnotation. State)  { /**  /** * Human node with validation.  * Human node with validation. */  */ apiCall(); // This code will be re-executed when the node is resumed.  apiCall();  // This code will be re-executed when the node is resumed.   const answer = interrupt(question);  const  answer  =  interrupt(question);} }
```

```
import { interrupt } from "@langchain/langgraph"; import  { interrupt  }  from  "@langchain/langgraph";  function humanNode(state: typeof GraphAnnotation.State) { function  humanNode(state:  typeof  GraphAnnotation. State)  { /**  /** * Human node with validation.  * Human node with validation. */  */   const answer = interrupt(question);  const  answer  =  interrupt(question);   apiCall(answer); // OK as it's after the interrupt  apiCall(answer);  // OK as it's after the interrupt} }
```

```
import { interrupt } from "@langchain/langgraph"; import  { interrupt  }  from  "@langchain/langgraph";  function humanNode(state: typeof GraphAnnotation.State) { function  humanNode(state:  typeof  GraphAnnotation. State)  { /**  /** * Human node with validation.  * Human node with validation. */  */   const answer = interrupt(question);  const  answer  =  interrupt(question);   return {  return  { answer  answer };  };} }  function apiCallNode(state: typeof GraphAnnotation.State) { function  apiCallNode(state:  typeof  GraphAnnotation. State)  { apiCall(); // OK as it's in a separate node  apiCall();  // OK as it's in a separate node} }
```

### 作为函数调用的子图[¶](#subgraphs-called-as-functions "Permanent link")

当[作为函数](../low_level/#as-a-function)调用子图时，**父图**将从调用子图的**节点开头**（以及触发 `interrupt` 的地方）恢复执行。同样，**子图**将从调用 `interrupt()` 函数的**节点开头**恢复。

例如：

```
async function nodeInParentGraph(state: typeof GraphAnnotation.State) { async  function  nodeInParentGraph(state:  typeof  GraphAnnotation. State)  { someCode(); // <-- This will re-execute when the subgraph is resumed.  someCode();  // <-- This will re-execute when the subgraph is resumed. // Invoke a subgraph as a function.  // Invoke a subgraph as a function. // The subgraph contains an `interrupt` call.  // The subgraph contains an `interrupt` call. const subgraphResult = await subgraph.invoke(someInput);  const  subgraphResult  =  await  subgraph. invoke(someInput); ...  ...} }
```

 **示例：父图和子图的执行流程**

假设我们有一个包含 3 个节点的父图：

**父图**：`node_1` → `node_2`（子图调用） → `node_3`

子图有 3 个节点，其中第二个节点包含 `interrupt`：

**子图**：`sub_node_1` → `sub_node_2`（`interrupt`） → `sub_node_3`

恢复图时，执行将按以下方式进行：

1. **跳过父图中的 `node_1`**（已执行，图状态已保存为快照）。
2. **从头开始重新执行父图中的 `node_2`**。
3. **跳过子图中的 `sub_node_1`**（已执行，图状态已保存为快照）。
4. **从头开始重新执行子图中的 `sub_node_2`**。
5. 继续执行 `sub_node_3` 和后续节点。

这是一个缩写的示例代码，您可以用来理解子图如何与中断一起工作。它计算每个节点进入的次数并打印计数。

```
import { import  { StateGraph,  StateGraph, START,  START, interrupt,  interrupt, Command,  Command, MemorySaver,  MemorySaver,  Annotation  Annotation} from "@langchain/langgraph"; }  from  "@langchain/langgraph";  const GraphAnnotation = Annotation.Root({ const  GraphAnnotation  =  Annotation. Root({ stateCounter: Annotation<number>({  stateCounter:  Annotation< number>({ reducer: (a, b) => a + b,  reducer:  (a,  b)  =>  a  +  b, default: () => 0  default:  ()  =>  0 })  })}) })  let counterNodeInSubgraph = 0; let  counterNodeInSubgraph  =  0;  function nodeInSubgraph(state: typeof GraphAnnotation.State) { function  nodeInSubgraph(state:  typeof  GraphAnnotation. State)  { counterNodeInSubgraph += 1; // This code will **NOT** run again!  counterNodeInSubgraph  +=  1;  // This code will **NOT** run again! console.log(`Entered 'nodeInSubgraph' a total of ${counterNodeInSubgraph} times`);  console. log(`Entered 'nodeInSubgraph' a total of ${counterNodeInSubgraph}  times`); return {};  return  {};} }  let counterHumanNode = 0; let  counterHumanNode  =  0;  async function humanNode(state: typeof GraphAnnotation.State) { async  function  humanNode(state:  typeof  GraphAnnotation. State)  { counterHumanNode += 1; // This code will run again!  counterHumanNode  +=  1;  // This code will run again! console.log(`Entered humanNode in sub-graph a total of ${counterHumanNode} times`);  console. log(`Entered humanNode in sub-graph a total of ${counterHumanNode}  times`); const answer = await interrupt("what is your name?");  const  answer  =  await  interrupt("what is your name?"); console.log(`Got an answer of ${answer}`);  console. log(`Got an answer of ${answer} `); return {};  return  {};} }  const checkpointer = new MemorySaver(); const  checkpointer  =  new  MemorySaver();  const subgraphBuilder = new StateGraph(GraphAnnotation) const  subgraphBuilder  =  new  StateGraph(GraphAnnotation) .addNode("some_node", nodeInSubgraph)  . addNode("some_node",  nodeInSubgraph) .addNode("human_node", humanNode)  . addNode("human_node",  humanNode) .addEdge(START, "some_node")  . addEdge(START,  "some_node") .addEdge("some_node", "human_node")  . addEdge("some_node",  "human_node")const subgraph = subgraphBuilder.compile({ checkpointer }); const  subgraph  =  subgraphBuilder. compile({ checkpointer  });  let counterParentNode = 0; let  counterParentNode  =  0;  async function parentNode(state: typeof GraphAnnotation.State) { async  function  parentNode(state:  typeof  GraphAnnotation. State)  { counterParentNode += 1; // This code will run again on resuming!  counterParentNode  +=  1;  // This code will run again on resuming! console.log(`Entered 'parentNode' a total of ${counterParentNode} times`);  console. log(`Entered 'parentNode' a total of ${counterParentNode}  times`);   // Please note that we're intentionally incrementing the state counter  // Please note that we're intentionally incrementing the state counter // in the graph state as well to demonstrate that the subgraph update  // in the graph state as well to demonstrate that the subgraph update // of the same key will not conflict with the parent graph (until  // of the same key will not conflict with the parent graph (until const subgraphState = await subgraph.invoke(state);  const  subgraphState  =  await  subgraph. invoke(state); return subgraphState;  return  subgraphState;} }  const builder = new StateGraph(GraphAnnotation) const  builder  =  new  StateGraph(GraphAnnotation) .addNode("parent_node", parentNode)  . addNode("parent_node",  parentNode) .addEdge(START, "parent_node")  . addEdge(START,  "parent_node")  // A checkpointer must be enabled for interrupts to work! // A checkpointer must be enabled for interrupts to work!const graph = builder.compile({ checkpointer }); const  graph  =  builder. compile({ checkpointer  });  const config = { const  config  =  { configurable: {  configurable:  { thread_id: crypto.randomUUID(),  thread_id:  crypto.randomUUID(), }  }}; };  for await (const chunk of await graph.stream({ stateCounter: 1 }, config)) { for  await  (const  chunk  of  await  graph. stream({ stateCounter:  1  },  config))  { console.log(chunk);  console. log(chunk);} }  console.log('--- Resuming ---'); console. log('--- Resuming ---');  for await (const chunk of await graph.stream(new Command({ resume: "35" }), config)) { for  await  (const  chunk  of  await  graph. stream(new  Command({ resume:  "35"  }),  config))  { console.log(chunk);  console. log(chunk);} }
```

这将打印出

```
 --- First invocation --- ---  First  invocation  ---In parent node: { foo: 'bar' } In  parent  node:  { foo:  'bar'  } Entered 'parentNode' a total of 1 times Entered  'parentNode'  a  total  of  1  times Entered 'nodeInSubgraph' a total of 1 times Entered  'nodeInSubgraph'  a  total  of  1  timesEntered humanNode in sub-graph a total of 1 times Entered  humanNode  in  sub - graph  a  total  of  1  times{ __interrupt__: [{ value: 'what is your name?', resumable: true, ns: ['parent_node:0b23d72f-aaba-0329-1a59-ca4f3c8bad3b', 'human_node:25df717c-cb80-57b0-7410-44e20aac8f3c'], when: 'during' }] } { __interrupt__:  [{ value:  'what is your name?',  resumable:  true,  ns:  ['parent_node:0b23d72f-aaba-0329-1a59-ca4f3c8bad3b',  'human_node:25df717c-cb80-57b0-7410-44e20aac8f3c'],  when:  'during'  }]  }  --- Resuming --- ---  Resuming  ---In parent node: { foo: 'bar' } In  parent  node:  { foo:  'bar'  } Entered 'parentNode' a total of 2 times Entered  'parentNode'  a  total  of  2  timesEntered humanNode in sub-graph a total of 2 times Entered  humanNode  in  sub - graph  a  total  of  2  times Got an answer of 35 Got  an  answer  of  35{ parent_node: null } { parent_node:  null  }
```

### 使用多个中断[¶](#using-multiple-interrupts "Permanent link")

在**单个**节点中使用多个中断可能有助于实现诸如[验证人类输入](#validating-human-input)之类的模式。然而，如果在同一节点中使用多个中断且不小心处理，可能会导致意外行为。

当一个节点包含多个中断调用时，LangGraph 会为执行该任务的节点保留一个特定于任务的恢复值列表。每当执行恢复时，它都会从节点的开头开始。对于遇到的每个中断，LangGraph 都会检查任务的恢复列表中是否存在匹配的值。匹配是**严格基于索引**的，因此中断调用在节点中的顺序至关重要。

为避免问题，请避免在执行之间动态更改节点结构。这包括添加、删除或重新排序中断调用，因为此类更改可能导致索引不匹配。这些问题通常源于非常规模式，例如通过 `Command.resume(...).update(SOME_STATE_MUTATION)` 改变状态或依赖全局变量动态修改节点结构。

 不正确的代码示例

```
import { v4 as uuidv4 } from "uuid"; import  { v4  as  uuidv4  }  from  "uuid";import { import  { StateGraph,  StateGraph, MemorySaver,  MemorySaver, START,  START, interrupt,  interrupt, Command,  Command,  Annotation  Annotation} from "@langchain/langgraph"; }  from  "@langchain/langgraph";  const GraphAnnotation = Annotation.Root({ const  GraphAnnotation  =  Annotation. Root({ name: Annotation<string>(),  name:  Annotation< string>(), age: Annotation<string>()  age:  Annotation< string>()}); });  function humanNode(state: typeof GraphAnnotation.State) { function  humanNode(state:  typeof  GraphAnnotation. State)  { let name;  let  name; if (!state.name) {  if  (! state. name)  { name = interrupt("what is your name?");  name  =  interrupt("what is your name?"); } else {  }  else  { name = "N/A";  name  =  "N/A"; }  }   let age;  let  age; if (!state.age) {  if  (! state. age)  { age = interrupt("what is your age?");  age  =  interrupt("what is your age?"); } else {  }  else  { age = "N/A";  age  =  "N/A"; }  }   console.log(`Name: ${name}. Age: ${age}`);  console. log(`Name: ${name}. Age: ${age} `);   return {  return  { age,  age, name,  name, };  };} }  const builder = new StateGraph(GraphAnnotation) const  builder  =  new  StateGraph(GraphAnnotation) .addNode("human_node", humanNode);  . addNode("human_node",  humanNode); .addEdge(START, "human_node");  . addEdge(START,  "human_node");  // A checkpointer must be enabled for interrupts to work! // A checkpointer must be enabled for interrupts to work!const checkpointer = new MemorySaver(); const  checkpointer  =  new  MemorySaver();  const graph = builder.compile({ checkpointer }); const  graph  =  builder. compile({ checkpointer  });  const config = { const  config  =  { configurable: {  configurable:  { thread_id: uuidv4(),  thread_id:  uuidv4(), }  }}; };  for await (const chunk of await graph.stream({ age: undefined, name: undefined }, config)) { for  await  (const  chunk  of  await  graph. stream({ age:  undefined,  name:  undefined  },  config))  { console.log(chunk);  console. log(chunk);} }  for await (const chunk of await graph.stream( for  await  (const  chunk  of  await  graph. stream( new Command({ resume: "John", update: { name: "foo" } }),  new  Command({ resume:  "John",  update:  { name:  "foo"  }  }),  config  config)) { ))  { console.log(chunk);  console. log(chunk);} }
```

```
{ __interrupt__: [{ { __interrupt__:  [{ value: 'what is your name?',  value:  'what is your name?', resumable: true,  resumable:  true, ns: ['human_node:3a007ef9-c30d-c357-1ec1-86a1a70d8fba'],  ns:  ['human_node:3a007ef9-c30d-c357-1ec1-86a1a70d8fba'], when: 'during'  when:  'during'}]} }]}Name: N/A. Age: John Name:  N/ A.  Age:  John{ human_node: { age: 'John', name: 'N/A' } } { human_node:  { age:  'John',  name:  'N/A'  }  }
```

## 附加资源 📚[¶](#additional-resources "Permanent link")

* [**概念指南：持久化**](../persistence/#replay)：阅读持久化指南以获取有关重放的更多上下文。
* [**操作指南：人机协作**](/langgraphjs/how-tos/#human-in-the-loop)：了解如何在 LangGraph 中实现人机协作工作流。
* [**如何实现多轮对话**](/langgraphjs/how-tos/multi-agent-multi-turn-convo)：了解如何在 LangGraph 中实现多轮对话。