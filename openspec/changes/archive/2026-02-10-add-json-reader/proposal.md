## Why

当前缺少统一的 JSON 文件行级读取入口，导致不同模块可能重复实现、行为不一致。新增 jsonreader 类可以明确约束只处理 .json 文件，并稳定输出 list[str]，便于后续检索与处理。

## What Changes

- 在 `core/rag/models.py` 中新增 `jsonreader` 类，提供将 JSON 文件按行读取并返回 `list[str]` 的方法。
- 读取前校验文件扩展名，仅允许 `.json` 文件；非法扩展名返回明确错误。
- 为文件读取与解析失败提供清晰的异常路径，便于上层处理。

## Capabilities

### New Capabilities
- `json-line-reader`: 提供统一的 JSON 文件逐行读取能力（类 `jsonreader`），输出 `list[str]`。

### Modified Capabilities

<!-- 无 -->

## Impact

- 影响 `core/rag/models.py` 及其调用方。
- 不引入新依赖、不修改外部 API。
