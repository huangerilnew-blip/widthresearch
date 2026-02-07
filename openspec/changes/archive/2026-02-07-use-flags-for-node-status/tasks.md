## 1. State Schema Updates

- [x] 1.1 在 `MultiAgentState` 中新增 `flags` 字段并定义节点名称列表
- [x] 1.2 在 `run` 初始状态中初始化 `flags` 为节点全量且默认 `false`
- [x] 1.3 将 `inited_vector_index` 初始值设置为 `false`

## 2. Node Flag Writes

- [x] 2.1 为所有节点成功路径写入 `flags["<node>"]=true`
- [x] 2.2 为异常捕获路径写入 `flags["<node>"]=error`，并移除 `state.error` 写入
- [x] 2.3 对“无输入跳过处理”的节点保持 `flags["<node>"]=false`

## 3. Run Status Aggregation

- [x] 3.1 在 `run` 汇总 `flags` 并生成执行成功/失败标记
- [x] 3.2 将失败节点列表写入返回结果元数据

## 4. Cleanup and Validation

- [x] 4.1 检查并移除残留的 `state.error` 使用
- [x] 4.2 更新日志输出以包含 `flags` 诊断信息
