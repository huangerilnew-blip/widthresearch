# [muzinan110](https://www.cnblogs.com/muzinan110)

* [博客园](https://www.cnblogs.com/)
* [首页](https://www.cnblogs.com/muzinan110/)
* [新随笔](https://i.cnblogs.com/EditPosts.aspx?opt=1)
* [联系](https://msg.cnblogs.com/send/muzinan110)
* [订阅](javascript:void(0))
* [管理](https://i.cnblogs.com/)

# [LangGraph高级技巧：图结构应用程序删除消息的使用技巧](https://www.cnblogs.com/muzinan110/p/18540149 "发布于 2024-11-11 17:22")

## 一、消息删除的重要性

在图结构应用中，消息的累积可能会导致性能问题和不必要的复杂性。因此，适时删除不再需要的消息是很有必要的。LangGraph提供了几种方法来实现这一目标。

## 二、使用delete\_messages函数

LangGraph提供了`delete_messages`函数，它可以根据指定的条件删除消息。这个函数可以在图的节点中使用，特别是在处理完某些消息后。

```
from import  ToolMessage def process_and_delete(state): #  处理消息的逻辑 # ... #  删除已处理的消息 lambda x: isinstance(x, ToolMessage)) return  state #  在图结构中使用 Graph() graph.add_node(" process_and_delete ", process_and_delete) # ...
```

## 三、消息过滤技巧

除了直接删除消息，我们还可以使用过滤技巧来控制消息的流动：

### 3.1 使用条件边

```
graph.add_conditional_edge( " node_a ", " node_b ", condition lambda not isinstance(x, ToolMessage) )
```

### 3.2 在节点函数中进行过滤

```
def filter_messages(state): filtered_messages for in ' messages ' if not isinstance(msg, ToolMessage)] return " messages ": filtered_messages} graph.add_node(" filter "
```

## 四、消息修剪策略

在长时间运行的应用中，可能需要定期修剪消息以保持性能：

### 4.1 基于时间的修剪

```
from import datetime, timedelta def prune_old_messages(state): current_time  datetime.now() recent_messages  [ msg for in ' messages '] if) ] return " messages ": recent_messages} graph.add_node(" prune "
```

### 4.2 基于数量的修剪

```
def): return " messages " ' messages 'max_messages:]} graph.add_node(" prune " lambda
```

## 五、实际应用案例：智能客服系统

考虑一个智能客服系统，它需要处理用户查询，但同时要保持对话的简洁性：

```
from import ToolMessage, HumanMessage def process_query(state): #  处理用户查询 # ... return  state def summarize_and_prune(state): #  总结对话 ' messages ']) #  保留最新的人类消息和总结 for in ' messages ' if:] new_messages.append(ToolMessage(contentsummary)) return " messages ": new_messages} graph  Graph() graph.add_node(" process_query ", process_query) graph.add_node(" summarize_and_prune ", summarize_and_prune) graph.add_edge(" process_query " " summarize_and_prune ") graph.add_edge(" summarize_and_prune " " process_query "
```

## 总结

通过合理使用LangGraph提供的消息删除和过滤功能，我们可以有效地管理图结构应用中的消息流。这不仅可以提高应用的性能，还能使对话更加清晰和有针对性。在实际应用中，根据具体需求选择适当的消息管理策略至关重要。

posted @ 2024-11-11 17:22  [muzinan110](https://www.cnblogs.com/muzinan110)  阅读(613)  评论(0)    [收藏](javascript:void(0))  [举报](javascript:void(0))

[刷新页面](#)[返回顶部](#top)

[博客园](https://www.cnblogs.com/)   ©  2004-2026   
 [浙公网安备 33010602011771号](http://www.beian.gov.cn/portal/registerSystemInfo?recordcode=33010602011771) [浙ICP备2021040463号-3](https://beian.miit.gov.cn)

 