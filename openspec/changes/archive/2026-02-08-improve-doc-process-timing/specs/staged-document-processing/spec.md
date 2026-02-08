## ADDED Requirements

### Requirement: Stage-aligned document processing
系统 SHALL 在每次文档去重完成后立即处理对应的文档集合，而不是等待所有阶段结束后统一处理。

#### Scenario: 第一次去重后处理
- **WHEN** 第一阶段去重完成并产出 `first_processed_file_paths`
- **THEN** 系统 SHALL 立刻对第一阶段文档执行处理并生成对应的文档片段

#### Scenario: 第二次去重后处理
- **WHEN** 第二阶段去重完成并产出 `second_processed_file_paths`
- **THEN** 系统 SHALL 立刻对第二阶段文档执行处理并生成对应的文档片段

### Requirement: Aggregated processed nodes
系统 SHALL 将每次处理得到的文档片段累积到同一份 `llama_docs` 列表，并将其作为向量化输入。

#### Scenario: 累积处理结果
- **WHEN** 任一阶段完成文档处理
- **THEN** 系统 SHALL 将新的文档片段追加到已有 `llama_docs` 列表
