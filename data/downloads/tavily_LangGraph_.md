[↓快轉到主要內容](#main-content)



# LangGraph: LangChain Agent 的殺手鐧 (進階)

[LangChain](/tags/langchain/) [LangGraph](/tags/langgraph/) [Agent](/tags/agent/)

目錄

[LangGraph](https://langchain-ai.github.io/langgraph/) 三部曲

* 入門: [LangGraph 是什麼？](https://ywctech.net/ml-ai/langchain-langgraph-agent-part1/)
* 進階: LangGraph 的特點
* 範例: [用 LangGraph 解 LeetCode](https://ywctech.net/ml-ai/write-leetcode-agent-in-langgraph/)

前一篇 LangGraph 的介紹，身為 **LangChain v0.2 主打的 Agent 框架**可不只如此！本篇內容很多，包括

* **State reduce**: 讓 LangGraph 自動合併 state
* **Super step & branching**: 同時執行多節點
* **Checkpointer**: 當個有記憶的 graph, 處理多使用者
* **Human-in-the-loop**: 中斷給人介入，驗證、竄改、時間旅行
* **聊天機器人**: 用 LangGraph 寫更清晰
* **開發注意事項**: 光看文件，不見得注意到
* **要不要用 LangGraph?** – 芙莉蓮告訴你

---

## Reduce state: 合併、不覆蓋 [#](#reduce-state-%e5%90%88%e4%bd%b5%e4%b8%8d%e8%a6%86%e8%93%8b)

前篇說：Node 回傳的 partial state 會把該 key 的值覆蓋。因此以下範例 最後結果是 `{"messages": [4]}` , 不是 `[1,2,3,4]`

```
class MyState(TypedDict): class MyState(TypedDict): class MyState messages: list  messages: list   def fn1(state: MyState): def fn1(state: MyState): def fn1 return {"messages": [4]}  return {"messages": [4]} return "messages" 4   # ... (ignore codes of start->fn1->end, blah blah) # ... (ignore codes of start->fn1->end, blah blah) # ... (ignore codes of start->fn1->end, blah blah)   r = graph.invoke({"messages": [1, 2, 3]}) r = graph.invoke({"messages": [1, 2, 3]}) =. "messages" 1 2 3
```

**如果你就是想要 `[1, 2, 3, 4]` 呢？**

一種方法：從 state 拿出現在的值，加工，然後回傳

```
def fn1(state: MyState): def fn1(state: MyState): def fn1 old = state.get("messages", [])  old = state.get("messages", []) =. "messages" return {"messages": old + [4]}  return {"messages": old + [4]} return "messages" + 4
```

但 LangGraph 提供了另一種方法：利用 python 的 [Annotated](https://docs.python.org/3/library/typing.html#typing.Annotated)

### Annotated 只是註釋 [#](#annotated-%e5%8f%aa%e6%98%af%e8%a8%bb%e9%87%8b)

Python 的 `typing.Annotated` 只是對於「型態」的一種「註釋」，執行時預設並無影響

```
salary: int # 就是個整數 salary: int # 就是個整數 # 就是個整數   # 宣告 tw_salary 不但是個 int # 宣告 tw_salary 不但是個 int # 宣告 tw_salary 不但是個 int # 而且良心註釋要比 27470 大 # 而且良心註釋要比 27470 大 # 而且良心註釋要比 27470 大tw_salary: Annotated[int, "must be > 27470"] tw_salary: Annotated[int, "must be > 27470"] "must be > 27470"   tw_salary = 22000 # 不會有事 tw_salary = 22000 # 不會有事 = 22000 # 不會有事
```

但是，程式可以拿到這個註釋！

```
Annotated[int, "must be > 27470"].__metadata__ Annotated[int, "must be > 27470"].__metadata__ "must be > 27470".# 拿到 tuple ('must be > 27470',) # 拿到 tuple ('must be > 27470',) # 拿到 tuple ('must be > 27470',)
```

所以 LangGraph 說：「你就用這手法**外掛你想要的函數**，反正掛了不影響執行，但我可以拿到它，用它做事！」

### LangGraph Reducer [#](#langgraph-reducer)

外掛怎麼用？先看解答

```
def concat_lists(original: list, new: list) -> list: def concat_lists(original: list, new: list) -> list: def concat_lists -> return original + new  return original + new return +   class MyState(TypedDict): class MyState(TypedDict): class MyState # messages: list  # messages: list # messages: list messages: Annotated[list, concat_lists]  messages: Annotated[list, concat_lists]   def fn1(state: MyState): def fn1(state: MyState): def fn1 return {"messages": [4]}  return {"messages": [4]} return "messages" 4   r = graph.invoke({"messages": [1, 2, 3]}) r = graph.invoke({"messages": [1, 2, 3]}) =. "messages" 1 2 3print(r) print(r) # 結果是 {'messages': [1, 2, 3, 4]} # 結果是 {'messages': [1, 2, 3, 4]} # 結果是 {'messages': [1, 2, 3, 4]}
```

* MyState 的 messages 宣告是 `Annotated`, 裡面掛著 function `concat_lists`
* `fn1` 回傳的是新元素 4 ，不是整串 1,2,3,4

---

`Annotated` 裡面，第一個是型態宣告，之後的是註釋。

以 schema 的每個 key 為單位，LangGraph 會先看過 key 的型態宣告

* 若有 Annotated 就拿注釋的第一個（例 `concat_lists` function ）
* 對於該 key，LangGraph 把**原來的 state** 跟 **node 回傳值** 一起加工：兩者丟進去那個 function，其回傳值將會是這個 key 的新 state

這行為叫 “**reduce**”: **新元素**如何跟**舊歷史**融合，變成**新的歷史**。例如儲存聊天記錄，最常見的 reduce 是一直附加上去，也就是範例的 `concat_lists`

記住，**這操作是以 key (channel) 為單位**。你能猜到下面執行的結果嗎？

```
class MyState(TypedDict): class MyState(TypedDict): class MyState v: int  v: int  total: Annotated[int, lambda x, y: x+y]  total: Annotated[int, lambda x, y: x+y] lambda +   def fn1(state: MyState): def fn1(state: MyState): def fn1 return {"v": 89, "total": 89}  return {"v": 89, "total": 89} return "v" 89 "total" 89   def fn2(state: MyState): def fn2(state: MyState): def fn2 return {"v": 64, "total": 64}  return {"v": 64, "total": 64} return "v" 64 "total" 64   workflow = StateGraph(MyState) workflow = StateGraph(MyState) =workflow.add_node(fn1) workflow.add_node(fn1) .workflow.add_node(fn2) workflow.add_node(fn2) .workflow.set_entry_point("fn1") workflow.set_entry_point("fn1") . "fn1"workflow.add_edge("fn1", "fn2") workflow.add_edge("fn1", "fn2") . "fn1" "fn2"workflow.add_edge("fn2", END) workflow.add_edge("fn2", END) . "fn2"   graph = workflow.compile() graph = workflow.compile() =.r = graph.invoke({"v": 0, "total": 0}) r = graph.invoke({"v": 0, "total": 0}) =. "v" 0 "total" 0# r == {'v': 64, 'total': 153} # r == {'v': 64, 'total': 153} # r == {'v': 64, 'total': 153}
```

### State call-by-什麼？ [#](#state-call-by-%e4%bb%80%e9%ba%bc)

雖然我覺得不要找自己麻煩，不過**如果你想在 node function 裡面直接更改 state** (而不是回傳覆蓋或 reduce)，先猜測下面兩個的結果

```
class MyState(TypedDict): class MyState(TypedDict): class MyState reassign: list  reassign: list  inplace: list  inplace: list   def fn1(state: MyState): def fn1(state: MyState): def fn1 state["reassign"] = [9, 8, 7]  state["reassign"] = [9, 8, 7] "reassign" = 9 8 7 state["inplace"].append(4)  state["inplace"].append(4) "inplace". 4  return None  return None return None   ... ... ...r = graph.invoke({ r = graph.invoke({ =. "reassign": [1, 2, 3],  "reassign": [1, 2, 3], "reassign" 1 2 3 "inplace": [1, 2, 3]  "inplace": [1, 2, 3] "inplace" 1 2 3}) })   print(r) print(r) # {'reassign': [1, 2, 3], 'inplace': [1, 2, 3, 4]} # {'reassign': [1, 2, 3], 'inplace': [1, 2, 3, 4]} # {'reassign': [1, 2, 3], 'inplace': [1, 2, 3, 4]}
```

這跟平常 python function 的行為一樣

（目前個人偏見：在 node function 裡更改 state 有點破壞「node 獨立執行、彼此通訊」的設計；state 不會只在 node 邊界被改變，可能未來 debug 會有點困難）

### State 總結與注意事項 [#](#state-%e7%b8%bd%e7%b5%90%e8%88%87%e6%b3%a8%e6%84%8f%e4%ba%8b%e9%a0%85)

* 若你想 state 的某個變數被自動合併 reduce（而非重新給值），用 Annotated 把 reducer function 掛在那個變數的型態宣告上
* 在 node function 裡直接改變 state 的行為跟 python 本身類似
* [前篇](https://ywctech.net/ml-ai/langchain-langgraph-agent-part1/)提的：如果 `StateGraph(state_schema=dict)`，不但沒有 Annotated 無法 reduce，而且任何一個步驟只要沒有回傳那個 key，他以前的值就會消失

那麼，要不要用 reducer 呢？

* reduce 的話，這個 key 的所有處理都自動經過 reducer，無需在每個 node 裡重寫同樣的程式加工
* 如果想臨時在某個 node 做不同處理，要額外花很多工夫（例如某個情況不想合併了，這樣的**邏輯要寫在同個 reducer 裡，且所有 node 都會這樣做**） (*Human-in-the-Loop 除外*)
* “Reduce” 這個心態，**讓每個 node 能獨立執行，不須理會別人在做啥！**（見下段）

總之，這取決於這個變數的本質，能否用同一種 reduce 的心態處理各種情境

關於 state, 有興趣追原始碼的可看 [langgraph state.py](https://github.com/langchain-ai/langgraph/blob/500a1abfeb3fcbdac18580f1c24ff774f077c686/langgraph/graph/state.py#L110)

## 同時執行多節點: Superstep [#](#%e5%90%8c%e6%99%82%e5%9f%b7%e8%a1%8c%e5%a4%9a%e7%af%80%e9%bb%9e-superstep)

前一篇說 LangGraph 是「程式裡寫程式」… 忘掉這個比喻！

### 輪到「你們」了 [#](#%e8%bc%aa%e5%88%b0%e4%bd%a0%e5%80%91%e4%ba%86)

一個點可以連去多個點，多個點也可以連到同一個點！

```
 graph.set_entry_point("n1")  graph.set_entry_point("n1") . "n1" graph.add_edge("n1", "n2")  graph.add_edge("n1", "n2") . "n1" "n2" graph.add_edge("n1", "n3")  graph.add_edge("n1", "n3") . "n1" "n3" graph.add_edge("n2", "n4")  graph.add_edge("n2", "n4") . "n2" "n4" graph.add_edge("n3", "n4")  graph.add_edge("n3", "n4") . "n3" "n4" graph.add_edge("n4", END)  graph.add_edge("n4", END) . "n4"
```

請看[完整程式碼](https://github.com/unclefomotw/lang-or-llama/blob/main/src/super_step/diamond.py)，猜猜執行結果是什麼？

答案是 `++1+2+3+4`，但執行的方法可能不是你想像的。這個 graph 只花了三步執行：

* 想像每個 node 都有旗子
* 當某個/群 node 執行完畢後，接下去連到的那個/群 node 都會舉起旗子（上一輪跑完的旗子放下來）。只要有舉旗子的 node, 下一「步驟」會同時**平行執行**
* Graph 執行的結束不是因為跑到 END, 而是**因為所有的 node 都不舉旗子**

有 `Annotated` reducer 才能讓 node 一連多。換句話說，當這步驟跑兩個 node 時，就是原有的 state 做兩次合併，reduce 兩個 node 回傳的結果，不會有誰蓋過誰的問題

由於一個步驟能跑一個或多個 node，所以稱作 **superstep**

如果你真的跑一遍程式碼，會發現更多

* 我在 n2 sleep 10 秒，n3 sleep 6 秒。因為同一個 superstep 裡面平行跑，所以 10 秒後 n4 執行
* 雖然印訊息是 n3 先印，但 n4 拿到的 state 裡面，不一定先更新 n3 回傳的：實際上 `++1+2+3+4`，是 n2 回傳的資料先更新到 state
* State 更新的順序理論上[不能預期](https://github.com/langchain-ai/langgraph/blob/500a1abfeb3fcbdac18580f1c24ff774f077c686/langgraph/channels/base.py#L65)。雖然實際應該是照 `add_node()` 的順序，但不要假設會這樣
* 如果更新的順序很重要，請參考[官方文件 Stable Sorting](https://langchain-ai.github.io/langgraph/how-tos/branching/#stable-sorting) : 自己多埋一個重要性的值，並多開一個 node 重新排序
* **n4 在這個例子只會執行一次**，因為同一個 superstep 的 n2 n3 後面都是緊接著 n4
* 看 `StateSnapshot` 的 `metadata.step` 可知進到此 node 是第幾個 superstep
* 開頭是 `++` 而不是 `+` 是因為有個隱性的 START node 先 reduce 了一次

### 多連一 不是你想像的 [#](#%e5%a4%9a%e9%80%a3%e4%b8%80-%e4%b8%8d%e6%98%af%e4%bd%a0%e6%83%b3%e5%83%8f%e7%9a%84)

請看另一個[完整程式碼](https://github.com/unclefomotw/lang-or-llama/blob/main/src/super_step/longshort.py)，猜猜結果？

```
 graph.set_entry_point("start")  graph.set_entry_point("start") . "start"    graph.add_edge("start", "left_1")  graph.add_edge("start", "left_1") . "start" "left_1" graph.add_edge("start", "right_1")  graph.add_edge("start", "right_1") . "start" "right_1" graph.add_edge("left_1", "merge")  graph.add_edge("left_1", "merge") . "left_1" "merge" graph.add_edge("right_1", "right_2")  graph.add_edge("right_1", "right_2") . "right_1" "right_2" graph.add_edge("right_2", "right_3")  graph.add_edge("right_2", "right_3") . "right_2" "right_3" graph.add_edge("right_3", "merge")  graph.add_edge("right_3", "merge") . "right_3" "merge" graph.add_edge("merge", END)  graph.add_edge("merge", END) . "merge"
```

同樣先一連二，往左邊一個點，往右邊三個點，最後會合。結果呢？

`++s+L1+R1+R2+m+R3+m`

右邊 (R) 還沒跑完，merge (m) 就先跑了，而且最終結果 merge 被執行兩次！為什麼？

* 對 “merge” 來說，left\_1 跟 right\_3 都是他的上游；當某個上游被執行到了以後，就通知下游「資料更新了，換你做事」
* 直到**所有的 node 都不會被輪到**，graph 才會結束。merge 第一次跑完後，下一步還有 right\_3 要跑，所以會繼續

前一個例子 n4 沒有跑兩次是因為，n2 跟 n3 通知 n4 的時候是在同一個 superstep。如此 LangGraph 只會在一個 superstep 內執行同一個 node 一次

### 我想 wait [#](#%e6%88%91%e6%83%b3-wait)

如果你想要 merge 「等待」，直到左邊跟右邊都跑完以後才執行，該怎麼做？

```
 graph.add_edge("start", "left_1")  graph.add_edge("start", "left_1") . "start" "left_1" graph.add_edge("start", "right_1")  graph.add_edge("start", "right_1") . "start" "right_1" graph.add_edge("right_1", "right_2")  graph.add_edge("right_1", "right_2") . "right_1" "right_2" graph.add_edge("right_2", "right_3")  graph.add_edge("right_2", "right_3") . "right_2" "right_3" graph.add_edge(["left_1", "right_3"], "merge") # 合成 list  graph.add_edge(["left_1", "right_3"], "merge") # 合成 list . "left_1" "right_3" "merge" # 合成 list graph.add_edge("merge", END)  graph.add_edge("merge", END) . "merge"
```

讓 left\_1 跟 right\_3 變成一個整體，變成 merge 的共同上游（[完整程式碼](https://github.com/unclefomotw/lang-or-llama/blob/main/src/super_step/longshort_wait.py)）

題外話，`add_edge()` 的第一個參數可以傳 list 代表多個 node (整體上游)，但第二個參數不能多個 node

---

最後，官方文件 [Branching](https://langchain-ai.github.io/langgraph/how-tos/branching/?h=superstep#parallel-node-fan-out-and-fan-in) 有更多厲害的模式

關於 super step, 有興趣追原始碼的可看 [langgraph pregel 實作](https://github.com/langchain-ai/langgraph/blob/500a1abfeb3fcbdac18580f1c24ff774f077c686/langgraph/pregel/__init__.py#L871)，

「程式裡寫程式 + state 是變數表」雖然好理解，但本質上，他們受 [Google Pregel](https://research.google/pubs/pregel-a-system-for-large-scale-graph-processing/) 的啟發， LangGraph 其實是利用節點間的通訊，分多步驟 (supersteps)，每一次 superstep 同步讓多節點利用 reduce 處理 state

搭配 [Subgraph](https://langchain-ai.github.io/langgraph/how-tos/subgraph/) 在實作 multi-agent 多代理人協作有優勢！

不過還沒完！下面兩個 LangGraph 支援的功能讓開發者可以套用到更多實務場景

## LangGraph 的記憶 checkpointer [#](#langgraph-%e7%9a%84%e8%a8%98%e6%86%b6-checkpointer)

* 在一次的執行中，graph 的流程跑到哪裡，可以被記錄下來
* 同個 graph 同個流程，可以有不同使用者 / session 去跑，也能各別記錄

checkpointer 就是拿來記錄這些資料，好比遊戲存檔，不同玩家不同場次，可以存起來，可以載入接關，甚至可以竄改更新！

一個最簡單用 checkpointer 的例子

```
from langgraph.checkpoint import MemorySaver from langgraph.checkpoint import MemorySaver from import   ... ... ...graph = workflow.compile( graph = workflow.compile( =. checkpointer=MemorySaver()  checkpointer=MemorySaver() =) )   config = {"configurable": {"thread_id": "John-9527"}} config = {"configurable": {"thread_id": "John-9527"}} = "configurable" "thread_id""John-9527"r = graph.invoke( r = graph.invoke( =. {"i": 1000, "j": 123},  {"i": 1000, "j": 123}, "i" 1000 "j" 123 config=config  config=config =) ) 
```

* graph compile 時多加 checkpointer 的物件：有很多種實作，例如 `MemorySaver`, `SqliteSaver` 等等
* config 是一個字典；`configurable` 跟 `thread_id` 這兩個字是寫死的
* **同個 `thread_id` 就像同個記錄檔一樣能接續；不同 `thread_id` 不會互相影響**
* graph 呼叫無論是 `.invoke()`, `.stream()` 等等，都可以表明哪一個 config

例如在 [多輪對話](https://ywctech.net/ml-ai/langchain-vs-llamaindex-rag-chat/)中，加入 checkpointer 記憶，只要使用同一個 config，就算是呼叫 graph 多次也不怕，對話記錄（甚至是 graph 一切的歷史狀態）都會存起來！

## 人工介入 Human-in-the-loop [#](#%e4%ba%ba%e5%b7%a5%e4%bb%8b%e5%85%a5-human-in-the-loop)

眾所周知 LLM 會幻想，如果相信 LLM 的指示做動作有時候很危險！你說「*如果能在流程中人工審查就好了*」，這就是 **Human-in-the-loop** (HITL)

LangGraph 達成 HITL 人工介入的方法是，在 `graph.compile()` 時傳入

* `interrupt_before=["node名", "node名", ...]` , 或
* `interrupt_after=["node名", "node名", ...]`

到那些 node 執行之前或之後，graph 的執行會先中斷（就算後面還有 node 要執行）

中斷以後，能繼續接關、竄改 state、從比較早的關卡繼續… 能做到這都是因為遊戲存檔：StateSnapshot

### StateSnapshot [#](#statesnapshot)

**graph 每個步驟執行後，都有一個 `StateSnapshot` 的物件**，把當時的 state, 接下來要往哪走等等的都記錄下來

每一步都留足跡，變成一個歷史的 list

必須要有 checkpointer 才能拿 snapshot 遊戲存檔：

* `graph.get_state(config)` 拿到最近一次的 state (snapshot)
* `graph.get_state_history(config)` 拿到所有 state (snapshots)，由舊到新

以下會列出各種招式的做法，不過先有個概念：無論 graph 流程你跳到哪個 node 看起來像回溯執行，StateSnapshot 都不會消失，歷史存檔是一直往後加的

### 招數：從中斷之處繼續 [#](#%e6%8b%9b%e6%95%b8%e5%be%9e%e4%b8%ad%e6%96%b7%e4%b9%8b%e8%99%95%e7%b9%bc%e7%ba%8c)

請務必對照[原始碼](https://github.com/unclefomotw/lang-or-llama/blob/main/src/hitl/2_resume.py) : `n1 -> n2 -> ... -> n6` 線性的 graph , 進 node 會印訊息，state 變數是 “crew” 的 list, 有 reducer

如果希望程式在 n3 之後先停下來，加 `interrupt_after`

```
graph = workflow.compile( graph = workflow.compile( =. checkpointer=MemorySaver(),  checkpointer=MemorySaver(), = interrupt_after=["n3"]  interrupt_after=["n3"] = "n3") ) 
```

執行 graph，會只看到一半的結果，而且從 state (snapshot) 看得出來下一個 node 是 “n4”

```
r = graph.invoke({"crew": []}, config=session(1)) r = graph.invoke({"crew": []}, config=session(1)) =. "crew" = 1print(f"Result: {r}") print(f"Result: {r}") f"Result: {} "print(graph.get_state(session(1))) print(graph.get_state(session(1))) . 1
```

```
## Resume Number 1 here! Number 2 here! Number 3 here! Result: {'crew': [1, 2, 3]} StateSnapshot(values={'crew': [1, 2, 3]}, next=('n4',), ... 
```

**要繼續很簡單，只要再呼叫 `.invoke()` 或 `.stream()` 傳 input=`None` 就好**

```
r = graph.invoke(None, config=session(1)) r = graph.invoke(None, config=session(1)) =. None = 1print(f"Result: {r}") # {'crew': [1, 2, 3, 4, 5, 6]} print(f"Result: {r}") # {'crew': [1, 2, 3, 4, 5, 6]} f"Result: {} "# {'crew': [1, 2, 3, 4, 5, 6]}
```

六個點都跑完，next 是空的表示沒有需要跑的了

如果中斷以後，硬是傳一個不是 `None` 的呢？這就單純表示你想重新呼叫這個 graph 而已

```
r = graph.invoke({"crew": []}, config=session(2)) r = graph.invoke({"crew": []}, config=session(2)) =. "crew" = 2 # Calling with a new input just starts it over # Calling with a new input just starts it over # Calling with a new input just starts it overr = graph.invoke({"crew": [66, 77]}, config=session(2)) r = graph.invoke({"crew": [66, 77]}, config=session(2)) =. "crew" 66 77 = 2
```

```
Number 1 here! Number 2 here! Number 3 here! Result: {'crew': [1, 2, 3]} Number 1 here! Number 2 here! Number 3 here! Result: {'crew': [1, 2, 3, 66, 77, 1, 2, 3]} 
```

第一次跑的 1,2,3 因為有 checkpointer 紀錄所以還在，第二次呼叫初始傳入的 66,77 是重新一輪，所以從起點跑到 n3 又中斷了

### 招數：回到過去 [#](#%e6%8b%9b%e6%95%b8%e5%9b%9e%e5%88%b0%e9%81%8e%e5%8e%bb)

請務必對照[原始碼](https://github.com/unclefomotw/lang-or-llama/blob/main/src/hitl/3_travel_to_past.py)

我們傳入的所謂 “config” 目前只有 `thread_id`，有點像表明他是哪個使用者 / session

不過如果你有真的執行上一個程式的話，會看到 `StateSnapshot` 裡的 config 還多了 `thread_ts` 的欄位：這是在**哪一步、哪個時間**的意思

```
StateSnapshot(..., config={'configurable': {'thread_id': '1', 'thread_ts': '1ef2985c-bed5-6dee-8003-6037939ae5aa'}}, ...) 
```

所以在同一個 thread\_id 的 state history 裡面，有很多的 StateSnapshot，每一個的 `thread_ts` 都不同：我們可以找到想要回溯的那個步驟，重新執行

```
# 找到下一步是 "n2" 的那個 state, 裡面的 config / thread_ts # 找到下一步是 "n2" 的那個 state, 裡面的 config / thread_ts # 找到下一步是 "n2" 的那個 state, 裡面的 config / thread_ts # 也就是 "n1" 的 # 也就是 "n1" 的 # 也就是 "n1" 的 # 不知為什麼 LangGraph 不把 "n1" 也加入 StateSnapshot 裡的某個欄位，例如 source 或 present 之類的 # 不知為什麼 LangGraph 不把 "n1" 也加入 StateSnapshot 裡的某個欄位，例如 source 或 present 之類的 # 不知為什麼 LangGraph 不把 "n1" 也加入 StateSnapshot 裡的某個欄位，例如 source 或 present 之類的   for h in graph.get_state_history(session(1)): for h in graph.get_state_history(session(1)): for in. 1 if h.next == ("n2", ):  if h.next == ("n2", ): if. == "n2" past_config = h.config  past_config = h.config =.  break  break break
```

上面的 past\_config 就是有 thread\_ts 的 config，代表過去的那個時間點

我們要「回到過去」執行 graph，只要把含有 thread\_ts 的 config 傳入 `.invoke()` 或 `.stream()` 就好

```
# Rewind: resume from the past # Rewind: resume from the past # Rewind: resume from the pastfor s in graph.stream( for s in graph.stream( for in. input=None,  input=None, = None config=past_config, # <--  config=past_config, # <-- =# <-- stream_mode="values"  stream_mode="values" = "values"): ):  print(s)  print(s) 
```

```
Number 2 here! {'crew': [1, 2]} Number 3 here! {'crew': [1, 2, 3]} 
```

就算 input 是 `None`，並不是做 4,5,6 而是回溯到 n1 做完以後的那個時間點接續（而且 n1 做過的事情不會消滅，所以有 1）所以是 1,2,3 … 然後又 interrupt 了

### 招數：改變現在 [#](#%e6%8b%9b%e6%95%b8%e6%94%b9%e8%ae%8a%e7%8f%be%e5%9c%a8)

請務必對照[原始碼](https://github.com/unclefomotw/lang-or-llama/blob/main/src/hitl/4_update.py)

* State 現在有會 reduce 的 `crew` 跟沒有 reduce (直接覆蓋) 的 `v`
* Node function 除了會附加 `crew` 以外，還會印出前面一個 node 給過來的 `v` 是什麼

graph 執行中斷以後，如果覺得 state 裡面的值不對，想要更改，可以用 `update_state`

```
graph.update_state( graph.update_state( . config=session(1),  config=session(1), = 1 values={"crew": [66, 77], "v": "BAD GUY"}  values={"crew": [66, 77], "v": "BAD GUY"} = "crew" 66 77 "v" "BAD GUY") ) 
```

從頭執行、到中斷、再到更改、最後接關的結果如下

```
Number 1 sees None coming in Number 2 sees No. 1 coming in Number 3 sees No. 2 coming in Result: {'v': 'No. 3', 'crew': [1, 2, 3]} StateSnapshot(values={'v': 'No. 3', 'crew': [1, 2, 3]}, next=('n4',), ... 'step': 3 ...) >> after update StateSnapshot(values={'v': 'BAD GUY', 'crew': [1, 2, 3, 66, 77]}, next=('n4',), ... 'step': 4 ...) >> resume Number 4 sees BAD GUY coming in Number 5 sees No. 4 coming in Number 6 sees No. 5 coming in Result: {'v': 'No. 6', 'crew': [1, 2, 3, 66, 77, 4, 5, 6]} 
```

嚴格講，「改變現在」不是把最後一步竄改掉，而是「安插」步驟（看兩個 snapshot 的 `step` 數字），所以**如果更新的 state 是有 reducer 的，會連之前的 state 一起 reduce** – 要看看這是否符合你的使用情境！！

所以 crew 最後的結果是 1,2,3 (中斷前) + 66,77 (更新的那個) + 4,5,6 (接續下去)

沒有 reducer 的 state，像是 `v` 就沒這個問題： n4 接收到的 state 是 BAD GUY，他無法知道 n3 原本回傳什麼

好的，如果你真的有看原始碼，會發現我用了兩個寫法，第二個是用「回到過去」的手法，拿到最新的那個 thread\_ts。然而，兩種執行方法沒有差別，因為「現在」就是那個 thread\_ts。不過…

### 招數：竄改過去 [#](#%e6%8b%9b%e6%95%b8%e7%ab%84%e6%94%b9%e9%81%8e%e5%8e%bb)

請務必對照[原始碼](https://github.com/unclefomotw/lang-or-llama/blob/main/src/hitl/5_rewrite_past.py)

「過去」有「過去的時間點」跟「過去的 node」

啊？

先看例子跟結果好了

```
# 找到過去的「時間」 # 找到過去的「時間」 # 找到過去的「時間」for h in graph.get_state_history(session(1)): for h in graph.get_state_history(session(1)): for in. 1 if h.next == ("n2",):  if h.next == ("n2",): if. == "n2" past_config = h.config  past_config = h.config =.  break  break break   graph.update_state( graph.update_state( . config=past_config, # 從過去的時間開始跑  config=past_config, # 從過去的時間開始跑 = # 從過去的時間開始跑 values={"crew": [66, 77], "v": "BAD GUY"}  values={"crew": [66, 77], "v": "BAD GUY"} = "crew" 66 77 "v" "BAD GUY") ) 
```

```
Number 1 sees None coming in Number 2 sees No. 1 coming in Number 3 sees No. 2 coming in >> resume Number 2 sees BAD GUY coming in Number 3 sees No. 2 coming in Result: {'v': 'No. 3', 'crew': [1, 66, 77, 2, 3]} 
```

上面的作法跟「回到過去」一樣，拿到 “n2” 的**時間點**，就 crew 的值來說，**歷史被抹滅**，從 `[1, 2, 3]` 變成 `[1]`

然後從哪一個 node 往後開始執行呢？預設是傳給 `.update_config()` 的時間點的當時跑到的 node，也就是 “n2”

所以在附加 `[66, 77]` 以後，resume 接續下去的跑 “n2”… 就是附加 `[2, 3]` （然後中斷）

好像很顯然？這應該是大部分人想的竄改過去。然而有另一種：

```
graph.update_state( graph.update_state( . config=session(2), # 傳「現在」的時間點  config=session(2), # 傳「現在」的時間點 = 2 # 傳「現在」的時間點 values={"crew": [66, 77], "v": "BAD GUY"},  values={"crew": [66, 77], "v": "BAD GUY"}, = "crew" 66 77 "v" "BAD GUY" as_node="n1" # 但是當作從 n1 「node」 開始跑  as_node="n1" # 但是當作從 n1 「node」 開始跑 = "n1" # 但是當作從 n1 「node」 開始跑) ) 
```

```
Number 1 sees None coming in Number 2 sees No. 1 coming in Number 3 sees No. 2 coming in >> resume Number 2 sees BAD GUY coming in Number 3 sees No. 2 coming in Result: {'v': 'No. 3', 'crew': [1, 2, 3, 66, 77, 2, 3]} 
```

因為 config 傳的是沒有 `thread_ts` 的，意味著「時間」是現在，歷史沒有被抹滅

但是多傳了一個 `as_node="n1"`：這表示，這個 update state **像是從 n1 node 安插的更新**

所以 crew 最後的結果是 1,2,3 (中斷前) + 66,77 (更新的那個) + 2,3 (從 n1 接續下去，然後中斷)

簡單說，`.update_state(config=..., as_node=...)`

* `config` 代表**時間點**；過去的哪個步驟開始蓋掉（不要忘了 State History 永遠不滅，只是看起來像蓋掉）
* `as_node` 代表**哪裡**；從哪一個 node 接續下去

這兩個甚至可以混用（原始碼的 Case 3），有點複雜就不在這提了

---

到目前為止都還沒用到 LLM，學了這麼多，該實戰了吧！

## 用 LangGraph 做 LLM 聊天 [#](#%e7%94%a8-langgraph-%e5%81%9a-llm-%e8%81%8a%e5%a4%a9)

用 LangGraph 做多輪對話的聊天機器人

```
from typing import TypedDict, Annotated from typing import TypedDict, Annotated from importfrom langchain_core.messages import HumanMessage from langchain_core.messages import HumanMessage from import from langchain_openai import ChatOpenAI from langchain_openai import ChatOpenAI from importfrom langgraph.checkpoint import MemorySaver from langgraph.checkpoint import MemorySaver from importfrom langgraph.graph import StateGraph from langgraph.graph import StateGraph from import   llm = ChatOpenAI() llm = ChatOpenAI() =   def concat(original: list, new: list) -> list: def concat(original: list, new: list) -> list: def concat -> return original + new  return original + new return +   class ChatState(TypedDict): class ChatState(TypedDict): class ChatState messages: Annotated[list, concat]  messages: Annotated[list, concat]   def chat(state: ChatState): def chat(state: ChatState): def chat answer = llm.invoke(state["messages"])  answer = llm.invoke(state["messages"]) =. "messages" return {"messages": [answer]}  return {"messages": [answer]} return "messages"   workflow = StateGraph(ChatState) workflow = StateGraph(ChatState) =workflow.add_node(chat) workflow.add_node(chat) .workflow.set_entry_point("chat") workflow.set_entry_point("chat") . "chat"workflow.add_edge("chat", "__end__") workflow.add_edge("chat", "__end__") . "chat" "__end__"graph = workflow.compile(checkpointer=MemorySaver()) graph = workflow.compile(checkpointer=MemorySaver()) =. =   config = {"configurable": {"thread_id": "1"}} config = {"configurable": {"thread_id": "1"}} = "configurable" "thread_id" "1"while True: while True: while True user_input = input(">>> ")  user_input = input(">>> ") =">>> " r = graph.invoke(  r = graph.invoke( =. {"messages": [HumanMessage(user_input)]},  {"messages": [HumanMessage(user_input)]}, "messages" config=config  config=config = )  )  print("AI: " + r["messages"][-1].content)  print("AI: " + r["messages"][-1].content) "AI: " + "messages" - 1.
```

只要這樣，結束。每次使用者先講話 `>>>` ，然後 `AI:` 回應

```
>>> What is the total sum from 1 to 10? AI: The total sum from 1 to 10 is 55. >>> How about 100? AI: The total sum from 1 to 100 is 5050. >>> 
```

第二次問答看得出聊天有歷史記錄：就算只問「那 100 呢？」ChatGPT 也知道你的意思是「那 1 加到 100 呢？」

**想要更高深的範例？** 請看下一篇 LeetCode 解題機器人，[或是看原始碼](https://github.com/unclefomotw/lang-or-llama/tree/main/src/leetcode_agent)先

但就算是簡單的 chatbot，也有一些能學的：

* 這沒有用 interrupt 之類的 HITL。單純就是不斷呼叫 graph，利用 checkpointer + reducer 記錄聊天歷史
* 沒錯，就算 graph 執行結束 checkpointer 還是會保留，下次呼叫 graph 仍然不斷累積
* 因為 state 是所有的聊天記錄，所以印 AI 的回答只印最後一條 `r["messages"][-1]`
* 「記錄聊天應該要附加 一句人類的 跟 一條 AI 的，可是只有 `chat` 一個 node 在 reduce AI 訊息耶？」
  + 因為有個 node 叫 `START` ; `set_entry_point()` 其實是把 `START` 連到 `chat`
  + 呼叫 graph 時會先跑 `START`：把 `graph.invoke()` 的輸入寫進去 reduce 到 state 裡：在這個例子就是人類的訊息
  + 所以更前面的例子，輸出的開頭才會是兩個加號 `++1+2+3+4`，因為 `START` 先 reduce 了（空白字串）輸入，先加了一個加號
* 你在其他文件應該會看到 `from langgraph.graph.message import add_messages` ，這 reducer 跟 list 相加 87% 像，只不過處理了更多特例
* 附有 debug 功能的[原始碼在這](https://github.com/unclefomotw/lang-or-llama/blob/main/src/langgraph_chatbot.py#L10)，可以把 `_debug` 打開自行跑一遍

---

LangGraph 的功能還很多，[官方文件](https://langchain-ai.github.io/langgraph/tutorials/)是寶庫，先介紹到這。我反而想講開發的感想

## LangGraph 開發注意事項 [#](#langgraph-%e9%96%8b%e7%99%bc%e6%b3%a8%e6%84%8f%e4%ba%8b%e9%a0%85)

當你 `StateGraph` 的 `state_schema` 是 `TypedDict` 時

* 如果 node 回傳 `state_schema` 沒有的 key，不會因此新增那個 key 給 state，但是框架也不會報錯
* 所以回傳**打錯字時會很嚴重：沒作用又沒報錯**
* 可以考慮 `pydantic.BaseModel`

如果 `state_schema` 是 `pydantic.BaseModel`，當有多個 key / member 時，變相不能「只回傳部分的 key」，除非

* BaseModel 的初始值要表明 (例如 `i: Optional[int] = None` )，這是 pydantic 本身的特性
* 或者是「混搭」：在 node function 裡回傳 dict 而不是 `BaseModel` 物件（對，你可以這樣，LangGraph 會 coerce 過去 ）

edge 能讀 state 但不會去改 state

## Best practice [#](#best-practice)

不，我沒有 best practice (被打)，但我覺得這是社群可共同建立的

### Logic leak [#](#logic-leak)

流程「決定」要做在哪？是 Conditional edge 還是一個 node？

邊界在哪？State 要裝控制 flag 嗎？跟邏輯大小、影響 state 與否有關？

### 程式裡寫程式：Graph 內或外？ [#](#%e7%a8%8b%e5%bc%8f%e8%a3%a1%e5%af%ab%e7%a8%8b%e5%bc%8fgraph-%e5%85%a7%e6%88%96%e5%a4%96)

Human-in-the-Loop: 要用 interrupt-before/after 或者是做在一個 node 裡？如果不時間旅行 undo 的話

要塞多少東西在 Graph 裡？哪些是寫在 Graph 外的？

## But, Why LangGraph [#](#but-why-langgraph)

「一定要用 LangGraph 嗎？」可能才是最重要的問題。LangGraph 有它的好處：

### Flow engineering [#](#flow-engineering)

Flow engineering 是把問題解法拆成多個階段、單目的、逐步迭代改進，包括自我測試、生成等等

這概念不能說新穎，不過最近 [CodiumAI](https://www.codium.ai/) 在他們的論文 [AlphaCodium 程式生成](https://arxiv.org/pdf/2401.08500)，讓社群又注意到了 Flow engineering 的重要性

以下圖片摘自 CodiumAI 的論文 <https://arxiv.org/pdf/2401.08500>

LangGraph 的設計理念與 flow engineering 不謀而合。而且某種角度，也強迫開發者以 unit/modular 心態去開發

### 既有實用功能 [#](#%e6%97%a2%e6%9c%89%e5%af%a6%e7%94%a8%e5%8a%9f%e8%83%bd)

State machine + persistence + human-in-the-loop (state snapshot, update state, undo, …)

雖然在簡單的情境下，這些提供的功能會被高估，但反過來當情境複雜的時候就很有用了。例如分岔融合，就不用自己維護 queue 或 graph

### Observability [#](#observability)

Debug 方便 – [LangSmith](https://www.langchain.com/langsmith) 是 LangChain 生態系自家的 instrumentation 工具，能夠輕易檢查執行的 graph/chain 裡面的 LLM API 的 input 與 output，以及各個 node 流程與 state

### 但是 [#](#%e4%bd%86%e6%98%af)

* 上面那些有用到嗎？例如，流程真的複雜嗎？抑或只有兩個線性 LLM call 結束？
* 反過來，如果流程太自由複雜，LangGraph 這種預先 compile 非動態決定流程的，光靠 conditional edge 是否能方便實作？
* 概念通了以後，自己做花多少時間？自己累積的函式庫夠不夠深？
* LangChain / LangGraph 學起來有障礙嗎？
* LangChain 快速迭代下，願意保持版本而自加功能，或更新版本冒著不相容的風險嗎？

---

總之， [下一篇](https://ywctech.net/ml-ai/write-leetcode-agent-in-langgraph/) 讓我分享用 LangGraph 解 Leetcode 吧！

若您覺得有趣, 請 [追蹤我的Facebook](https://www.facebook.com/ywchen88/) 或  [Linkedin](https://www.linkedin.com/in/yi-wei-chen/), 讓你獲得更多資訊！

測試版本: LangGraph 0.0.65 (+LangChain 0.2.3) 抱怨一下，他們版本真的跑太快了