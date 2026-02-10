## Context

当前代码库中缺少统一的 JSON 文件行级读取入口，相关模块可能各自实现，导致行为不一致。此次变更需要在 `core/rag/models.py` 中新增 `jsonreader` 类，用于将 `.json` 文件按行读取并返回 `list[str]`。

## Goals / Non-Goals

**Goals:**
- 提供一个简单、稳定的 JSON 文件逐行读取入口，输出 `list[str]`。
- 仅允许 `.json` 文件，扩展名校验失败时给出明确错误。
- 对文件不存在、读取失败等场景给出清晰异常，便于上层处理。

**Non-Goals:**
- 不引入新的第三方依赖（如 jsonlines）。
- 不处理 JSON 内容解析或结构校验，仅返回每行文本。
- 不支持 `.jsonl` / `.ndjson` 等其他扩展名（若后续需要可另起变更）。

## Decisions

- **类命名**：采用 `jsonreader` 类名，遵循需求描述而非传统 CamelCase。
  - 备选：`JsonReader` 更符合 Python 风格，但会偏离需求，故不采用。
- **扩展名校验**：使用 `Path(file_path).suffix.lower()` 判断，仅接受 `.json`。
  - 备选：允许 `.jsonl` 等扩展名，可能与“只允许 json 类文件使用”的要求不符，故不采用。
- **读取方式**：以 `utf-8` 打开文件，逐行读取并使用 `rstrip("\n")` 去除换行符后加入列表。
  - 备选：保留换行符，易造成上层处理歧义，故不采用。

## Risks / Trade-offs

- **大文件内存占用** → 返回 `list[str]` 必然一次性加载全部行；在需求范围内接受。
- **扩展名限制过严** → `.jsonl` 文件会被拒绝；通过明确错误信息引导用户。
