# Add and manage memory - Docs by LangChain

**URL**:
https://docs.langchain.com/oss/javascript/langgraph/add-memory

## 元数据
- 发布日期: 2025-05-05T00:00:00+00:00

## 完整内容
---
> Fetch the complete documentation index at: https://docs.langchain.com/llms.txt
> Use this file to discover all available pages before exploring further.
> 
> ## Documentation Index

# Memory

AI applications need [memory] to share context across multiple interactions. In LangGraph, you can add two types of memory:

- [Add long-term memory] to store user-specific or application-level data across sessions.
- [Add short-term memory] as a part of your agent's [state] to enable multi-turn conversations.

## Add short-term memory

Short-term memory (thread-level [persistence]) enables agents to track multi-turn conversations. To add short-term memory:

```typescript
import { MemorySaver, StateGraph } from "@langchain/langgraph";

const checkpointer = new MemorySaver();

const builder = new StateGraph(...);
const graph = builder.compile({ checkpointer });

await graph.invoke(
  { messages: [{ role: "user", content: "hi! i am Bob" }] },
  { configurable: { thread_id: "1" } }
);

```

### Use in production

In production, use a checkpointer backed by a database:

```typescript
import { PostgresSaver } from "@langchain/langgraph-checkpoint-postgres";

const DB_URI = "postgresql://postgres:postgres@localhost:5442/postgres?sslmode=disable";
const checkpointer = PostgresSaver.fromConnString(DB_URI);

const builder = new StateGraph(...);
const graph = builder.compile({ checkpointer });

```

## Example: using Postgres checkpointer

```
npm install @langchain/langgraph-checkpoint-postgres

```

You need to call `checkpointer.setup()` the first time you're using Postgres checkpointer

```typescript
import { ChatAnthropic } from "@langchain/anthropic";
import { StateGraph, StateSchema, MessagesValue, GraphNode, START } from "@langchain/langgraph";
import { PostgresSaver } from "@langchain/langgraph-checkpoint-postgres";

const State = new StateSchema({
  messages: MessagesValue,
});

const model = new ChatAnthropic({ model: "claude-haiku-4-5-20251001" });

const DB_URI = "postgresql://postgres:postgres@localhost:5442/postgres?sslmode=disable";
const checkpointer = PostgresSaver.fromConnString(DB_URI);
// await checkpointer.setup();

const callModel: GraphNode<typeof State> = async (state) => {
  const response = await model.invoke(state.messages);
  return { messages: [response] };
};

const builder = new StateGraph(State)
  .addNode("call_model", callModel)
  .addEdge(START, "call_model");

const graph = builder.compile({ checkpointer });

const config = {
  configurable: {
    thread_id: "1"
  }
};

for await (const chunk of await graph.stream(
  { messages: [{ role: "user", content: "hi! I'm bob" }] },
  { ...config, streamMode: "values" }
)) {
  console.log(chunk.messages.at(-1)?.content);
}

for await (const chunk of await graph.stream(
  { messages: [{ role: "user", content: "what's my name?" }] },
  { ...config, streamMode: "values" }
)) {
  console.log(chunk.messages.at(-1)?.content);
}

```

### Use in subgraphs

If your graph contains [subgraphs], you only need to provide the checkpointer when compiling the parent graph. LangGraph will automatically propagate the checkpointer to the child subgraphs.

```typescript
import { StateGraph, StateSchema, START, MemorySaver } from "@langchain/langgraph";
import { z } from "zod/v4";

const State = new StateSchema({ foo: z.string() });

const subgraphBuilder = new StateGraph(State)
  .addNode("subgraph_node_1", (state) => {
    return { foo: state.foo + "bar" };
  })
  .addEdge(START, "subgraph_node_1");
const subgraph = subgraphBuilder.compile();

const builder = new StateGraph(State)
  .addNode("node_1", subgraph)
  .addEdge(START, "node_1");

const checkpointer = new MemorySaver();
const graph = builder.compile({ checkpointer });

```

If you want the subgraph to have its own memory, you can compile it with the appropriate checkpointer option. This is useful in [multi-agent] systems, if you want agents to keep track of their internal message histories.

```typescript
const subgraphBuilder = new StateGraph(...);
const subgraph = subgraphBuilder.compile({ checkpointer: true });  // [!code highlight]

```

## Add long-term memory

Use long-term memory to store user-specific or application-specific data across conversations.

```typescript
import { InMemoryStore, StateGraph } from "@langchain/langgraph";

const store = new InMemoryStore();

const builder = new StateGraph(...);
const graph = builder.compile({ store });

```

### Access the store inside nodes

Once you compile a graph with a store, LangGraph automatically injects the store into your node functions. The recommended way to access the store is through the `Runtime` object.

