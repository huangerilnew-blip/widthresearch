## 1. Document structure analysis

- [x] 1.1 盘点 documents 来源字段（downloaded_papers + 去重路径解析）并整理字段优先级
- [x] 1.2 明确 source/title/url 的提取规则与回退值

## 2. get_nodes 元数据规范化

- [x] 2.1 调整 get_nodes 元数据构建，仅写入 source/title/url
- [x] 2.2 统一 PDF 与 MarkdownReader 的 metadata 写入逻辑并补充缺失回退值

## 3. 验证与说明

- [x] 3.1 运行静态诊断（lsp_diagnostics）确保改动无新增问题
- [x] 3.2 更新/补充必要日志或注释说明字段来源（如需要）
