## Why

`file_deduplicator.py` 的测试代码使用 `print()` 语句输出测试信息，不符合项目的日志规范。该项目使用统一的 `core.log_config.setup_logger` 进行日志管理。测试代码应使用适当的日志级别（info、warning、debug）来替换 print 语句，以提高一致性和生产环境的可维护性。

## What Changes

- 将 `file_deduplicator.py` 测试代码中的 `print()` 语句替换为 `logger` 调用
- 根据信息类型使用合适的日志级别：
  - `logger.info()` - 测试开始/完成标记、关键成功信息
  - `logger.warning()` - 降级方案警告（如 sklearn 不可用时）
  - `logger.debug()` - 装饰性分隔符、详细配置参数

## Capabilities

### New Capabilities
<!-- 无新增功能 -->

### Modified Capabilities
- `file_deduplicator.py 测试代码`: 改进日志输出一致性，符合项目日志规范

## Impact

- `core/file_deduplicator.py` (第 292-317 行): 替换测试代码中的 print 语句为 logger 调用
