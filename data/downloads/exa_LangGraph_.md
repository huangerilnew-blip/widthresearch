# LangGraph: LangChain Agent 的殺手鐧(進階) - YWC 科技筆記

**URL**:
https://ywctech.net/ml-ai/langchain-langgraph-agent-part2/

## 元数据
- 发布日期: 2024-06-13T00:00:00+00:00

## 完整内容
---
LangGraph 三部曲 入門:
 LangGraph 是什麼？ 進階: LangGraph 的特點 範例:
 用 LangGraph 解 LeetCode 前一篇 LangGraph 的介紹，身為 LangChain v0.2 主打的 Agent 框架 可不只如此！本篇內容很多，包括 State reduce: 讓 LangGraph 自動合併 state Super step &amp; branching: 同時執行多節點 Checkpointer: 當個有記憶的 graph, 處理多使用者 Human-in-the-loop: 中斷給人介入，驗證、竄改、時間旅行 聊天機器人: 用 LangGraph 寫更清晰 開發注意事項: 光看文件，不見得注意到 要不要用 LangGraph? – 芙莉蓮告訴你 可用目錄連結跳著看！ Reduce state: 合併、不覆蓋 # 前篇說：Node 回傳的 partial state 會把該 key 的值覆蓋。因此以下範例
最後結果是 {"messages": [4]} , 不是 [1,2,3,4] class MyState (TypedDict):
 messages: list
 
 def fn1 (state: MyState):
 return { "messages": [ 4]}
 
 # ... (ignore codes of start-&gt;fn1-&gt;end, blah blah) 
 
 r = graph. invoke({ "messages": [ 1, 2, 3]})
 如果你就是想要 [1, 2, 3, 4] 呢？ 一種方法：從 state 拿出現在的值，加工，然後回傳 def fn1 (state: MyState):
 old = state. get( "messages", [])
 return { "messages": old + [ 4]}
 但 LangGraph 提供了另一種方法：利用 python 的 Annotated Annotated 只是註釋 # Python 的 typing.Annotated 只是對於「型態」的一種「註釋」，執行時預設並無影響 salary: int # 就是個整數 
 
 # 宣告 tw_salary 不但是個 int 
 # 而且良心註釋要比 27470 大 
 tw_salary: Annotated[int, "must be &gt; 27470"]
 
 tw_salary = 22000 # 不會有事 
 但是，程式可以拿到這個註釋！ Annotated[int, "must be &gt; 27470"]. __metadata__
 # 拿到 tuple ('must be &gt; 27470',) 
 所以 LangGraph 說：「你就用這手法 外掛你想要的函數 ，反正掛了不影響執行，但我可以拿到它，用它做事！」 LangGraph Reducer # 外掛怎麼用？先看解答 def concat_lists (original: list, new: list) -&gt; list:
 return original + new
 
 class MyState (TypedDict):
 # messages: list 
 messages: Annotated[list, concat_lists]
 
 def fn1 (state: MyState):
 return { "messages": [ 4]}
 
 r = graph. invoke({ "messages": [ 1, 2, 3]})
 print(r)
 # 結果是 {'messages': [1, 2, 3, 4]} 
 MyState 的 messages 宣告是 Annotated, 裡面掛著 function concat_lists fn1 回傳的是新元素 4 ，不是整串 1,2,3,4 Annotated 裡面，第一個是型態宣告，之後的是註釋。 以 schema 的每個 key 為單位，LangGraph 會先看過 key 的型態宣告 若有 Annotated 就拿注釋的第一個（例 concat_lists function ） 對於該 key，LangGraph 把 原來的 state 跟 node 回傳值 一起加工：兩者丟進去那個 function，其回傳值將會是這個 key 的新 state 這行為叫 “ reduce ”: 新元素 如何跟 舊歷史 融合，變成 新的歷史 。例如儲存聊天記錄，最常見的 reduce 是一直附加上去，也就是範例的 concat_lists 記住， 這操作是以 key (channel) 為單位 。你能猜到下面執行的結果嗎？ class MyState (TypedDict):
 v: int
 total: Annotated[int, lambda x, y: x + y]
 
 def fn1 (state: MyState):
 return { "v": 89, "total": 89}
 
 def fn2 (state: MyState):
 return { "v": 64, "total": 64}
 
 workflow = StateGraph(MyState)
 workflow. add_node(fn1)
 workflow. add_node(fn2)
 workflow. set_entry_point( "fn1")
 workflow. add_edge( "fn1", "fn2")
 workflow. add_edge( "fn2", END)
 
 graph = workflow. compile()
 r = graph. invoke({ "v": 0, "total": 0})
 # r == {'v': 64, 'total': 153} 
 State call-by-什麼？ # 雖然我覺得不要找自己麻煩，不過 如果你想在 node function 裡面直接更改 state (而不是回傳覆蓋或 reduce)，先猜測下面兩個的結果 class MyState (TypedDict):
 reassign: list
 inplace: list
 
 def fn1 (state: MyState):
 state[ "reassign"] = [ 9, 8, 7]
 state[ "inplace"]. append( 4)
 return None 
 
... 
 r = graph. invoke({
 "reassign": [ 1, 2, 3],
 "inplace": [ 1, 2, 3]
})
 
 print(r)
 # {'reassign': [1, 2, 3], 'inplace': [1, 2, 3, 4]} 
 這跟平常 python function 的行為一樣 （目前個人偏見：在 node function 裡更改 state 有點破壞「node 獨立執行、彼此通訊」的設計；state 不會只在 node 邊界被改變，可能未來 debug 會有點困難） State 總結與注意事項 # 若你想 state 的某個變數被自動合併 reduce（而非重新給值），用 Annotated 把 reducer function 掛在那個變數的型態宣告上 在 node function 裡直接改變 state 的行為跟 python 本身類似 前篇 提的：如果 StateGraph(state_schema=dict) ，不但沒有 Annotated 無法 reduce，而且任何一個步驟只要沒有回傳那個 key，他以前的值就會消失 那麼，要不要用 reducer 呢？ reduce 的話，這個 key 的所有處理都自動經過 reducer，無需在每個 node 裡重寫同樣的程式加工 如果想臨時在某個 node 做不同處理，要額外花很多工夫（例如某個情況不想合併了，這樣的 邏輯要寫在同個 reducer 裡，且所有 node 都會這樣做 ） ( Human-in-the-Loop 除外) “Reduce” 這個心態， 讓每個 node 能獨立執行，不須理會別人在做啥！ （見下段） 總之，這取決於這個變數的本質，能否用同一種 reduce 的心態處理各種情境 關於 state, 有興趣追原始碼的可看 langgraph state.py 同時執行多節點: Superstep # 前一篇說 LangGraph 是「程式裡寫程式」… 忘掉這個比喻！ 輪到「你們」了 # 一個點可以連去多個點，多個點也可以連到同一個點！ graph. set_entry_point( "n1")
 graph. add_edge( "n1", "n2")
 graph. add_edge( "n1", "n3")
 graph. add_edge( "n2", "n4")
 graph. add_edge( "n3", "n4")
 graph. add_edge( "n4", END)
 請看 完整程式碼 ，猜猜執行結果是什麼？ 答案是 ++1+2+3+4 ，但執行的方法可能不是你想像的。這個 graph 只花了三步執行： 想像每個 node 都有旗子 當某個/群 node 執行完畢後，接下去連到的那個/群 node 都會舉起旗子（上一輪跑完的旗子放下來）。只要有舉旗子的 node,


---
*数据来源: Exa搜索 | 获取时间: 2026-02-19 20:08:35*