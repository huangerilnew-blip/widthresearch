# 将状态图的检查点保存到Redis 数据库_langgraph redis-CSDN博客

**URL**:
https://blog.csdn.net/u013172930/article/details/148042595

## 元数据
- 发布日期: 2025-05-18T00:00:00+00:00

## 完整内容
---

 最新推荐文章于 2025-06-22 20:25:15 发布 
 
 
 彬彬侠 
 
 最新推荐文章于 2025-06-22 20:25:15 发布 
 
 
 
 
 
 版权声明：本文为博主原创文章，遵循 CC 4.0 BY-SA 版权协议，转载请附上原文出处链接和本声明。
 
 
 
 
 
 
 
 
 langgraph.checkpoint.redis.RedisSaver 是 LangGraph 库中 langgraph.checkpoint.redis 模块的一个检查点保存器类，继承自 BaseCheckpointSaver ，用于将状态图的检查点保存到 Redis 数据库中。LangGraph 是 LangChain 生态的扩展框架，专注于构建复杂、有状态的 AI 系统，通过状态图（StateGraph）管理节点和边，支持动态路由、循环和状态管理。检查点（Checkpoint）是 LangGraph 的核心功能，用于在图执行的每一步保存状态，支持状态持久化、恢复和多轮交互。 RedisSaver 使用 Redis 作为后端存储，支持同步操作，适合生产环境中的高并发场景。 
 
 1. 定义与功能 
 1.1 类定义 
 RedisSaver 是 BaseCheckpointSaver 的子类，定义如下： 
 from langgraph. checkpoint. redis import RedisSaver
 class RedisSaver ( BaseCheckpointSaver): 
 """
 使用 Redis 数据库存储检查点的检查点保存器（同步操作）。
 参数：
 connection: Redis 连接对象（redis.Redis）。
 serde: 可选的序列化器，默认为 JsonPlusSerializer。
 ttl_config: TTL 配置，指定检查点存活时间和读取行为。
 示例：
 from redis import Redis
 from langgraph.checkpoint.redis import RedisSaver
 redis_client = Redis.from_url("redis://localhost:6379")
 checkpointer = RedisSaver(connection=redis_client)
 checkpointer.setup()
 """ 
 
 继承 ：继承自 BaseCheckpointSaver ，实现其抽象方法，提供 Redis 存储逻辑。 依赖 ：使用 redis 库（Python Redis 客户端）与 Redis 数据库交互，需 RedisJSON 和 RediSearch 模块支持。 作用 ：将检查点数据持久化存储到 Redis，支持生产级应用的高并发和快速访问。 
 1.2 核心功能 
 持久化存储 ：将检查点保存到 Redis，数据在应用重启后仍可恢复。 线程隔离 ：通过 thread_id 管理多线程，确保不同会话的状态独立。 同步操作 ：提供同步方法（如 get 、 put ），适合同步编程环境。 索引管理 ：通过 setup() 方法创建 Redis 索引（如 Checkpoints Index、Channel Values Index），优化查询。 TTL 支持 ：支持 Time-To-Live（TTL）配置，自动过期旧数据，减少存储占用。 序列化支持 ：通过 serde 参数支持自定义序列化，默认使用 JsonPlusSerializer 。 高性能 ：利用 Redis 的内存数据库特性，支持快速读写和高并发。 
 1.3 使用场景 
 生产环境 ：需要持久化存储的 AI 应用，如聊天机器人、自动化工作流。 多轮对话 ：保存对话历史，支持上下文连续性。 高并发场景 ：Redis 的高性能支持大规模并发访问。 状态恢复 ：从中断点恢复任务，确保工作流连续性。 同步编程 ：适合同步操作环境，需高性能存储的场景。 
 
 2. 参数与初始化 
 2.1 初始化参数 
 connection ： 
 类型 ： redis.Redis 描述 ：Redis 连接对象，必需，用于与 Redis 数据库交互。 示例 ： from redis import Redis
