## MODIFIED Requirements

### Requirement: Stage-aligned document processing
系统 SHALL 在每次文档去重完成后立即处理对应的文档集合，并将处理结果写入阶段对应的文档片段列表。

#### Scenario: 第一次去重后处理
- **WHEN** 第一阶段去重完成并产出 `first_processed_file_paths`
- **THEN** 系统 SHALL 立刻对第一阶段文档执行处理并生成对应的文档片段
- **AND** 系统 SHALL 将处理结果写入 `first_llama_docs`

#### Scenario: 第二次去重后处理
- **WHEN** 第二阶段去重完成并产出 `second_processed_file_paths`
- **THEN** 系统 SHALL 立刻对第二阶段文档执行处理并生成对应的文档片段
- **AND** 系统 SHALL 将处理结果写入 `second_llama_docs`

### Requirement: Aggregated processed nodes
系统 SHALL 维护 `first_llama_docs` 与 `second_llama_docs` 两份文档片段列表，并在向量化时基于完成状态合并入库。

#### Scenario: 第一阶段结果就绪时入库
- **WHEN** `process_first_documents` 完成且 `state["flags"]["process_first_documents"]` 为 `true`
- **THEN** 系统 SHALL 将 `first_llama_docs` 入库向量化

#### Scenario: 第二阶段结果就绪时入库
- **WHEN** `process_second_documents` 完成且 `state["flags"]["process_second_documents"]` 为 `true`
- **THEN** 系统 SHALL 将 `second_llama_docs` 入库向量化
