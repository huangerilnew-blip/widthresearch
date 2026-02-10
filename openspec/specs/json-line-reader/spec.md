## ADDED Requirements

### Requirement: jsonreader 逐行读取 JSON 文件
系统必须提供 `jsonreader` 类，用于将输入的 JSON 文件按行读取并返回 `list[str]`，列表元素顺序与文件行顺序一致。

#### Scenario: 读取有效 JSON 文件
- **WHEN** 提供存在且扩展名为 `.json` 的文件路径
- **THEN** 返回的 `list[str]` 包含文件中每一行的字符串内容

### Requirement: 仅允许 .json 扩展名
系统必须在读取前校验文件扩展名，仅允许 `.json` 文件；不符合要求的文件必须抛出明确异常。

#### Scenario: 扩展名校验失败
- **WHEN** 提供的文件路径扩展名不是 `.json`
- **THEN** 系统抛出异常并说明仅允许 `.json` 文件

### Requirement: 读取失败时抛出异常
系统在文件不存在或读取失败时必须抛出异常，确保上层可以感知失败原因。

#### Scenario: 文件不存在
- **WHEN** 提供的文件路径不存在
- **THEN** 系统抛出文件不存在的异常