redis_client = Redis. from_url ( "redis://localhost:6379") 
 serde ： 
 类型 ： Optional[SerializerProtocol] 默认值 ： None （使用 JsonPlusSerializer ） 描述 ：序列化器，处理检查点数据的序列化和反序列化，支持 LangChain 和 LangGraph 原生类型。 ttl_config ： 
 类型 ： dict 默认值 ： {"default_ttl": 60, "refresh_on_read": True} 描述 ：TTL 配置，包含： 
 default_ttl ：检查点存活时间（分钟），默认 60 分钟。 refresh_on_read ：读取时是否刷新 TTL，默认 True 。 示例 ： ttl_config = { "default_ttl": 120, "refresh_on_read": False} 
 
 2.2 初始化方法 
 直接初始化 ： from redis import Redis
 from langgraph. checkpoint. redis import RedisSaver
redis_client = Redis. from_url ( "redis://localhost:6379") 
checkpointer = RedisSaver ( connection = redis_client, ttl_config = { "default_ttl": 120}) 
 使用连接字符串 ： checkpointer = RedisSaver. from_conn_string ( "redis://localhost:6379") 
 
 2.3 索引初始化 
 方法 ： setup() 
 描述 ：创建必要的 Redis 索引（如 Checkpoints Index、Channel Values Index），首次使用时必须调用。 调用 ： checkpointer. setup () 
 注意 ： 
 确保 Redis 实例支持 RedisJSON 和 RediSearch 模块。 Redis &lt; 8.0 需使用 Redis Stack 或单独安装模块。 
 
 3. 使用方法 
 3.1 安装与环境准备 
 安装依赖 ： pip install langgraph-checkpoint-redis
 
 必需依赖： redis&gt;=5.2.1 、 redisvl&gt;=0.5.1 、 langgraph-checkpoint&gt;=2.0.24 。 可选：安装 Redis Stack 以支持 RedisJSON 和 RediSearch。 Redis 配置 ： 
 确保 Redis 服务器运行，推荐版本 8.0+，或使用 Redis Stack。 配置连接信息（主机、端口、数据库、密码）。 验证 RedisJSON 和 RediSearch 模块是否启用： redis-cli MODULE LIST
 连接设置 ： 
 创建 Redis 连接时，建议配置连接池： from redis import Redis
redis_client = Redis. from_url ( "redis://localhost:6379", max_connections = 20) 
 
 3.2 集成到状态图 
 创建状态图 ： from langgraph. graph import StateGraph
builder = StateGraph ( int) 
builder. add_node ( "add_one", lambda x: x + 1) 
builder. set_entry_point ( "add_one") 
builder. set_finish_point ( "add_one") 
 编译图 ： from langgraph. checkpoint. redis import RedisSaver
 from redis import Redis
redis_client = Redis. from_url ( "redis://localhost:6379") 
checkpointer = RedisSaver ( connection = redis_client) 
checkpointer. setup () 
graph = builder. compile ( checkpointer = checkpointer) 
 运行图 ： config = { "configurable": { "thread_id": "thread-1"}} 
result = graph. invoke ( 1, config = config) 
 print ( result) # 输出: 2 
 
 3.3 操作检查点 
 获取检查点 ： checkpoint = checkpointer. get_tuple ( config) 
 print ( checkpoint) # 输出: CheckpointTuple(...) 
 列出检查点 ： checkpoints = list ( checkpointer. list ( config)) 
 for cp in checkpoints: 
 print ( cp) 
 保存检查点 ：由状态图自动调用 put ，无需手动操作。 
 3.4 完整示例：多轮对话 
 以下示例展示如何使用 RedisSaver 实现多轮对话： 
 from typing import List
 from typing_extensions import TypedDict
 from langgraph. graph import StateGraph, START
 from langgraph. checkpoint. redis import RedisSaver
 from langchain_core. messages import HumanMessage
 from redis import Redis
 # 定义状态 
 class State ( TypedDict): 
 messages: List [ dict] 
 # 定义节点 
 def agent_node ( state: State) - &gt; State: 
 last_message = state [ "messages"] [ - 1] [ "content"] 
 return { "messages": state [ "messages"] +


---
*数据来源: Exa搜索 | 获取时间: 2026-02-20 20:40:47*