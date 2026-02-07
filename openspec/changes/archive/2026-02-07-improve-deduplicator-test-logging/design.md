## Context

`file_deduplicator.py` 已经在文件开头导入了 `setup_logger(__name__)` 并初始化了 `logger`。测试代码部分（`__main__` 块）使用 `print()` 语句输出测试信息。项目采用统一的日志管理策略，所有模块应使用 `core.log_config.setup_logger` 进行日志记录。

## Goals / Non-Goals

**Goals:**
- 将测试代码中的 `print()` 语句替换为 `logger` 调用
- 根据信息类型选择合适的日志级别（info、warning、debug）
- 保持测试代码的功能和输出信息完整性

**Non-Goals:**
- 不修改测试代码的业务逻辑
- 不修改类内部的日志记录方式
- 不修改 `logging.basicConfig()` 配置（保留控制台输出）

## Decisions

### Decision 1: 日志级别选择策略

- **INFO**: 用于测试流程的关键节点（开始、成功、完成）和重要状态信息
- **WARNING**: 用于降级方案警告（如 sklearn 不可用时的 MD5 回退）
- **DEBUG**: 用于装饰性分隔符和详细配置参数

**Rationale**: 这种分类符合最佳实践，使生产环境可以灵活控制日志详细程度。

### Decision 2: logger 使用方式

使用已在文件顶部初始化的 `logger` 实例，不创建新的 logger。

**Rationale**: 保持一致性，避免重复配置。

### Decision 3: 保留 logging.basicConfig()

测试代码中的 `logging.basicConfig()` 保留不变，确保控制台输出同时存在。

**Rationale**: 测试代码通常需要即时控制台反馈，保留 basicConfig 可同时支持文件日志和控制台输出。