```typescript
import { StateGraph, StateSchema, MessagesValue, GraphNode, START } from "@langchain/langgraph";
import { v4 as uuidv4 } from "uuid";

const State = new StateSchema({
  messages: MessagesValue,
});

const callModel: GraphNode<typeof State> = async (state, runtime) => {
  const userId = runtime.context?.userId;
  const namespace = [userId, "memories"];

  // Search for relevant memories
  const memories = await runtime.store?.search(namespace, {
    query: state.messages.at(-1)?.content,
    limit: 3,
  });
  const info = memories?.map((d) => d.value.data).join("\n") || "";

  // ... Use memories in model call

  // Store a new memory
  await runtime.store?.put(namespace, uuidv4(), { data: "User prefers dark mode" });
};

const builder = new StateGraph(State)
  .addNode("call_model", callModel)
  .addEdge(START, "call_model");
const graph = builder.compile({ store });

// Pass context at invocation time
await graph.invoke(
  { messages: [{ role: "user", content: "hi" }] },
  { configurable: { thread_id: "1" }, context: { userId: "1" } }
);

```

### Use in production

In production, use a store backed by a database:

```typescript
import { PostgresStore } from "@langchain/langgraph-checkpoint-postgres/store";

const DB_URI = "postgresql://postgres:postgres@localhost:5442/postgres?sslmode=disable";
const store = PostgresStore.fromConnString(DB_URI);

const builder = new StateGraph(...);
const graph = builder.compile({ store });

```

## Example: using Postgres store

```
npm install @langchain/langgraph-checkpoint-postgres

```

You need to call `store.setup()` the first time you're using Postgres store

```typescript
import { ChatAnthropic } from "@langchain/anthropic";
import { StateGraph, StateSchema, MessagesValue, GraphNode, START } from "@langchain/langgraph";
import { PostgresSaver } from "@langchain/langgraph-checkpoint-postgres";
import { PostgresStore } from "@langchain/langgraph-checkpoint-postgres/store";
import { v4 as uuidv4 } from "uuid";

const State = new StateSchema({
  messages: MessagesValue,
});

const model = new ChatAnthropic({ model: "claude-haiku-4-5-20251001" });

const callModel: GraphNode<typeof State> = async (state, runtime) => {
  const userId = runtime.context?.userId;
  const namespace = ["memories", userId];
  const memories = await runtime.store?.search(namespace, { query: state.messages.at(-1)?.content });
  const info = memories?.map(d => d.value.data).join("\n") || "";
  const systemMsg = `You are a helpful assistant talking to the user. User info: ${info}`;

  // Store new memories if the user asks the model to remember
  const lastMessage = state.messages.at(-1);
  if (lastMessage?.content?.toLowerCase().includes("remember")) {
    const memory = "User name is Bob";
    await runtime.store?.put(namespace, uuidv4(), { data: memory });
  }

  const response = await model.invoke([
    { role: "system", content: systemMsg },
    ...state.messages
  ]);
  return { messages: [response] };
};

const DB_URI = "postgresql://postgres:postgres@localhost:5442/postgres?sslmode=disable";

const store = PostgresStore.fromConnString(DB_URI);
const checkpointer = PostgresSaver.fromConnString(DB_URI);
// await store.setup();
// await checkpointer.setup();

const builder = new StateGraph(State)
  .addNode("call_model", callModel)
  .addEdge(START, "call_model");

const graph = builder.compile({
  checkpointer,
  store,
});

for await (const chunk of await graph.stream(
  { messages: [{ role: "user", content: "Hi! Remember: my name is Bob" }] },
  { configurable: { thread_id: "1" }, context: { userId: "1" }, streamMode: "values" }
)) {
  console.log(chunk.messages.at(-1)?.content);
}

for await (const chunk of await graph.stream(
  { messages: [{ role: "user", content: "what is my name?" }] },
  { configurable: { thread_id: "2" }, context: { userId: "1" }, streamMode: "values" }
)) {
  console.log(chunk.messages.at(-1)?.content);
}

```

### Use semantic search

Enable semantic search in your graph's memory store to let graph agents search for items in the store by semantic similarity.

```typescript
import { OpenAIEmbeddings } from "@langchain/openai";
import { InMemoryStore } from "@langchain/langgraph";

// Create store with semantic search enabled
const embeddings = new OpenAIEmbeddings({ model: "text-embedding-3-small" });
const store = new InMemoryStore({
  index: {
    embeddings,
    dims: 1536,
  },
});

await store.put(["user_123", "memories"], "1", { text: "I love pizza" });
await store.put(["user_123", "memories"], "2", { text: "I am a plumber" });

const items = await store.search(["user_123", "memories"], {
  query: "I'm hungry",
  limit: 1,
});

```

## Long-term memory with semantic search

```typescript
import { OpenAIEmbeddings, ChatOpenAI } from "@langchain/openai";
import { StateGraph, StateSchema, MessagesValue, GraphNode, START, InMemoryStore } from "@langchain/langgraph";

const State = new StateSchema({
  messages: MessagesValue,
});

const model = new ChatOpenAI({ model: "gpt-4.1-mini" });

// Create store with semantic search enabled
const embeddings = new OpenAIEmbeddings({ model: "text-embedding-3-small" });
const store = new InMemoryStore({
  index: {
    embeddings,
    dims: 1536,
  }
});

await store.put(["user_123"


---
*数据来源: Exa搜索 | 获取时间: 2026-02-19 10:55:13*