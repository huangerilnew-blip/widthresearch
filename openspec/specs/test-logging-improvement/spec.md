# test-logging-improvement Specification

## Purpose
TBD - created by archiving change improve-deduplicator-test-logging. Update Purpose after archive.
## Requirements
### Requirement: 测试代码使用标准日志级别

`file_deduplicator.py` 的测试代码 SHALL 使用项目的标准日志记录方式，而不是 print 语句。

#### Scenario: 替换测试开始标记为 info 级别

- **WHEN** 测试代码开始执行（`__main__` 块）
- **THEN** SHALL 使用 `logger.info()` 输出测试标题和分隔符
- **AND** 分隔符使用 `logger.debug()` 级别

#### Scenario: 降级方案使用 warning 级别

- **WHEN** scikit-learn 不可用，系统将使用 MD5 回退方案
- **THEN** SHALL 使用 `logger.warning()` 记录降级信息
- **AND** 警告信息明确说明降级到 MD5 方案

#### Scenario: 初始化成功信息使用 info 级别

- **WHEN** FileDeduplicator 实例成功初始化
- **THEN** SHALL 使用 `logger.info()` 输出成功标记
- **AND** 配置详情（阈值、批处理大小、文件类型）使用 `logger.debug()` 级别

#### Scenario: 测试完成使用 info 级别

- **WHEN** 所有测试步骤执行完成
- **THEN** SHALL 使用 `logger.info()` 输出"测试通过"消息
- **AND** 分隔符使用 `logger.debug()` 级别

#### Scenario: 保留控制台日志配置

- **WHEN** 测试代码运行
- **THEN** SHALL 保留 `logging.basicConfig()` 配置，确保控制台输出
- **AND** SHALL 同时使用文件 logger（通过 `setup_logger(__name__)`）

